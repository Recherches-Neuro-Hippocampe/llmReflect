from typing import Any
from langchain.chains import LLMChain
from llmreflect.Prompt.BasicPrompt import BasicPrompt
from langchain.base_language import BaseLanguageModel
from abc import ABC, abstractclassmethod
from llmreflect.Retriever.BasicRetriever import BasicRetriever
from dataclasses import dataclass
from langchain.chat_models import ChatOpenAI
from llmreflect.Utils.log import get_logger
from llmreflect.Utils.log import openai_trace_var


@dataclass
class LLM_BACKBONE_MODEL:
    gpt_4 = "gpt-4"
    gpt_4_0314 = "gpt-4-0314"
    gpt_4_0613 = "gpt-4-0613"
    gpt_4_32k = "gpt-4-32k"
    gpt_4_32k_0314 = "gpt-4-32k-0314"
    gpt_4_32k_0613 = "gpt-4-32k-0613"
    gpt_3_5_turbo = "gpt-3.5-turbo"
    gpt_3_5_turbo_0301 = "gpt-3.5-turbo-0301"
    gpt_3_5_turbo_0613 = "gpt-3.5-turbo-0613"
    gpt_3_5_turbo_16k = "gpt-3.5-turbo-16k"
    gpt_3_5_turbo_16k_0613 = "gpt-3.5-turbo-16k-0613"
    text_ada_001 = "text-ada-001"
    ada = "ada"
    text_babbage_001 = "text-babbage-001"
    babbage = "babbage"
    text_curie_001 = "text-curie-001"
    curie = "curie"
    davinci = "davinci"
    text_davinci_003 = "text-davinci-003"
    text_davinci_002 = "text-davinci-002"
    code_davinci_002 = "code-davinci-002"
    code_davinci_001 = "code-davinci-001"
    code_cushman_002 = "code-cushman-002"
    code_cushman_001 = "code-cushman-001"


class Agent(LLMChain, ABC):
    '''
    Abstract class for agent, in this design each agent should have
    a retriever, retriever is for retrieving the final result based
    on the gross output by LLM.
    For example, a database retriever does the following job:
    extract the sql command from the llm output and then
    execute the command in the database.
    '''
    def __init__(self, prompt: BasicPrompt, llm: BaseLanguageModel):
        super().__init__(prompt=prompt.get_langchain_prompt_template(),
                         llm=llm)
        # Agent class inherit from the LLM chain class
        object.__setattr__(self, 'retriever', None)
        object.__setattr__(self, "logger", get_logger(self.__class__.__name__))

    @abstractclassmethod
    def equip_retriever(self, retriever: BasicRetriever):
        object.__setattr__(self, 'retriever', retriever)

    def get_inputs(self):
        """_summary_
        showing inputs for the prompt template being used
        Returns:
            _type_: _description_
        """
        return self.prompt.input_variables

    def predict(self, **kwargs: Any) -> str:
        return super().predict([openai_trace_var.get()], **kwargs)


class OpenAIAgent(Agent):
    '''
    Abstract class for agent, in this design each agent should have
    a retriever, retriever is for retrieving the final result based
    on the gross output by LLM.
    For example, a database retriever does the following job:
    extract the sql command from the llm output and then
    execute the command in the database.
    '''
    def __init__(self, open_ai_key: str,
                 prompt_name: str = '',
                 max_output_tokens: int = 512,
                 temperature: float = 0.0,
                 llm_model=LLM_BACKBONE_MODEL.gpt_3_5_turbo):
        prompt = BasicPrompt.\
            load_prompt_from_json_file(prompt_name)
        llm = ChatOpenAI(temperature=temperature,
                         openai_api_key=open_ai_key,
                         model=llm_model)
        llm.max_tokens = max_output_tokens
        super().__init__(prompt=prompt,
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
        return self.prompt.input_variables
