from abc import ABC, abstractclassmethod


class BasicRetriever(ABC):
    @abstractclassmethod
    def retrieve(self, llm_output: str) -> str:
        pass
