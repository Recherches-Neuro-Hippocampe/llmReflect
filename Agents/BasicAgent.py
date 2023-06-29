from langchain.chains import LLMChain
from Prompt.BasicPrompt import BasicPrompt
from langchain.llms.base import BaseLLM
from abc import ABC, abstractclassmethod
from Retriever.BasicRetriever import BasicRetriever


class Agent(LLMChain, ABC):
    '''
    Abstract class for agent, in this design each agent should have
    a retriever, retriever is for retrieving the final result based
    on the gross output by LLM.
    For example, a database retriever does the following job:
    extract the sql command from the llm output and then
    execute the command in the database.
    '''
    def __init__(self, prompt: BasicPrompt, llm: BaseLLM):
        super().__init__(prompt=prompt.get_langchain_prompt_template(),
                         llm=llm)
        # Agent class inherit from the LLM chain class
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
