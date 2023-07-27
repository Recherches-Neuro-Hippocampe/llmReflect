from llmreflect.Prompt.BasicPrompt import BasicPrompt


def example_edit_prompt():
    """
    An example for how to modify prompt in llmreflect
    """
    bp = BasicPrompt.load_prompt_from_json_file("moderate_database")
    bp.input_format = {
        'topic': {
            'type': 'CONTEXT',
            'explanation': 'the expected theme for the requests'},
        'included_tables': {
            'type': 'CONTEXT',
            'explanation': 'the expected theme for the requests'},
        'request': {
            'type': 'INPUT',
            'explanation': "user's request"},
        'response': {
            'type': 'OUTPUT',
            'explanation': 'your decision, [APPROVE] or [REJECT]'},
        'reason': {
            'type': 'OUTPUT',
            'explanation': 'Reason for your decision'}
    }
    bp.save_prompt()


def example_clear_logs():
    from llmreflect.Utils.log import clear_logs
    clear_logs()
