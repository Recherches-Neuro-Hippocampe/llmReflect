Module llmreflect.Agents.ModerateAgent
======================================

Classes
-------

`DatabaseModerateAgent(open_ai_key: str, prompt_name: str = 'moderate_database', max_output_tokens: int = 512, temperature: float = 0.0, database_topic: str = 'patient data')`
:   Agent for filtering out illegal and malicious requests.
    
    Agent for filtering out illegal and malicious requests.
    Args:
        open_ai_key (str): API key to connect to chatgpt service.
        prompt_name (str, optional): name for the prompt json file.
            Defaults to 'moderate_database'.
        max_output_tokens (int, optional): maximum completion length.
            Defaults to 512.
        temperature (float, optional): how consistent the llm performs.
            The lower the more consistent. To obtain diverse questions,
            a high temperature is recommended.
            Defaults to 0.0.

    ### Ancestors (in MRO)

    * llmreflect.Agents.BasicAgent.OpenAIAgent
    * llmreflect.Agents.BasicAgent.Agent
    * langchain.chains.llm.LLMChain
    * langchain.chains.base.Chain
    * langchain.load.serializable.Serializable
    * pydantic.main.BaseModel
    * pydantic.utils.Representation
    * abc.ABC

    ### Methods

    `equip_retriever(self, retriever: llmreflect.Retriever.BasicRetriever.BasicQuestionModerateRetriever)`
    :

    `predict_decision_explained(self, user_input: str) ‑> dict`
    :   predict judgement with explanation
        Args:
            user_input (str): User's natural language input
        
        Returns:
            dict: {'decision': bool, 'explanation': str}

    `predict_decision_only(self, user_input: str) ‑> bool`
    :   predict whether accept the request or not
        Args:
            user_input (str): User's natural language input
        
        Returns:
            bool: boolean answer, true or false