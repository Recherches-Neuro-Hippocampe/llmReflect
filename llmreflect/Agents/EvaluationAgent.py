from llmreflect.Agents.BasicAgent import Agent
from llmreflect.Prompt.GradingPrompt import GradingPrompt
from langchain.llms.openai import OpenAI
from decouple import config
from llmreflect.Utils.message import message
from llmreflect.Retriever.BasicRetriever import BasicEvaluationRetriever


class PostgressqlGradingAgent(Agent):
    """_summary_
    This is the agent class use for grading postgresql generation.
    Args:
        Agent (_type_): _description_
    """
    def __init__(self):
        """
        Temperature set to 0, since evaluation needs to be consistent.
        """
        prompt = GradingPrompt.\
            load_prompt_from_json_file('gradingpostgresql')
        llm = OpenAI(temperature=0.0, openai_api_key=config('OPENAI_API_KEY'))
        llm.max_tokens = int(config('MAX_OUTPUT'))
        super().__init__(prompt=prompt,
                         llm=llm)

    def equip_retriever(self, retriever: BasicEvaluationRetriever):
        object.__setattr__(self, 'retriever', retriever)

    def grade(self, request: str, sql_cmd: str, db_summary: str) -> dict:
        """
        Convert LLM output into a score and an explanation.
        Detailed work done by the BasicEvaluationRetriever.
        Args:
            request (str): user's input, natural language for querying db
            sql_cmd (str): sql command generated from LLM
            db_summary (str): a brief report for the query summarized by
            retriever.

        Returns:
            a dictionary, {'grading': grading, 'explanation': explanation}
        """
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
