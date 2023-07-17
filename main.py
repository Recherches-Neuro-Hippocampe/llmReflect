from llmreflect.Prompt.BasicPrompt import BasicPrompt


def example_edit_prompt():
    """
    An example for how to modify prompt in llmreflect
    """
    bp = BasicPrompt.load_prompt_from_json_file("moderate_database")

    inconext_list = bp._in_context_learning_list
    inconext_list.extend(
        [
            {
                'request': 'show me all patients that are likely to have an \
error in their birth date',
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


def example_clear_logs():
    from llmreflect.Utils.log import clear_logs
    clear_logs()
