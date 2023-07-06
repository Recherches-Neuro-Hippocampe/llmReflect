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

### 2. Case 2:
How to write your own prompt and save it to your prompt base in llmReflect

```
from llmreflect.Prompt.BasicPrompt import BasicPrompt  # import the prompt class


prompt_dict = {
    "HARD": "most important rules, like general context, role acting etc.",
    'SOFT': "minor rules/guide for the llm, what need to pay attention to.",
    'INCONTEXT': [
        # show llm some examples
        {
            'request': "show me the names and phone numbers of the patients that are likely to have an error in their birth date",
            'command': '''\
select "uuid_patient","patient_code", "patient_first_name","patient_last_name",array_agg("phones") filter (where phones <> '{{}}') as "phones"
from tb_patient
where "patient_birth_date" > current_date
or "patient_birth_date" < '1900-01-01'
group by "uuid_patient", "patient_code","patient_first_name","patient_last_name"
limit 500;
''',
            'summary': "Error: Found 0 record! Empty response!",
            'grading': "9.2",
            'explanation': "It is very good. It filled the blank of what could be an error in birth date by some common sense. The syntax is correct, the query is executable. Even though it got an empty response, it is because the dataset does not contain such content."
        }
    ],
    'FORMAT': { # dictionary indicating the format for llm
        'request': {'type': 'INPUT',
                    'explanation': "User's natural language request"},
        'command': {
            'type': 'INPUT',
            'explanation': "the generated postgresql command"
        },
        'summary': {
            'type': 'INPUT',
            'explanation': "a summary for the excution result from database"
        },
        'grading': {
            'type': 'OUTPUT',
            'explanation': "the score you assign to the postgresql command, a number range from 0 to 10"
        },
        'explanation': {
            'type': 'OUTPUT',
            'explanation': "the reason for your scoring"
        },
    }
}

p = BasicPrompt(
    prompt_dict=prompt_dict,
    promptname="gradingpostgresql" # the name is used for saving and referencing
)
p.save_prompt()

```

