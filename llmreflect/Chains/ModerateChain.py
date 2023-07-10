from llmreflect.Agents.ModerateAgent import PostgresqlModerateAgent
from llmreflect.Chains.BasicChain import BasicChain
from llmreflect.Retriever.BasicRetriever import BasicQuestionModerateRetriever
from typing import Any


class ModerateChain(BasicChain):
    def __init__(self, agent: PostgresqlModerateAgent,
                 retriever: BasicQuestionModerateRetriever):
        super().__init__(agent, retriever)

    @classmethod
    def from_config(cls,
                    open_ai_key: str,
                    include_tables: list,
                    prompt_name: str = 'moderatepostgresql',
                    max_output_tokens: int = 512,
                    temperature: float = 0.0):

        agent = PostgresqlModerateAgent(
            open_ai_key=open_ai_key,
            prompt_name=prompt_name,
            max_output_tokens=max_output_tokens,
            temperature=temperature
        )
        retriever = BasicQuestionModerateRetriever(
            include_tables=include_tables)
        return cls(agent=agent, retriever=retriever)

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
