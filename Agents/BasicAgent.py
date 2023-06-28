from langchain.chains import LLMChain
from Prompt.BasicPrompt import BasicPrompt
from langchain.llms.base import BaseLLM
from abc import ABC, abstractclassmethod
from Retriever.BasicRetriever import BasicRetriever


class Agent(LLMChain, ABC):
    def __init__(self, prompt: BasicPrompt, llm: BaseLLM):
        super().__init__(prompt=prompt.get_langchain_prompt_template(),
                         llm=llm)
        object.__setattr__(self, 'retriever', None)

    @abstractclassmethod
    def equip_retriever(self, retriever: BasicRetriever):
        object.__setattr__(self, 'retriever', retriever)

    def get_inputs(self):
        """_summary_
        showing inputs for the prompt template being used
        Returns:
            _type_: _description_
        """
        print(self.prompt.input_variables)
        return self.prompt.input_variables
