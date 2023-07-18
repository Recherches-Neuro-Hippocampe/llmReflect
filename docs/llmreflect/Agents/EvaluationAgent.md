Module llmreflect.Agents.EvaluationAgent
========================================

Classes
-------

`DatabaseGradingAgent(open_ai_key: str, prompt_name: str = 'grading_database', max_output_tokens: int = 512, temperature: float = 0.0)`
:   This is the agent class use for grading database command generation.
    
    Agent class for grading the performance of database command generator.
    Args:
        open_ai_key (str): API key to connect to chatgpt service.
        prompt_name (str, optional): name for the prompt json file.
            Defaults to 'grading_database'.
        max_output_tokens (int, optional): maximum completion length.
            Defaults to 512.
        temperature (float, optional): how consistent the llm performs.
            The lower the more consistent. Defaults to 0.0.

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

    `equip_retriever(self, retriever: llmreflect.Retriever.DatabaseRetriever.DatabaseEvaluationRetriever)`
    :

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