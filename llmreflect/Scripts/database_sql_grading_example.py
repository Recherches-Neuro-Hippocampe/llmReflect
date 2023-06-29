from llmreflect.Agents.EvaluationAgent import PostgressqlGradingAgent
from llmreflect.Retriever.BasicRetriever import BasicEvaluationRetriever

from llmreflect.Scripts import database_answer_example,\
    database_question_example


def run(n_question: int = 5):
    questions = database_question_example.run(n_questions=n_question)
    agent = PostgressqlGradingAgent()
    retriever = BasicEvaluationRetriever()
    agent.equip_retriever(retriever)

    for q in questions:
        result = database_answer_example.run(q, return_cmd=True)
        cmd = result['cmd']
        summary = result['summary']

        grading = agent.grade(
            request=q,
            sql_cmd=cmd,
            db_summary=summary
        )
        print(q)
        print(result['cmd'])
        print(result['summary'])
        print(grading)
        print("=============================")
