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
from Utils.message import message
import json
import re

PROMPT_BASE_DIR = os.path.join(os.getcwd(), 'Prompt', 'promptbase')


class BasicPrompt:
    def __init__(self, js: Dict[str, Any]) -> None:
        self.hard_rules = js["HARD"]
        self.soft_rules = js["SOFT"]
        self.in_context_learning = js["INCONTEXT"]
        self.input_list = self.__get_inputs__()
        self.string_temp = ""
        self.__assemble__()
        self.prompt_template = PromptTemplate(input_variables=self.input_list,
                                              template=self.string_temp)

    def __get_inputs__(self):
        pattern = r'{([^}]*)}'
        matches = re.findall(pattern, self.hard_rules)
        matches.append("input")
        return matches

    def __assemble__(self):
        self.string_temp = ""
        self.string_temp += self.hard_rules
        self.string_temp += "\n"
        self.string_temp += self.soft_rules
        self.string_temp += "\n"
        self.string_temp += self.in_context_learning
        self.string_temp += "\n"
        self.string_temp += "Request: {input}"
        self.string_temp += "\n"
        self.string_temp += "Answer: "

    def get_langchain_prompt_template(self):
        return self.prompt_template


def load_prompt(promptname: str) -> BasicPrompt:
    # Method for loading prompt based on the name of the prompt
    default_js = {
            "HARD": "",
            "SOFT": "",
            "INCONTEXT": ""
        }
    prompt_dir = os.path.join(PROMPT_BASE_DIR, promptname + '.json')

    try:
        with open(prompt_dir, 'r') as openfile:
            js = json.load(openfile)
        message(msg=f"{promptname} prompt loaded successfully!", color="green")

    except Exception as error:
        print(type(error).__name__)
        message(msg=f"Prompt {promptname} not found!", color="red")
        js = default_js
    return BasicPrompt(js=js)


def save_prompt(promptname, prompt_dict: dict):
    try:
        assert len(prompt_dict.keys()) == 3
        assert "HARD" in prompt_dict.keys()
        assert "SOFT" in prompt_dict.keys()
        assert "INCONTEXT" in prompt_dict.keys()
    except Exception:
        message(msg="Prompt dictionary format is illegal!", color="red")
        return

    saving_dir = os.path.join(PROMPT_BASE_DIR, f"{promptname}.json")
    with open(saving_dir, 'w') as writefile:
        json.dump(prompt_dict, writefile)

    message(msg=f"{promptname} has been dumped into {saving_dir}",
            color="green")
