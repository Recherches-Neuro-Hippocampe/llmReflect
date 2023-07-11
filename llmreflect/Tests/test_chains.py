"""
Have not figured out a way to test current chains without database.
Future work...
"""
import os
import pytest
from llmreflect.Utils.log import get_logger

LOGGER = get_logger("test")


def in_workflow():
    return os.getenv("GITHUB_ACTIONS")\
        or os.getenv("TRAVIS") \
        or os.getenv("CIRCLECI") \
        or os.getenv("GITLAB_CI")


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_moderate_answer_fix_chain():

    from llmreflect.Chains.DatabaseChain import \
        DatabaseModerateNAnswerNFixChain
    from decouple import config

    uri = f"postgresql+psycopg2://{config('DBUSERNAME')}:\
{config('DBPASSWORD')}@{config('DBHOST')}:{config('DBPORT')}/postgres"

    ch = DatabaseModerateNAnswerNFixChain.from_config(
        uri=uri,
        include_tables=[
            'tb_patient',
            'tb_patients_allergies',
            'tb_appointment_patients',
            'tb_patient_mmse_and_moca_scores',
            'tb_patient_medications'
        ],
        open_ai_key=config('OPENAI_API_KEY')
    )

    result, _ = ch.perform_cost_monitor(
        user_input="give me a list of patients",
        explain_moderate=True)

    assert result['moderate_decision']

    result, _ = ch.perform_cost_monitor(
        user_input="Cats are the true rulers",
        explain_moderate=True)
    assert not result['moderate_decision']
    assert len(result['moderate_explanation']) > 0


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_moderate_chain():
    from llmreflect.Chains.ModerateChain import ModerateChain
    from decouple import config
    ch = ModerateChain.from_config(
        open_ai_key=config('OPENAI_API_KEY'),
        include_tables=[
            'tb_patient',
            'tb_patients_allergies',
            'tb_appointment_patients',
            'tb_patient_mmse_and_moca_scores',
            'tb_patient_medications'
        ]
    )
    result, _ = ch.perform_cost_monitor(
        user_input="give me a list of patients",
        with_explanation=True)
    assert result['decision']

    result, _ = ch.perform_cost_monitor(
        user_input="Cats are the true rulers",
        with_explanation=True)
    assert not result['decision']
    assert len(result['explanation']) > 0


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_grading_chain():
    from llmreflect.Chains.DatabaseChain import DatabaseQnAGradingChain
    from decouple import config
    import pandas as pd

    SAVE_LOG = False
    N_QUESTIONS = 12

    uri = f"postgresql+psycopg2://{config('DBUSERNAME')}:\
{config('DBPASSWORD')}@{config('DBHOST')}:{config('DBPORT')}/postgres"

    ch = DatabaseQnAGradingChain.from_config(
        uri=uri,
        include_tables=[
            'tb_patient',
            'tb_patients_allergies',
            'tb_appointment_patients',
            'tb_patient_mmse_and_moca_scores',
            'tb_patient_medications'
        ],
        a_max_output_tokens=512,
        g_max_output_tokens=256,
        open_ai_key=config('OPENAI_API_KEY')
    )
    logs, _ = ch.perform_cost_monitor(n_question=N_QUESTIONS)
    if SAVE_LOG:
        df = pd.DataFrame.from_records(logs)
        df.to_csv("self_grading.csv")
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


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_self_fix_chain():
    from llmreflect.Chains.DatabaseChain import DatabaseQuestionChain,\
        DatabaseAnswerChain, DatabaseSelfFixChain
    from decouple import config

    uri = f"postgresql+psycopg2://{config('DBUSERNAME')}:\
{config('DBPASSWORD')}@{config('DBHOST')}:{config('DBPORT')}/postgres"
    include_tables = [
        'tb_patient',
        'tb_patients_allergies',
        'tb_appointment_patients',
        'tb_patient_mmse_and_moca_scores',
        'tb_patient_medications'
    ]
    open_ai_key = config('OPENAI_API_KEY')
    max_output_tokens = 512

    q_ch = DatabaseQuestionChain.from_config(
        uri=uri,
        include_tables=include_tables,
        open_ai_key=open_ai_key,
        prompt_name="questionpostgresql",
        max_output_tokens=max_output_tokens,
        temperature=0.7,
        sample_rows=0
    )

    a_ch = DatabaseAnswerChain.from_config(
        uri=uri,
        include_tables=include_tables,
        open_ai_key=open_ai_key,
        prompt_name="postgresql",
        max_output_tokens=max_output_tokens,
        temperature=0.0,
        sample_rows=0,
        max_rows_return=500
    )

    self_fix_ch = DatabaseSelfFixChain.from_config(
        uri=uri,
        include_tables=include_tables,
        open_ai_key=open_ai_key,
        prompt_name="postgresqlfix",
        max_output_tokens=max_output_tokens,
        temperature=0.1,
        sample_rows=0,
        max_rows_return=500
    )

    questions, _ = q_ch.perform_cost_monitor(n_questions=5)
    for q in questions:
        cmd_summary, _ = a_ch.perform_cost_monitor(user_input=q)
        cmd = cmd_summary['cmd']
        summary = cmd_summary['summary']
        if "Error" not in summary:
            crooked_cmd = cmd.replace("tb_", "")
            crooked_summary = a_ch.retriever.retrieve_summary(
                llm_output=crooked_cmd)
            LOGGER.info("Question: " + q)
            LOGGER.info("Crooked command: " + crooked_cmd)
            LOGGER.info("Crooked summary: " + crooked_summary)
            result_dict, _ = self_fix_ch.perform_cost_monitor(
                user_input=q,
                history=crooked_cmd,
                his_error=crooked_summary
            )
            fixed_cmd = result_dict['cmd']
            fixed_summary = result_dict['summary']
            LOGGER.info("Fixed command: " + fixed_cmd)
            LOGGER.info("Fixed summary: " + fixed_summary)
            assert "error" not in fixed_summary.lower()


@pytest.mark.skipif(bool(in_workflow()),
                    reason="Only test database operations \
                    in local env")
def test_answerNfix_chain():

    from llmreflect.Chains.DatabaseChain import DatabaseAnswerNFixChain
    from decouple import config
    uri = f"postgresql+psycopg2://{config('DBUSERNAME')}:\
{config('DBPASSWORD')}@{config('DBHOST')}:{config('DBPORT')}/postgres"

    ch = DatabaseAnswerNFixChain.from_config(
        uri=uri,
        include_tables=[
            'tb_patient',
            'tb_patients_allergies',
            'tb_appointment_patients',
            'tb_patient_mmse_and_moca_scores',
            'tb_patient_medications'
        ],
        open_ai_key=config('OPENAI_API_KEY'),
        answer_chain_prompt_name="postgresql",
        fix_chain_prompt_name="postgresqlfix"
    )
    result_dict, _ = ch.perform_cost_monitor(
        user_input="give me a list overweight patients")
    assert len(result_dict['summary']) > 0
    assert type(result_dict['error']) is list
