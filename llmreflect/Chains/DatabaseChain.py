from llmreflect.Chains.BasicChain import BasicChain, BasicCombinedChain
from llmreflect.Agents.QuestionAgent import PostgresqlQuestionAgent
from llmreflect.Agents.PostgresqlAgent import PostgresqlAgent, \
    PostgresqlSelfFixAgent
from llmreflect.Agents.EvaluationAgent import PostgressqlGradingAgent
from llmreflect.Retriever.DatabaseRetriever import DatabaseQuestionRetriever, \
    DatabaseRetriever
from llmreflect.Retriever.BasicRetriever import BasicEvaluationRetriever
from llmreflect.Chains.ModerateChain import ModerateChain
from typing import List


class DatabaseQuestionChain(BasicChain):
    def __init__(self, agent: PostgresqlQuestionAgent,
                 retriever: DatabaseQuestionRetriever):
        """
        A chain for creating questions given by a dataset.
        Args:
            agent (PostgresqlQuestionAgent): _description_
            retriever (DatabaseQuestionRetriever): _description_
        """
        super().__init__(agent, retriever)

    @classmethod
    def from_config(cls, uri: str,
                    include_tables: List,
                    open_ai_key: str,
                    prompt_name: str = 'questionpostgresql',
                    max_output_tokens: int = 512,
                    temperature: float = 0.7,
                    sample_rows: int = 0):
        agent = PostgresqlQuestionAgent(
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
            n_questions (int, optional): _description_. Defaults to 5.

        Returns:
            list: a list of questions, each question is a str object.
        """
        result = self.agent.predict_n_questions(n_questions=n_questions)
        return result


class DatabaseAnswerChain(BasicChain):
    def __init__(self, agent: PostgresqlAgent, retriever: DatabaseRetriever):
        """
        Chain for generating postgresql cmd based on questions in natural
        language.
        Args:
            agent (PostgresqlAgent): _description_
            retriever (DatabaseRetriever): _description_
        """
        super().__init__(agent, retriever)

    @classmethod
    def from_config(cls, uri: str,
                    include_tables: List,
                    open_ai_key: str,
                    prompt_name: str = 'postgresql',
                    max_output_tokens: int = 512,
                    temperature: float = 0.0,
                    sample_rows: int = 0,
                    max_rows_return=500):
        agent = PostgresqlAgent(
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
    def __init__(self, agent: PostgressqlGradingAgent,
                 retriever: BasicEvaluationRetriever):
        """_summary_
        A chain for the following workflow:
        1. given by questions about a database and according
            postgresql solutions for questions
        2. evaluate the generated solutions
        Args:
            agent (PostgressqlGradingAgent): _description_
            retriever (BasicEvaluationRetriever): _description_
        """
        super().__init__(agent, retriever)

    @classmethod
    def from_config(cls,
                    open_ai_key: str,
                    max_output_tokens: int = 256,
                    prompt_name: str = "gradingpostgresql",
                    temperature: float = 0.7):
        """_summary_

        Args:
            open_ai_key (str): _description_
            max_output_tokens (int, optional): dont need to be long.
                Defaults to 256.
            prompt_name (str, optional): _description_.
                Defaults to "gradingpostgresql".
            temperature (float, optional): questions should be diverse.
                Set this to a high value but lower than 1. Defaults to 0.7.

        Returns:
            _type_: _description_
        """
        agent = PostgressqlGradingAgent(
            open_ai_key=open_ai_key,
            prompt_name=prompt_name,
            max_output_tokens=max_output_tokens,
            temperature=temperature)

        retriever = BasicEvaluationRetriever()
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
                    question_chain_prompt_name: str = 'questionpostgresql',
                    answer_chain_prompt_name: str = 'postgresql',
                    grading_chain_prompt_name: str = 'gradingpostgresql',
                    q_max_output_tokens: int = 256,
                    q_temperature: float = 0.7,
                    a_max_output_tokens: int = 512,
                    g_max_output_tokens: int = 256,
                    a_temperature: float = 0.0,
                    g_temperature: float = 0.0,
                    sample_rows: int = 0,
                    max_rows_return=500):

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
            open_ai_key=open_ai_key,
            prompt_name=grading_chain_prompt_name,
            max_output_tokens=g_max_output_tokens,
            temperature=g_temperature)

        return cls(chains=[db_q_chain, db_a_chain, db_g_chain],
                   q_batch_size=5)

    def perform(self, n_question: int = 5) -> dict:
        """_summary_

        Args:
            n_question (int, optional): _description_. Defaults to 5.

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
        """_summary_

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
    """
    A chain class for fixing sql errors
    Args:
        BasicChain (_type_): _description_
    """
    def __init__(self,
                 agent: PostgresqlSelfFixAgent,
                 retriever: DatabaseRetriever):
        super().__init__(agent, retriever)

    @classmethod
    def from_config(cls, uri: str,
                    include_tables: List,
                    open_ai_key: str,
                    prompt_name: str = 'postgresqlfix',
                    max_output_tokens: int = 512,
                    temperature: float = 0.0,
                    sample_rows: int = 0,
                    max_rows_return: int = 500):
        agent = PostgresqlSelfFixAgent(
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
        """_summary_

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
            answer_chain_prompt_name: str = "postgresql",
            fix_chain_prompt_name: str = "postgresqlfix",
            moderate_chain_prompt_name: str = "moderatepostgresql",
            max_output_tokens_a: int = 512,
            max_output_tokens_f: int = 512,
            max_output_tokens_m: int = 256,
            temperature_a: float = 0.0,
            temperature_f: float = 0.0,
            temperature_m: float = 0.0,
            sample_row: int = 0,
            max_rows_return: int = 500,
            fix_patience: int = 3):

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
            sample_row=sample_row,
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
        """_summary_

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
