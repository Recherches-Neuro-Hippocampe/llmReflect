Module llmreflect.Agents.QuestionAgent
======================================

Classes
-------

`DatabaseQuestionAgent(open_ai_key: str, prompt_name: str = 'question_database', max_output_tokens: int = 512, temperature: float = 0.7)`
:   Agent for creating questions based on a given database
    Args:
        Agent (_type_): _description_
    
    Agent for creating questions based on a given database
    Args:
        open_ai_key (str): API key to connect to chatgpt service.
        prompt_name (str, optional): name for the prompt json file.
            Defaults to 'question_database'.
        max_output_tokens (int, optional): maximum completion length.
            Defaults to 512.
        temperature (float, optional): how consistent the llm performs.
            The lower the more consistent. To obtain diverse questions,
            a high temperature is recommended.
            Defaults to 0.0.

    ### Ancestors (in MRO)

    * llmreflect.Agents.BasicAgent.OpenAIAgent
    * llmreflect.Agents.BasicAgent.Agent
    * langchain.chains.llm.LLMChain
    * langchain.chains.base.Chain
    * langchain.load.serializable.Serializable
    * pydantic.main.BaseModel
    * pydantic.utils.Representation
    * abc.ABC

    ### Methods

    `equip_retriever(self, retriever: llmreflect.Retriever.DatabaseRetriever.DatabaseQuestionRetriever)`
    :

    `predict_n_questions(self, n_questions: int = 5) ‑> str`
    :   Create n questions given by a dataset
        Args:
            n_questions (int, optional):
            number of questions to generate in a run. Defaults to 5.
        
        Returns:
            str: a list of questions, I love list.