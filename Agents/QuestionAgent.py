from Agents.BasicAgent import Agent
from Prompt.QuestionPrompt import QuestionPostgresPrompt
from langchain.llms.openai import OpenAI
from decouple import config
from Utils.message import message
from Retriever.DatabaseRetriever import DatabaseQuestionRetriever


class PostgressqlQuestionAgent(Agent):
    """
    Agent for creating questions based on a given database
    Args:
        Agent (_type_): _description_
    """
    def __init__(self):
        """
        A high temperature is required to obtain
        more diverse questions.
        """
        prompt = QuestionPostgresPrompt.\
            load_prompt_from_json_file('questionpostgressql')
        llm = OpenAI(temperature=0.7, openai_api_key=config('OPENAI_API_KEY'))
        llm.max_tokens = int(config('MAX_OUTPUT'))
        super().__init__(prompt=prompt,
                         llm=llm)

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
            message("Error: Retriever is not equipped.", color="red")
        else:
            llm_output = self.predict(
                table_info=self.retriever.table_info,
                n_questions=n_questions
            )
            result = self.retriever.retrieve(llm_output)
        return result
