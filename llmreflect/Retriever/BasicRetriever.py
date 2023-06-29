from abc import ABC, abstractclassmethod


class BasicRetriever(ABC):
    @abstractclassmethod
    def retrieve(self, llm_output: str) -> str:
        pass


class BasicTextRetriever(BasicRetriever):
    # Class for general postprocessing llm output string
    def retrieve(self, llm_output: str) -> str:
        return llm_output.strip('\n').strip(' ')


class BasicEvaluationRetriever(BasicRetriever):
    # Class for general postprocessing llm output string
    def retrieve(self, llm_output: str) -> dict:
        llm_output = llm_output.strip('\n').strip(' ')
        grading = float(llm_output.split("\n")[0].split(']')[-1])
        explanation = llm_output.split(']')[-1]
        return {'grading': grading, 'explanation': explanation}
