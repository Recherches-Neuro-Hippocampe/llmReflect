from llmreflect.Agents.BasicAgent import Agent
from llmreflect.Prompt.BasicPrompt import BasicPrompt
from langchain.llms.openai import OpenAI
from llmreflect.Utils.message import message
from llmreflect.Retriever.BasicRetriever import \
    BasicQuestionModerateRetriever


class PostgresqlModerateAgent(Agent):
    """
    Agent for filtering out illegal and malicious requests.
    Args:
        Agent (_type_): _description_
    """
    def __init__(self, open_ai_key: str,
                 prompt_name: str = 'moderatepostgresql',
                 max_output_tokens: int = 512,
                 temperature: float = 0.0):
        """
        Agent for filtering out illegal and malicious requests.
        Args:
            open_ai_key (str): API key to connect to chatgpt service.
            prompt_name (str, optional): name for the prompt json file.
                Defaults to 'moderatepostgresql'.
            max_output_tokens (int, optional): maximum completion length.
                Defaults to 512.
            temperature (float, optional): how consistent the llm performs.
                The lower the more consistent. To obtain diverse questions,
                a high temperature is recommended.
                Defaults to 0.0.
        """
        prompt = BasicPrompt.\
            load_prompt_from_json_file(prompt_name)
        llm = OpenAI(temperature=temperature, openai_api_key=open_ai_key)
        llm.max_tokens = max_output_tokens
        super().__init__(prompt=prompt,
                         llm=llm)

    def equip_retriever(self, retriever: BasicQuestionModerateRetriever):
        # notice it requires DatabaseQuestionModerateRetriever
        object.__setattr__(self, 'retriever', retriever)

    def predict_decision_only(self, user_input: str) -> bool:
        """
        predict whether accept the request or not
        Args:
            user_input (str): _description_

        Returns:
            bool: boolean answer, true or false
        """
        result = "Failed, no output from LLM."
        if self.retriever is None:
            message("Error: Retriever is not equipped.", color="red")
        else:
            llm_output = self.predict(
                topic="patient data",
                included_tables=self.retriever.include_tables,
                request=user_input
            )
            result = self.retriever.retrieve(llm_output)['decision']
        return result

    def predict_decision_explained(self, user_input: str) -> dict:
        """
        predict judgement with explanation
        Args:
            user_input (str): _description_

        Returns:
            dict: {'decision': bool, 'explanation': str}
        """
        result = "Failed, no output from LLM."
        if self.retriever is None:
            message("Error: Retriever is not equipped.", color="red")
        else:
            llm_output = self.predict(
                topic="patient data",
                included_tables=self.retriever.include_tables,
                request=user_input
            )
            result = self.retriever.retrieve(llm_output,
                                             explanation=True)
        return result
