Module llmreflect.Agents.DatabaseAgent
======================================

Classes
-------

`DatabaseAgent(llm_core: llmreflect.LLMCore.LLMCore.LLMCore, split_symbol='[answer]', **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
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

    ### Ancestors (in MRO)

    * llmreflect.Agents.BasicAgent.Agent
    * llmreflect.Agents.BasicAgent.BasicAgent
    * abc.ABC

    ### Descendants

    * llmreflect.Agents.DatabaseAgent.DatabaseSelfFixAgent

    ### Class variables

    `PROMPT_NAME`
    :

    ### Methods

    `equip_retriever(self, retriever: llmreflect.Retriever.DatabaseRetriever.DatabaseRetriever)`
    :   Equip DatabaseRetriever for an instance of DatabaseAgent.
        
        Args:
            retriever (DatabaseRetriever): use database retriever

    `predict_db(self, user_input: str, get_cmd: bool = False, get_summary: bool = False, get_db: bool = False) ‑> str`
    :   Predict sql cmd based on the user's description then
        use the langchain method run_no_throw
        to retrieve sql result.
        Args:
            user_input (str): users description for the query.
        
        Returns:
            str: I know its odd but it is a string. It converts the
            database cursor result into a string. Not very useful, I dont
            know why Im keeping this method.

    `predict_db_summary(self, user_input: str, return_cmd: bool = False) ‑> Any`
    :   Predict sql cmd based on the user's description then
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

    `predict_sql_cmd(self, user_input: str) ‑> str`
    :   Generate the database command, it is a gross output which means
        no post processing. It could be a wrong format that not executable.
        Need extraction and cleaning and formatting.
        Args:
            user_input (str): users description for the query.
        
        Returns:
            str: gross output of the llm attempt for generating sql cmd.

`DatabaseSelfFixAgent(llm_core: llmreflect.LLMCore.LLMCore.LLMCore, split_symbol='[answer]', **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
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

    ### Ancestors (in MRO)

    * llmreflect.Agents.DatabaseAgent.DatabaseAgent
    * llmreflect.Agents.BasicAgent.Agent
    * llmreflect.Agents.BasicAgent.BasicAgent
    * abc.ABC

    ### Class variables

    `PROMPT_NAME`
    :

    ### Methods

    `predict_db(self, user_input: str, history: str, his_error: str, get_cmd: bool = False, get_summary: bool = False, get_db: bool = False) ‑> str`
    :   Predict sql cmd based on the user's description then
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

    `predict_db_summary(self, user_input: str, history: str, his_error: str, return_cmd: bool = False) ‑> Any`
    :   Predict sql cmd based on the user's description then
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

    `predict_sql_cmd(self, user_input: str, history: str, his_error: str) ‑> str`
    :   Generate a database query command, it is a gross output which means
        no post processing. It could be a wrong format that not executable.
        Need extraction and cleaning and formatting.
        Args:
            user_input (str): users description for the query.
            history (str): history command used for query
            his_error (str): the errors raised from executing the history cmd
        Returns:
            str: gross output of the llm attempt for generating sql cmd.