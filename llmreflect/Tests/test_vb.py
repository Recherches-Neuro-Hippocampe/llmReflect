from llmreflect.Retriever.VectorDatabaseRetriever import \
    VectorDatabaseRetriever
import pytest
import os


def in_workflow():
    return os.getenv("GITHUB_ACTIONS")\
        or os.getenv("TRAVIS") \
        or os.getenv("CIRCLECI") \
        or os.getenv("GITLAB_CI")


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_vb():
    search_engine = VectorDatabaseRetriever()
    question = "How do we recruit new patients?"
    result = search_engine.retrieve(question)
    assert len(result.response) > 0
