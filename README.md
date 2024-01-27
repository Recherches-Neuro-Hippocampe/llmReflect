# llmReflect
[![PyPI version](https://badge.fury.io/py/llmreflect.svg)](https://badge.fury.io/py/llmreflect)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://img.shields.io/badge/python-3.11-blue.svg)
[![Python package](https://github.com/Recherches-Neuro-Hippocampe/llmReflect/actions/workflows/python-package.yml/badge.svg)](https://github.com/Recherches-Neuro-Hippocampe/llmReflect/actions/workflows/python-package.yml)
[![Upload Python Package](https://github.com/Recherches-Neuro-Hippocampe/llmReflect/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Recherches-Neuro-Hippocampe/llmReflect/actions/workflows/python-publish.yml)
llmReflect is a python package designed for large language model (**LLM**) applications. We have seen numerous emergent abilities so far. Given by a right prompt, a LLM is capable of various tasks. Also the art of writing a prompt usually determines the performance of the LLM at that task. So is there a chance that we can use LLM to evaluate / improve itself's prompt?

**Warning!** This project is at the very early stage!

## Installation
* 1.  llmReflect is on PYPI. \
`pip install llmreflect`

* 2. use pipenv and git clone \
`git clone https://github.com/Recherches-Neuro-Hippocampe/llmReflect.git` \
`pipenv shell` \
`pipenv install`

## Basic usage
### 1. Case 1: Use a combined chain to retrieve information from database based on users' natural language description

```
from llmreflect.LLMCore.LLMCore import LOCAL_MODEL, OPENAI_MODEL
from llmreflect.Utils.log import get_logger
from llmreflect.Chains.DatabaseChain import \
    DatabaseModerateNAnswerNFixChain
from decouple import config
# Assume you have a .env file storing OpenAI API key, db credentials and etc..

LOGGER = get_logger("test")


def example_chain_running(local=False):
    # If you have a local Llama.cpp supported model, you can specify `local=True`

    MODEL_PATH = LOCAL_MODEL.upstage_70_b
    URI = f"postgresql+psycopg2://{config('DBUSERNAME')}:\
{config('DBPASSWORD')}@{config('DBHOST')}:{config('DBPORT')}/postgres"

    INCLUDE_TABLES = [
        'tb_patient',
        'tb_patients_allergies',
        'tb_appointment_patients',
        'tb_patient_mmse_and_moca_scores',
        'tb_patient_medications'
    ]

    LOCAL_LLM_CONFIG = {
        "max_output_tokens": 512,
        "max_total_tokens": 5000,
        "model_path": MODEL_PATH,
        "n_batch": 512,
        "n_gpus_layers": 4,
        "n_threads": 16,
        "temperature": 0.0,
        "verbose": False
    }
    OPENAI_LLM_CONFIG = {
        "llm_model": OPENAI_MODEL.gpt_3_5_turbo_0613,
        "max_output_tokens": 512,
        "open_ai_key": config("OPENAI_API_KEY"),
        "temperature": 0.0
    }

    chain_config = {
        "DatabaseAnswerNFixChain": {
            "DatabaseAnswerChain": {
                "llm_config": LOCAL_LLM_CONFIG if local else OPENAI_LLM_CONFIG,
                "other_config": {},
                "retriever_config": {
                    "include_tables": INCLUDE_TABLES,
                    "max_rows_return": 500,
                    "sample_rows": 0,
                    "uri": URI
                }
            },
            "DatabaseSelfFixChain": {
                "llm_config": LOCAL_LLM_CONFIG if local else OPENAI_LLM_CONFIG,
                "other_config": {},
                "retriever_config": {
                    "include_tables": INCLUDE_TABLES,
                    "max_rows_return": 500,
                    "sample_rows": 0,
                    "uri": URI
                }
            },
        },
        "ModerateChain": {
            "llm_config": LOCAL_LLM_CONFIG if local else OPENAI_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES
            }
        },
    }
    ch = DatabaseModerateNAnswerNFixChain.from_config(**chain_config)  # Initialize a chain
    question = "Show me the patients who have taken the medication \
Donepezil and are considered as overweight."
    result, traces = ch.perform_cost_monitor(
        user_input=question,
        explain_moderate=True)  # Run the chain

    # Presenting the results of execution

    LOGGER.info(f"Question: {question}")
    LOGGER.info(f"LLM Moderate Decision: {result['moderate_decision']}")
    LOGGER.info(f"LLM Moderate Comment: {result['moderate_explanation']}")
    LOGGER.info(f"LLM Generated Postgresql: {result['cmd']}")
    LOGGER.info(f"Postgresql Execution Result: {result['summary']}")
```
### 2. Case 2: Semantic Search on Files

```
from llmreflect.Retriever.VectorDatabaseRetriever import \
    VectorDatabaseRetriever

search_engine = VectorDatabaseRetriever()
# Initialize the search engine
question = "How do we recruit new patients?"
result = search_engine.retrieve(question)
assert len(result.response) > 0
```

The returned result is a pandatic model which contains 2 attributes:
    1. `response`: str, the response from LLM describing the returned result.
    2. `citations`: List [Citation], the citations/reference for the resources.

As for the pandantic model `Citation`, it contains 4 attributes:
    1. `text`: str, text content of the citation.
    2. `file_path`: str, the file path for the source file.
    3. `bucket`: str, the bucket name for the source s3 bucket.
    4. `page`: int, page number for the source in this file.
