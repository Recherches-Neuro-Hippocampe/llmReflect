from llmreflect.Chains.BasicChain import BasicChain
from llmreflect.Agents.QuestionAgent import PostgresqlQuestionAgent
from llmreflect.Agents.PostgresqlAgent import PostgresqlAgent
from llmreflect.Agents.EvaluationAgent import PostgressqlGradingAgent
from llmreflect.Retriever.DatabaseRetriever import DatabaseQuestionRetriever, \
    DatabaseRetriever
from llmreflect.Retriever.BasicRetriever import BasicEvaluationRetriever
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


class DatabaseQnAGradingChain(BasicChain):
    def __init__(self, agent: PostgressqlGradingAgent,
                 retriever: BasicEvaluationRetriever,
                 db_q_chain: DatabaseQuestionChain,
                 db_a_chain: DatabaseAnswerChain,
                 q_batch_size: int = 5):
        """
        A chain for the following workflow:
        1. create questions based on the database
        2. generate postgresql solutions for questions
        3. evaluate the generated solutions
        Args:
            agent (PostgressqlGradingAgent): _description_
            retriever (BasicEvaluationRetriever): _description_
            db_q_chain: chain for questioning
            db_a_chain: chain for answering
            q_batch_size: in each batch, ask how many questions
        """
        super().__init__(agent, retriever)
        self.db_q_chain = db_q_chain
        self.db_a_chain = db_a_chain
        self.q_batch_size = q_batch_size

    @classmethod
    def from_config(cls, uri: str,
                    include_tables: List,
                    open_ai_key: str,
                    q_prompt_name: str = 'questionpostgresql',
                    a_prompt_name: str = 'postgresql',
                    g_prompt_name: str = 'gradingpostgresql',
                    q_max_output_tokens: int = 512,
                    q_temperature: float = 0.7,
                    a_max_output_tokens: int = 512,
                    g_max_output_tokens: int = 512,
                    a_temperature: float = 0.0,
                    g_temperature: float = 0.0,
                    sample_rows: int = 0,
                    max_rows_return=500):

        db_q_chain = DatabaseQuestionChain.from_config(
            uri=uri,
            include_tables=include_tables,
            open_ai_key=open_ai_key,
            prompt_name=q_prompt_name,
            max_output_tokens=q_max_output_tokens,
            temperature=q_temperature,
            sample_rows=sample_rows
        )

        db_a_chain = DatabaseAnswerChain.from_config(
            uri=uri,
            include_tables=include_tables,
            open_ai_key=open_ai_key,
            prompt_name=a_prompt_name,
            max_output_tokens=a_max_output_tokens,
            temperature=a_temperature,
            sample_rows=sample_rows,
            max_rows_return=max_rows_return
        )

        agent = PostgressqlGradingAgent(
            open_ai_key=open_ai_key,
            prompt_name=g_prompt_name,
            max_output_tokens=g_max_output_tokens,
            temperature=g_temperature)

        retriever = BasicEvaluationRetriever()
        return cls(agent=agent, retriever=retriever,
                   db_a_chain=db_a_chain,
                   db_q_chain=db_q_chain,
                   q_batch_size=5)

    def perform(self, n_question: int = 5):
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
            grad_dict = self.agent.grade(
                request=q,
                sql_cmd=temp_dict['cmd'],
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
