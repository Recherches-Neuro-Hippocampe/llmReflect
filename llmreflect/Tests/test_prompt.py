def test_prompt_loading():
    from llmreflect.Prompt.BasicPrompt import BasicPrompt
    prompt_names = [
        "gradingpostgresql",
        "moderatepostgresql",
        "postgresql",
        "questionpostgresql"
    ]
    for prompt_name in prompt_names:
        prompt = BasicPrompt.load_prompt_from_json_file(prompt_name)
        assert len(prompt.input_list) > 0
        assert len(prompt.get_langchain_prompt_template().template) > 0
