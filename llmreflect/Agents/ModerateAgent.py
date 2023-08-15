from llmreflect.Agents.BasicAgent import Agent
from llmreflect.LLMCore.LLMCore import LLMCore
from llmreflect.Retriever.BasicRetriever import \
    BasicQuestionModerateRetriever
from llmreflect.Utils.log import get_logger


class DatabaseModerateAgent(Agent):
    PROMPT_NAME = "moderate_database"

    def __init__(self, llm_core: LLMCore,
                 database_topic: str = 'patient data',
                 **kwargs):
        """
        Agent for filtering out illegal and malicious requests.
        Args:
            llm_core (LLMCore): the llm core to use for prediction.
            database_topic (str): the main topic of the database.
        """
        super().__init__(llm_core=llm_core, **kwargs)
        object.__setattr__(self, "logger", get_logger(self.__class__.__name__))
        object.__setattr__(self, 'database_topic', database_topic)

    def equip_retriever(self, retriever: BasicQuestionModerateRetriever):
        # notice it requires DatabaseQuestionModerateRetriever
        object.__setattr__(self, 'retriever', retriever)

    def predict_decision_only(self, user_input: str) -> bool:
        """
        predict whether accept the request or not
        Args:
            user_input (str): User's natural language input

        Returns:
            bool: boolean answer, true or false
        """
        result = "Failed, no output from LLM."
        if self.retriever is None:
            self.logger.error("Error: Retriever is not equipped.")
        else:
            llm_output = self.predict(
                topic=self.database_topic,
                included_tables=self.retriever.include_tables,
                request=user_input
            )
            self.logger.debug(llm_output)
            result = self.retriever.retrieve(llm_output)['decision']
        return result

    def predict_decision_explained(self, user_input: str) -> dict:
        """
        predict judgement with explanation
        Args:
            user_input (str): User's natural language input

        Returns:
            dict: {'decision': bool, 'explanation': str}
        """
        result = "Failed, no output from LLM."
        if self.retriever is None:
            self.logger.error("Error: Retriever is not equipped.")
        else:
            llm_output = self.predict(
                topic=self.database_topic,
                included_tables=self.retriever.include_tables,
                request=user_input
            )
            self.logger.debug(llm_output)
            result = self.retriever.retrieve(llm_output,
                                             explanation=True)
        return result
