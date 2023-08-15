from llmreflect.Agents.BasicAgent import Agent
from llmreflect.LLMCore.LLMCore import LLMCore
from llmreflect.Retriever.DatabaseRetriever import DatabaseQuestionRetriever
from llmreflect.Utils.log import get_logger


class DatabaseQuestionAgent(Agent):
    PROMPT_NAME = "question_database"

    def __init__(self, llm_core: LLMCore, **kwargs):
        """
        Agent for creating questions based on a given database
         Args:
            llm_core (LLMCore): the llm core to use for prediction.
        """
        super().__init__(llm_core=llm_core, **kwargs)
        object.__setattr__(self, "logger", get_logger(self.__class__.__name__))

    def equip_retriever(self, retriever: DatabaseQuestionRetriever):
        # notice it requires DatabaseQuestionRetriever
        object.__setattr__(self, 'retriever', retriever)

    def predict_n_questions(self, n_questions: int = 5) -> str:
        """
        Create n questions given by a dataset
        Args:
            n_questions (int, optional):
            number of questions to generate in a run. Defaults to 5.

        Returns:
            str: a list of questions, I love list.
        """
        result = "Failed, no output from LLM."
        if self.retriever is None:
            self.logger.error("Error: Retriever is not equipped.")
        else:
            llm_output = self.predict(
                table_info=self.retriever.table_info,
                n_questions=n_questions,
                dialect=self.retriever.database_dialect
            )
            self.logger.debug(llm_output)
            result = self.retriever.retrieve(llm_output)
        return result
