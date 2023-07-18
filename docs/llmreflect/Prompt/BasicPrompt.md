Module llmreflect.Prompt.BasicPrompt
====================================
Module for prompt template, based on langchain prompt.
A prompt can be divied into 3 parts:
1. Hard rules which are fixed and permanant.
2. Soft rule which can be modified by Agents only when necessary.
3. In-context learning, places for holding in-context learning examples,
the major part that Agents can tune.

Classes
-------

`BasicPrompt(prompt_dict: Dict[str, Any], promptname: str, customized_input_list: list = [])`
:   Mighty mother of all prompts (In this repo I mean)
    
    If you want to start working on a prompt from scratch,
    a dictionary containing the prompts and name of this prompt
    are required.
    Args:
        prompt_dict (Dict[str, Any]): In this design,
        a prompt can be divided into 4 parts,
        hard rules, soft rule and in-context learning and format.
        Hard rules indicate the general context for the LLM and
        we usually do not change the hard rules.
        Soft rules are the rules that focus on the refine the
        behavior for the model, used for formatting or tuning.
        In-context learning is just a cool word to say examples.
        We all need examples right?
        promptname (str): nickname by you for the prompt.
        Also used as the file name to store the prompt in
        json format in 'promptbase' folder.
    
        Overall this design is to enable the model to tune itself.
        So there are rules the model can touch and others cant.
        Also I hate people keeping prompts in the coding logic place.

    ### Class variables

    `logger`
    :

    ### Static methods

    `get_prompt_dict_template()`
    :

    `load_prompt_from_json_file(promptname: str)`
    :

    `wrap_key_name(key_name)`
    :

    ### Instance variables

    `completion_head_up`
    :

    `hard_rules`
    :

    `in_context_learning`
    :

    `input_format`
    :

    `soft_rules`
    :

    ### Methods

    `get_langchain_prompt_template(self)`
    :

    `save_prompt(self)`
    :   save prompt into json file.