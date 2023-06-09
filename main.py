from Prompt import BasicPrompt


hard = '''\
Given an input question, you should answer the question by\
creating a syntactically correct {dialect} query to run.

You must query only the columns that are needed to answer the question.

All columns used for selecting or odering must not be null.

When asking for patients, you must include full names, patient ID,\
phone number, email address.

The columns involved in selecting and ordering must be included too.

You should assume all values in the database are in lowercase.

Limit the number of returning records by the number specified in the question.\
If the question is about a maximum or a minimum value,\
do not limit, otherwise limit the number of returning by {max_present}.

Wrap each column name in double quotes (") to denote them as delimited \
identifiers. You should reply with a syntactically correct {dialect} \
query only.

The schema of the database is:
{table_info}
'''

soft = '''\
Pay attention to use only the column names you can see in the \
tables below. Be careful to not query for columns that do not exist. Also, \
pay attention to which column is in which table. Pay attention to use \
CURRENT_DATE function to get the current date, if the question involves \
"today".
'''

in_context = '''\
Request: give me a list of patients with lowest mmse
Answer: SELECT
"patient_code","patient_first_name", "patient_last_name","patient_mmse_score",\
array_agg("phones") FILTER (WHERE phones <> '{{}}') AS "phones",\
array_agg("patient_email") AS "patient_emails",\
array_agg("patient_visit_companion_phone") \
AS "patient_visit_companion_phones",\
array_agg("patient_visit_companion_email") \
AS "patient_visit_companion_emails"
FROM tb_patient
INNER JOIN tb_patient_mmse_and_moca_scores
ON tb_patient.id = tb_patient_mmse_and_moca_scores.patient_id
WHERE "patient_mmse_score" IS NOT null
GROUP by "patient_code","patient_first_name","patient_last_name", \
"patient_mmse_score"
ORDER BY "patient_mmse_score" ASC
LIMIT 500;

Request: give me a list of overweight patients who toke donezepil
Answer: SELECT "patient_code", "patient_first_name", "patient_last_name",\
array_agg("phones") FILTER (WHERE phones <> '{{}}') AS "phones",\
array_agg("patient_email") AS "patient_emails",\
array_agg("patient_visit_companion_phone") \
AS "patient_visit_companion_phones",\
array_agg("patient_visit_companion_email") \
AS "patient_visit_companion_emails",\
array_agg("patient_treatment") AS "patient_treatments",\
array_agg("medication_name") AS "medication_names",\
array_agg("patient_bmi") AS "patient_bmi"
FROM tb_patient
INNER JOIN tb_patient_medications
ON tb_patient.id = tb_patient_medications.patient_id
WHERE ("medication_name" SIMILAR TO '%don(e|é)p(e|é)zil%'
OR "patient_treatment" SIMILAR TO '%don(e|é)p(e|é)zil%')
AND "patient_bmi" IS NOT NULL
AND "patient_bmi" > 25
GROUP by "patient_code","patient_first_name","patient_last_name"
LIMIT 500;

Request: Show me the oldest 3 person who used memantine \
with valid contact
Answer: SELECT "patient_code", "patient_first_name", "patient_last_name", \
"patient_birth_date", \
array_agg("phones") FILTER (WHERE phones <> '{{}}') AS "phones",\
array_agg("patient_email") AS "patient_emails",\
array_agg("patient_visit_companion_phone") \
AS "patient_visit_companion_phones",\
array_agg("patient_visit_companion_email") \
AS "patient_visit_companion_emails",\
array_agg("patient_treatment") AS "patient_treatments", \
array_agg("medication_name") AS "medication_names"
FROM tb_patient
INNER JOIN tb_patient_medications
ON tb_patient.id = tb_patient_medications.patient_id
WHERE ("medication_name" SIMILAR TO '%m(e|é)mantine%'
OR "patient_treatment" SIMILAR TO '%m(e|é)mantine%')
AND (array_length("phones", 1) > 0 \
OR "patient_email" IS NOT NULL \
OR "patient_visit_companion_phone" IS NOT NULL \
OR "patient_visit_companion_email" IS NOT NULL)
AND "patient_birth_date" IS NOT null
GROUP BY "patient_first_name", "patient_last_name", "patient_code", \
"patient_birth_date"
ORDER BY "patient_birth_date" ASC
LIMIT 3;

Request: is the patient suzanne allergic to anything?
Answer: SELECT "patient_code", "patient_first_name", "patient_last_name",\
array_agg("allergy_name") AS "allergy_names"
FROM tb_patient
INNER JOIN tb_patients_allergies
ON tb_patient.id = tb_patients_allergies.patient_id
WHERE "patient_first_name" = 'suzanne'
AND "allergy_name" IS NOT null
GROUP BY "patient_code","patient_first_name", "patient_last_name";
'''

BasicPrompt.save_prompt(
    promptname="SQL",
    prompt_dict={
        "HARD": hard,
        "SOFT": soft,
        "INCONTEXT": in_context
    }
)
