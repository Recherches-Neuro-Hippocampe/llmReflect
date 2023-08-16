Module llmreflect.Agents.BasicAgent
===================================

Classes
-------

`Agent(llm_core: llmreflect.LLMCore.LLMCore.LLMCore, **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    Initialization for Agent class.
    
    Args:
        llm_core (LLMCore): An instance of LLMCore class
            Used for inferencing.

    ### Ancestors (in MRO)

    * llmreflect.Agents.BasicAgent.BasicAgent
    * abc.ABC

    ### Descendants

    * llmreflect.Agents.DatabaseAgent.DatabaseAgent
    * llmreflect.Agents.EvaluationAgent.DatabaseGradingAgent
    * llmreflect.Agents.ModerateAgent.DatabaseModerateAgent
    * llmreflect.Agents.QuestionAgent.DatabaseQuestionAgent

    ### Static methods

    `from_config(llm_config: dict = {}, other_config: dict = {}) ‑> llmreflect.Agents.BasicAgent.BasicAgent`
    :   Initialize an instance of Agent class from config.
        
        Args:
            llm_config (dict, optional): Configuration for the LLMCore.
                Usually, in llmreflect, the Agent class is always used
                inside a Chain class.
                To know more about this config of your chain,
                You can always use `NameOfYourChain.local_config_dict` or
                `NameOfYourChain.openai_config_dict`
                Also, it is used for either `init_llm_from_llama` or
                `init_llm_from_openai` functions.
                Defaults to {}.
            other_config (dict, optional): Configuration other than llm_config
                Defaults to {}.
        
        Returns:
            BasicAgent: An instance of the Agent class.

    `init_llm_from_llama(model_path: str, prompt_name: str, max_total_tokens: int = 4096, max_output_tokens: int = 512, temperature: float = 0.0, verbose: bool = False, n_gpus_layers: int = 8, n_threads: int = 16, n_batch: int = 512) ‑> llmreflect.Agents.BasicAgent.BasicAgent`
    :   Return a llama.cpp llmcore instance.
        Args:
            model_path (str): path to the model file,
                options can be found in LLMCORE.LLMCORE.LOCAL_MODEL
            prompt_name (str): name of the prompt file
            max_total_tokens (int, optional): the entire context length.
                Defaults to 4096.
            max_output_tokens (int, optional): the maximum length
                for the completion. Defaults to 512.
            temperature (float, optional): The temperature to use for
                sampling. The lower the stabler. Defaults to 0.
            verbose (bool, optional): whether to show. Defaults to False.
            n_gpus_layers (int, optional): Number of layers to be loaded
                into gpu memory. Defaults to 8.
            n_threads (int, optional): Number of threads to use.
                Defaults to 16.
            n_batch (int, optional): Maximum number of prompt tokens to batch
                together when calling llama_eval. Defaults to 512.
        
        Returns:
            BasicAgent: Return a llama.cpp llmcore instance.

    `init_llm_from_openai(open_ai_key: str, prompt_name: str, max_output_tokens: int = 512, temperature: float = 0.0, llm_model='gpt-3.5-turbo') ‑> llmreflect.Agents.BasicAgent.BasicAgent`
    :   Return an openai llmcore instance.
        Args:
            open_ai_key (str): OpenAI key
            prompt_name (str, optional): name for the prompt. Defaults to ''.
            max_output_tokens (int, optional): maximum number of output tokens.
                Defaults to 512.
            temperature (float, optional): Flexibility of the output.
                Defaults to 0.0.
            llm_model (str, optional): string indicating the mode to use.
                Should be included in class LLM_BACKBONE_MODEL.
                Defaults to LLM_BACKBONE_MODEL.gpt_3_5_turbo.
        
        Returns:
            BasicAgent: Return an openai llmcore instance.

`BasicAgent(llm_core: llmreflect.LLMCore.LLMCore.LLMCore, **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    In this design each agent should have
    a retriever, retriever is for retrieving the final result based
    on the gross output by LLM.
    For example, a database retriever does the following job:
    extract the sql command from the llm output and then
    execute the command in the database.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * llmreflect.Agents.BasicAgent.Agent

    ### Class variables

    `PROMPT_NAME`
    :

    ### Static methods

    `from_config(**kwargs) ‑> Any`
    :   Initialize an instance from config
        
        Raises:
            NotImplementedError: Abstract method has to be implemented.
        
        Returns:
            Any: an instance of BasicAgent class.

    `predict(**kwargs: Any) ‑> Any`
    :   Use LLM to predict, core function of an agent.
        
        Raises:
            NotImplementedError: Abstract method has to be implemented.
        
        Returns:
            Any: llm result.

    ### Methods

    `equip_retriever(self, retriever: llmreflect.Retriever.BasicRetriever.BasicRetriever)`
    :   Equip retriever for an agent object
        
        Args:
            retriever (BasicRetriever): A retriever instance.