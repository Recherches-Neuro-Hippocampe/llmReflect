from llmreflect.Chains.BasicChain import BasicChain, BasicCombinedChain
from llmreflect.Agents.QuestionAgent import DatabaseQuestionAgent
from llmreflect.Agents.DatabaseAgent import DatabaseAgent, \
    DatabaseSelfFixAgent
from llmreflect.Agents.EvaluationAgent import DatabaseGradingAgent
from llmreflect.Retriever.DatabaseRetriever import DatabaseQuestionRetriever, \
    DatabaseRetriever, DatabaseEvaluationRetriever
from llmreflect.Chains.ModerateChain import ModerateChain
from typing import List


class DatabaseQuestionChain(BasicChain):
    def __init__(self, agent: DatabaseQuestionAgent,
                 retriever: DatabaseQuestionRetriever):
        """
        A chain for creating questions given by a dataset.
        Args:
            agent (DatabaseQuestionAgent): DatabaseQuestionAgent
            retriever (DatabaseQuestionRetriever): DatabaseQuestionRetriever
        """
        super().__init__(agent, retriever)

    @classmethod
    def from_config(cls, uri: str,
                    include_tables: List,
                    open_ai_key: str,
                    prompt_name: str = 'question_database',
                    max_output_tokens: int = 512,
                    temperature: float = 0.7,
                    sample_rows: int = 0) -> BasicChain:
        """
        Initialize class from configurations
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
        """
        agent = DatabaseQuestionAgent(
            open_ai_key=open_ai_key,
            prompt_name=prompt_name,
            max_output_tokens=max_output_tokens,
            temperature=temperature)

        retriever = DatabaseQuestionRetriever(
            uri=uri,
            include_tables=include_tables,
            sample_rows=sample_rows
        )
        return cls(agent=agent, retriever=retriever)

    def perform(self, n_questions: int = 5) -> list:
        """
        Overwrite perform function.
        Generate n questions.
        Args:
            n_questions (int, optional): number of questions to generate.
                Defaults to 5.

        Returns:
            list: a list of questions, each question is a str object.
        """
        result = self.agent.predict_n_questions(n_questions=n_questions)
        return result


class DatabaseAnswerChain(BasicChain):
    def __init__(self, agent: DatabaseAgent, retriever: DatabaseRetriever):
        """
        Chain for generating database query cmd based on questions in natural
        language.
        Args:
            agent (DatabaseAgent): DatabaseAgent
            retriever (DatabaseRetriever): DatabaseRetriever
        """
        super().__init__(agent, retriever)

    @classmethod
    def from_config(cls, uri: str,
                    include_tables: List,
                    open_ai_key: str,
                    prompt_name: str = 'answer_database',
                    max_output_tokens: int = 512,
                    temperature: float = 0.0,
                    sample_rows: int = 0,
                    max_rows_return=500) -> BasicChain:
        """
        Initialize class from configurations
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
        """
        agent = DatabaseAgent(
            open_ai_key=open_ai_key,
            prompt_name=prompt_name,
            max_output_tokens=max_output_tokens,
            temperature=temperature)

        retriever = DatabaseRetriever(
            uri=uri,
            include_tables=include_tables,
            max_rows_return=max_rows_return,
            sample_rows=sample_rows
        )
        return cls(agent=agent, retriever=retriever)

    def perform(self,
                user_input: str,
                get_cmd: bool = True,
                get_db: bool = False,
                get_summary: bool = True) -> dict:
        """_summary_

        Args:
            user_input (str): user's description
            get_cmd (bool, optional): if return cmd. Defaults to True.
            get_db (bool, optional): if return queried db gross result.
                Defaults to False.
            get_summary (bool, optional): if return a summary of the result.
                Defaults to True.

        Returns:
            dict: {'cmd': sql_cmd, 'summary': summary, 'db': gross db response}
        """
        return self.agent.predict_db(
            user_input=user_input,
            get_cmd=get_cmd,
            get_summary=get_summary,
            get_db=get_db)


class DatabaseGradingChain(BasicChain):
    def __init__(self, agent: DatabaseGradingAgent,
                 retriever: DatabaseEvaluationRetriever):
        """
        A chain for the following workflow:
        1. given by questions about a database and according
            database query solutions for questions
        2. evaluate the generated solutions
        Args:
            agent (PostgressqlGradingAgent): PostgressqlGradingAgent
            retriever (DatabaseEvaluationRetriever):
                DatabaseEvaluationRetriever
        """
        super().__init__(agent, retriever)

    @classmethod
    def from_config(cls,
                    open_ai_key: str,
                    uri: str,
                    include_tables: list,
                    max_output_tokens: int = 256,
                    prompt_name: str = "grading_database",
                    temperature: float = 0.0,
                    ) -> BasicChain:
        """
        Initialize an object of DatabaseGradingChain from configurations.
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
        """
        agent = DatabaseGradingAgent(
            open_ai_key=open_ai_key,
            prompt_name=prompt_name,
            max_output_tokens=max_output_tokens,
            temperature=temperature)

        retriever = DatabaseEvaluationRetriever(uri=uri,
                                                include_tables=include_tables)
        return cls(agent=agent, retriever=retriever)

    def perform(self, question: str,
                query: str,
                db_summary: str) -> dict:
        """_summary_

        Args:
            question (str): queries about a dataset
            query (str): generated queries
            db_summary (str): execution summary

        Returns:
            dict: {"grading": a float number between 0 to 10,
                    "explanation": explanation for the score assigned}
        """
        grad_dict = self.agent.grade(request=question,
                                     sql_cmd=query,
                                     db_summary=db_summary)
        return grad_dict


class DatabaseQnAGradingChain(BasicCombinedChain):
    def __init__(self, chains: List[BasicChain], q_batch_size: int = 5):
        """
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
        """
        super().__init__(chains)
        assert len(chains) == 3

        for chain in self.chains:
            if chain.__class__ == DatabaseAnswerChain:
                self.db_a_chain = chain
            elif chain.__class__ == DatabaseQuestionChain:
                self.db_q_chain = chain
            elif chain.__class__ == DatabaseGradingChain:
                self.db_g_chain = chain
            else:
                raise Exception("Illegal chains!")
        self.q_batch_size = q_batch_size

    @classmethod
    def from_config(cls, uri: str,
                    include_tables: List,
                    open_ai_key: str,
                    question_chain_prompt_name: str = 'question_database',
                    answer_chain_prompt_name: str = 'answer_database',
                    grading_chain_prompt_name: str = 'grading_database',
                    q_max_output_tokens: int = 256,
                    a_max_output_tokens: int = 512,
                    g_max_output_tokens: int = 256,
                    q_temperature: float = 0.7,
                    a_temperature: float = 0.0,
                    g_temperature: float = 0.0,
                    sample_rows: int = 0,
                    max_rows_return=500) -> BasicCombinedChain:
        """
        Initialize a DatabaseQnAGradingChain object.
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
        """
        db_q_chain = DatabaseQuestionChain.from_config(
            uri=uri,
            include_tables=include_tables,
            open_ai_key=open_ai_key,
            prompt_name=question_chain_prompt_name,
            max_output_tokens=q_max_output_tokens,
            temperature=q_temperature,
            sample_rows=sample_rows
        )

        db_a_chain = DatabaseAnswerChain.from_config(
            uri=uri,
            include_tables=include_tables,
            open_ai_key=open_ai_key,
            prompt_name=answer_chain_prompt_name,
            max_output_tokens=a_max_output_tokens,
            temperature=a_temperature,
            sample_rows=sample_rows,
            max_rows_return=max_rows_return
        )

        db_g_chain = DatabaseGradingChain.from_config(
            uri=uri,
            include_tables=include_tables,
            open_ai_key=open_ai_key,
            prompt_name=grading_chain_prompt_name,
            max_output_tokens=g_max_output_tokens,
            temperature=g_temperature)

        return cls(chains=[db_q_chain, db_a_chain, db_g_chain],
                   q_batch_size=5)

    def perform(self, n_question: int = 5) -> dict:
        """
        perform the q and a and grading chain.
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
        """
        if n_question <= self.q_batch_size:
            t_questions = self.db_q_chain.perform(n_questions=n_question)
        else:
            t_questions = []
            for i in range(n_question // self.q_batch_size):
                t_questions.extend(
                    self.db_q_chain.perform(n_questions=self.q_batch_size))
            t_questions.extend(
                self.db_q_chain.perform(n_questions=(
                    n_question % self.q_batch_size)))
        t_logs = []

        for q in t_questions:
            temp_dict = self.db_a_chain.perform(
                user_input=q,
                get_cmd=True,
                get_summary=True,
                get_db=False
            )
            grad_dict = self.db_g_chain.perform(
                question=q,
                query=temp_dict['cmd'],
                db_summary=temp_dict['summary']
            )
            t_logs.append({
                "question": q,
                "cmd": temp_dict['cmd'],
                "summary": temp_dict['summary'],
                "grading": grad_dict['grading'],
                "explanation": grad_dict['explanation']
            })

        return t_logs


class DatabaseAnswerNFixChain(BasicCombinedChain):
    def __init__(self, chains: List[BasicChain], fix_patience: int = 3):
        """
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
        """
        super().__init__(chains)
        assert len(chains) == 2
        self.fix_patience = fix_patience
        for chain in self.chains:
            if chain.__class__ == DatabaseAnswerChain:
                self.answer_chain = chain
            elif chain.__class__ == DatabaseSelfFixChain:
                self.fix_chain = chain
            else:
                raise Exception("Illegal chains!")

    @classmethod
    def from_config(
            cls,
            uri: str,
            include_tables: list,
            open_ai_key: str,
            answer_chain_prompt_name: str,
            fix_chain_prompt_name: str,
            max_output_tokens_a: int = 512,
            max_output_tokens_f: int = 512,
            temperature_a: float = 0.0,
            temperature_f: float = 0.0,
            sample_row: int = 0,
            max_rows_return: int = 500,
            fix_patience: int = 3):

        db_a_chain = DatabaseAnswerChain.from_config(
            uri=uri,
            include_tables=include_tables,
            open_ai_key=open_ai_key,
            prompt_name=answer_chain_prompt_name,
            max_output_tokens=max_output_tokens_a,
            temperature=temperature_a,
            sample_rows=sample_row,
            max_rows_return=max_rows_return
        )
        db_fix_chain = DatabaseSelfFixChain.from_config(
            uri=uri,
            include_tables=include_tables,
            open_ai_key=open_ai_key,
            prompt_name=fix_chain_prompt_name,
            max_output_tokens=max_output_tokens_f,
            temperature=temperature_f,
            sample_rows=sample_row,
            max_rows_return=max_rows_return
        )
        return cls(chains=[db_a_chain, db_fix_chain],
                   fix_patience=fix_patience)

    def perform(self,
                user_input: str,
                get_cmd: bool = True,
                get_db: bool = False,
                get_summary: bool = True,
                log_fix: bool = True) -> dict:
        """
        Perform the main function for this chain.
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
        """
        assert get_cmd or get_db or get_summary

        answer_dict = self.answer_chain.perform(
            user_input=user_input,
            get_cmd=True,
            get_db=get_db,
            get_summary=True
        )
        sql_cmd = answer_dict['cmd']
        summary = answer_dict['summary']
        db_result = ""
        if get_db:
            db_result = answer_dict['db']
        fix_attempt = 0

        error_logs = []

        while 'error' in summary.lower() and fix_attempt < self.fix_patience:
            if log_fix:
                self.logger.warning(f"Error detected: {summary}")
                self.logger.warning(f"Self-fix Attempt: {fix_attempt}")
                self.logger.warning("Self-fixing...")
                error_logs.append({
                    'cmd': sql_cmd,
                    'error': summary})
            fixed_answer_dict = self.fix_chain.perform(
                user_input=user_input,
                history=sql_cmd,
                his_error=summary,
                get_cmd=True,
                get_db=get_db,
                get_summary=True
            )
            sql_cmd = fixed_answer_dict['cmd']
            summary = fixed_answer_dict['summary']
            if get_db:
                db_result = fixed_answer_dict['db']

            if 'error' not in summary.lower() and log_fix:
                self.logger.info("Self-fix finished.")
            fix_attempt += 1

        if 'error' in summary.lower() and log_fix:
            self.logger.error("Self-fix failed!")

        if not get_cmd:
            sql_cmd = ""
        if not get_summary:
            get_summary = ""

        return {'cmd': sql_cmd,
                'summary': summary,
                'db': db_result,
                'error': error_logs}


class DatabaseSelfFixChain(BasicChain):
    def __init__(self,
                 agent: DatabaseSelfFixAgent,
                 retriever: DatabaseRetriever):
        """
        A Basic chain class for fix database queries.
        Args:
            agent (DatabaseSelfFixAgent): DatabaseSelfFixAgent
            retriever (DatabaseRetriever): DatabaseRetriever
        """
        super().__init__(agent, retriever)

    @classmethod
    def from_config(cls, uri: str,
                    include_tables: List,
                    open_ai_key: str,
                    prompt_name: str = 'fix_database',
                    max_output_tokens: int = 512,
                    temperature: float = 0.0,
                    sample_rows: int = 0,
                    max_rows_return: int = 500) -> BasicChain:
        """
        Initialize a DatabaseSelfFixChain object from configurations.
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
        """
        agent = DatabaseSelfFixAgent(
            open_ai_key=open_ai_key,
            prompt_name=prompt_name,
            max_output_tokens=max_output_tokens,
            temperature=temperature)

        retriever = DatabaseRetriever(
            uri=uri,
            include_tables=include_tables,
            max_rows_return=max_rows_return,
            sample_rows=sample_rows
        )
        return cls(agent=agent, retriever=retriever)

    def perform(self,
                user_input: str,
                history: str,
                his_error: str,
                get_cmd: bool = True,
                get_db: bool = False,
                get_summary: bool = True) -> dict:
        """
        Perform chain function.
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
        """
        return self.agent.predict_db(
            user_input=user_input,
            history=history,
            his_error=his_error,
            get_cmd=get_cmd,
            get_summary=get_summary,
            get_db=get_db)


class DatabaseModerateNAnswerNFixChain(BasicCombinedChain):
    def __init__(self, chains: List[BasicChain], fix_patience: int = 3):
        """
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
        """
        super().__init__(chains)
        assert len(chains) == 2
        self.fix_patience = fix_patience
        for chain in self.chains:
            if chain.__class__ == ModerateChain:
                self.moderate_chain = chain
            elif chain.__class__ == DatabaseAnswerNFixChain:
                self.a_n_f_chain = chain
            else:
                raise Exception("Illegal chains!")

    @classmethod
    def from_config(
            cls,
            uri: str,
            include_tables: list,
            open_ai_key: str,
            answer_chain_prompt_name: str = "answer_database",
            fix_chain_prompt_name: str = "fix_database",
            moderate_chain_prompt_name: str = "moderate_database",
            max_output_tokens_a: int = 512,
            max_output_tokens_f: int = 512,
            max_output_tokens_m: int = 256,
            temperature_a: float = 0.0,
            temperature_f: float = 0.0,
            temperature_m: float = 0.0,
            sample_rows: int = 0,
            max_rows_return: int = 500,
            fix_patience: int = 3) -> BasicCombinedChain:
        """
        Initialize a DatabaseModerateNAnswerNFixChain object from
        configuration.
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
        """

        db_m_chain = ModerateChain.from_config(
            open_ai_key=open_ai_key,
            include_tables=include_tables,
            prompt_name=moderate_chain_prompt_name,
            max_output_tokens=max_output_tokens_m,
            temperature=temperature_m
        )
        db_a_fix_chain = DatabaseAnswerNFixChain.from_config(
            uri=uri,
            include_tables=include_tables,
            open_ai_key=open_ai_key,
            answer_chain_prompt_name=answer_chain_prompt_name,
            fix_chain_prompt_name=fix_chain_prompt_name,
            max_output_tokens_a=max_output_tokens_a,
            max_output_tokens_f=max_output_tokens_f,
            temperature_a=temperature_a,
            temperature_f=temperature_f,
            sample_row=sample_rows,
            max_rows_return=max_rows_return,
            fix_patience=fix_patience
        )

        return cls(chains=[db_m_chain, db_a_fix_chain],
                   fix_patience=fix_patience)

    def perform(self,
                user_input: str,
                get_cmd: bool = True,
                get_db: bool = False,
                get_summary: bool = True,
                log_fix: bool = True,
                explain_moderate: bool = True) -> dict:
        """
        Perform chain function.
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
        """
        assert get_cmd or get_db or get_summary

        moderate_dict = self.moderate_chain.perform(
            user_input=user_input,
            with_explanation=explain_moderate
        )
        moderate_decision = moderate_dict['decision']
        moderate_explanation = moderate_dict['explanation']
        if not moderate_decision:
            return_dict = {'cmd': "",
                           'summary': "",
                           'db': "",
                           'error': "",
                           'moderate_decision': moderate_decision,
                           'moderate_explanation': moderate_explanation
                           }
            return return_dict

        answer_dict = self.a_n_f_chain.perform(
            user_input=user_input,
            get_cmd=True,
            get_db=get_db,
            get_summary=True,
            log_fix=log_fix
        )

        return {'cmd': answer_dict['cmd'],
                'summary': answer_dict['summary'],
                'db': answer_dict['db'],
                'error': answer_dict['error'],
                'moderate_decision': moderate_decision,
                'moderate_explanation': moderate_explanation}
