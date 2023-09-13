"""
Have not figured out a way to test current chains without database.
Future work...
"""
import os
import pytest
from llmreflect.Utils.log import get_logger, traces_2_str
from decouple import config


def in_workflow():
    return os.getenv("GITHUB_ACTIONS")\
        or os.getenv("TRAVIS") \
        or os.getenv("CIRCLECI") \
        or os.getenv("GITLAB_CI")


if not bool(in_workflow()):
    from llmreflect.LLMCore.LLMCore import LOCAL_MODEL, OPENAI_MODEL
    LOGGER = get_logger("test")

    MODEL_PATH = LOCAL_MODEL.upstage_70_b
    URI = f"postgresql+psycopg2://{config('DBUSERNAME')}:\
{config('DBPASSWORD')}@{config('DBHOST')}:{config('DBPORT')}/postgres"

    INCLUDE_TABLES = [
        'tb_adverse_events',
        'tb_allergies',
        'tb_alternate_paragraph',
        'tb_apoe',
        'tb_appointment_employees',
        'tb_appointments',
        'tb_assets',
        'tb_clinical_dementia_rating',
        'tb_clinics',
        'tb_csf',
        'tb_employee_asset_assignments',
        'tb_employee_bosses',
        'tb_employees',
        'tb_medical_problems',
        'tb_medications',
        'tb_mmse',
        'tb_moca',
        'tb_mri',
        'tb_notes',
        'tb_patient_documents',
        'tb_patient_medications',
        'tb_patient_study_profile_partners',
        'tb_patient_study_profiles',
        'tb_patient_study_status',
        'tb_patient_tags',
        'tb_patients',
        'tb_patients_allergies',
        'tb_pet',
        'tb_positions',
        'tb_rbans',
        'tb_rooms',
        'tb_studies',
        'tb_study_partners',
        'tb_treatments',
        'tb_vitals'
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
        "llm_model": OPENAI_MODEL.gpt_3_5_turbo_16k,
        "max_output_tokens": 512,
        "open_ai_key": config("OPENAI_API_KEY"),
        "temperature": 0.0
    }


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_moderate_answer_fix_chain(local=False):

    from llmreflect.Chains.DatabaseChain import \
        DatabaseModerateNAnswerNFixChain

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

    questions = [
        "Give me all the patients allergic to fish",
        "Give me all the patients allergic to pollen",
        "give me a list of overweight patients who take donezepil",
        "Average mmse scores for patients per province. \
Round values to 2 decimals",
        "Give me max, min, avg, median and standard deviation on \
patients ages",
        "Get me a list of every patient who is on Aricept and whose primary \
clinic is in Ottawa. Filter out any patients with diabetes."
    ]
    for q in questions:
        print(q)
        result, traces = ch.perform_cost_monitor(
            user_input=q,
            explain_moderate=True)
        print(result["cmd"])
        print(result["summary"])
        print("=======================")


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_QAGrading_chain(n_questions=5, budget=0.1, local=False):
    from llmreflect.Chains.DatabaseChain import DatabaseQnAGradingChain
    import pandas as pd

    SAVE_LOG = True
    N_QUESTIONS = n_questions

    chain_config = {
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
        "DatabaseQuestionChain": {
            "llm_config": LOCAL_LLM_CONFIG if local else OPENAI_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES,
                "sample_rows": 0,
                "uri": URI
            }
        },
        "DatabaseGradingChain": {
            "llm_config": LOCAL_LLM_CONFIG if local else OPENAI_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES,
                "sample_rows": 0,
                "uri": URI
            }
        }
    }

    ch = DatabaseQnAGradingChain.from_config(**chain_config)

    logs, traces = ch.perform_cost_monitor(n_question=N_QUESTIONS,
                                           budget=budget)
    if SAVE_LOG:
        print(type(logs))
        df = pd.DataFrame.from_records(logs)
        df.to_csv("self_grading.csv", mode='a', index=False, header=False)

    else:
        for log in logs:
            LOGGER.info("Question: " + log["question"])
            LOGGER.info("Query: " + log["cmd"])
            LOGGER.info("Summary: " + log["summary"])
            LOGGER.info("Score: %.2f" % log["grading"])
            LOGGER.info("Explain: " + log["explanation"])
            assert len(log["question"]) > 0
            assert len(log["cmd"]) > 0
            assert len(log["summary"]) > 0
            assert len(log["explanation"]) > 0
            assert log["grading"] >= 0
    LOGGER.debug(traces_2_str(traces))


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_answerNfix_chain(local=False):

    from llmreflect.Chains.DatabaseChain import DatabaseAnswerNFixChain

    chain_config = {
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
        }
    }
    ch = DatabaseAnswerNFixChain.from_config(**chain_config)
    result_dict, traces = ch.perform_cost_monitor(
        user_input="give me a list overweight patients")
    assert len(result_dict['summary']) > 0
    assert type(result_dict['error']) is list
    LOGGER.debug(traces_2_str(traces))
