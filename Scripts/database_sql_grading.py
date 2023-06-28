from Agents.EvaluationAgent import PostgressqlGradingAgent
from Retriever.BasicRetriever import BasicTextRetriever


def run(request: str, sql_cmd: str, db_summary: str):
    agent = PostgressqlGradingAgent()
    retrivever = BasicTextRetriever()
    agent.equip_retriever(retrivever)
    result = agent.grade(
        request=request,
        sql_cmd=sql_cmd,
        db_summary=db_summary
    )
    return result
