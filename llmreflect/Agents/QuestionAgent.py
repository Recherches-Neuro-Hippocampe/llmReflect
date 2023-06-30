from llmreflect.Agents.BasicAgent import Agent
from llmreflect.Prompt.QuestionPrompt import QuestionPostgresPrompt
from langchain.llms.openai import OpenAI
from llmreflect.Utils.message import message
from llmreflect.Retriever.DatabaseRetriever import DatabaseQuestionRetriever


class PostgresqlQuestionAgent(Agent):
    """
    Agent for creating questions based on a given database
    Args:
        Agent (_type_): _description_
    """
    def __init__(self, open_ai_key: str,
                 prompt_name: str = 'questionpostgresql',
                 max_output_tokens: int = 512,
                 temperature: float = 0.7):
        """
        Agent class for querying database.
        Args:
            open_ai_key (str): API key to connect to chatgpt service.
            prompt_name (str, optional): name for the prompt json file.
                Defaults to 'questionpostgresql'.
            max_output_tokens (int, optional): maximum completion length.
                Defaults to 512.
            temperature (float, optional): how consistent the llm performs.
                The lower the more consistent. To obtain diverse questions,
                a high temperature is recommended.
                Defaults to 0.0.
        """
        prompt = QuestionPostgresPrompt.\
            load_prompt_from_json_file(prompt_name)
        llm = OpenAI(temperature=temperature, openai_api_key=open_ai_key)
        llm.max_tokens = max_output_tokens
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
