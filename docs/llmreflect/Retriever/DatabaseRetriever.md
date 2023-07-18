Module llmreflect.Retriever.DatabaseRetriever
=============================================

Classes
-------

`DatabaseEvaluationRetriever(uri: str, include_tables: List, sample_rows: int = 0)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    Class for general postprocessing llm output string
    Args:
        uri (str): A url used for database connection.
        include_tables (List): a list of strings,
            indicate which tables in the database to include.
        sample_rows (int, optional): Number of row to provide
            to llm as an example. Defaults to 0.

    ### Ancestors (in MRO)

    * llmreflect.Retriever.DatabaseRetriever.DatabaseRetriever
    * llmreflect.Retriever.BasicRetriever.BasicRetriever
    * abc.ABC

    ### Methods

    `retrieve(self, llm_output: str) ‑> dict`
    :   Retrieve the scores and the explanation for score
        from llm output.
        Args:
            llm_output (str): gross llm output.
        
        Returns:
            dict: {'grading': float, score given by llm,
                'explanation': str, reason for the score.}

`DatabaseQuestionRetriever(uri: str, include_tables: List[str], sample_rows: int = 0)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    Retriever class for retrieving question based on DatabaseRetriever
    Args:
        uri (str): A url used for database connection.
        include_tables (List): a list of strings,
            indicate which tables in the database to include.
        sample_rows (int, optional): Number of row to provide
            to llm as an example. Defaults to 0.

    ### Ancestors (in MRO)

    * llmreflect.Retriever.DatabaseRetriever.DatabaseRetriever
    * llmreflect.Retriever.BasicRetriever.BasicRetriever
    * abc.ABC

    ### Methods

    `retrieve(self, llm_output: str) ‑> List[str]`
    :   Retrieve questions about the database from llm output.
        Args:
            llm_output (str): output from llm
        
        Returns:
            List: a list of questions. Each question is a `str`

`DatabaseRetriever(uri: str, include_tables: List, max_rows_return: int, sample_rows: int = 0)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    Retriever based on BasicRetriever, used for querying database
    Args:
        uri (str): database connection uri
        include_tables (List): which tables to include
        max_rows_return (int): maximum row to return

    ### Ancestors (in MRO)

    * llmreflect.Retriever.BasicRetriever.BasicRetriever
    * abc.ABC

    ### Descendants

    * llmreflect.Retriever.DatabaseRetriever.DatabaseEvaluationRetriever
    * llmreflect.Retriever.DatabaseRetriever.DatabaseQuestionRetriever

    ### Methods

    `retrieve(self, llm_output: str, split_symbol: str = '] ') ‑> str`
    :   retrieve a database query execution result.
        It is converted into a string.
        Args:
            llm_output (str):  Gross output from llm.
            split_symbol (str, optional): Symbols used to split.
                Defaults to "] ".
        Returns:
            str: A string representing the database execution result.

    `retrieve_cmd(self, llm_output: str, split_symbol: str = '] ') ‑> str`
    :   retrieve database query sql command from llm output
        Args:
            llm_output (str): Gross output from llm.
            split_symbol (str, optional): Symbols used to split.
                Defaults to "] ".
        
        Returns:
            str: database query

    `retrieve_summary(self, llm_output: str, return_cmd: bool = False, split_symbol: str = '] ')`
    :   1. Retrieve the sql cmd from gross llm output.
        2. execute the cmd
        3. summarize the executed result into a brief report.
        Args:
            llm_output (str): Gross output from llm.
            return_cmd (bool, optional): If return query. Defaults to False.
            split_symbol (str, optional): Symbols used to split.
                Defaults to "] ".
        
        Return:
            str: A brief summary of database execution result.
                If `return_cmd` is set to 'True'
            dict: A dictionary when `return_cmd` is set to 'False',
                {'cmd', database query, 'summary': brief summary}