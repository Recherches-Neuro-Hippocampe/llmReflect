Module llmreflect.Chains.BasicChain
===================================

Classes
-------

`BasicChain(agent: llmreflect.Agents.BasicAgent.BasicAgent, retriever: llmreflect.Retriever.BasicRetriever.BasicRetriever, **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    Abstract class for Chain class.
    A chain class should be the atomic unit for completing a job.
    A chain contains at least two components:
    1. an agent 2. a retriever
    A chain object must have the function to perform a job.
    Each chain is also equipped with a logger
    
    Args:
        agent (BasicAgent): An instance of Agent class.
        retriever (BasicRetriever): An instance of Retriever class.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * llmreflect.Chains.BasicChain.BasicCombinedChain
    * llmreflect.Chains.DatabaseChain.DatabaseAnswerChain
    * llmreflect.Chains.DatabaseChain.DatabaseGradingChain
    * llmreflect.Chains.DatabaseChain.DatabaseQuestionChain
    * llmreflect.Chains.DatabaseChain.DatabaseSelfFixChain
    * llmreflect.Chains.ModerateChain.ModerateChain

    ### Class variables

    `AgentClass`
    :   Helper class that provides a standard way to create an ABC using
        inheritance.

    `RetrieverClass`
    :   Helper class that provides a standard way to create an ABC using
        inheritance.

    ### Static methods

    `from_config(**kwargs: Any) ‑> Any`
    :   Initialize an instance of a Chain class from configuration.
        
        Returns:
            Any: An instance of the Chain itself.

    `get_config_dict(local: bool = True) ‑> dict`
    :   Return a form (instruction) of the configuration
        required by a chain.
        Which is going to be converted into a prettier string by the
        `classproperty` decorator.
        
        Args:
            local (bool, optional): whether to use local model.
                If False, will use OpenAI Api.
                Defaults to True.
        
        Returns:
            dict: The instructions to initialize the chain.

    `get_required_retriever(**kwargs) ‑> llmreflect.Retriever.BasicRetriever.BasicRetriever`
    :   A class method to get an instance from required Retriever class.
        
        Returns:
            BasicRetriever: An instance of Retriever class.

    `init(agent: llmreflect.Agents.BasicAgent.BasicAgent, retriever: llmreflect.Retriever.BasicRetriever.BasicRetriever) ‑> Any`
    :   A class method to initialize the class itself.
        Not put in any use for now.
        
        Args:
            agent (BasicAgent): An instance of an Agent class.
            retriever (BasicRetriever): An instance of a Retriever class.
        
        Returns:
            Any: An instance of the chain itself.

    `perform(**kwargs: Any) ‑> Any`
    :   Core function to perform.
        Returns:
            Any: the chain execution result.

    ### Instance variables

    `local_config_dict`
    :

    `openai_config_dict`
    :

    ### Methods

    `perform_cost_monitor(self, budget: float = 100, **kwargs: Any) ‑> Any`
    :   performing the chain function while
        logging the cost and other llm behaviors
        Args:
            budget (float, optional): _description_. Defaults to 100.
        
        Returns:
            Any: the chain execution result and a llm callback handler

`BasicCombinedChain(chains: List[llmreflect.Chains.BasicChain.BasicChain])`
:   Abstract class for combined Chain class.
    A combined chain is a chain with multiple chains
    A chain class should be the atomic unit for completing a job.
    A chain object must have the function to perform a job.
    
    Initialize an instance of the BasicCombinedChain class.
    
    Args:
        chains (List[BasicChain]): A list of BasicChains.

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

    ### Descendants

    * llmreflect.Chains.DatabaseChain.DatabaseAnswerNFixChain
    * llmreflect.Chains.DatabaseChain.DatabaseModerateNAnswerNFixChain
    * llmreflect.Chains.DatabaseChain.DatabaseQnAGradingChain

    ### Class variables

    `REQUIRED_CHAINS`
    :

    ### Static methods

    `from_config(**kwargs) ‑> llmreflect.Chains.BasicChain.BasicChain`
    :   Initialize from configuration
        
        Returns:
            BasicChain: An instance of the BasicCombinedChain.
                which belongs to BasicChain.

    `get_config_dict(local: bool = True) ‑> dict`
    :   A recursive function to return the configuration.
        
        Args:
            local (bool, optional): whether use local LLM.
                Defaults to True.
        
        Returns:
            dict: a configuration dictionary in a nest form.

`PrettyDict(value: Any)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = {}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)
    
    This a wrapper class to print pretty dictionary.
    
    Args:
        value (Any): A dictionary usually.

    ### Ancestors (in MRO)

    * builtins.dict

`classproperty(method: Callable)`
:   A decorator, a wrapper class for class property: configuration.
    Since the configurations as dictionaries are ugly,
    so we convert it to a json format to make it look better.
    Args:
        method (Callable): _description_