from Agents.BasicAgent import Agent
from langchain.llms.openai import OpenAI
from decouple import config
from Utils.message import message
from Retriever.DatabaseRetriever import DatabaseRetriever
from Prompt.BasicPrompt import BasicPrompt


class PostgresSQLAgent(Agent):

    def __init__(self):
        prompt = BasicPrompt.load_prompt_from_json_file('postgressql')
        llm = OpenAI(temperature=0, openai_api_key=config('OPENAI_API_KEY'))
        llm.max_tokens = int(config('MAX_OUTPUT'))
        super().__init__(prompt=prompt,
                         llm=llm)

    def equip_retriever(self, retriever: DatabaseRetriever):
        object.__setattr__(self, 'retriever', retriever)

    def predict_sql_cmd(self, user_input: str) -> str:
        llm_output = "Failed, no output from LLM."
        if self.retriever is None:
            message("Error: Retriever is not equipped.", color="red")
        else:
            llm_output = self.predict(
                dialect=self.retriever.database_dialect,
                max_present=self.retriever.max_rows_return,
                table_info=self.retriever.table_info,
                input=user_input
            )
        return llm_output

    def predict_db(self, user_input: str) -> str:
        llm_output = self.predict_sql_cmd(user_input=user_input)
        sql_result = self.retriever.retrieve(llm_output=llm_output)
        return sql_result

    def predict_db_summary(self, user_input: str,
                           return_cmd: bool = False) -> str:
        llm_output = self.predict_sql_cmd(user_input=user_input)
        result = self.retriever.retrieve_summary(
            llm_output=llm_output,
            return_cmd=return_cmd)
        return result
