from typing import Any, Dict
from Prompt.BasicPrompt import BasicPrompt
import re


class GradingPrompt(BasicPrompt):
    def __init__(self, prompt_dict: Dict[str, Any], promptname: str) -> None:
        super().__init__(prompt_dict, promptname)

    def __assemble__(self):
        self.string_temp = ""
        self.string_temp += self.hard_rules
        self.string_temp += "\n\n"
        self.string_temp += self.soft_rules
        self.string_temp += "\n\n"
        if len(self.in_context_learning) > 0:
            self.string_temp += "For examples:\n\n"
            self.string_temp += self.in_context_learning
            self.string_temp += "\n\n"
        self.string_temp += '''\
Use the following format:

[Request] "User's natural language request"
[Command] "postgresql command"
[Summary] "Summarized postgresql result"
[Grading] "A number from 0 to 10"
[Explanation] "Your explanation for the grade you assigned"

[Request] {request}
[Command] {sql_cmd}
[Summary] {db_summary}

'''

    def __get_inputs__(self):
        pattern = r'{([^}]*)}'
        matches = re.findall(pattern, self.hard_rules)
        matches.append("request")
        matches.append("sql_cmd")
        matches.append("db_summary")
        return matches
