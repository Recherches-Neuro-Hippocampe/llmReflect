from llmreflect.Prompt.BasicPrompt import BasicPrompt


def example_edit_prompt():
    """
    An example for how to modify prompt in llmreflect
    """
    bp = BasicPrompt.load_prompt_from_json_file("answer_database")
    bp.in_context_learning = [
        {
            "request": "",
            "answer": ""
        },
    ]
    bp.save_prompt()
    print(bp.in_context_learning)
    print(bp.get_langchain_prompt_template())


def example_clear_logs():
    from llmreflect.Utils.log import clear_logs
    clear_logs()


def example_chain_running(local=False):
    from llmreflect.LLMCore.LLMCore import LOCAL_MODEL, OPENAI_MODEL
    from llmreflect.Utils.log import get_logger
    from llmreflect.Chains.DatabaseChain import \
        DatabaseModerateNAnswerNFixChain
    from decouple import config

    LOGGER = get_logger("test")

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
    ch = DatabaseModerateNAnswerNFixChain.from_config(**chain_config)
    question = "Show me the patients who have taken the medication \
Donepezil and are considered as overweight."
    result, traces = ch.perform_cost_monitor(
        user_input=question,
        explain_moderate=True)

    LOGGER.info(f"Question: {question}")
    LOGGER.info(f"LLM Moderate Decision: {result['moderate_decision']}")
    LOGGER.info(f"LLM Moderate Comment: {result['moderate_explanation']}")
    LOGGER.info(f"LLM Generated Postgresql: {result['cmd']}")
    LOGGER.info(f"Postgresql Execution Result: {result['summary']}")
