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
        """
        Retrieve the processed llm result
        Args:
            llm_output (str):  output from llm

        Returns:
            dict: the processed result
        """
        llm_output = llm_output.strip('\n').strip(' ')
        try:
            grading = float(llm_output.split("\n")[0].split('[grading]')[-1])
            explanation = llm_output.split(']')[-1]
        except Exception:
            grading = 0.
            explanation = "Error encountered in grading process!"
        return {'grading': grading, 'explanation': explanation}


class BasicQuestionModerateRetriever(BasicRetriever):
    def __init__(self, include_tables: List) -> None:
        """
        Retriever class based on BasicRetriever.
        The LLM will ask questions about the database.
        And this retriever retrieves processed questions generated by LLM.
        Args:
            include_tables (List):
                A list of tables to be included in the database.
        """
        super().__init__()
        self.include_tables = include_tables

    def retrieve(self, llm_output: str, explanation: bool = False) -> dict:
        """
        Retrieve the processed llm result
        Args:
            llm_output (str): output from llm
            explanation (str): wether return with explanation or not
        Returns:
            dict: the processed result
        """
        processed_llm_output = llm_output.strip("\n").strip(' ')
        result_dict = {}
        if "APPROVE" in processed_llm_output:
            result_dict['decision'] = 1
        elif "IRRELEVANT" in processed_llm_output:
            result_dict['decision'] = 0
        else:
            result_dict['decision'] = -1
        if explanation:
            result_dict['explanation'] = \
                processed_llm_output.split('[reason]')[-1].strip()
        return result_dict
