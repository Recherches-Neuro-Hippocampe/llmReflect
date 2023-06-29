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


class BasicPrompt:
    """
    Mighty mother of all prompts (In this repo I mean)
    """
    def __init__(self, prompt_dict: Dict[str, Any], promptname: str) -> None:
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
        self.prompt_dict = prompt_dict
        self._hard_rules = prompt_dict["HARD"]
        self._soft_rules = prompt_dict["SOFT"]
        self._in_context_learning = prompt_dict["INCONTEXT"]
        self.input_list = self.__get_inputs__()
        self.string_temp = ""
        self.__assemble__()
        self.prompt_template = PromptTemplate(input_variables=self.input_list,
                                              template=self.string_temp)

    def __get_inputs__(self):
        # function for find all input variables in the f string
        # (prompt template)
        pattern = r'{([^}]*)}'
        matches = re.findall(pattern, self.hard_rules)
        matches.append("input")
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
        self.string_temp += "Request: {input}"
        self.string_temp += "\n"
        self.string_temp += "Answer: "

    def get_langchain_prompt_template(self):
        return self.prompt_template

    @classmethod
    def load_prompt_from_json_file(cls, promptname: str):
        # Method for loading prompt based on the name of the prompt
        default_js = {
            "HARD": "",
            "SOFT": "",
            "INCONTEXT": ""}
        prompt_dir = os.path.join(PROMPT_BASE_DIR, promptname + '.json')
        print(prompt_dir)
        try:
            with open(prompt_dir, 'r') as openfile:
                js = json.load(openfile)
            message(msg=f"{promptname} prompt loaded successfully!",
                    color="green")

        except Exception as error:
            print(type(error).__name__)
            message(msg=f"Prompt {promptname} not found!", color="red")
            js = default_js

        return cls(prompt_dict=js, promptname=promptname)

    def save_prompt(self):
        """
        save prompt into json file.
        """
        try:
            assert len(self.prompt_dict.keys()) == 3
            assert "HARD" in self.prompt_dict.keys()
            assert "SOFT" in self.prompt_dict.keys()
            assert "INCONTEXT" in self.prompt_dict.keys()
        except Exception:
            message(msg="Prompt dictionary format is illegal!", color="red")
            return

        saving_dir = os.path.join(PROMPT_BASE_DIR, f"{self.promptname}.json")
        with open(saving_dir, 'w') as writefile:
            json.dump(self.prompt_dict, writefile)

        message(msg=f"{self.promptname} has been dumped into {saving_dir}",
                color="green")

    @property
    def hard_rules(self):
        return self._hard_rules

    @hard_rules.setter
    def hard_rules(self, rule: str):
        self._hard_rules = rule
        self.prompt_dict['HARD'] = self._hard_rules
        self.__assemble__()

    @property
    def soft_rules(self):
        return self._soft_rules

    @soft_rules.setter
    def soft_rules(self, rule: str):
        self._soft_rules = rule
        self.prompt_dict['SOFT'] = self._soft_rules
        self.__assemble__()

    @property
    def in_context_learning(self):
        return self._in_context_learning

    @in_context_learning.setter
    def in_context_learning(self, rule: str):
        self._in_context_learning = rule
        self.prompt_dict['INCONTEXT'] = self._in_context_learning
        self.__assemble__()
