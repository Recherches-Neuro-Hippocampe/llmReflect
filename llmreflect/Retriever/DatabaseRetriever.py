from llmreflect.Retriever.BasicRetriever import BasicRetriever
from typing import List
from llmreflect.Utils.database import upper_boundary_maximum_records
from langchain.sql_database import SQLDatabase
from sqlalchemy import text
import random


class DatabaseRetriever(BasicRetriever):
    """Retriever based on BasicRetriever, used for querying database
    Args:
        BasicRetriever (_type_): _description_
    """
    def __init__(self, uri: str, include_tables: List,
                 max_rows_return: int,
                 sample_rows: int = 0) -> None:
        """_summary_

        Args:
            uri (str): database connection uri
            include_tables (List): which tables to include
            max_rows_return (int): maximum row to return

        Returns:
            _type_: _description_
        """
        super().__init__()
        self.max_rows_return = max_rows_return
        self.database = SQLDatabase.\
            from_uri(
                uri,
                include_tables=include_tables,
                sample_rows_in_table_info=sample_rows)

        self.database_dialect = self.database.dialect
        self.table_info = self.database.get_table_info_no_throw()

    def retrieve_cmd(self, llm_output: str, split_symbol: str = "] "):
        processed_llm_output = llm_output.split(split_symbol)[-1]
        processed_llm_output = processed_llm_output.strip('\n').strip(' ')
        return processed_llm_output

    def retrieve(self, llm_output: str, split_symbol: str = "] "):
        sql_cmd = self.retrieve_cmd(llm_output=llm_output,
                                    split_symbol=split_symbol)
        sql_cmd = upper_boundary_maximum_records(
            sql_cmd=sql_cmd,
            max_present=self.max_rows_return).lower()
        # if getting an error from the database
        # we take the error as another format of output
        result = self.database.run_no_throw(command=sql_cmd)
        return result

    def retrieve_summary(self, llm_output: str, return_cmd: bool = False,
                         split_symbol: str = "] "):
        sql_cmd = self.retrieve_cmd(llm_output=llm_output,
                                    split_symbol=split_symbol)
        sql_cmd = upper_boundary_maximum_records(
            sql_cmd=sql_cmd,
            max_present=self.max_rows_return).lower()
        sql_cmd = text(sql_cmd)
        col_names = []
        with self.database._engine.begin() as connection:
            try:
                result = connection.execute(sql_cmd)
                for col in result.cursor.description:
                    col_names.append(col.name)
                items = result.cursor.fetchall()
                n_records = len(items)
                if n_records == 0:
                    raise Exception("Found 0 record! Empty response!")
                example = [str(item) for item in random.choice(items)]
                summary = f'''\
You retrieved {n_records} entries with {len(col_names)} columns from the \
database.
The columns are {','.join(col_names)}.
An example of entries is: {','.join(example)}.'''
            except Exception as e:
                summary = f"Error: {e}"
        if return_cmd:
            return {'cmd': sql_cmd.__str__(), 'summary': summary}
        else:
            return summary


class DatabaseQuestionRetriever(DatabaseRetriever):
    """_summary_
    Retriever class based on DatabaseRetriever
    Args:
        DatabaseRetriever (_type_): _description_
    """
    def __init__(self, uri: str, include_tables: List,
                 sample_rows: int = 0) -> None:
        super().__init__(uri=uri,
                         include_tables=include_tables,
                         max_rows_return=None,
                         sample_rows=sample_rows)

    def retrieve(self, llm_output: str):
        """_summary_

        Args:
            llm_output (str): output from llm

        Returns:
            _type_: a processed string
        """
        processed_llm_output = llm_output.strip("\n").strip(' ')
        q_e_list = processed_llm_output.split('\n')[1:]
        results = []
        for line in q_e_list:
            results.append(line.split('] ')[-1])
        return results
