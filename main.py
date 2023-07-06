from llmreflect.Prompt.BasicPrompt import BasicPrompt

"""
An example for how to write prompt in llmreflect
"""

bp_dict = {
    "HARD": '''\
You are a {dialect} expert. Your job is to fix a problematic \
{dialect} query. This query was created to solve a question.
You will be given the question and the query, also \
the information about the database where the query executed on. \
Fix the errors in the query and make sure \
that your {dialect} query is syntactically correct and answer \
the question.
You must not access tables that are not included.
''',
    "SOFT": '''\
You should assume all values in the database are in lowercase.\
Return the syntactically correct query only.
Limit the number of returning records by \
the number specified in the question. \
If there is no limitation, limit the number of returning by {max_present}.
''',
    "INCONTEXT": [
    ],
    "FORMAT": {
        "table_info": {
            'type': 'INPUT',
            'explanation': 'the information for the database'
        },
        "request": {
            'type': 'INPUT',
            'explanation': "user's request",
        },
        "history": {
            'type': 'INPUT',
            'explanation': "{dialect} command with error.",
        },
        "his_error": {
            'type': 'INPUT',
            'explanation': "Errors reported by the database",
        },
        "answer": {
            'type': 'OUTPUT',
            'explanation': "The {dialect} command corrected by you."
        }
    }
}

bp = BasicPrompt(prompt_dict=bp_dict, promptname='postgresqlfix')
bp.save_prompt()
