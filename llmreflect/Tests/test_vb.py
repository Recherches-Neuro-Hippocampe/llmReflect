from llmreflect.Retriever.VectorDatabaseRetriever import \
    VectorDatabaseRetriever


def test_vb():
    search_engine = VectorDatabaseRetriever()
    question = "How do we recruit new patients?"
    result = search_engine.retrieve(question)
    assert len(result.response) > 0
