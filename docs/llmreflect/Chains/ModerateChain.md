Module llmreflect.Chains.ModerateChain
======================================

Classes
-------

`ModerateChain(agent: llmreflect.Agents.ModerateAgent.DatabaseModerateAgent, retriever: llmreflect.Retriever.BasicRetriever.BasicQuestionModerateRetriever)`
:   Abstract class for Chain class.
    A chain class should be the atomic unit for completing a job.
    A chain contains at least two components:
    1. an agent 2. a retriever
    A chain object must have the function to perform a job.
    Each chain is also equipped with a logger
    
    A chain for filtering out toxic questions and injection attacks.
    Args:
        agent (DatabaseModerateAgent): DatabaseModerateAgent
        retriever (BasicQuestionModerateRetriever):
            BasicQuestionModerateRetriever

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

    ### Static methods

    `from_config(open_ai_key: str, include_tables: list, prompt_name: str = 'moderate_database', max_output_tokens: int = 512, temperature: float = 0.0) ‑> llmreflect.Chains.BasicChain.BasicChain`
    :   Initialize a ModerateChain object from configurations.
        Args:
            open_ai_key (str): Openai api key.
            include_tables (list): A list of database tables names to include.
            prompt_name (str, optional): Prompt file name.
                Defaults to 'moderate_database'.
            max_output_tokens (int, optional): Maximum completion tokens.
                Defaults to 512.
            temperature (float, optional): The higher the more unstable.
                Defaults to 0.0.
        
        Returns:
            BasicChain: _description_

    ### Methods

    `perform(self, user_input: str, with_explanation: bool = False) ‑> Any`
    :   Overwrite perform function.
        Sensor the questions if they are allowed
        Args:
            user_input (str): user's natural language request
            with_explanation (bool): if add explanation
        
        Returns:
            without explanation: return a boolean variable
            with explanation: dict: {'decision': bool, 'explanation': str}