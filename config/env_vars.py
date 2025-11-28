import os
from dotenv import load_dotenv

load_dotenv()

CARPETA_CSV = os.getenv("CARPETA_CSV")
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
ETL_OUTPUT_FILE = os.getenv("ETL_OUTPUT_FILE")

for var_name, var_value in [
    ("CARPETA_CSV", CARPETA_CSV),
    ("SQL_SERVER", SQL_SERVER),
    ("SQL_DATABASE", SQL_DATABASE),
    ("ETL_OUTPUT_FILE", ETL_OUTPUT_FILE)
]:
    if not var_value:
        raise ValueError(f"No se ha definido {var_name} en el .env")
