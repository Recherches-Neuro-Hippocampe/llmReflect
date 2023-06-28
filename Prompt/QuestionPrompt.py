from typing import Any, Dict
from Prompt.BasicPrompt import BasicPrompt
import re


class QuestionPostgresPrompt(BasicPrompt):
    def __init__(self, prompt_dict: Dict[str, Any], promptname: str) -> None:
        super().__init__(prompt_dict, promptname)

    def __assemble__(self):
        self.string_temp = ""
        self.string_temp += self.hard_rules
        self.string_temp += "\n\n"
        self.string_temp += self.soft_rules
        self.string_temp += "\n\n"
        self.string_temp += "For examples:\n\n"
        self.string_temp += self.in_context_learning
        self.string_temp += "\n\n"
        self.string_temp += '''Come up with {n_questions} question(s) \
similar to the examples. You must use the following format:

Question: "the question created by you"
Explanation:
    "1.Why it is a good question"
    "2.Why it is a good question"
    "3.Why it is a good question"
    ...
    "n.Why it is a good question"

Question: "the second question created by you"
Explanation:
    "1.Why it is a good question"
    ...
    "n.Why it is a good question"
'''

    def __get_inputs__(self):
        pattern = r'{([^}]*)}'
        matches = re.findall(pattern, self.hard_rules)
        matches.append("n_questions")
        return matches
