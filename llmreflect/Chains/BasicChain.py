from abc import ABC, abstractclassmethod
from llmreflect.Retriever.BasicRetriever import BasicRetriever
from llmreflect.Agents.BasicAgent import LLMCore
from llmreflect.Prompt.BasicPrompt import BasicPrompt
from typing import Any, List
from langchain.llms.openai import OpenAI
from llmreflect.Utils.log import get_logger, openai_cb_2_str
from llmreflect.Utils.log import get_openai_tracer, get_general_tracer


class BasicChain(ABC):
    '''
    Abstract class for Chain class.
    A chain class should be the atomic unit for completing a job.
    A chain contains at least two components:
    1. an agent 2. a retriever
    A chain object must have the function to perform a job.
    Each chain is also equipped with a logger
    '''
    def __init__(self, agent: LLMCore, retriever: BasicRetriever):
        object.__setattr__(self, 'agent', agent)
        object.__setattr__(self, 'retriever', retriever)
        self.agent.equip_retriever(self.retriever)
        object.__setattr__(self, 'logger', get_logger(self.__class__.__name__))

    @abstractclassmethod
    def from_config(cls,
                    open_ai_key: str,
                    prompt_name: str = 'question_database',
                    temperature: float = 0.0) -> Any:
        """
        Initialize a BasicChain class from configurations
        Args:
            open_ai_key (str): openai api key
            prompt_name (str, optional): prompt to use.
            temperature (float, optional): how unstable the llm should behave.
                Defaults to 0.0.

        Returns:
            BasicChain: the Basic Chain class itself.
        """
        llm = OpenAI(temperature=temperature, openai_api_key=open_ai_key)
        agent = LLMCore(prompt=BasicPrompt.load_prompt_from_json_file(
                    prompt_name), llm=llm)
        retriever = BasicRetriever()
        return cls(agent=agent, retriever=retriever)

    @abstractclassmethod
    def perform(self, **kwargs: Any) -> Any:
        """
        Core function to perform.
        Returns:
            Any: the chain execution result.
        """
        result = self.agent.predict(kwargs)
        return result

    def perform_cost_monitor(self, budget: float = 100, **kwargs: Any):
        """
        Specific for OpenAI API use.
        Args:
            budget (float, optional): _description_. Defaults to 100.

        Returns:
            _type_: _description_
        """
        with get_openai_tracer(id=self.__class__.__name__,
                               budget=budget) as cb:
            try:
                result = self.perform(**kwargs)
            except Exception as e:
                result = str(e)
                self.logger.warning(cb.cur_trace.output)
        self.logger.propagate = False
        self.logger.cost(openai_cb_2_str(cb))

        return result, cb

    def perform_monitor(self, **kwargs: Any):
        """
        Specific for Llamacpp use.
        Args:
        Returns:
            _type_: _description_
        """
        with get_general_tracer(id=self.__class__.__name__) as cb:
            try:
                result = self.perform(**kwargs)
            except Exception as e:
                result = str(e)
                self.logger.warning(cb.cur_trace.output)
        print(cb.cur_trace.output)
        self.logger.cost(openai_cb_2_str(cb))
        return result, cb


class BasicCombinedChain(BasicChain, ABC):
    '''
    Abstract class for combined Chain class.
    A combined chain is a chain with multiple chains
    A chain class should be the atomic unit for completing a job.
    A chain object must have the function to perform a job.
    '''
    def __init__(self, chains: List[BasicChain]):
        object.__setattr__(self, "chains", chains)
        object.__setattr__(self, "logger", get_logger(self.__class__.__name__))

    @abstractclassmethod
    def from_config(cls, **kwargs: Any):
        pass

    @abstractclassmethod
    def perform(self, **kwargs: Any):
        pass
