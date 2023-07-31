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


def grading_chain():
    from llmreflect.Tests.test_chains import test_grading_chain
    total_cost = 0.
    for i in range(50):
        traces = test_grading_chain(n_questions=20, budget=1.0)
        total_cost += traces.total_cost
        print(f"Total cost:{total_cost}")


'''
Create a {dialect} query in response to a user's request, adhering to these guidelines:

Include only needed columns; ensure they are not null.
For patients, include uuid_patient, full names, phone, and email.
Assume all database values are lowercase.
Limit records by the specified number, except for max/min values. Otherwise, use {max_present}.
Wrap column names in double quotes (").
Use CURRENT_DATE for "today."
Refer to {table_info} for the schema, and query only existing columns.
Example:
[request] list of patients with lowest mmse
[answer] SELECT "uuid_patient", ... ORDER BY "patient_mmse_score" ASC LIMIT 500;

Format:
[request] user's request
[answer] the {dialect} query you created

[request] {request}'''

bp = BasicPrompt.load_prompt_from_json_file("answer_database_short")
bp.hard_rules = '''\
Given a user's request, create a syntactically correct {dialect} query based on the following guidelines:

Columns: Query only the necessary columns, ensuring they are not null.
Patients: Include uuid_patient, full names, phone number, email address, and any selecting or ordering columns.
Case Sensitivity: Assume all values are in lowercase.
Limiting Records: Limit records by the number specified in the request or by {max_present}, except for questions about maximum or minimum values.
Delimited Identifiers: Wrap column names in double quotes (") to denote them as delimited identifiers.
'''
bp.soft_rules = '''\
Database Schema: Refer to the provided {table_info}, querying only existing columns and being mindful of their respective tables.
Date Handling: Use CURRENT_DATE function if the question involves "today".
'''
bp.in_context_learning = [
    {
        'request': 'Show me the oldest 3 person who used memantine with valid contact',
        'answer': '''\
SELECT "uuid_patient","patient_code", "patient_first_name", "patient_last_name", "patient_birth_date", array_agg("phones") FILTER (WHERE phones <> '{{}}') AS "phones",array_agg("patient_email") AS "patient_emails",array_agg("patient_visit_companion_phone") AS "patient_visit_companion_phones",array_agg("patient_visit_companion_email") AS "patient_visit_companion_emails",array_agg("patient_treatment") AS "patient_treatments", array_agg("medication_name") AS "medication_names"
FROM tb_patient
INNER JOIN tb_patient_medications
ON tb_patient.uuid_patient = tb_patient_medications.patient
WHERE ("medication_name" SIMILAR TO '%m(e|é)mantine%'
OR "patient_treatment" SIMILAR TO '%m(e|é)mantine%')
AND (array_length("phones", 1) > 0 OR "patient_email" IS NOT NULL OR "patient_visit_companion_phone" IS NOT NULL OR "patient_visit_companion_email" IS NOT NULL)
AND "patient_birth_date" IS NOT null
GROUP BY "uuid_patient", "patient_first_name", "patient_last_name", "patient_code", "patient_birth_date"
ORDER BY "patient_birth_date" ASC
LIMIT 3;'''
    },
]

bp.save_prompt()
print(bp.prompt_template.template)

from llmreflect.Tests.test_chains import test_database_answering_chain
test_database_answering_chain()

# from llmreflect.Retriever.DatabaseRetriever import DatabaseRetriever
# from decouple import config
# uri = f"postgresql+psycopg2://{config('DBUSERNAME')}:\
# {config('DBPASSWORD')}@{config('DBHOST')}:{config('DBPORT')}/postgres"

# retriever = DatabaseRetriever(
#     uri=uri,
#     include_tables=[
#             'tb_patient',
#             'tb_patients_allergies',
#             'tb_appointment_patients',
#             'tb_patient_mmse_and_moca_scores',
#             'tb_patient_medications'
#         ],
#     max_rows_return=500,
#     sample_rows=0
# )
# print(retriever.database.get_table_info_no_throw())
