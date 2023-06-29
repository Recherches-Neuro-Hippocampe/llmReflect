from Retriever.BasicRetriever import BasicRetriever
from typing import List
from Utils.database import SQLDatabase, upper_boundary_maximum_records
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

    def retrieve(self, llm_output: str):
        processed_llm_output = llm_output.strip('\n').strip(' ')
        processed_llm_output = upper_boundary_maximum_records(
            sql_cmd=processed_llm_output,
            max_present=self.max_rows_return).lower()
        # if getting an error from the database
        # we take the error as another format of output
        result = self.database.run_no_throw(command=processed_llm_output)
        return result

    def retrieve_summary(self, llm_output: str, return_cmd: bool = False):
        processed_llm_output = llm_output.strip('\n').strip(' ')

        sql_cmd = upper_boundary_maximum_records(
            sql_cmd=processed_llm_output,
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
        # print(processed_llm_output)
        q_e_list = processed_llm_output.split('\n')
        results = []
        for string in q_e_list:
            if string.startswith('Question: '):
                processed_question = string.split("Question:")[-1]
                processed_question = processed_question.strip('\n').strip(' ')
                results.append(processed_question)
        return results
