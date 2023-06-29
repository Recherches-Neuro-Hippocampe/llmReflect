from Agents.QuestionAgent import PostgresqlQuestionAgent
from Retriever.DatabaseRetriever import DatabaseQuestionRetriever
from decouple import config


def run(n_questions=5):
    agent = PostgresqlQuestionAgent()
    uri = "postgresql+psycopg2://"\
        + f"postgres:{config('DBPASSWORD')}@localhost:5432/postgres"
    db_retriever = DatabaseQuestionRetriever(
        uri=uri,
        include_tables=[
            'tb_patient',
            'tb_patients_allergies',
            'tb_appointment_patients',
            'tb_patient_mmse_and_moca_scores',
            'tb_patient_medications'
        ],
        sample_rows=0
    )
    agent.equip_retriever(db_retriever)
    result = agent.predict_n_questions(n_questions=n_questions)
    return result
