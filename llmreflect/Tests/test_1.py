def test():
    print("pseudo test")
    assert True


# def test_grading_chain():

#     from llmreflect.Chains.DatabaseChain import DatabaseQnAGradingChain
#     from decouple import config
#     uri = f"postgresql+psycopg2://{config('DBUSERNAME')}:\
# {config('DBPASSWORD')}@{config('DBHOST')}:{config('DBPORT')}/postgres"

#     ch = DatabaseQnAGradingChain.from_config(
#         uri=uri,
#         include_tables=[
#             'tb_patient',
#             'tb_patients_allergies',
#             'tb_appointment_patients',
#             'tb_patient_mmse_and_moca_scores',
#             'tb_patient_medications'
#         ],
#         open_ai_key=config('OPENAI_API_KEY')
#     )
#     logs = ch.perform(n_question=1)
#     for log in logs:
#         print(log)
