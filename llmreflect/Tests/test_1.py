from llmreflect.Agents.EvaluationAgent import PostgressqlGradingAgent
from llmreflect.Retriever.BasicRetriever import BasicEvaluationRetriever


def test_postgres_grading_agent():
    agent = PostgressqlGradingAgent()
    retriever = BasicEvaluationRetriever()
    agent.equip_retriever(retriever)
