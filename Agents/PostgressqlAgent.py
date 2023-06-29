from Agents.BasicAgent import Agent
from langchain.llms.openai import OpenAI
from decouple import config
from Utils.message import message
from Retriever.DatabaseRetriever import DatabaseRetriever
from Prompt.BasicPrompt import BasicPrompt
from typing import Any


class PostgresqlAgent(Agent):
    """
    Agent class for executing postgresql command
    Args:
        Agent (_type_): _description_
    """
    def __init__(self):
        prompt = BasicPrompt.load_prompt_from_json_file('postgressql')
        llm = OpenAI(temperature=0, openai_api_key=config('OPENAI_API_KEY'))
        llm.max_tokens = int(config('MAX_OUTPUT'))
        super().__init__(prompt=prompt,
                         llm=llm)

    def equip_retriever(self, retriever: DatabaseRetriever):
        """_summary_

        Args:
            retriever (DatabaseRetriever): use database retriever
        """
        object.__setattr__(self, 'retriever', retriever)

    def predict_sql_cmd(self, user_input: str) -> str:
        """
        Generate the postgresql command, it is a gross output which means
        no post processing. It could be a wrong format that not executable.
        Need extraction and cleaning and formatting.
        Args:
            user_input (str): users description for the query.

        Returns:
            str: gross output of the llm attempt for generating sql cmd.
        """
        llm_output = "Failed, no output from LLM."
        if self.retriever is None:
            message("Error: Retriever is not equipped.", color="red")
        else:
            llm_output = self.predict(
                dialect=self.retriever.database_dialect,
                max_present=self.retriever.max_rows_return,
                table_info=self.retriever.table_info,
                input=user_input
            )
        return llm_output

    def predict_db(self, user_input: str) -> str:
        """
        Predict sql cmd based on the user's description then
        use the langchain method run_no_throw
        to retrieve sql result.
        Args:
            user_input (str): users description for the query.

        Returns:
            str: I know its odd but it is a string. It converts the
            database cursor result into a string. Not very useful, I dont
            know why Im keeping this method.
        """
        llm_output = self.predict_sql_cmd(user_input=user_input)
        sql_result = self.retriever.retrieve(llm_output=llm_output)
        return sql_result

    def predict_db_summary(self, user_input: str,
                           return_cmd: bool = False) -> Any:
        """
        Predict sql cmd based on the user's description then
        use the sqlalchemy to retrieve the sql result,
        then summarize the result into a shorten string.
        It is used to provide llm context and condense information
        and save tokens. cheaper better money little
        Args:
            user_input (str): user's description for the query
            return_cmd (bool, optional):
            Decide if return the middle step sql cmd.
            Defaults to False.
            If true, return a dictionary.

        Returns:
            str: If the middle step (sql cmd) is not required,
            return a single string which summarize the query result.
            Otherwise return a dict.
            {'cmd': sql_cmd, 'summary': summary}
        """
        llm_output = self.predict_sql_cmd(user_input=user_input)
        result = self.retriever.retrieve_summary(
            llm_output=llm_output,
            return_cmd=return_cmd)
        return result
