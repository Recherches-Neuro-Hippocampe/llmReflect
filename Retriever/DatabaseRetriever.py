from Retriever.BasicRetriever import BasicRetriever
from typing import List
from Utils.database import SQLDatabase, upper_boundary_maxiunm_records


class DatabaseRetriever(BasicRetriever):
    def __init__(self, uri: str, include_tables: List,
                 max_rows_return: int) -> None:
        super().__init__()
        self.max_rows_return = max_rows_return
        self.databse = SQLDatabase.from_uri(uri,
                                            include_tables=include_tables,
                                            sample_rows_in_table_info=0)
        self.database_dialect = self.databse.dialect
        self.table_info = self.databse.get_table_info_no_throw()

    def retrieve(self, llm_output: str, ):
        processed_llm_output = llm_output.strip("\n").strip(' ')
        processed_llm_output = upper_boundary_maxiunm_records(
            sql_cmd=processed_llm_output,
            max_present=self.max_rows_return
            ).lower()
        result = self.databse.run_no_throw(command=processed_llm_output)
        print(result)
        return result
