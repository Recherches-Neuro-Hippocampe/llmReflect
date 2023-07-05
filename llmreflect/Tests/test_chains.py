"""
Have not figured out a way to test current chains without database.
Future work...
"""


def test():
    print("pseudo test")
    assert True

# def test_question():

#     from llmreflect.Chains.DatabaseChain import DatabaseQuestionChain
#     from decouple import config
#     uri = f"postgresql+psycopg2://{config('DBUSERNAME')}:\
# {config('DBPASSWORD')}@{config('DBHOST')}:{config('DBPORT')}/postgres"

#     ch = DatabaseQuestionChain.from_config(
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

#     logs = ch.perform(n_questions=10)
#     for log in logs:
#         print(log)

# def test_sql():

#     from llmreflect.Chains.DatabaseChain import DatabaseAnswerChain
#     from decouple import config
#     uri = f"postgresql+psycopg2://{config('DBUSERNAME')}:\
# {config('DBPASSWORD')}@{config('DBHOST')}:{config('DBPORT')}/postgres"

#     ch = DatabaseAnswerChain.from_config(
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

#     log = ch.perform(user_input="Show me the oldest 3 person who used \
# memantine with valid contact",
#                       get_cmd=True,
#                       get_db=True,
#                       get_summary=True)
#     print(log)

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
#     logs = ch.perform(n_question=5)
#     for log in logs:
#         print(log)
