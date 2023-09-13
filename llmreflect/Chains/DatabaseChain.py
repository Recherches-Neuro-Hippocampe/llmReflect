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
    AgentClass = DatabaseQuestionAgent
    RetrieverClass = DatabaseQuestionRetriever

    def __init__(self, agent: DatabaseQuestionAgent,
                 retriever: DatabaseQuestionRetriever,
                 **kwargs):
        """
        A chain for creating questions given by a dataset.
        Args:
            agent (DatabaseQuestionAgent): DatabaseQuestionAgent
            retriever (DatabaseQuestionRetriever): DatabaseQuestionRetriever
        """
        super().__init__(agent, retriever, **kwargs)

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
    AgentClass = DatabaseAgent
    RetrieverClass = DatabaseRetriever

    def __init__(self, agent: DatabaseAgent, retriever: DatabaseRetriever,
                 **kwargs):
        """
        Chain for generating database query cmd based on questions in natural
        language.
        Args:
            agent (DatabaseAgent): DatabaseAgent
            retriever (DatabaseRetriever): DatabaseRetriever
        """
        super().__init__(agent, retriever, **kwargs)

    def perform(self,
                user_input: str,
                get_cmd: bool = True,
                get_db: bool = False,
                get_summary: bool = True) -> dict:
        """
        Core function of the chain. Obtain the LLM result based on input.
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
    AgentClass = DatabaseGradingAgent
    RetrieverClass = DatabaseEvaluationRetriever

    def __init__(self, agent: DatabaseGradingAgent,
                 retriever: DatabaseEvaluationRetriever,
                 **kwargs):
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
        super().__init__(agent, retriever, **kwargs)

    def perform(self, request: str,
                sql_cmd: str,
                db_summary: str) -> dict:
        """Core function of the chain. Obtain the LLM result based on input.

        Args:
            request (str): queries about a dataset
            query (str): generated queries
            db_summary (str): execution summary

        Returns:
            dict: {"grading": a float number between 0 to 10,
                    "explanation": explanation for the score assigned}
        """
        grad_dict = self.agent.grade(request=request,
                                     sql_cmd=sql_cmd,
                                     db_summary=db_summary)
        return grad_dict


class DatabaseSelfFixChain(BasicChain):
    AgentClass = DatabaseSelfFixAgent
    RetrieverClass = DatabaseRetriever

    def __init__(self,
                 agent: DatabaseSelfFixAgent,
                 retriever: DatabaseRetriever,
                 **kwargs):
        """
        A Basic chain class for fix database queries.
        Args:
            agent (DatabaseSelfFixAgent): DatabaseSelfFixAgent
            retriever (DatabaseRetriever): DatabaseRetriever
        """
        super().__init__(agent, retriever, **kwargs)

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


class DatabaseQnAGradingChain(BasicCombinedChain):
    REQUIRED_CHAINS = [
        DatabaseAnswerChain,
        DatabaseQuestionChain,
        DatabaseGradingChain
    ]

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
    REQUIRED_CHAINS = [
        DatabaseAnswerChain,
        DatabaseSelfFixChain
    ]

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


class DatabaseModerateNAnswerNFixChain(BasicCombinedChain):
    REQUIRED_CHAINS = [
        ModerateChain,
        DatabaseAnswerNFixChain
    ]

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
