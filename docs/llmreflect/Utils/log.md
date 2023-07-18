Module llmreflect.Utils.log
===========================

Functions
---------

    
`addLoggingLevel(levelName: str, levelNum: int, methodName: str = None)`
:   Comprehensively adds a new logging level to the `logging` module and the
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

    
`check_current_openai_balance(input_prompt: str, max_output_tokens: int, model_name: str, logger: Any = None) ‑> bool`
:   Check if the budget balance can cover this round of llm run.
    
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

    
`clear_logs()`
:   remove all logs

    
`export_log(dir: str)`
:   A simple interface copying the log file to a designated directory.
    
    Args:
        file_path (_type_): designated directory

    
`get_logger(name: str = 'Default') ‑> logging.Logger`
:   A function to get a logger given by a name.
    All logs are expected to go into one file, 'logs/llmreflect.log'
    Args:
        name (str, optional): _description_. Defaults to "Default".
    
    Returns:
        logging.Logger: _description_

    
`get_openai_tracer(id: str = '', budget: float = 0.1) ‑> Generator[llmreflect.Utils.log.OpenAITracer, None, None]`
:   Get OpenAI callback handler in a context manager.

    
`message(msg, color=None)`
:   

    
`openai_cb_2_str(cb: llmreflect.Utils.log.OpenAITracer) ‑> str`
:   converting openai tracer info to one string.
    Args:
        cb (OpenAITracer): tracer/callback handlers for openai
    
    Returns:
        str: A string describing the cost

    
`traces_2_str(cb: llmreflect.Utils.log.OpenAITracer) ‑> str`
:   converting openai tracer info to one string.
    Similar to openai_cb_2_str function but with more details
    Args:
        cb (OpenAITracer): tracer/callback handlers for openai
    
    Returns:
        str: A string describing the cost

Classes
-------

`CustomFormatter(fmt)`
:   Logging colored formatter,
    adapted from https://stackoverflow.com/a/56944256/3638629
    
    Initialize the formatter with specified format strings.
    
    Initialize the formatter either with the specified format string, or a
    default as described above. Allow for specialized date formatting with
    the optional datefmt argument. If datefmt is omitted, you get an
    ISO8601-like (or RFC 3339-like) format.
    
    Use a style parameter of '%', '{' or '$' to specify that you want to
    use one of %-formatting, :meth:`str.format` (``{}``) formatting or
    :class:`string.Template` formatting in your format string.
    
    .. versionchanged:: 3.2
       Added the ``style`` parameter.

    ### Ancestors (in MRO)

    * logging.Formatter

    ### Class variables

    `blue`
    :

    `bold_red`
    :

    `grey`
    :

    `red`
    :

    `reset`
    :

    `yellow`
    :

    ### Methods

    `format(self, record)`
    :   Format the specified record as text.
        
        The record's attribute dictionary is used as the operand to a
        string formatting operation which yields the returned string.
        Before formatting the dictionary, a couple of preparatory steps
        are carried out. The message attribute of the record is computed
        using LogRecord.getMessage(). If the formatting string uses the
        time (as determined by a call to usesTime(), formatTime() is
        called to format the event time. If there is exception information,
        it is formatted using formatException() and appended to the message.

`LLMTRACE(input: str = '', output: str = '', completion_tokens: int = 0, prompt_tokens: int = 0, model_name: str = '', completion_cost: float = 0.0, prompt_cost: float = 0.0)`
:   

`OpenAITracer(id: str = '', budget: float = 0.01)`
:   Callback Handler that tracks OpenAI info.

    ### Ancestors (in MRO)

    * langchain.callbacks.openai_info.OpenAICallbackHandler
    * langchain.callbacks.base.BaseCallbackHandler
    * langchain.callbacks.base.LLMManagerMixin
    * langchain.callbacks.base.ChainManagerMixin
    * langchain.callbacks.base.ToolManagerMixin
    * langchain.callbacks.base.RetrieverManagerMixin
    * langchain.callbacks.base.CallbackManagerMixin
    * langchain.callbacks.base.RunManagerMixin

    ### Instance variables

    `budget`
    :

    `budget_rest`
    :

    ### Methods

    `on_chain_error(self, error: Exception | KeyboardInterrupt, *, run_id: uuid.UUID, parent_run_id: uuid.UUID | None = None, **kwargs: Any) ‑> Any`
    :   Run when chain errors.

    `on_llm_end(self, response: langchain.schema.output.LLMResult, **kwargs: Any) ‑> None`
    :   Collect token usage.

    `on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) ‑> None`
    :   Print out the prompts.