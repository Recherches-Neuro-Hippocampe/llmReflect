Module llmreflect.Chains.DatabaseChain
======================================

Classes
-------

`DatabaseAnswerChain(agent: llmreflect.Agents.DatabaseAgent.DatabaseAgent, retriever: llmreflect.Retriever.DatabaseRetriever.DatabaseRetriever)`
:   Abstract class for Chain class.
    A chain class should be the atomic unit for completing a job.
    A chain contains at least two components:
    1. an agent 2. a retriever
    A chain object must have the function to perform a job.
    Each chain is also equipped with a logger
    
    Chain for generating database query cmd based on questions in natural
    language.
    Args:
        agent (DatabaseAgent): DatabaseAgent
        retriever (DatabaseRetriever): DatabaseRetriever

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

    ### Static methods

    `from_config(uri: str, include_tables: List, open_ai_key: str, prompt_name: str = 'answer_database', max_output_tokens: int = 512, temperature: float = 0.0, sample_rows: int = 0, max_rows_return=500) ‑> llmreflect.Chains.BasicChain.BasicChain`
    :   Initialize class from configurations
        Args:
            uri (str): uri to connect to the database
            include_tables (List): a list of names of database tables
                to include
            open_ai_key (str): openai api key
            prompt_name (str, optional): prompt file name.
                Defaults to 'answer_database'.
            max_output_tokens (int, optional): Maximum completion tokens.
                Defaults to 512.
            temperature (float, optional): How unstable the llm is.
                Defaults to 0.0.
            sample_rows (int, optional): Rows from db provided to llm
                as a sample. Defaults to 0.
            max_rows_return (int, optional): Maximum rows retrieve from db.
                Defaults to 500.
        
        Returns:
            BasicChain: A DatabaseAnswerChain object.

    ### Methods

    `perform(self, user_input: str, get_cmd: bool = True, get_db: bool = False, get_summary: bool = True) ‑> dict`
    :   _summary_
        
        Args:
            user_input (str): user's description
            get_cmd (bool, optional): if return cmd. Defaults to True.
            get_db (bool, optional): if return queried db gross result.
                Defaults to False.
            get_summary (bool, optional): if return a summary of the result.
                Defaults to True.
        
        Returns:
            dict: {'cmd': sql_cmd, 'summary': summary, 'db': gross db response}

`DatabaseAnswerNFixChain(chains: List[llmreflect.Chains.BasicChain.BasicChain], fix_patience: int = 3)`
:   Abstract class for combined Chain class.
    A combined chain is a chain with multiple chains
    A chain class should be the atomic unit for completing a job.
    A chain object must have the function to perform a job.
    
    A combined chain with two sub-basic chains, database answer chain
    and self-fix chain. This chain is responsible for the following work:
    1. answering natural language questions by creating database queries.
    2. try executing the query, if encounter error, fix the query.
    Args:
        chains (List[BasicChain]): a list of chains,
            Supposed to be 2 chains. DatabaseAnswerChain and
            DatabaseSelfFixChain.
        fix_patience (int, optional): maximum self-fix attempts allowed.
            Defaults to 3.
    
    Raises:
        Exception: Illegal chain error when the list of chains do not meet
            requirements.

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicCombinedChain
    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

    ### Methods

    `perform(self, user_input: str, get_cmd: bool = True, get_db: bool = False, get_summary: bool = True, log_fix: bool = True) ‑> dict`
    :   Perform the main function for this chain.
        Args:
            user_input (str): user's natural language question.
            get_cmd (bool, optional): Flag, if return the database query
                command. Defaults to True.
            get_db (bool, optional): Flag, if return database execution
                results. Defaults to False.
            get_summary (bool, optional): Flag, if return a summary of
                the database execution results. Defaults to True.
            log_fix (bool, optional): Flag, if log the fix attempts by
                logger. Defaults to True.
        
        Returns:
            dict: 'cmd': str, sql_cmd,
                'summary': str, summary,
                'db': str, db_result,
                'error': dict, error_logs: 'cmd', what sql cmd caused error,
                                            'error', what is the error

`DatabaseGradingChain(agent: llmreflect.Agents.EvaluationAgent.DatabaseGradingAgent, retriever: llmreflect.Retriever.DatabaseRetriever.DatabaseEvaluationRetriever)`
:   Abstract class for Chain class.
    A chain class should be the atomic unit for completing a job.
    A chain contains at least two components:
    1. an agent 2. a retriever
    A chain object must have the function to perform a job.
    Each chain is also equipped with a logger
    
    A chain for the following workflow:
    1. given by questions about a database and according
        database query solutions for questions
    2. evaluate the generated solutions
    Args:
        agent (PostgressqlGradingAgent): PostgressqlGradingAgent
        retriever (DatabaseEvaluationRetriever):
            DatabaseEvaluationRetriever

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

    ### Static methods

    `from_config(open_ai_key: str, uri: str, include_tables: list, max_output_tokens: int = 256, prompt_name: str = 'grading_database', temperature: float = 0.0) ‑> llmreflect.Chains.BasicChain.BasicChain`
    :   Initialize an object of DatabaseGradingChain from configurations.
        Args:
            open_ai_key (str): openai api key.
            max_output_tokens (int, optional): Maximum completion tokens.
                Dont need to be long. Defaults to 256.
            prompt_name (str, optional): Prompt file name.
                Defaults to "grading_database".
            temperature (float, optional): How unstable the llm is.
                Defaults to 0.0.
        
        Returns:
            BasicChain: A DatabaseGradingChain object.

    ### Methods

    `perform(self, question: str, query: str, db_summary: str) ‑> dict`
    :   _summary_
        
        Args:
            question (str): queries about a dataset
            query (str): generated queries
            db_summary (str): execution summary
        
        Returns:
            dict: {"grading": a float number between 0 to 10,
                    "explanation": explanation for the score assigned}

`DatabaseModerateNAnswerNFixChain(chains: List[llmreflect.Chains.BasicChain.BasicChain], fix_patience: int = 3)`
:   Abstract class for combined Chain class.
    A combined chain is a chain with multiple chains
    A chain class should be the atomic unit for completing a job.
    A chain object must have the function to perform a job.
    
    A combined chain for: moderating user input, generating
    database query to solve the question, when encounter an
    error during execution, fix the query.
    Args:
        chains (List[BasicChain]): A list of chains.
        Should be two chain, a basic chain and a combined chain.
        The basic chain is the ModerateChain. And the combined
        chain should be DatabaseAnswerNFixChain.
        fix_patience (int, optional): maximum self-fix attempts allowed.
            Defaults to 3.
    
    Raises:
        Exception: Illegal chain error when the list of chains do not meet
            requirements.

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicCombinedChain
    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

    ### Static methods

    `from_config(uri: str, include_tables: list, open_ai_key: str, answer_chain_prompt_name: str = 'answer_database', fix_chain_prompt_name: str = 'fix_database', moderate_chain_prompt_name: str = 'moderate_database', max_output_tokens_a: int = 512, max_output_tokens_f: int = 512, max_output_tokens_m: int = 256, temperature_a: float = 0.0, temperature_f: float = 0.0, temperature_m: float = 0.0, sample_rows: int = 0, max_rows_return: int = 500, fix_patience: int = 3) ‑> llmreflect.Chains.BasicChain.BasicCombinedChain`
    :   Initialize a DatabaseModerateNAnswerNFixChain object from configuration.
        Args:
            uri (str): A uri to connect to the database.
            include_tables (list): A list of names of database tables
                to include.
            open_ai_key (str): openai api key.
            answer_chain_prompt_name (str, optional): Prompt file for answer
                chain. Defaults to "answer_database".
            fix_chain_prompt_name (str, optional): Prompt file for fix chain.
                Defaults to "fix_database".
            moderate_chain_prompt_name (str, optional): prompt file for
                moderate chain . Defaults to "moderate_database".
            max_output_tokens_a (int, optional): Maximum completion tokens for
                answering. Defaults to 512.
            max_output_tokens_f (int, optional): Maximum completion tokens for
                fixing. Defaults to 512.
            max_output_tokens_m (int, optional): Maximum completion tokens for
                moderation. Defaults to 512.
            temperature_a (float, optional): temperature for answering chain.
                Defaults to 0.0.
            temperature_f (float, optional): temperature for fixing chain.
                Defaults to 0.0.
            temperature_m (float, optional): temperature for moderation chain.
                Defaults to 0.0.
            sample_rows (int, optional): Rows from db provided to llm
                as a sample. Defaults to 0.
            max_rows_return (int, optional): Maximum rows retrieve from db.
                Defaults to 500.
            fix_patience (int, optional): Maximum self-fix attempts allowed.
                Defaults to 3.
        
        Returns:
            BasicCombinedChain: An object of DatabaseModerateNAnswerNFixChain.

    ### Methods

    `perform(self, user_input: str, get_cmd: bool = True, get_db: bool = False, get_summary: bool = True, log_fix: bool = True, explain_moderate: bool = True) ‑> dict`
    :   Perform chain function.
        Args:
            user_input (str): _description_
            get_cmd (bool, optional): _description_. Defaults to True.
            get_db (bool, optional): _description_. Defaults to False.
            get_summary (bool, optional): _description_. Defaults to True.
            log_fix (bool, optional): _description_. Defaults to True.
        
        Returns:
            dict: 'cmd': str, sql_cmd,
                'summary': str, summary,
                'db': str, db_result,
                'error': dict, error_logs: 'cmd', what sql cmd caused error,
                                            'error', what is the error

`DatabaseQnAGradingChain(chains: List[llmreflect.Chains.BasicChain.BasicChain], q_batch_size: int = 5)`
:   Abstract class for combined Chain class.
    A combined chain is a chain with multiple chains
    A chain class should be the atomic unit for completing a job.
    A chain object must have the function to perform a job.
    
    A combined chain for following workflow:
    1. creating questions given by a dataset.
    2. answering the questions by generating database queries.
    3. evaluating the generated answers.
    Args:
        chains (List[BasicChain]): a list of chains to complete the job.
            Expecting three exact chain: DatabaseQuestionChain,
            DatabaseAnswerChain, DatabaseGradingChain
        q_batch_size (int, optional): size of batch for generating
            questions. Defaults to 5. The reasons for generating questions
            by batch is that I found generating too many questions all at
            once, the questions become repetitive.
    
    Raises:
        Exception: Illegal chain error when the list of chains do not meet
            requirements.

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicCombinedChain
    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

    ### Static methods

    `from_config(uri: str, include_tables: List, open_ai_key: str, question_chain_prompt_name: str = 'question_database', answer_chain_prompt_name: str = 'answer_database', grading_chain_prompt_name: str = 'grading_database', q_max_output_tokens: int = 256, a_max_output_tokens: int = 512, g_max_output_tokens: int = 256, q_temperature: float = 0.7, a_temperature: float = 0.0, g_temperature: float = 0.0, sample_rows: int = 0, max_rows_return=500) ‑> llmreflect.Chains.BasicChain.BasicCombinedChain`
    :   Initialize a DatabaseQnAGradingChain object.
        Args:
            uri (str): A uri to connect to the database.
            include_tables (List): a list of names of database tables
                to include.
            open_ai_key (str): openai api key.
            question_chain_prompt_name (str, optional): Prompt file name for
                question chain. Defaults to 'question_database'.
            answer_chain_prompt_name (str, optional): Prompt file name for
                answer chain. Defaults to 'answer_database'.
            grading_chain_prompt_name (str, optional): Prompt file name for
                grading chain. Defaults to 'grading_database'.
            q_max_output_tokens (int, optional): Maximum completion tokens for
                generating questions. Defaults to 256.
            a_max_output_tokens (int, optional): Maximum completion tokens for
                generating answers. Defaults to 512.
            g_max_output_tokens (int, optional): Maximum completion tokens for
                evaluating answers. Defaults to 256.
            q_temperature (float, optional): temperature for question.
                Defaults to 0.7.
            a_temperature (float, optional): temperature for answer.
                Defaults to 0.0.
            g_temperature (float, optional): temperature for grading.
                Defaults to 0.0.
            sample_rows (int, optional): Rows from db provided to llm
                as a sample. Defaults to 0.
            max_rows_return (int, optional): Maximum rows retrieve from db.
                Defaults to 500.
        Returns:
            BasicCombinedChain: _description_

    ### Methods

    `perform(self, n_question: int = 5) ‑> dict`
    :   perform the q and a and grading chain.
        Args:
            n_question (int, optional): number of questions to create.
                Defaults to 5.
        
        Returns:
            dict: {
                'question': str, question generated,
                'cmd': str, generated cmd,
                'summary': str, summary from executing the cmd,
                'grading': float, scores by grading agent
                'explanation': str, reasons for such score, str
            }

`DatabaseQuestionChain(agent: llmreflect.Agents.QuestionAgent.DatabaseQuestionAgent, retriever: llmreflect.Retriever.DatabaseRetriever.DatabaseQuestionRetriever)`
:   Abstract class for Chain class.
    A chain class should be the atomic unit for completing a job.
    A chain contains at least two components:
    1. an agent 2. a retriever
    A chain object must have the function to perform a job.
    Each chain is also equipped with a logger
    
    A chain for creating questions given by a dataset.
    Args:
        agent (DatabaseQuestionAgent): DatabaseQuestionAgent
        retriever (DatabaseQuestionRetriever): DatabaseQuestionRetriever

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

    ### Static methods

    `from_config(uri: str, include_tables: List, open_ai_key: str, prompt_name: str = 'question_database', max_output_tokens: int = 512, temperature: float = 0.7, sample_rows: int = 0) ‑> llmreflect.Chains.BasicChain.BasicChain`
    :   Initialize class from configurations
        Args:
            uri (str): uri to connect to the database
            include_tables (List): a list of names of database tables
                to include
            open_ai_key (str): openai api key
            prompt_name (str, optional): prompt file name without json.
            max_output_tokens (int, optional): maximum completion tokens.
                Defaults to 512.
            temperature (float, optional): how unstable the llm is.
                Defaults to 0.7. Since this chain is used for generating
                random questions. We would like it to be creative.
            sample_rows (int, optional): rows from db provided to llm
                as a sample. Defaults to 0.
        
        Returns:
            BasicChain: A DatabaseQuestionChain object.

    ### Methods

    `perform(self, n_questions: int = 5) ‑> list`
    :   Overwrite perform function.
        Generate n questions.
        Args:
            n_questions (int, optional): number of questions to generate.
                Defaults to 5.
        
        Returns:
            list: a list of questions, each question is a str object.

`DatabaseSelfFixChain(agent: llmreflect.Agents.DatabaseAgent.DatabaseSelfFixAgent, retriever: llmreflect.Retriever.DatabaseRetriever.DatabaseRetriever)`
:   Abstract class for Chain class.
    A chain class should be the atomic unit for completing a job.
    A chain contains at least two components:
    1. an agent 2. a retriever
    A chain object must have the function to perform a job.
    Each chain is also equipped with a logger
    
    A Basic chain class for fix database queries.
    Args:
        agent (DatabaseSelfFixAgent): DatabaseSelfFixAgent
        retriever (DatabaseRetriever): DatabaseRetriever

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

    ### Static methods

    `from_config(uri: str, include_tables: List, open_ai_key: str, prompt_name: str = 'fix_database', max_output_tokens: int = 512, temperature: float = 0.0, sample_rows: int = 0, max_rows_return: int = 500) ‑> llmreflect.Chains.BasicChain.BasicChain`
    :   Initialize a DatabaseSelfFixChain object from configurations.
        Args:
            uri (str): A uri to connect to the database.
            include_tables (List): A list of names of database tables
                to include.
            open_ai_key (str): openai api key.
            prompt_name (str, optional): Prompt file name.
                Defaults to 'fix_database'.
            max_output_tokens (int, optional): Maximum completion tokens.
                Defaults to 512.
            temperature (float, optional): How unstable the llm is.
                Defaults to 0.0.
            sample_rows (int, optional): Rows from db provided to llm
                as a sample. Defaults to 0.
            max_rows_return (int, optional): Maximum rows retrieve from db.
                Defaults to 500.
        
        Returns:
            BasicChain: A DatabaseSelfFixChain object.

    ### Methods

    `perform(self, user_input: str, history: str, his_error: str, get_cmd: bool = True, get_db: bool = False, get_summary: bool = True) ‑> dict`
    :   Perform chain function.
        Args:
            user_input (str): user's description
            history (str): history command used for query
            his_error (str): the errors raised from executing the history cmd
            get_cmd (bool, optional): if return cmd. Defaults to True.
            get_db (bool, optional): if return queried db gross result.
                Defaults to False.
            get_summary (bool, optional): if return a summary of the result.
                Defaults to True.
        
        Returns:
            dict: {'cmd': sql_cmd, 'summary': summary, 'db': gross db response}