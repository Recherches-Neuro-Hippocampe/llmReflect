from llmreflect.Agents.BasicAgent import OpenAIAgent
from llmreflect.Retriever.DatabaseRetriever import DatabaseQuestionRetriever


class DatabaseQuestionAgent(OpenAIAgent):
    """
    Agent for creating questions based on a given database
    Args:
        Agent (_type_): _description_
    """
    def __init__(self, open_ai_key: str,
                 prompt_name: str = 'question_database',
                 max_output_tokens: int = 512,
                 temperature: float = 0.7):
        """
        Agent for creating questions based on a given database
        Args:
            open_ai_key (str): API key to connect to chatgpt service.
            prompt_name (str, optional): name for the prompt json file.
                Defaults to 'question_database'.
            max_output_tokens (int, optional): maximum completion length.
                Defaults to 512.
            temperature (float, optional): how consistent the llm performs.
                The lower the more consistent. To obtain diverse questions,
                a high temperature is recommended.
                Defaults to 0.0.
        """
        super().__init__(open_ai_key=open_ai_key,
                         prompt_name=prompt_name,
                         max_output_tokens=max_output_tokens,
                         temperature=temperature)

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
