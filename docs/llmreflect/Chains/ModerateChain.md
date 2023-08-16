Module llmreflect.Chains.ModerateChain
======================================

Classes
-------

`ModerateChain(agent: llmreflect.Agents.ModerateAgent.DatabaseModerateAgent, retriever: llmreflect.Retriever.BasicRetriever.BasicQuestionModerateRetriever, **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    A chain for filtering out toxic questions and injection attacks.
    Args:
        agent (DatabaseModerateAgent): DatabaseModerateAgent
        retriever (BasicQuestionModerateRetriever):
            BasicQuestionModerateRetriever

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

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