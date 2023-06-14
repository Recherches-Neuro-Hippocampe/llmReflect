from langchain.chains import LLMChain
from Prompt.Prompt import BasicPrompt
from langchain.llms.base import BaseLLM


class Agent(LLMChain):
    def __init__(self, prompt: BasicPrompt, llm: BaseLLM):
        super().__init__(prompt=prompt.get_langchain_prompt_template(),
                         llm=llm)
        object.__setattr__(self, 'retriever', None)
