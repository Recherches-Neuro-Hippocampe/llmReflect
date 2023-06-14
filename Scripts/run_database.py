from Agents.PostgressqlAgent import PostgresSQLAgent
from Retriever.DatabaseRetriever import DatabaseRetriever
from decouple import config


def run():
    agent = PostgresSQLAgent()
    uri = "postgresql+psycopg2://"\
        + f"postgres:{config('DBPASSWORD')}@localhost:5432/postgres"
    db_retrivever = DatabaseRetriever(
        uri=uri,
        include_tables=[
            'tb_patient',
            'tb_patients_allergies',
            'tb_appointment_patients',
            'tb_patient_mmse_and_moca_scores',
            'tb_patient_medications'
        ],
        max_rows_return=100
    )
    agent.equip_retriever(db_retrivever)
    agent.predict_retrieve_databse("give me 5 patients")
