import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST_BRNO", os.getenv("DB_HOST", "localhost"))
DB_PORT = int(os.getenv("POSTGRES_PORT_BRNO", os.getenv("DB_PORT", "5433")))

conn_params_brno = {
    "host": DB_HOST,
    "port": DB_PORT,
    "dbname": os.getenv("POSTGRES_DB_BRNO"),
    "user": os.getenv("POSTGRES_USER_BRNO"),
    "password": os.getenv("POSTGRES_PASSWORD_BRNO"),
}

CONN_BRNO = psycopg2.connect(**conn_params_brno)