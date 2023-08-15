from llmreflect.Agents.ModerateAgent import DatabaseModerateAgent
from llmreflect.Chains.BasicChain import BasicChain
from llmreflect.Retriever.BasicRetriever import BasicQuestionModerateRetriever
from typing import Any


class ModerateChain(BasicChain):
    AgentClass = DatabaseModerateAgent
    RetrieverClass = BasicQuestionModerateRetriever

    def __init__(self, agent: DatabaseModerateAgent,
                 retriever: BasicQuestionModerateRetriever,
                 **kwargs):
        """
        A chain for filtering out toxic questions and injection attacks.
        Args:
            agent (DatabaseModerateAgent): DatabaseModerateAgent
            retriever (BasicQuestionModerateRetriever):
                BasicQuestionModerateRetriever
        """
        super().__init__(agent, retriever, **kwargs)

    def perform(self, user_input: str,
                with_explanation: bool = False) -> Any:
        """
        Overwrite perform function.
        Sensor the questions if they are allowed
        Args:
            user_input (str): user's natural language request
            with_explanation (bool): if add explanation

        Returns:
            without explanation: return a boolean variable
            with explanation: dict: {'decision': bool, 'explanation': str}
        """
        if with_explanation:
            result = self.agent.predict_decision_explained(
                user_input=user_input)
        else:
            result = self.agent.predict_decision_only(user_input=user_input)
        return result
