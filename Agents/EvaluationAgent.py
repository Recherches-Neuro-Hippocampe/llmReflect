from Agents.BasicAgent import Agent
from Prompt.GradingPrompt import GradingPrompt
from langchain.llms.openai import OpenAI
from decouple import config
from Utils.message import message
from Retriever.BasicRetriever import BasicTextRetriever


class PostgressqlGradingAgent(Agent):

    def __init__(self):
        prompt = GradingPrompt.\
            load_prompt_from_json_file('gradingpostgresql')
        llm = OpenAI(temperature=0.0, openai_api_key=config('OPENAI_API_KEY'))
        llm.max_tokens = int(config('MAX_OUTPUT'))
        super().__init__(prompt=prompt,
                         llm=llm)

    def equip_retriever(self, retriever: BasicTextRetriever):
        object.__setattr__(self, 'retriever', retriever)

    def grade(self, request: str, sql_cmd: str, db_summary: str) -> str:
        result = "Failed, no output from LLM."
        if self.retriever is None:
            message("Error: Retriever is not equipped.", color="red")
        else:
            llm_output = self.predict(
                request=request,
                sql_cmd=sql_cmd,
                db_summary=db_summary
            )
            result = self.retriever.retrieve(llm_output)
        return result
