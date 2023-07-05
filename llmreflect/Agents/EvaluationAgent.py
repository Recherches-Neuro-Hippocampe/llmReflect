from llmreflect.Agents.BasicAgent import Agent
from llmreflect.Prompt.BasicPrompt import BasicPrompt
from langchain.llms.openai import OpenAI
from llmreflect.Utils.message import message
from llmreflect.Retriever.BasicRetriever import BasicEvaluationRetriever


class PostgressqlGradingAgent(Agent):
    """
    This is the agent class use for grading postgresql generation.
    Args:
        Agent (_type_): _description_
    """
    def __init__(self, open_ai_key: str,
                 prompt_name: str = 'gradingpostgresql',
                 max_output_tokens: int = 512,
                 temperature: float = 0.0):
        """
        Agent class for grading the performance of postgresql generator.
        Args:
            open_ai_key (str): API key to connect to chatgpt service.
            prompt_name (str, optional): name for the prompt json file.
                Defaults to 'gradingpostgresql'.
            max_output_tokens (int, optional): maximum completion length.
                Defaults to 512.
            temperature (float, optional): how consistent the llm performs.
                The lower the more consistent. Defaults to 0.0.
        """
        prompt = BasicPrompt.\
            load_prompt_from_json_file(prompt_name)
        llm = OpenAI(temperature=temperature, openai_api_key=open_ai_key)
        llm.max_tokens = max_output_tokens
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
                command=sql_cmd,
                summary=db_summary
            )
            result = self.retriever.retrieve(llm_output)
        return result
