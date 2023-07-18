Module llmreflect.Chains.BasicChain
===================================

Classes
-------

`BasicChain(agent: llmreflect.Agents.BasicAgent.Agent, retriever: llmreflect.Retriever.BasicRetriever.BasicRetriever)`
:   Abstract class for Chain class.
    A chain class should be the atomic unit for completing a job.
    A chain contains at least two components:
    1. an agent 2. a retriever
    A chain object must have the function to perform a job.
    Each chain is also equipped with a logger

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * llmreflect.Chains.BasicChain.BasicCombinedChain
    * llmreflect.Chains.DatabaseChain.DatabaseAnswerChain
    * llmreflect.Chains.DatabaseChain.DatabaseGradingChain
    * llmreflect.Chains.DatabaseChain.DatabaseQuestionChain
    * llmreflect.Chains.DatabaseChain.DatabaseSelfFixChain
    * llmreflect.Chains.ModerateChain.ModerateChain

    ### Static methods

    `from_config(open_ai_key: str, prompt_name: str = 'question_database', temperature: float = 0.0) ‑> Any`
    :   Initialize a BasicChain class from configurations
        Args:
            open_ai_key (str): openai api key
            prompt_name (str, optional): prompt to use.
            temperature (float, optional): how unstable the llm should behave.
                Defaults to 0.0.
        
        Returns:
            BasicChain: the Basic Chain class itself.

    `perform(**kwargs: Any) ‑> Any`
    :   Core function to perform.
        Returns:
            Any: the chain execution result.

    ### Methods

    `perform_cost_monitor(self, budget: float = 100, **kwargs: Any)`
    :

`BasicCombinedChain(chains: List[llmreflect.Chains.BasicChain.BasicChain])`
:   Abstract class for combined Chain class.
    A combined chain is a chain with multiple chains
    A chain class should be the atomic unit for completing a job.
    A chain object must have the function to perform a job.

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

    ### Descendants

    * llmreflect.Chains.DatabaseChain.DatabaseAnswerNFixChain
    * llmreflect.Chains.DatabaseChain.DatabaseModerateNAnswerNFixChain
    * llmreflect.Chains.DatabaseChain.DatabaseQnAGradingChain