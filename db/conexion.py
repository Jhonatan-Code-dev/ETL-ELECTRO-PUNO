import pyodbc
from config.env_vars import SQL_SERVER, SQL_DATABASE

def get_sql_connection():
    encrypt_value = "no"
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        "Trusted_Connection=yes;"
        f"Encrypt={encrypt_value};"
    )
    return pyodbc.connect(connection_string, autocommit=False, unicode_results=True)
