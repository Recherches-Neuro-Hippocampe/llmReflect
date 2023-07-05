"""
Module for prompt template, based on langchain prompt.
A prompt can be divied into 3 parts:
1. Hard rules which are fixed and permanant.
2. Soft rule which can be modified by Agents only when necessary.
3. In-context learning, places for holding in-context learning examples,
the major part that Agents can tune.
"""
from typing import Dict, Any
from langchain.prompts.prompt import PromptTemplate
import os
from llmreflect.Utils.message import message
import json
import re

PROMPT_BASE_DIR = os.path.join(os.getcwd(),
                               'llmreflect', 'Prompt', 'promptbase')
INPUT_KEY_TYPE_CHOICE = ['INPUT', 'OUTPUT']


class BasicPrompt:
    """
    Mighty mother of all prompts (In this repo I mean)
    """
    def __init__(self, prompt_dict: Dict[str, Any], promptname: str,
                 customized_input_list: list = []) -> None:
        """
        If you want to start working on a prompt from scratch,
        a dictionary containing the prompts and name of this prompt
        are required.
        Args:
            prompt_dict (Dict[str, Any]): In this design,
            a prompt can be divided into 3 parts,
            hard rules, soft rule and in-context learning.
            Hard rules indicate the general context for the LLM and
            we usually do not change the hard rules.
            Soft rules are the rules that focus on the refine the
            behavior for the model, used for formatting or tuning.
            In-context learning is just a cool word to say examples.
            We all need examples right?
            promptname (str): nickname by you for the prompt.
            Also used as the file name to store the prompt in
            json format in 'promptbase' folder.

            Overall this design is to enable the model to tune itself.
            So there are rules the model can touch and others cant.
            Also I hate people keeping prompts in the coding logic place.

        """
        self.promptname = promptname
        self.__valid_prompt_dict(prompt_dict)
        self.prompt_dict = prompt_dict
        self._hard_rules = prompt_dict["HARD"]
        self._soft_rules = prompt_dict["SOFT"]
        self._in_context_learning_list = prompt_dict["INCONTEXT"]
        self._format_dict = prompt_dict["FORMAT"]

        self.__assemble__()
        if len(customized_input_list) > 0:
            self.input_list = customized_input_list
        else:
            self.input_list = self.__get_inputs__()
        self.prompt_template = PromptTemplate(input_variables=self.input_list,
                                              template=self.string_temp)

    def __valid_prompt_dict(self, prompt_dict):
        """
        method for validating prompt dictionary
        Args:
            prompt_dict (_type_): _description_
        """
        assert "HARD" in prompt_dict.keys()
        assert "SOFT" in prompt_dict.keys()
        assert "INCONTEXT" in prompt_dict.keys()
        assert "FORMAT" in prompt_dict.keys()
        assert type(prompt_dict["HARD"]) is str
        assert type(prompt_dict["SOFT"]) is str
        assert type(prompt_dict["INCONTEXT"]) is list
        assert type(prompt_dict["FORMAT"]) is dict
        for item in prompt_dict["INCONTEXT"]:
            for key in item.keys():
                assert key in prompt_dict["FORMAT"].keys()
        for key in prompt_dict["FORMAT"]:
            assert "type" in prompt_dict["FORMAT"][key].keys()
            assert "explanation" in prompt_dict["FORMAT"][key].keys()
            assert prompt_dict["FORMAT"][key]['type'] in INPUT_KEY_TYPE_CHOICE

    def __get_inputs__(self):
        # function for find all input variables in the f string
        # (prompt template)
        pattern = r'{([^}]*)}'
        matches = re.findall(pattern, self.hard_rules)
        matches.extend(re.findall(pattern, self.soft_rules))
        matches.extend(re.findall(pattern, self.input_format))
        matches.extend(re.findall(pattern, self.completion_head_up))
        matches = set(matches)  # the input variables cannot have same keys
        return matches

    def __assemble__(self):
        """
        assemble into one string
        """
        self.string_temp = ""
        self.string_temp += self.hard_rules
        self.string_temp += "\n\n"
        self.string_temp += self.soft_rules
        self.string_temp += "\n\n"
        self.string_temp += "For examples:\n\n"
        self.string_temp += self.in_context_learning
        self.string_temp += "\n\n"
        self.string_temp += "You must use the following format:\n\n"
        self.string_temp += self.input_format
        self.string_temp += "\n\n"
        self.string_temp += self.completion_head_up

    def get_langchain_prompt_template(self):
        return self.prompt_template

    @classmethod
    def load_prompt_from_json_file(cls, promptname: str):
        js = cls._load_json_file(promptname=promptname)
        message(msg=f"{promptname} prompt loaded successfully!",
                color="green")

        return cls(prompt_dict=js, promptname=promptname)

    @classmethod
    def _load_json_file(cls, promptname: str):
        prompt_dir = os.path.join(PROMPT_BASE_DIR, promptname + '.json')

        with open(prompt_dir, 'r') as openfile:
            js = json.load(openfile)
        return js

    def save_prompt(self):
        """
        save prompt into json file.
        """
        try:
            self.__valid_prompt_dict(self.prompt_dict)
        except Exception:
            message(msg="Prompt dictionary format is illegal!", color="red")
            return

        saving_dir = os.path.join(PROMPT_BASE_DIR, f"{self.promptname}.json")
        with open(saving_dir, 'w') as writefile:
            json.dump(self.prompt_dict, writefile)

        message(msg=f"{self.promptname} has been dumped into {saving_dir}",
                color="green")

    @classmethod
    def wrap_key_name(cls, key_name):
        return "[" + key_name + "]"

    @property
    def hard_rules(self):
        return self._hard_rules

    @hard_rules.setter
    def hard_rules(self, rule: str):
        self._hard_rules = rule
        self.prompt_dict['HARD'] = self._hard_rules
        self.__valid_prompt_dict()
        self.__assemble__()

    @property
    def soft_rules(self):
        return self._soft_rules

    @soft_rules.setter
    def soft_rules(self, rule: str):
        self._soft_rules = rule
        self.prompt_dict['SOFT'] = self._soft_rules
        self.__valid_prompt_dict()
        self.__assemble__()

    @property
    def in_context_learning(self):
        txt = ""

        for each_dict in self._in_context_learning_list:
            for key in each_dict.keys():
                txt += "\n"
                txt += self.wrap_key_name(key)
                txt += " "
                txt += each_dict[key]
            txt += "\n"
        return txt

    @in_context_learning.setter
    def in_context_learning(self, rule: list):
        self._in_context_learning = rule
        self.prompt_dict['INCONTEXT'] = self._in_context_learning
        self.__valid_prompt_dict()
        self.__assemble__()

    @property
    def input_format(self):
        txt = ""
        for key in self._format_dict.keys():
            txt += "\n"
            txt += self.wrap_key_name(key)
            txt += " "
            txt += self._format_dict[key]['explanation']
        return txt

    @input_format.setter
    def input_format(self, input_format: dict):
        self._format_dict = input_format
        self.prompt_dict["FORMAT"] = self._format_dict
        self.__valid_prompt_dict()
        self.__assemble__()

    @property
    def completion_head_up(self):
        txt = ""
        for key in self._format_dict.keys():
            if self._format_dict[key]['type'] == "INPUT":
                txt += "\n"
                txt += self.wrap_key_name(key)
                txt += " "
                txt += "{"
                txt += key
                txt += "}"
        return txt
