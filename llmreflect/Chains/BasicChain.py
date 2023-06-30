from abc import ABC, abstractclassmethod
from llmreflect.Retriever.BasicRetriever import BasicRetriever
from llmreflect.Agents.BasicAgent import Agent
from typing import Any


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
    def perform(self, **kwargs: Any):
        result = self.agent.predict(kwargs)
        return result
