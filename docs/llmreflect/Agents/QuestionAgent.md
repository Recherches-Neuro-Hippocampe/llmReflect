Module llmreflect.Agents.QuestionAgent
======================================

Classes
-------

`DatabaseQuestionAgent(llm_core: llmreflect.LLMCore.LLMCore.LLMCore, **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    Agent for creating questions based on a given database
     Args:
        llm_core (LLMCore): the llm core to use for prediction.

    ### Ancestors (in MRO)

    * llmreflect.Agents.BasicAgent.Agent
    * llmreflect.Agents.BasicAgent.BasicAgent
    * abc.ABC

    ### Class variables

    `PROMPT_NAME`
    :

    ### Methods

    `predict_n_questions(self, n_questions: int = 5) ‑> str`
    :   Create n questions given by a dataset
        Args:
            n_questions (int, optional):
            number of questions to generate in a run. Defaults to 5.
        
        Returns:
            str: a list of questions, I love list.