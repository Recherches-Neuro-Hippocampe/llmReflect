import logging
import os
import shutil


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
    """A simple interface copying the log file to a designated place.

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


def openai_cb_2_str(cb) -> str:
    tmp_str = ""
    tmp_str += f"[Total Tokens] {cb.total_tokens}, "
    tmp_str += f"[Prompt Tokens] {cb.prompt_tokens}, "
    tmp_str += f"[Completion Tokens] {cb.completion_tokens}, "
    tmp_str += f"[Successful Requests] {cb.successful_requests}, "
    tmp_str += f"[Total Cost (USD) $] {cb.total_cost}"
    return tmp_str


addLoggingLevel("COST", 25)
