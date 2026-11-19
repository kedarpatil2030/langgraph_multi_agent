
import sqlite3
import requests

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "chinook.db"

CHINOOK_URL = (
    "https://raw.githubusercontent.com/lerocha/"
    "chinook-database/master/ChinookDatabase/"
    "DataSources/Chinook_Sqlite.sql"
)


def initialize_database():

    DATA_DIR.mkdir(exist_ok=True)

    if DB_PATH.exists():
        print("Chinook database already exists.")
        return

    print("Downloading Chinook database SQL...")

    response = requests.get(
        CHINOOK_URL,
        timeout=30
    )

    response.raise_for_status()

    sql_script = response.text

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.executescript(sql_script)
        connection.commit()
        print("Chinook database created successfully.")
    finally:
        connection.close()


def get_connection():

    return sqlite3.connect(DB_PATH)


def execute_query(query, params=()):

    connection = get_connection()

    try:
        connection.row_factory = sqlite3.Row

        cursor = connection.execute(query, params)

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    finally:
        connection.close()
