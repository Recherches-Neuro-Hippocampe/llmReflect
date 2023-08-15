from abc import ABC, abstractclassmethod
from llmreflect.Retriever.BasicRetriever import BasicRetriever
from llmreflect.Agents.BasicAgent import BasicAgent
from typing import Any, List, Callable
from llmreflect.Utils.log import get_logger, tracer_2_str
from llmreflect.Utils.log import get_tracer
import inspect
import json


class PrettyDict(dict):
    def __init__(self, value: Any):
        """This a wrapper class to print pretty dictionary.

        Args:
            value (Any): A dictionary usually.
        """
        super().__init__(value)
        self.value = value

    def __str__(self) -> str:
        """Override string conversion

        Returns:
            str: diction prettified by json
        """
        return str(json.dumps(
            self.value,
            sort_keys=True, indent=4
        ))

    def __repr__(self) -> dict:
        return self.value


class classproperty:
    def __init__(self, method: Callable):
        """
        A decorator, a wrapper class for class property: configuration.
        Since the configurations as dictionaries are ugly,
        so we convert it to a json format to make it look better.
        Args:
            method (Callable): _description_
        """
        self.method = method

    def __get__(self, instance, owner):
        return PrettyDict(self.method.__func__(owner))


class BasicChain(ABC):

    AgentClass = BasicAgent
    RetrieverClass = BasicRetriever

    def __init__(self, agent: BasicAgent, retriever: BasicRetriever,
                 **kwargs):
        """
        Abstract class for Chain class.
        A chain class should be the atomic unit for completing a job.
        A chain contains at least two components:
        1. an agent 2. a retriever
        A chain object must have the function to perform a job.
        Each chain is also equipped with a logger

        Args:
            agent (BasicAgent): An instance of Agent class.
            retriever (BasicRetriever): An instance of Retriever class.
        """
        object.__setattr__(self, 'agent', agent)
        object.__setattr__(self, 'retriever', retriever)
        self.agent.equip_retriever(self.retriever)
        object.__setattr__(self, 'logger', get_logger(self.__class__.__name__))

    @classmethod
    def get_required_retriever(cls, **kwargs) -> BasicRetriever:
        """A class method to get an instance from required Retriever class.

        Returns:
            BasicRetriever: An instance of Retriever class.
        """
        return cls.RetrieverClass(**kwargs)

    @classmethod
    def init(cls, agent: BasicAgent, retriever: BasicRetriever) -> Any:
        """A class method to initialize the class itself.
        Not put in any use for now.

        Args:
            agent (BasicAgent): An instance of an Agent class.
            retriever (BasicRetriever): An instance of a Retriever class.

        Returns:
            Any: An instance of the chain itself.
        """
        return cls(agent=agent, retriever=retriever)

    @classmethod
    def from_config(cls, **kwargs: Any) -> Any:
        """Initialize an instance of a Chain class from configuration.

        Returns:
            Any: An instance of the Chain itself.
        """
        retriever_config = kwargs.get("retriever_config", {})
        llm_config = kwargs.get("llm_config", {})
        other_config = kwargs.get("other_config", {})
        retriever = cls.get_required_retriever(**retriever_config)
        agent = cls.AgentClass.from_config(llm_config=llm_config,
                                           other_config=other_config)
        return cls(agent=agent, retriever=retriever)

    @classmethod
    def get_config_dict(cls, local: bool = True) -> dict:
        """Return a form (instruction) of the configuration
        required by a chain.
        Which is going to be converted into a prettier string by the
        `classproperty` decorator.

        Args:
            local (bool, optional): whether to use local model.
                If False, will use OpenAI Api.
                Defaults to True.

        Returns:
            dict: The instructions to initialize the chain.
        """
        retriever_sig = inspect.signature(cls.RetrieverClass.__init__)

        if local:
            init_llm_func = cls.AgentClass.init_llm_from_llama
        else:
            init_llm_func = cls.AgentClass.init_llm_from_openai

        init_llm_sig = inspect.signature(init_llm_func)

        other_sig = inspect.signature(cls.AgentClass.__init__)

        config = {}
        llm_config = {}
        other_config = {}
        retriever_config = {}

        for name, param in retriever_sig.parameters.items():
            if name == "self":
                continue
            if param.default == inspect.Parameter.empty:
                retriever_config[name] = "Requiring"
            else:
                retriever_config[name] = param.default
        config["retriever_config"] = retriever_config

        for name, param in init_llm_sig.parameters.items():
            if name == "self":
                continue
            if param.default == inspect.Parameter.empty:
                if name == "prompt_name":
                    other_config["prompt_name"] = cls.AgentClass.PROMPT_NAME
                else:
                    llm_config[name] = "Requiring"

            else:
                llm_config[name] = param.default
        config["llm_config"] = llm_config

        for name, param in other_sig.parameters.items():
            if name == "self" or name == "llm_core" or name == "kwargs":
                continue
            if param.default == inspect.Parameter.empty:
                other_config[name] = "Requiring"
            else:
                other_config[name] = param.default
        config["other_config"] = other_config

        return config

    @classproperty
    @classmethod
    def local_config_dict(cls) -> dict:
        """A class property indicating the configurations
        required to initialize the chain using local LLM.

        Returns:
            dict: a dictionary but will be converted into string
            by the decorator `classproperty`

        """
        return cls.get_config_dict(local=True)

    @classproperty
    @classmethod
    def openai_config_dict(cls) -> dict:
        """A class property indicating the configurations
        required to initialize the chain using OpenAI LLM.

        Returns:
            dict: a dictionary but will be converted into string
            by the decorator `classproperty`

        """
        return cls.get_config_dict(local=False)

    @abstractclassmethod
    def perform(self, **kwargs: Any) -> Any:
        """
        Core function to perform.
        Returns:
            Any: the chain execution result.
        """
        result = self.agent.predict(kwargs)
        return result

    def perform_cost_monitor(self, budget: float = 100, **kwargs: Any) -> Any:
        """
        performing the chain function while
        logging the cost and other llm behaviors
        Args:
            budget (float, optional): _description_. Defaults to 100.

        Returns:
            Any: the chain execution result and a llm callback handler
        """
        with get_tracer(id=self.__class__.__name__,
                        budget=budget) as cb:
            try:
                result = self.perform(**kwargs)
            except Exception as e:
                result = str(e)
                self.logger.warning(cb.cur_trace.output)
        self.logger.propagate = False
        self.logger.cost(tracer_2_str(cb))

        return result, cb


class BasicCombinedChain(BasicChain, ABC):
    '''
    Abstract class for combined Chain class.
    A combined chain is a chain with multiple chains
    A chain class should be the atomic unit for completing a job.
    A chain object must have the function to perform a job.
    '''
    REQUIRED_CHAINS = []

    def __init__(self, chains: List[BasicChain]):
        """Initialize an instance of the BasicCombinedChain class.

        Args:
            chains (List[BasicChain]): A list of BasicChains.
        """
        object.__setattr__(self, "chains", chains)
        object.__setattr__(self, "logger", get_logger(self.__class__.__name__))

    @classmethod
    def from_config(cls, **kwargs) -> BasicChain:
        """Initialize from configuration

        Returns:
            BasicChain: An instance of the BasicCombinedChain.
                which belongs to BasicChain.
        """
        list_chains = []
        chains_dict = {}
        for chain in cls.REQUIRED_CHAINS:
            chains_dict[chain.__name__] = chain
        for key in kwargs.keys():
            list_chains.append(chains_dict[key].from_config(**kwargs[key]))
        return cls(list_chains)

    @abstractclassmethod
    def perform(self, **kwargs: Any):
        """
        Core function to perform.
        Returns:
            Any: the chain execution result.
        """
        pass

    @classmethod
    def get_config_dict(cls, local: bool = True) -> dict:
        """A recursive function to return the configuration.

        Args:
            local (bool, optional): whether use local LLM.
                Defaults to True.

        Returns:
            dict: a configuration dictionary in a nest form.
        """
        config = {}
        for chain in cls.REQUIRED_CHAINS:
            config[chain.__name__] = chain.get_config_dict(local)
        return config
