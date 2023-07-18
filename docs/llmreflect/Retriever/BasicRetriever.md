Module llmreflect.Retriever.BasicRetriever
==========================================

Classes
-------

`BasicEvaluationRetriever()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * llmreflect.Retriever.BasicRetriever.BasicRetriever
    * abc.ABC

    ### Methods

    `retrieve(self, llm_output: str) ‑> dict`
    :

`BasicQuestionModerateRetriever(include_tables: List)`
:   _summary_
    Retriever class based on DatabaseQuestionRetriever.
    For filtering out malicious content
    Args:
        DatabaseQuestionRetriever (_type_): _description_

    ### Ancestors (in MRO)

    * llmreflect.Retriever.BasicRetriever.BasicRetriever
    * abc.ABC

    ### Methods

    `retrieve(self, llm_output: str, explanation: bool = False) ‑> dict`
    :   _summary_
        
        Args:
            llm_output (str): output from llm
            explanation (str): wether return with explanation or not
        Returns:
            _type_: a processed string

`BasicRetriever()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * llmreflect.Retriever.BasicRetriever.BasicEvaluationRetriever
    * llmreflect.Retriever.BasicRetriever.BasicQuestionModerateRetriever
    * llmreflect.Retriever.BasicRetriever.BasicTextRetriever
    * llmreflect.Retriever.DatabaseRetriever.DatabaseRetriever

    ### Static methods

    `retrieve(llm_output: str) ‑> str`
    :

`BasicTextRetriever()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * llmreflect.Retriever.BasicRetriever.BasicRetriever
    * abc.ABC

    ### Methods

    `retrieve(self, llm_output: str) ‑> str`
    :