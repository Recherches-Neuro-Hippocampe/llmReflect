import logging
import os
import shutil
from uuid import UUID
from langchain.callbacks import OpenAICallbackHandler
from langchain.callbacks.openai_info import standardize_model_name
from langchain.callbacks.openai_info import MODEL_COST_PER_1K_TOKENS
from langchain.callbacks.openai_info import get_openai_token_cost_for_model
from typing import Dict, Any, List, Generator, Optional
from langchain.schema import LLMResult
from contextlib import contextmanager
from contextvars import ContextVar
import tiktoken


class OpenAITracer(OpenAICallbackHandler):
    def __init__(self, id: str = "", budget: float = 0.01) -> None:
        super().__init__()
        self.traces = []
        self.id = id
        self.raise_error = True
        self._budget = budget

    @property
    def budget(self):
        return self._budget

    @property
    def budget_rest(self):
        return self._budget - self.total_cost

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        self.cur_trace = LLMTRACE(input=prompts[0])

    def on_chain_error(self, error: Exception | KeyboardInterrupt, *,
                       run_id: UUID, parent_run_id: UUID | None = None,
                       **kwargs: Any) -> Any:
        self.cur_trace.output = str(error)
        self.traces.append(self.cur_trace)
        return super().on_chain_error(error,
                                      run_id=run_id,
                                      parent_run_id=parent_run_id,
                                      **kwargs)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Collect token usage."""
        if response.llm_output is None:
            return None
        else:
            self.cur_trace.output = response.generations[0][0].text
        self.successful_requests += 1

        if "token_usage" not in response.llm_output:
            return None
        token_usage = response.llm_output["token_usage"]

        self.cur_trace.completion_tokens = token_usage.get(
            "completion_tokens", 0)
        self.cur_trace.prompt_tokens = token_usage.get("prompt_tokens", 0)
        self.cur_trace.model_name = standardize_model_name(
            response.llm_output.get("model_name", ""))
        if self.cur_trace.model_name in MODEL_COST_PER_1K_TOKENS:
            self.cur_trace.completion_cost = get_openai_token_cost_for_model(
                self.cur_trace.model_name,
                self.cur_trace.completion_tokens,
                is_completion=True
            )
            self.cur_trace.prompt_cost = get_openai_token_cost_for_model(
                self.cur_trace.model_name,
                self.cur_trace.prompt_tokens)
            self.cur_trace.total_cost = self.cur_trace.prompt_cost + \
                self.cur_trace.completion_cost
        self.cur_trace.total_tokens = token_usage.get("total_tokens", 0)
        self.total_tokens += self.cur_trace.total_tokens
        self.total_cost += self.cur_trace.total_cost
        self.traces.append(self.cur_trace)


class LLMTRACE:
    def __init__(
            self,
            input: str = "",
            output: str = "",
            completion_tokens: int = 0,
            prompt_tokens: int = 0,
            model_name: str = "",
            completion_cost: float = 0.,
            prompt_cost: float = 0.,
    ) -> None:
        self.input = input
        self.output = output
        self.completion_tokens = completion_tokens
        self.prompt_tokens = prompt_tokens
        self.model_name = model_name
        self.completion_cost = completion_cost
        self.prompt_cost = prompt_cost
        self.total_cost = prompt_cost + completion_cost
        self.total_tokens = prompt_tokens + completion_tokens


openai_trace_var: ContextVar[Optional[OpenAITracer]] = ContextVar(
    "openai_trace", default=None
)


@contextmanager
def get_openai_tracer(id: str = "",
                      budget: float = 0.1) -> \
        Generator[OpenAITracer, None, None]:
    """Get OpenAI callback handler in a context manager."""
    cb = OpenAITracer(id=id, budget=budget)
    openai_trace_var.set(cb)
    yield cb
    openai_trace_var.set(None)


def check_current_openai_balance(input_prompt: str,
                                 max_output_tokens: int,
                                 model_name: str,
                                 logger: Any = None) -> bool:
    """Check if the budget balance can cover this round of llm run.

    Args:
        input_prompt (str): the input prompt for the llm
        max_output_tokens (int): the maximum number of completion tokens,
            configured in llm class.
        model_name (str): the model name used for referencing,
            Check LLM_BACKBONE_MODEL.
        logger (Any, optional): Log predicted cost information
            when logger provided.

    Returns:
        bool: _description_
    """
    openai_tracer = openai_trace_var.get()
    encoding = tiktoken.get_encoding("cl100k_base")
    input_tokens = len(encoding.encode(input_prompt))
    input_cost = get_openai_token_cost_for_model(
        model_name=model_name,
        num_tokens=input_tokens,
        is_completion=False
    )
    possible_output_cost = get_openai_token_cost_for_model(
        model_name=model_name,
        num_tokens=max_output_tokens,
        is_completion=True
    )
    next_possible_cost = input_cost + possible_output_cost
    if logger:
        logger.debug(f"Total cost now: {openai_tracer.total_cost}")
        logger.debug(f"Next round possible cost: {next_possible_cost}")
    return openai_tracer.budget_rest >= next_possible_cost


class CustomFormatter(logging.Formatter):
    """Logging colored formatter,
    adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }
        self.default_fmt = self.yellow + self.fmt + self.reset

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.default_fmt)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def addLoggingLevel(levelName: str, levelNum: int, methodName: str = None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        raise AttributeError(
            '{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError(
            '{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError(
            '{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


def get_logger(name: str = "Default") -> logging.Logger:
    """
    A function to get a logger given by a name.
    All logs are expected to go into one file, 'logs/llmreflect.log'
    Args:
        name (str, optional): _description_. Defaults to "Default".

    Returns:
        logging.Logger: _description_
    """
    tmp_log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    if not os.path.exists(tmp_log_dir):
        os.mkdir(tmp_log_dir)

    logger = logging.getLogger(f'llmreflect/{name}')
    logger.setLevel(logging.DEBUG)

    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    handler_std = logging.StreamHandler()
    handler_std.setLevel(logging.INFO)
    handler_std.setFormatter(CustomFormatter(format_str))

    handler_file = logging.FileHandler(
        filename=os.path.join(
            tmp_log_dir, 'llmreflect.log'), mode='a+',)
    formatter = logging.Formatter(format_str)
    handler_file.setFormatter(formatter)

    logger.addHandler(handler_std)
    logger.addHandler(handler_file)
    return logger


def export_log(dir: str):
    """A simple interface copying the log file to a designated directory.

    Args:
        file_path (_type_): designated directory
    """
    tmp_log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    logger = get_logger("log export")
    n_s = 0
    n_f = 0
    for file_name in os.listdir(tmp_log_dir):
        try:
            shutil.copy2(os.path.join(tmp_log_dir, file_name), dir)
            n_s += 1
        except Exception as e:
            logger.error(str(e))
            n_f += 1
    logger.info(f"Logger exported, {n_s} files copied, {n_f} filed failed.")


def clear_logs():
    """remove all logs
    """
    tmp_log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    shutil.rmtree(tmp_log_dir)


def message(msg, color=None):
    COLORS = {
        'red': '\033[31m',
        'green': '\033[32m',
        'blue': '\033[34m',
        'reset': '\033[0m',
        'yellow': '\033[33m'
    }

    if color not in COLORS.keys():
        color = 'reset'

    print(f'{COLORS[color]}{msg}{COLORS["reset"]}')


def openai_cb_2_str(cb: OpenAITracer) -> str:
    """
    converting openai tracer info to one string.
    Args:
        cb (OpenAITracer): tracer/callback handlers for openai

    Returns:
        str: A string describing the cost
    """
    tmp_str = ""
    tmp_str += f"[Total Tokens] {cb.total_tokens}, "
    tmp_str += f"[Successful Requests] {cb.successful_requests}, "
    tmp_str += f"[Total Cost (USD) $] {cb.total_cost}"
    return tmp_str


def traces_2_str(cb: OpenAITracer) -> str:
    """
    converting openai tracer info to one string.
    Similar to openai_cb_2_str function but with more details
    Args:
        cb (OpenAITracer): tracer/callback handlers for openai

    Returns:
        str: A string describing the cost
    """
    total_str = "\n"
    for trace in cb.traces:
        tmp_str = ""
        tmp_str += f"[Model Name] {trace.model_name}\n"
        tmp_str += f"[Brief Input] {trace.input[0:100]}\n"
        tmp_str += f"[Total Tokens] {trace.total_tokens}\n"
        tmp_str += f"[Completion Tokens] {trace.completion_tokens}\n"
        tmp_str += f"[Prompt Tokens] {trace.prompt_tokens}\n"
        tmp_str += f"[Completion Cost] {trace.completion_cost}\n"
        tmp_str += f"[Prompt Cost] {trace.prompt_cost}\n"
        tmp_str += f"[Total Cost] {trace.total_cost}\n"
        tmp_str += "====================================\n\n"
        total_str += tmp_str
    return total_str


addLoggingLevel("COST", 25)  # add a logging level for cost
