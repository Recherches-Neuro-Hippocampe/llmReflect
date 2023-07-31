from llmreflect.Retriever.BasicRetriever import BasicRetriever
from abc import ABC, abstractclassmethod
from llmreflect.LLMCore.LLMCore import LLMCore, LLM_BACKBONE_MODEL
from llmreflect.LLMCore.LLMCore import OpenAICore, LlamacppCore
from typing import Any


class BasicAgent(ABC):
    def __init__(self, llm_core: LLMCore) -> None:
        """
        In this design each agent should have
        a retriever, retriever is for retrieving the final result based
        on the gross output by LLM.
        For example, a database retriever does the following job:
        extract the sql command from the llm output and then
        execute the command in the database.
        """
        object.__setattr__(self, 'llm_core', llm_core)

    def equip_retriever(self, retriever: BasicRetriever):
        # notice it requires DatabaseQuestionModerateRetriever
        object.__setattr__(self, 'retriever', retriever)

    @classmethod
    @abstractclassmethod
    def predict(self, **kwargs: Any) -> str:
        pass

    @classmethod
    @abstractclassmethod
    def from_llama(cls,) -> Any:
        pass

    @classmethod
    @abstractclassmethod
    def from_openai(cls,) -> Any:
        pass


class Agent(BasicAgent):
    def __init__(self, llm_core: LLMCore) -> None:
        super().__init__(llm_core)

    def equip_retriever(self, retriever: BasicRetriever):
        object.__setattr__(self, 'retriever', retriever)

    @classmethod
    def from_llama(cls,
                   model_path: str,
                   prompt_name: str,
                   max_total_tokens: int = 2048,
                   max_output_tokens: int = 512,
                   temperature: float = 0.,
                   verbose: bool = False,
                   n_gpus_layers: int = 8,
                   n_threads: int = 16,
                   n_batch: int = 512
                   ) -> BasicAgent:
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
        return cls(llm_core)

    @classmethod
    def from_openai(cls,
                    open_ai_key: str,
                    prompt_name: str = '',
                    max_output_tokens: int = 512,
                    temperature: float = 0.0,
                    llm_model=LLM_BACKBONE_MODEL.gpt_3_5_turbo) -> BasicAgent:

        llm_core = OpenAICore(
            open_ai_key=open_ai_key,
            prompt_name=prompt_name,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            llm_model=llm_model
        )
        return cls(llm_core)

    def predict(self, **kwargs: Any) -> str:
        return self.llm_core.predict(**kwargs)
