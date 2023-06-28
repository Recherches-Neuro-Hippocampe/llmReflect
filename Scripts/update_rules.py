from Prompt import BasicPrompt

pt = BasicPrompt.BasicPrompt.load_prompt_from_json_file("postgressql")
pt.in_context_learning = '''
Request: give me a list of patients with lowest mmse
Answer: SELECT "uuid_patient",\
"patient_code","patient_first_name", "patient_last_name","patient_mmse_score",\
array_agg("phones") FILTER (WHERE phones <> '{{}}') AS "phones",\
array_agg("patient_email") AS "patient_emails",\
array_agg("patient_visit_companion_phone") \
AS "patient_visit_companion_phones",\
array_agg("patient_visit_companion_email") \
AS "patient_visit_companion_emails"
FROM tb_patient
INNER JOIN tb_patient_mmse_and_moca_scores
ON tb_patient.uuid_patient = tb_patient_mmse_and_moca_scores.patient
WHERE "patient_mmse_score" IS NOT null
GROUP by "uuid_patient", "patient_code","patient_first_name",\
"patient_last_name", "patient_mmse_score"
ORDER BY "patient_mmse_score" ASC
LIMIT 500;

Request: give me a list of overweight patients who toke donezepil
Answer: SELECT "uuid_patient","patient_code", "patient_first_name",\
"patient_last_name",\
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
ON tb_patient.uuid_patient = tb_patient_medications.patient
WHERE ("medication_name" SIMILAR TO '%don(e|é)p(e|é)zil%'
OR "patient_treatment" SIMILAR TO '%don(e|é)p(e|é)zil%')
AND "patient_bmi" IS NOT NULL
AND "patient_bmi" > 25
GROUP by "uuid_patient", "patient_code","patient_first_name",\
"patient_last_name"
LIMIT 500;

Request: Show me the oldest 3 person who used memantine \
with valid contact
Answer: SELECT "uuid_patient","patient_code", "patient_first_name", \
"patient_last_name", "patient_birth_date", \
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
ON tb_patient.uuid_patient = tb_patient_medications.patient
WHERE ("medication_name" SIMILAR TO '%m(e|é)mantine%'
OR "patient_treatment" SIMILAR TO '%m(e|é)mantine%')
AND (array_length("phones", 1) > 0 \
OR "patient_email" IS NOT NULL \
OR "patient_visit_companion_phone" IS NOT NULL \
OR "patient_visit_companion_email" IS NOT NULL)
AND "patient_birth_date" IS NOT null
GROUP BY "uuid_patient", "patient_first_name", "patient_last_name", \
"patient_code", "patient_birth_date"
ORDER BY "patient_birth_date" ASC
LIMIT 3;

Request: is the patient suzanne allergic to anything?
Answer: SELECT "uuid_patient", "patient_code", "patient_first_name",\
"patient_last_name",\
array_agg("allergy_name") AS "allergy_names"
FROM tb_patient
INNER JOIN tb_patients_allergies
ON tb_patient.uuid_patient = tb_patients_allergies.patient
WHERE "patient_first_name" = 'suzanne'
AND "allergy_name" IS NOT null
GROUP BY "uuid_patient", "patient_code","patient_first_name",\
"patient_last_name";
'''

pt.save_prompt()
