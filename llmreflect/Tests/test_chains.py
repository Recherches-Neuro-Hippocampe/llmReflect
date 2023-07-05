"""
Have not figured out a way to test current chains without database.
Future work...
"""
import os
import pytest


def in_workflow():
    return os.getenv("GITHUB_ACTIONS")\
        or os.getenv("TRAVIS") \
        or os.getenv("CIRCLECI") \
        or os.getenv("GITLAB_CI")


@pytest.mark.skipif(in_workflow(), reason="Only test database operations \
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
    result = ch.perform(user_input="give me a list of patients",
                        with_explanation="True")
    assert result['decision']

    result = ch.perform(user_input="Cats are the true rulers",
                        with_explanation="True")
    assert not result['decision']
    assert len(result['explanation']) > 0
    print(result['explanation'])


@pytest.mark.skipif(in_workflow(), reason="Only test database operations \
                    in local env")
def test_grading_chain():

    from llmreflect.Chains.DatabaseChain import DatabaseQnAGradingChain
    from decouple import config
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
        open_ai_key=config('OPENAI_API_KEY')
    )
    logs = ch.perform(n_question=5)
    for log in logs:
        print(log)
