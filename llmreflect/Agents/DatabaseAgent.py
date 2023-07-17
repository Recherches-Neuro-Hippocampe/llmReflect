from llmreflect.Agents.BasicAgent import OpenAIAgent
from llmreflect.Retriever.DatabaseRetriever import DatabaseRetriever
from typing import Any


class DatabaseAgent(OpenAIAgent):
    """
    Agent class for executing database query command
    Args:
        Agent (_type_): _description_
    """
    def __init__(self, open_ai_key: str,
                 prompt_name: str = 'answer_database',
                 max_output_tokens: int = 512,
                 temperature: float = 0.0,
                 split_symbol="[answer]"):
        """
        Agent class for querying database.
        Args:
            open_ai_key (str): API key to connect to chatgpt service.
            prompt_name (str, optional): name for the prompt json file.
                Defaults to 'answer_database'.
            max_output_tokens (int, optional): maximum completion length.
                Defaults to 512.
            temperature (float, optional): how consistent the llm performs.
                The lower the more consistent. Defaults to 0.0.
            split_symbol (str, optional): the string used for splitting answers
        """
        super().__init__(open_ai_key=open_ai_key,
                         prompt_name=prompt_name,
                         max_output_tokens=max_output_tokens,
                         temperature=temperature)
        object.__setattr__(self, 'split_symbol', split_symbol)

    def equip_retriever(self, retriever: DatabaseRetriever):
        """_summary_

        Args:
            retriever (DatabaseRetriever): use database retriever
        """
        object.__setattr__(self, 'retriever', retriever)

    def predict_sql_cmd(self, user_input: str) -> str:
        """
        Generate the database command, it is a gross output which means
        no post processing. It could be a wrong format that not executable.
        Need extraction and cleaning and formatting.
        Args:
            user_input (str): users description for the query.

        Returns:
            str: gross output of the llm attempt for generating sql cmd.
        """
        llm_output = "Failed, no output from LLM."
        if self.retriever is None:
            self.logger.error("Error: Retriever is not equipped.")
        else:
            llm_output = self.predict(
                dialect=self.retriever.database_dialect,
                max_present=self.retriever.max_rows_return,
                table_info=self.retriever.table_info,
                request=user_input
            )
            self.logger.debug(llm_output)
        return llm_output

    def predict_db(self, user_input: str,
                   get_cmd: bool = False,
                   get_summary: bool = False,
                   get_db: bool = False
                   ) -> str:
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
        assert get_cmd or get_summary or get_db, "At least get one thing"
        llm_output = self.predict_sql_cmd(user_input=user_input)
        cmd_n_summary = self.retriever.retrieve_summary(
            llm_output=llm_output,
            return_cmd=True,
            split_symbol=self.split_symbol)

        cmd = cmd_n_summary['cmd']
        summary = cmd_n_summary['summary']

        result_dict = {}
        if get_cmd:
            result_dict['cmd'] = cmd
        if get_summary:
            result_dict['summary'] = summary
        if get_db:
            db = self.retriever.retrieve(llm_output=llm_output,
                                         split_symbol=self.split_symbol)
            result_dict['db'] = db
        return result_dict

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
            return_cmd=return_cmd,
            split_symbol=self.split_symbol)
        return result


class DatabaseSelfFixAgent(DatabaseAgent):
    def predict_sql_cmd(self, user_input: str, history: str,
                        his_error: str) -> str:
        """
        Generate a database query command, it is a gross output which means
        no post processing. It could be a wrong format that not executable.
        Need extraction and cleaning and formatting.
        Args:
            user_input (str): users description for the query.
            history (str): history command used for query
            his_error (str): the errors raised from executing the history cmd
        Returns:
            str: gross output of the llm attempt for generating sql cmd.
        """
        llm_output = "Failed, no output from LLM."
        if self.retriever is None:
            self.logger.error("Error: Retriever is not equipped.")
        else:
            llm_output = self.predict(
                dialect=self.retriever.database_dialect,
                max_present=self.retriever.max_rows_return,
                table_info=self.retriever.table_info,
                request=user_input,
                history=history,
                his_error=his_error
            )
            self.logger.debug(llm_output)
        return llm_output

    def predict_db(self, user_input: str,
                   history: str,
                   his_error: str,
                   get_cmd: bool = False,
                   get_summary: bool = False,
                   get_db: bool = False
                   ) -> str:
        """
        Predict sql cmd based on the user's description then
        use the langchain method run_no_throw
        to retrieve sql result.
        Args:
            user_input (str): users description for the query.
            history (str): history command used for query
            his_error (str): the errors raised from executing the history cmd
        Returns:
            str: I know its odd but it is a string. It converts the
            database cursor result into a string. Not very useful, I dont
            know why Im keeping this method.
        """
        assert get_cmd or get_summary or get_db, "At least get one thing"
        llm_output = self.predict_sql_cmd(user_input=user_input,
                                          history=history,
                                          his_error=his_error)

        cmd_n_summary = self.retriever.retrieve_summary(
            llm_output=llm_output,
            return_cmd=True,
            split_symbol=self.split_symbol)

        cmd = cmd_n_summary['cmd']
        summary = cmd_n_summary['summary']

        result_dict = {}
        if get_cmd:
            result_dict['cmd'] = cmd
        if get_summary:
            result_dict['summary'] = summary
        if get_db:
            db = self.retriever.retrieve(llm_output=llm_output,
                                         split_symbol=self.split_symbol)
            result_dict['db'] = db
        return result_dict

    def predict_db_summary(self, user_input: str,
                           history: str,
                           his_error: str,
                           return_cmd: bool = False) -> Any:
        """
        Predict sql cmd based on the user's description then
        use the sqlalchemy to retrieve the sql result,
        then summarize the result into a shorten string.
        It is used to provide llm context and condense information
        and save tokens. cheaper better money little
        Args:
            user_input (str): user's description for the query
            history (str): history command used for query
            his_error (str): the errors raised from executing the history cmd
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
        llm_output = self.predict_sql_cmd(user_input=user_input,
                                          history=history,
                                          his_error=his_error)
        result = self.retriever.retrieve_summary(
            llm_output=llm_output,
            return_cmd=return_cmd,
            split_symbol=self.split_symbol)
        return result
