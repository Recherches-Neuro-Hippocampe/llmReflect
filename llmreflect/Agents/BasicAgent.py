from llmreflect.Retriever.BasicRetriever import BasicRetriever
from abc import ABC, abstractclassmethod
from llmreflect.LLMCore.LLMCore import LLMCore
from typing import Any


class BasicAgent(ABC):
    def __init__(self, llm_core: LLMCore, retriever: BasicRetriever) -> None:
        """
        In this design each agent should have
        a retriever, retriever is for retrieving the final result based
        on the gross output by LLM.
        For example, a database retriever does the following job:
        extract the sql command from the llm output and then
        execute the command in the database.
        """
        object.__setattr__(self, 'llm_core', llm_core)
        object.__setattr__(self, 'retriever', None)

    @classmethod
    @abstractclassmethod
    def predict(self, **kwargs: Any) -> str:
        pass

    @classmethod
    @abstractclassmethod
    def from_config(cls,) -> Any:
        pass


class Agent(BasicAgent):
    def __init__(self, llm_core: LLMCore, retriever: BasicRetriever) -> None:
        super().__init__(llm_core, retriever)

    def from_config(cls) -> BasicAgent:
        return cls

    def predict(self, **kwargs: Any) -> str:
        return self.llm_core.predict(**kwargs)
