from llmreflect.Agents.BasicAgent import Agent, BasicAgent
from llmreflect.LLMCore.LLMCore import LLM_BACKBONE_MODEL, \
    LlamacppCore, OpenAICore, LLMCore
from llmreflect.Retriever.BasicRetriever import \
    BasicQuestionModerateRetriever
from llmreflect.Utils.log import get_logger


class DatabaseModerateAgent(Agent):
    """
    Agent for filtering out illegal and malicious requests.
    """
    def __init__(self, llm_core: LLMCore,
                 database_topic: str = 'patient data'):
        """
        Agent for filtering out illegal and malicious requests.
        Args:
            open_ai_key (str): API key to connect to chatgpt service.
            prompt_name (str, optional): name for the prompt json file.
                Defaults to 'moderate_database'.
            max_output_tokens (int, optional): maximum completion length.
                Defaults to 512.
            temperature (float, optional): how consistent the llm performs.
                The lower the more consistent. To obtain diverse questions,
                a high temperature is recommended.
                Defaults to 0.0.
        """
        super().__init__(llm_core=llm_core)
        object.__setattr__(self, "logger", get_logger(self.__class__.__name__))
        object.__setattr__(self, 'database_topic', database_topic)

    @classmethod
    def from_openai(cls,
                    open_ai_key: str,
                    prompt_name: str = '',
                    max_output_tokens: int = 512,
                    temperature: float = 0,
                    llm_model=LLM_BACKBONE_MODEL.gpt_3_5_turbo,
                    database_topic: str = 'patient data') -> BasicAgent:
        llm_core = OpenAICore(
            open_ai_key=open_ai_key,
            prompt_name=prompt_name,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            llm_model=llm_model
        )
        return cls(llm_core=llm_core, database_topic=database_topic)

    @classmethod
    def from_llama(cls,
                   model_path: str,
                   prompt_name: str,
                   max_total_tokens: int = 2048,
                   max_output_tokens: int = 512,
                   temperature: float = 0,
                   verbose: bool = False,
                   n_gpus_layers: int = 8,
                   n_threads: int = 16,
                   n_batch: int = 512,
                   database_topic: str = 'patient data') -> BasicAgent:
        llm_core = LlamacppCore(
            model_path=model_path,
            prompt_name=prompt_name,
            max_total_tokens=max_total_tokens,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            verbose=verbose,
            n_gpus_layers=n_gpus_layers,
            n_threads=n_threads,
            n_batch=n_batch
        )
        return cls(llm_core=llm_core, database_topic=database_topic)

    def equip_retriever(self, retriever: BasicQuestionModerateRetriever):
        # notice it requires DatabaseQuestionModerateRetriever
        object.__setattr__(self, 'retriever', retriever)

    def predict_decision_only(self, user_input: str) -> bool:
        """
        predict whether accept the request or not
        Args:
            user_input (str): User's natural language input

        Returns:
            bool: boolean answer, true or false
        """
        result = "Failed, no output from LLM."
        if self.retriever is None:
            self.logger.error("Error: Retriever is not equipped.")
        else:
            llm_output = self.predict(
                topic=self.database_topic,
                included_tables=self.retriever.include_tables,
                request=user_input
            )
            self.logger.debug(llm_output)
            result = self.retriever.retrieve(llm_output)['decision']
        return result

    def predict_decision_explained(self, user_input: str) -> dict:
        """
        predict judgement with explanation
        Args:
            user_input (str): User's natural language input

        Returns:
            dict: {'decision': bool, 'explanation': str}
        """
        result = "Failed, no output from LLM."
        if self.retriever is None:
            self.logger.error("Error: Retriever is not equipped.")
        else:
            llm_output = self.predict(
                topic=self.database_topic,
                included_tables=self.retriever.include_tables,
                request=user_input
            )
            self.logger.debug(llm_output)
            result = self.retriever.retrieve(llm_output,
                                             explanation=True)
        return result
