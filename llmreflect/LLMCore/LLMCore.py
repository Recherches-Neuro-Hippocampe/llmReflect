from typing import Any, List, Dict, Union, Optional
from langchain.chains import LLMChain
from llmreflect.Prompt.BasicPrompt import BasicPrompt
from langchain.base_language import BaseLanguageModel
from abc import ABC
from dataclasses import dataclass
from langchain.chat_models import ChatOpenAI
from llmreflect.Utils.log import get_logger
from llmreflect.Utils.log import openai_trace_var,\
    check_current_openai_balance, general_trace_var
from langchain.callbacks.base import BaseCallbackHandler, BaseCallbackManager
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.manager import CallbackManagerForChainRun
import inspect
from langchain.load.dump import dumpd
from langchain.schema import RUN_KEY, RunInfo, LLMResult
from langchain.llms import LlamaCpp

Callbacks = Optional[Union[List[BaseCallbackHandler], BaseCallbackManager]]


@dataclass
class LLM_BACKBONE_MODEL:
    """
    LLM names used for referencing
    """
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


class LLMCore(LLMChain, ABC):
    def __init__(self, prompt: BasicPrompt, llm: BaseLanguageModel):
        super().__init__(prompt=prompt.get_langchain_prompt_template(),
                         llm=llm)
        """
        Abstract class for core functions of LLM, 
        inherit from the LLM chain class. 
        Args:
            prompt (BasicPrompt): Prompt class to use.
            llm_model (BaseLanguageModel): llm class to use
        """
        object.__setattr__(self, "logger", get_logger(self.__class__.__name__))
        object.__setattr__(self, "max_output_tokens", self.llm.max_tokens)
        object.__setattr__(self, "model_name", self.llm.model_name)

    def get_inputs(self) -> List[str]:
        """
        showing inputs for the prompt template being used
        Returns:
            List: a list of strings
        """
        return self.prompt.input_variables


class OpenAICore(LLMCore):
    def __init__(self, open_ai_key: str,
                 prompt_name: str = '',
                 max_output_tokens: int = 512,
                 temperature: float = 0.0,
                 llm_model=LLM_BACKBONE_MODEL.gpt_3_5_turbo):
        """
        Agent class specifically designed for openAI.
        Args:
            open_ai_key (str): OpenAI key
            prompt_name (str, optional): name for the prompt. Defaults to ''.
            max_output_tokens (int, optional): maximum number of output tokens. Defaults to 512.
            temperature (float, optional): Flexibility of the output. Defaults to 0.0.
            llm_model (str, optional): string indicating the mode to use.
                Should be included in class LLM_BACKBONE_MODEL.
                Defaults to LLM_BACKBONE_MODEL.gpt_3_5_turbo.
        """
        prompt = BasicPrompt.\
            load_prompt_from_json_file(prompt_name)
        llm = ChatOpenAI(temperature=temperature,
                         openai_api_key=open_ai_key,
                         model=llm_model)
        llm.max_tokens = max_output_tokens
        super().__init__(prompt=prompt,
                         llm=llm)

    def get_inputs(self) -> List[str]:
        """
        showing inputs for the prompt template being used
        Returns:
            List: A list of input variable, each one should be str
        """
        return self.prompt.input_variables

    def predict(self, **kwargs: Any) -> str:
        """
        The llm prediction interface.
        Returns:
            str: The output / completion generated by llm.
        """
        return self._predict(inputs=kwargs, callbacks=[openai_trace_var.get()])

    def _predict(
        self,
        inputs: Union[Dict[str, Any], Any],
        return_only_outputs: bool = False,
        callbacks: Callbacks = None,
        *,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        include_run_info: bool = False,
    ) -> Dict[str, Any]:
        """Execute the chain.

        Args:
            inputs: Dictionary of inputs, or single input if chain expects
                only one param. Should contain all inputs specified in
                `Chain.input_keys` except for inputs that will be set by the
                chain's memory.
            return_only_outputs: Whether to return only outputs in the
                response. If True, only new keys generated by this chain will
                be returned. If False, both input keys and new keys generated
                by this chain will be returned. Defaults to False.
            callbacks: Callbacks to use for this chain run. These will be
                called in addition to callbacks passed to the chain during
                construction, but only these runtime callbacks will propagate
                to calls to other objects.
            tags: List of string tags to pass to all callbacks. These will be
                passed in addition to tags passed to the chain during
                construction, but only these runtime tags will propagate to
                calls to other objects.
            metadata: Optional metadata associated with the chain.
                Defaults to None
            include_run_info: Whether to include run info in the response.
                Defaults to False.

        Returns:
            A dict of named outputs. Should contain all outputs specified in
                `Chain.output_keys`.
        """
        inputs = self.prep_inputs(inputs)
        callback_manager = CallbackManager.configure(
            callbacks,
            self.callbacks,
            self.verbose,
            tags,
            self.tags,
            metadata,
            self.metadata,
        )
        new_arg_supported = inspect.signature(self._call).\
            parameters.get("run_manager")
        run_manager = callback_manager.on_chain_start(
            dumpd(self),
            inputs,
        )
        try:
            outputs = (
                self._call(inputs, run_manager=run_manager)
                if new_arg_supported
                else self._call(inputs)
            )
        except (KeyboardInterrupt, Exception) as e:
            run_manager.on_chain_error(e)
            raise e
        run_manager.on_chain_end(outputs)
        final_outputs: Dict[str, Any] = self.prep_outputs(
            inputs, outputs, return_only_outputs
        )
        if include_run_info:
            final_outputs[RUN_KEY] = RunInfo(run_id=run_manager.run_id)
        return final_outputs[self.output_key]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        """call function used in _predict function

        Args:
            inputs (Dict[str, Any]): inputs prepared by `self.prep_input`
            run_manager (Optional[CallbackManagerForChainRun], optional):
                run manager provided by callback manager. Defaults to None.

        Returns:
            Dict[str, str]: llm outputs
        """
        response = self.generate([inputs], run_manager=run_manager)
        return self.create_outputs(response)[0]

    def generate(
        self,
        input_list: List[Dict[str, Any]],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> LLMResult:
        """
        The core function for generating LLM result from inputs.
        By using the "check_current_openai_balance". The generation
        will be stopped when the cost is going to exceed the budget.
        """
        prompts, stop = self.prep_prompts(input_list, run_manager=run_manager)
        run_permit = check_current_openai_balance(
            input_prompt=prompts[0].to_string(),
            max_output_tokens=self.max_output_tokens,
            model_name=self.model_name,
            logger=self.logger)
        if run_permit:
            return self.llm.generate_prompt(
                prompts,
                stop,
                callbacks=run_manager.get_child() if run_manager else None,
                **self.llm_kwargs,
            )
        else:
            raise Exception("Budget Error: The next round text completion \
is likely to exceed the budget. LLM is forced to stop.")


class LlamacppCore(LLMCore):
    def __init__(self,
                 model_path: str,
                 prompt_name: str = '',
                 max_total_tokens: int = 2048,
                 max_output_tokens: int = 512,
                 temperature: float = 0.0,
                 verbose: bool = False,
                 n_gpus_layers: int = 8,
                 n_threads: int = 16,
                 n_batch: int = 512,
                 ):
        """
        The Agent class using Llamacpp.
        Args:
            model_path (str): Path to the model.
            prompt_name (str, optional): name for prompt. Defaults to ''.
            max_total_tokens (int, optional): Maximum context size.
                Defaults to 2048.
            max_output_tokens (int, optional): Maximum size of completion.
                Defaults to 512.
            temperature (float, optional): Flexibility of the model.
                Defaults to 0.0.
            verbose (bool, optional): whether to print the status.
                Defaults to False.
            n_gpus_layers (int, optional): number of layer to load on gpu.
                Defaults to 8.
            n_threads (int, optional): Number of threads to use.
                Defaults to 16.
            n_batch (int, optional): Maximum number of prompt tokens to batch
                together when calling llama_eval.
                Defaults to 512.
        """
        prompt = BasicPrompt.\
            load_prompt_from_json_file(prompt_name)
        llm = LlamaCpp(
            model_path=model_path,
            n_ctx=max_total_tokens,
            max_tokens=max_output_tokens,
            temperature=temperature,
            n_gpu_layers=n_gpus_layers,
            n_threads=n_threads,
            n_batch=n_batch,
            verbose=verbose)

        super().__init__(prompt=prompt,
                         llm=llm)

    def get_inputs(self) -> List[str]:
        """
        showing inputs for the prompt template being used
        Returns:
            List: A list of input variable, each one should be str
        """
        return self.prompt.input_variables

    def predict(self, **kwargs: Any) -> str:
        """
        The llm prediction interface.
        Returns:
            str: The output / completion generated by llm.
        """
        return self._predict(inputs=kwargs, callbacks=[general_trace_var.get()])

    def _predict(
        self,
        inputs: Union[Dict[str, Any], Any],
        return_only_outputs: bool = False,
        callbacks: Callbacks = None,
        *,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        include_run_info: bool = False,
    ) -> Dict[str, Any]:
        """Execute the chain.

        Args:
            inputs: Dictionary of inputs, or single input if chain expects
                only one param. Should contain all inputs specified in
                `Chain.input_keys` except for inputs that will be set by the
                chain's memory.
            return_only_outputs: Whether to return only outputs in the
                response. If True, only new keys generated by this chain will
                be returned. If False, both input keys and new keys generated
                by this chain will be returned. Defaults to False.
            callbacks: Callbacks to use for this chain run. These will be
                called in addition to callbacks passed to the chain during
                construction, but only these runtime callbacks will propagate
                to calls to other objects.
            tags: List of string tags to pass to all callbacks. These will be
                passed in addition to tags passed to the chain during
                construction, but only these runtime tags will propagate to
                calls to other objects.
            metadata: Optional metadata associated with the chain.
                Defaults to None
            include_run_info: Whether to include run info in the response.
                Defaults to False.

        Returns:
            A dict of named outputs. Should contain all outputs specified in
                `Chain.output_keys`.
        """
        inputs = self.prep_inputs(inputs)
        callback_manager = CallbackManager.configure(
            callbacks,
            self.callbacks,
            self.verbose,
            tags,
            self.tags,
            metadata,
            self.metadata,
        )
        new_arg_supported = inspect.signature(self._call).\
            parameters.get("run_manager")
        run_manager = callback_manager.on_chain_start(
            dumpd(self),
            inputs,
        )
        try:
            outputs = (
                self._call(inputs, run_manager=run_manager)
                if new_arg_supported
                else self._call(inputs)
            )
        except (KeyboardInterrupt, Exception) as e:
            run_manager.on_chain_error(e)
            raise e
        run_manager.on_chain_end(outputs)
        final_outputs: Dict[str, Any] = self.prep_outputs(
            inputs, outputs, return_only_outputs
        )
        if include_run_info:
            final_outputs[RUN_KEY] = RunInfo(run_id=run_manager.run_id)
        return final_outputs[self.output_key]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        """call function used in _predict function

        Args:
            inputs (Dict[str, Any]): inputs prepared by `self.prep_input`
            run_manager (Optional[CallbackManagerForChainRun], optional):
                run manager provided by callback manager. Defaults to None.

        Returns:
            Dict[str, str]: llm outputs
        """
        response = self.generate([inputs], run_manager=run_manager)
        return self.create_outputs(response)[0]

    def generate(
        self,
        input_list: List[Dict[str, Any]],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> LLMResult:
        """
        The core function for generating LLM result from inputs.
        By using the "check_current_openai_balance". The generation
        will be stopped when the cost is going to exceed the budget.
        """
        prompts, stop = self.prep_prompts(input_list, run_manager=run_manager)

        return self.llm.generate_prompt(
            prompts,
            stop,
            callbacks=run_manager.get_child() if run_manager else None,
            **self.llm_kwargs,
        )
