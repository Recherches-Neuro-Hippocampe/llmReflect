from abc import ABC, abstractclassmethod
from llmreflect.Retriever.BasicRetriever import BasicRetriever
from llmreflect.Agents.BasicAgent import Agent
from llmreflect.Prompt.BasicPrompt import BasicPrompt
from typing import Any, List
from langchain.llms.openai import OpenAI
from langchain.callbacks import get_openai_callback
from llmreflect.Utils.log import LOGGER, openai_cb_2_str


class BasicChain(ABC):
    '''
    Abstract class for Chain class.
    A chain class should be the atomic unit for completing a job.
    A chain contains at least two components:
    1. an agent 2. a retriever
    A chain object must have the function to perform a job.
    '''
    def __init__(self, agent: Agent, retriever: BasicRetriever):
        self.agent = agent
        self.retriever = retriever
        self.agent.equip_retriever(self.retriever)

    @abstractclassmethod
    def from_config(cls,
                    open_ai_key: str,
                    prompt_name: str = 'questionpostgresql',
                    temperature: float = 0.0):
        llm = OpenAI(temperature=temperature, openai_api_key=open_ai_key)
        agent = Agent(prompt=BasicPrompt.
                      load_prompt_from_json_file(prompt_name),
                      llm=llm)
        retriever = BasicRetriever()
        return cls(agent=agent, retriever=retriever)

    @abstractclassmethod
    def perform(self, **kwargs: Any):
        result = self.agent.predict(kwargs)
        return result

    def perform_cost_monitor(self, **kwargs: Any):
        with get_openai_callback() as cb:
            result = self.perform(**kwargs)
        LOGGER.info(openai_cb_2_str(cb))
        return result, cb


class BasicCombinedChain(ABC):
    '''
    Abstract class for combined Chain class.
    A combined chain is a chain with multiple chains
    A chain class should be the atomic unit for completing a job.
    A chain object must have the function to perform a job.
    '''
    def __init__(self, chains: List[BasicChain]):
        self.chains = chains

    @abstractclassmethod
    def from_config(cls, **kwargs: Any):
        return

    @abstractclassmethod
    def perform(self, **kwargs: Any):
        return

    def perform_cost_monitor(self, **kwargs: Any):
        with get_openai_callback() as cb:
            result = self.perform(**kwargs)
        LOGGER.info(openai_cb_2_str(cb))
        return result, cb
