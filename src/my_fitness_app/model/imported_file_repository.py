import sqlite3
from pathlib import Path

from my_fitness_app.model.database import connect
from my_fitness_app.model.imported_file import ImportedFile, NewImportedFile


def create_imported_file(
    database_path: str | Path,
    imported_file: NewImportedFile,
) -> ImportedFile:
    connection = connect(database_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO imported_file (
                original_filename, stored_path, file_hash, file_type
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                imported_file.original_filename,
                imported_file.stored_path,
                imported_file.file_hash,
                imported_file.file_type,
            ),
        )
        connection.commit()
        created_id = cursor.lastrowid
        if created_id is None:
            raise RuntimeError("Failed to create imported file")
        created_file = get_imported_file(database_path, created_id)
        if created_file is None:
            raise RuntimeError("Created imported file could not be loaded")
        return created_file
    finally:
        connection.close()


def list_imported_files(database_path: str | Path) -> list[ImportedFile]:
    connection = connect(database_path)
    try:
        rows = connection.execute(
            """
            SELECT id, original_filename, stored_path, file_hash, file_type,
                   imported_at, created_at, updated_at
            FROM imported_file
            ORDER BY imported_at DESC, id DESC
            """
        ).fetchall()
    finally:
        connection.close()

    return [_imported_file_from_row(row) for row in rows]


def get_imported_file(
    database_path: str | Path,
    imported_file_id: int,
) -> ImportedFile | None:
    connection = connect(database_path)
    try:
        row = connection.execute(
            """
            SELECT id, original_filename, stored_path, file_hash, file_type,
                   imported_at, created_at, updated_at
            FROM imported_file
            WHERE id = ?
            """,
            (imported_file_id,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None
    return _imported_file_from_row(row)


def get_imported_file_by_hash(
    database_path: str | Path,
    file_hash: str,
) -> ImportedFile | None:
    connection = connect(database_path)
    try:
        row = connection.execute(
            """
            SELECT id, original_filename, stored_path, file_hash, file_type,
                   imported_at, created_at, updated_at
            FROM imported_file
            WHERE file_hash = ?
            """,
            (file_hash,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None
    return _imported_file_from_row(row)


def _imported_file_from_row(row: sqlite3.Row) -> ImportedFile:
    return ImportedFile(
        id=row["id"],
        original_filename=row["original_filename"],
        stored_path=row["stored_path"],
        file_hash=row["file_hash"],
        file_type=row["file_type"],
        imported_at=row["imported_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
