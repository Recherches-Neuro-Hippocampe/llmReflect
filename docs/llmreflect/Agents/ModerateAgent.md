Module llmreflect.Agents.ModerateAgent
======================================

Classes
-------

`DatabaseModerateAgent(llm_core: llmreflect.LLMCore.LLMCore.LLMCore, database_topic: str = 'patient data', **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    Agent for filtering out illegal and malicious requests.
    Args:
        llm_core (LLMCore): the llm core to use for prediction.
        database_topic (str): the main topic of the database.

    ### Ancestors (in MRO)

    * llmreflect.Agents.BasicAgent.Agent
    * llmreflect.Agents.BasicAgent.BasicAgent
    * abc.ABC

    ### Class variables

    `PROMPT_NAME`
    :

    ### Methods

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