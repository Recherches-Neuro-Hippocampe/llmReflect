from Agents.EvaluationAgent import PostgressqlGradingAgent
from Retriever.BasicRetriever import BasicEvaluationRetriever


def run(request: str, sql_cmd: str, db_summary: str):
    agent = PostgressqlGradingAgent()
    retriever = BasicEvaluationRetriever()
    agent.equip_retriever(retriever)
    result = agent.grade(
        request=request,
        sql_cmd=sql_cmd,
        db_summary=db_summary
    )
    return result
