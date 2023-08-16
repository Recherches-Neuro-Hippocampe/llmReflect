from llmreflect.Agents.BasicAgent import Agent
from llmreflect.Retriever.DatabaseRetriever import DatabaseEvaluationRetriever
from llmreflect.LLMCore.LLMCore import LLMCore
from llmreflect.Utils.log import get_logger


class DatabaseGradingAgent(Agent):
    PROMPT_NAME = "grading_database"

    def __init__(self, llm_core: LLMCore, **kwargs):
        """
        agent class use for grading database command generation.
        Args:
            llm_core (LLMCore): the llm core to use for prediction.
        """
        super().__init__(llm_core=llm_core, **kwargs)
        object.__setattr__(self, "logger", get_logger(self.__class__.__name__))

    def equip_retriever(self, retriever: DatabaseEvaluationRetriever):
        object.__setattr__(self, 'retriever', retriever)

    def grade(self, request: str, sql_cmd: str, db_summary: str) -> dict:
        """
        Convert LLM output into a score and an explanation.
        Detailed work done by the DatabaseEvaluationRetriever.
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
                    summary=db_summary,
                    dialect=self.retriever.database_dialect
                )
                self.logger.debug(llm_output)
                result = self.retriever.retrieve(llm_output)
            except Exception as e:
                self.logger.error(str(e))
                self.logger.error(llm_output)
        return result
