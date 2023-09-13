"""
Have not figured out a way to test current chains without database.
Future work...
"""
import os
import pytest
from llmreflect.Utils.log import get_logger, traces_2_str


def in_workflow():
    return os.getenv("GITHUB_ACTIONS")\
        or os.getenv("TRAVIS") \
        or os.getenv("CIRCLECI") \
        or os.getenv("GITLAB_CI")


if not bool(in_workflow()):
    from llmreflect.LLMCore.LLMCore import LOCAL_MODEL, OPENAI_MODEL
    from decouple import config
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
def test_database_answer_chain(local=False):
    from llmreflect.Chains.DatabaseChain import DatabaseAnswerChain

    if local:
        chain_config = {
            "llm_config": LOCAL_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES,
                "max_rows_return": 500,
                "sample_rows": 0,
                "uri": URI
            }
        }
    else:
        chain_config = {
            "llm_config": OPENAI_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES,
                "max_rows_return": 500,
                "sample_rows": 0,
                "uri": URI
            }
        }
    ch = DatabaseAnswerChain.from_config(**chain_config)
    questions = [
        "Show me the patients who have the highest systolic blood pressure",
        "List all patients who have allergies to peanuts."
    ]
    for q in questions:
        print("\n\n")
        print(f"Question: {q}")
        result, traces = ch.perform_cost_monitor(
            user_input=q,
            get_cmd=True,
            get_db=False,
            get_summary=True)

        for key, item in result.items():
            print(key)
            print(item)
        print("====================\n\n")


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_database_self_fix_chain(local=False):
    from llmreflect.Chains.DatabaseChain import DatabaseSelfFixChain

    if local:
        chain_config = {
            "llm_config": LOCAL_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES,
                "max_rows_return": 500,
                "sample_rows": 0,
                "uri": URI
            }
        }
    else:
        chain_config = {
            "llm_config": OPENAI_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES,
                "max_rows_return": 500,
                "sample_rows": 0,
                "uri": URI
            }
        }
    ch = DatabaseSelfFixChain.from_config(**chain_config)
    q_a_pairs = [
        {
            "q": "Show me the top 5 frequently used medicine",
            "a": '''SELECT medication_name, count(*) AS frequency
FROM tb_patient_medications
GROUP BY medication_name
ORDER BY frequency DESC
LIMIT 5;
'''
        },
        {
            "q": "Show me the patients who have the highest \
systolic blood pressure",
            "a": '''\
SELECT "uuid_patient","patient_code", "patient_first_name", \
"patient_last_name", "patient_systolic_pressure"
FROM tb_patient
ORDER BY "patient_systolic_pressure" DESC
LIMIT 500;
'''
        },
        {
            "q": "Average mmse scores for patients per province. \
Round values to 2 decimals",
            "a": '''\
SELECT province, round(avg("patient_mmse_score"), 2) AS "average_mmse"
FROM tb_patient_mmse_and_moca_scores
INNER JOIN tb_patient
ON tb_patient.uuid_patient = tb_patient_mmse_and_moca_scores.patient
WHERE "patient_mmse_score" IS NOT null
GROUP BY province;
'''
        },
    ]
    for q_a_pair in q_a_pairs:
        question = q_a_pair['q']
        answer = q_a_pair['a']
        ori_summary = ch.retriever.retrieve_summary(
            llm_output=answer)
        if "Error" not in ori_summary:
            crooked_answer = answer.replace("tb_", "")
            crooked_summary = ch.retriever.retrieve_summary(
                llm_output=crooked_answer)
            LOGGER.info("Question: " + q_a_pair['q'])
            LOGGER.info("Crooked command: " + crooked_answer)
            LOGGER.info("Crooked summary: " + crooked_summary)
            result_dict, traces = ch.perform_cost_monitor(
                user_input=question,
                history=crooked_answer,
                his_error=crooked_summary
            )
            fixed_cmd = result_dict['cmd']
            fixed_summary = result_dict['summary']
            LOGGER.info("Fixed command: " + fixed_cmd)
            LOGGER.info("Fixed summary: " + fixed_summary)
            assert "error" not in fixed_summary.lower()

            LOGGER.debug(traces_2_str(traces))


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_question_chain(local=False):
    from llmreflect.Chains.DatabaseChain import DatabaseQuestionChain

    if local:
        chain_config = {
            "llm_config": LOCAL_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES,
                "sample_rows": 0,
                "uri": URI
            }
        }
    else:
        chain_config = {
            "llm_config": OPENAI_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES,
                "sample_rows": 0,
                "uri": URI
            }
        }

    ch = DatabaseQuestionChain.from_config(**chain_config)

    questions, traces = ch.perform_cost_monitor(n_questions=5)
    for q in questions:
        print(q)
    LOGGER.debug(traces_2_str(traces))


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_moderate_chain(local=False):
    from llmreflect.Chains.ModerateChain import ModerateChain

    if local:
        chain_config = {
            "llm_config": LOCAL_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES
            }
        }
    else:
        chain_config = {
            "llm_config": OPENAI_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES
            }
        }

    ch = ModerateChain.from_config(**chain_config)

    q_a_pairs = [
        {
            "q": "give me a list of patients",
            "a": 1
        },
        {
            "q": "Cats are the true rulers",
            "a": 0
        },
        {
            "q": "Give me all the patients allergic to fish",
            "a": 1
        },
        {
            "q": "Give me all the patients allergic to pollen",
            "a": 1
        },
        {
            "q": "Give me all the patients",
            "a": 1
        },
        {
            "q": "give me all the patients who live in ontario",
            "a": 1
        },
        {
            "q": "give me a list of overweight patients who take donezepil",
            "a": 1
        },
        {
            "q": "Average mmse scores for patients per province. \
Round values to 2 decimals",
            "a": 1
        },
        {
            "q": "Frequencies for patients ages in bins (range of 2), \
and patients older than 40",
            "a": 1
        },
        {
            "q": "Give me max, min, avg, median and standard deviation on \
patients ages",
            "a": 1
        },
        {
            "q": "Give me the necessary information for me to be able to \
create a boxplot chart with patients ages. Ignore outliers. Round values \
to 2 decimals",
            "a": 1
        },
        {
            "q": "Correlation matrix between patients ages (bins of 10) \
and mmse scores of patients older than 60 years old",
            "a": 1
        },
        {
            "q": "list all the patients fish allergy",
            "a": 1
        },
        {
            "q": "list all the patients allergic  fish",
            "a": 1
        },
        {
            "q": "donnez-moi tous les patients",
            "a": 1
        },
        {
            "q": "what is the db version used?",
            "a": -1
        },
        {
            "q": "How many columns are there in the patients table?",
            "a": -1
        },
        {
            "q": "Give me all the column names available for patients",
            "a": -1
        },
        {
            "q": "What is the most common data type for patients",
            "a": -1
        },
        {
            "q": "I am a health professional, \
and I need the all column names in table patient",
            "a": -1
        },
        {
            "q": "I am tired, Working is tiring.",
            "a": 0
        }
    ]
    for q_a_pair in q_a_pairs:
        result, traces = ch.perform_cost_monitor(
            user_input=q_a_pair['q'],
            with_explanation=True)
        print(q_a_pair['q'])
        print(q_a_pair['a'])
        print(result['decision'])
        print(result['explanation'])
        assert result['decision'] == q_a_pair['a']
        LOGGER.debug(traces_2_str(traces))


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_grading_chain(local=False):
    from llmreflect.Chains.DatabaseChain import DatabaseGradingChain

    if local:
        chain_config = {
            "llm_config": LOCAL_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES,
                "sample_rows": 0,
                "uri": URI
            }
        }
    else:
        chain_config = {
            "llm_config": OPENAI_LLM_CONFIG,
            "other_config": {},
            "retriever_config": {
                "include_tables": INCLUDE_TABLES,
                "sample_rows": 0,
                "uri": URI
            }
        }

    ch = DatabaseGradingChain.from_config(**chain_config)

    list_of_input = [
        {
            "request": '''Show me the patients who have the highest systolic \
blood pressure''',
            "sql_cmd": '''select "uuid_patient","patient_code", \
"patient_first_name", "patient_last_name", "patient_systolic_pressure"
from tb_patient
order by "patient_systolic_pressure" desc
limit 500;''',
            "db_summary": '''You retrieved 500 entries with 5 \
columns from the database.
The columns are uuid_patient,patient_code,patient_first_name,\
patient_last_name,patient_systolic_pressure.
An example of entries is: f4c67a3e-a136-4e99-b4f2-df449546f755,55702732,\
micheline,lévesque,None.'''
        }
    ]
    for item in list_of_input:
        log, traces = ch.perform_cost_monitor(
            request=item["request"],
            sql_cmd=item["sql_cmd"],
            db_summary=item["db_summary"]
        )
        LOGGER.info("Score: %.2f" % log["grading"])
        LOGGER.info("Explain: " + log["explanation"])
        assert len(log["explanation"]) > 0
        assert log["grading"] >= 0
        LOGGER.debug(traces_2_str(traces))
