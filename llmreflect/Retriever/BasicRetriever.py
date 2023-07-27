from abc import ABC, abstractclassmethod
from typing import List


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
        try:
            grading = float(llm_output.split("\n")[0].split('[grading]')[-1])
            explanation = llm_output.split(']')[-1]
        except Exception:
            grading = 0.
            explanation = "Error encountered in grading process!"
        return {'grading': grading, 'explanation': explanation}


class BasicQuestionModerateRetriever(BasicRetriever):
    """_summary_
    Retriever class based on DatabaseQuestionRetriever.
    For filtering out malicious content
    Args:
        DatabaseQuestionRetriever (_type_): _description_
    """
    def __init__(self, include_tables: List) -> None:
        super().__init__()
        self.include_tables = include_tables

    def retrieve(self, llm_output: str, explanation: bool = False) -> dict:
        """_summary_

        Args:
            llm_output (str): output from llm
            explanation (str): wether return with explanation or not
        Returns:
            _type_: a processed string
        """
        processed_llm_output = llm_output.strip("\n").strip(' ')
        result_dict = {}
        if "[APPROVE]" in processed_llm_output:
            result_dict['decision'] = True
        else:
            result_dict['decision'] = False
        if explanation:
            result_dict['explanation'] = \
                processed_llm_output.split('[reason]]')[-1]
        return result_dict
