from abc import ABC, abstractclassmethod


class BasicRetriever(ABC):
    @abstractclassmethod
    def retrieve(self, llm_output: str) -> str:
        pass


class BasicTextRetriever(BasicRetriever):
    # Class for general postprocessing llm output string
    def retrieve(self, llm_output: str) -> str:
        return llm_output.strip('\n').strip(' ')
