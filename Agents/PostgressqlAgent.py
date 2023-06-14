from Agents.BasicAgent import Agent
from Prompt.Prompt import load_prompt
from langchain.llms.openai import OpenAI
from decouple import config
from Utils.message import message
from Retriever.DatabaseRetriever import DatabaseRetriever


class PostgresSQLAgent(Agent):

    def __init__(self):
        prompt = load_prompt('postgressql')
        llm = OpenAI(temperature=0, openai_api_key=config('OPENAI_API_KEY'))
        llm.max_tokens = int(config('MAX_OUTPUT'))
        super().__init__(prompt=prompt,
                         llm=llm)

    def equip_retriever(self, retriever: DatabaseRetriever):
        object.__setattr__(self, 'retriever', retriever)

    def user_input_only_predict(self, user_input: str) -> str:
        llm_output = "Failed, no output from LLM."
        if self.retriever is None:
            message("Error: Retriever is not equiped.", color="red")
        else:
            llm_output = self.predict(
                dialect=self.retriever.database_dialect,
                max_present=self.retriever.max_rows_return,
                table_info=self.retriever.table_info,
                input=user_input
            )
        return llm_output

    def predict_retrieve_databse(self, user_input: str) -> str:
        llm_output = self.user_input_only_predict(user_input=user_input)
        sql_result = self.retriever.retrieve(llm_output=llm_output)
        return sql_result
