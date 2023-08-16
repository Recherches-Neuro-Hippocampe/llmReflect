Module llmreflect.Chains.DatabaseChain
======================================

Classes
-------

`DatabaseAnswerChain(agent: llmreflect.Agents.DatabaseAgent.DatabaseAgent, retriever: llmreflect.Retriever.DatabaseRetriever.DatabaseRetriever, **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    Chain for generating database query cmd based on questions in natural
    language.
    Args:
        agent (DatabaseAgent): DatabaseAgent
        retriever (DatabaseRetriever): DatabaseRetriever

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

    ### Methods

    `perform(self, user_input: str, get_cmd: bool = True, get_db: bool = False, get_summary: bool = True) ‑> dict`
    :   Core function of the chain. Obtain the LLM result based on input.
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

    ### Class variables

    `REQUIRED_CHAINS`
    :

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

`DatabaseGradingChain(agent: llmreflect.Agents.EvaluationAgent.DatabaseGradingAgent, retriever: llmreflect.Retriever.DatabaseRetriever.DatabaseEvaluationRetriever, **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
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

    ### Methods

    `perform(self, request: str, sql_cmd: str, db_summary: str) ‑> dict`
    :   Core function of the chain. Obtain the LLM result based on input.
        
        Args:
            request (str): queries about a dataset
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

    ### Class variables

    `REQUIRED_CHAINS`
    :

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

    ### Class variables

    `REQUIRED_CHAINS`
    :

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

`DatabaseQuestionChain(agent: llmreflect.Agents.QuestionAgent.DatabaseQuestionAgent, retriever: llmreflect.Retriever.DatabaseRetriever.DatabaseQuestionRetriever, **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    A chain for creating questions given by a dataset.
    Args:
        agent (DatabaseQuestionAgent): DatabaseQuestionAgent
        retriever (DatabaseQuestionRetriever): DatabaseQuestionRetriever

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

    ### Methods

    `perform(self, n_questions: int = 5) ‑> list`
    :   Overwrite perform function.
        Generate n questions.
        Args:
            n_questions (int, optional): number of questions to generate.
                Defaults to 5.
        
        Returns:
            list: a list of questions, each question is a str object.

`DatabaseSelfFixChain(agent: llmreflect.Agents.DatabaseAgent.DatabaseSelfFixAgent, retriever: llmreflect.Retriever.DatabaseRetriever.DatabaseRetriever, **kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.
    
    A Basic chain class for fix database queries.
    Args:
        agent (DatabaseSelfFixAgent): DatabaseSelfFixAgent
        retriever (DatabaseRetriever): DatabaseRetriever

    ### Ancestors (in MRO)

    * llmreflect.Chains.BasicChain.BasicChain
    * abc.ABC

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