from Agents.BasicAgent import Agent
from Prompt.QuestionPrompt import QuestionPostgresPrompt
from langchain.llms.openai import OpenAI
from decouple import config
from Utils.message import message
from Retriever.DatabaseRetriever import DatabaseQuestionRetriever


class PostgressqlQuestionAgent(Agent):

    def __init__(self):
        prompt = QuestionPostgresPrompt.\
            load_prompt_from_json_file('questionpostgressql')
        llm = OpenAI(temperature=0.7, openai_api_key=config('OPENAI_API_KEY'))
        llm.max_tokens = int(config('MAX_OUTPUT'))
        super().__init__(prompt=prompt,
                         llm=llm)

    def equip_retriever(self, retriever: DatabaseQuestionRetriever):
        object.__setattr__(self, 'retriever', retriever)

    def predict_n_questions(self, n_questions: int = 5) -> str:
        result = "Failed, no output from LLM."
        if self.retriever is None:
            message("Error: Retriever is not equiped.", color="red")
        else:
            llm_output = self.predict(
                table_info=self.retriever.table_info,
                n_questions=n_questions
            )
            result = self.retriever.retrieve(llm_output)
        return result
