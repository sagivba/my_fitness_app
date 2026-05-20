import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(database_path: str | Path) -> sqlite3.Connection:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(database_path: str | Path) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    connection = connect(database_path)
    try:
        connection.executescript(schema)
    finally:
        connection.close()
