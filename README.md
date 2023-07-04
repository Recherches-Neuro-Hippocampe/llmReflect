# llmReflect
[![PyPI version](https://badge.fury.io/py/llmreflect.svg)](https://badge.fury.io/py/llmreflect) ![Python Versions](https://img.shields.io/pypi/pyversions/llmreflect) 
[![Python package](https://github.com/Recherches-Neuro-Hippocampe/llmReflect/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/Recherches-Neuro-Hippocampe/llmReflect/actions/workflows/python-package.yml)
[![Upload Python Package](https://github.com/Recherches-Neuro-Hippocampe/llmReflect/actions/workflows/python-publish.yml/badge.svg?branch=main)](https://github.com/Recherches-Neuro-Hippocampe/llmReflect/actions/workflows/python-publish.yml)

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
### 1. Case 1: 
Create a chain for a following workflow:
* asking questions given by a dataset
* generate postgresql cmd to solve the question
* score itself's performance

```
from llmreflect.Chains.DatabaseChain import DatabaseQnAGradingChain

def test_grading_chain():

    uri = "your database connection uri"

    ch = DatabaseQnAGradingChain.from_config(
        uri=uri,
        include_tables=[
            'table name 1',
            'table name 2',
        ],
        open_ai_key=config('OPENAI_API_KEY')
    )
    logs = ch.perform(n_question=1)

```

