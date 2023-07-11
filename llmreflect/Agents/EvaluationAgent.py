from llmreflect.Agents.BasicAgent import OpenAIAgent
from llmreflect.Retriever.BasicRetriever import BasicEvaluationRetriever


class PostgressqlGradingAgent(OpenAIAgent):
    """
    This is the agent class use for grading postgresql generation.
    Args:
        Agent (_type_): _description_
    """
    def __init__(self, open_ai_key: str,
                 prompt_name: str = 'gradingpostgresql',
                 max_output_tokens: int = 512,
                 temperature: float = 0.0):
        """
        Agent class for grading the performance of postgresql generator.
        Args:
            open_ai_key (str): API key to connect to chatgpt service.
            prompt_name (str, optional): name for the prompt json file.
                Defaults to 'gradingpostgresql'.
            max_output_tokens (int, optional): maximum completion length.
                Defaults to 512.
            temperature (float, optional): how consistent the llm performs.
                The lower the more consistent. Defaults to 0.0.
        """
        super().__init__(open_ai_key=open_ai_key,
                         prompt_name=prompt_name,
                         max_output_tokens=max_output_tokens,
                         temperature=temperature)

    def equip_retriever(self, retriever: BasicEvaluationRetriever):
        object.__setattr__(self, 'retriever', retriever)

    def grade(self, request: str, sql_cmd: str, db_summary: str) -> dict:
        """
        Convert LLM output into a score and an explanation.
        Detailed work done by the BasicEvaluationRetriever.
        Args:
            request (str): user's input, natural language for querying db
            sql_cmd (str): sql command generated from LLM
            db_summary (str): a brief report for the query summarized by
            retriever.

        Returns:
            a dictionary, {'grading': grading, 'explanation': explanation}
        """
        result = {'grading': 0, 'explanation': "Failed, no output from LLM."}
        if self.retriever is None:
            self.logger.error("Error: Retriever is not equipped.")
        else:
            try:
                llm_output = self.predict(
                    request=request,
                    command=sql_cmd,
                    summary=db_summary
                )
                self.logger.debug(llm_output)
                result = self.retriever.retrieve(llm_output)
            except Exception as e:
                self.logger.error(str(e))
                self.logger.error(llm_output)
        return result
