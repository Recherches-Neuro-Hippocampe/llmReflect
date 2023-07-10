from llmreflect.Prompt.BasicPrompt import BasicPrompt

"""
An example for how to modify prompt in llmreflect
"""

bp = BasicPrompt.load_prompt_from_json_file("moderatepostgresql")

inconext_list = bp._in_context_learning_list
inconext_list.extend(
    [
        {
            'request': 'show me all patients that are likely to have an error \
in their birth date',
            'response': '[APPROVE]'
        },
        {
            'request': 'show me all patients who cook',
            'response': '[APPROVE]'
        },
        {
            'request': 'show me 100 different kind of medicines used',
            'response': '[APPROVE]'
        },
    ]
)
bp.in_context_learning = inconext_list
bp.save_prompt()
