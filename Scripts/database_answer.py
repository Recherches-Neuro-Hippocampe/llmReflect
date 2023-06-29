from Agents.PostgressqlAgent import PostgresqlAgent
from Retriever.DatabaseRetriever import DatabaseRetriever
from decouple import config


def run(request: str, return_cmd: bool):
    agent = PostgresqlAgent()
    uri = "postgresql+psycopg2://"\
        + f"postgres:{config('DBPASSWORD')}@localhost:5432/postgres"
    db_retriever = DatabaseRetriever(
        uri=uri,
        include_tables=[
            'tb_patient',
            'tb_patients_allergies',
            'tb_appointment_patients',
            'tb_patient_mmse_and_moca_scores',
            'tb_patient_medications'
        ],
        max_rows_return=500
    )
    agent.equip_retriever(db_retriever)
    result = agent.predict_db_summary(request, return_cmd=return_cmd)
    return result
