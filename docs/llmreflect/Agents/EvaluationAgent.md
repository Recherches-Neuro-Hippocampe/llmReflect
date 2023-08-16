Module llmreflect.Agents.EvaluationAgent
========================================

Classes
-------

`DatabaseGradingAgent(llm_core: llmreflect.LLMCore.LLMCore.LLMCore, **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    agent class use for grading database command generation.
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

    `grade(self, request: str, sql_cmd: str, db_summary: str) ‑> dict`
    :   Convert LLM output into a score and an explanation.
        Detailed work done by the DatabaseEvaluationRetriever.
        Args:
            request (str): user's input, natural language for querying db
            sql_cmd (str): sql command generated from LLM
            db_summary (str): a brief report for the query summarized by
            retriever.
        
        Returns:
            a dictionary, {'grading': grading, 'explanation': explanation}