import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from my_fitness_app.model import imported_file_repository
from my_fitness_app.model.imported_file import ImportedFile, NewImportedFile
from my_fitness_app.utils.files import is_path_relative_to, sanitize_filename

ALLOWED_EXTENSIONS = {"csv", "tcx", "gpx", "fit"}


class ImportFileValidationError(ValueError):
    def __init__(self, errors: dict[str, str]):
        super().__init__("Invalid import file")
        self.errors = errors


@dataclass(frozen=True)
class ImportFileUploadResult:
    imported_file: ImportedFile
    is_duplicate: bool


def list_imported_files(database_path: str | Path) -> list[ImportedFile]:
    return imported_file_repository.list_imported_files(database_path)


def get_imported_file(
    database_path: str | Path,
    imported_file_id: int,
) -> ImportedFile | None:
    return imported_file_repository.get_imported_file(database_path, imported_file_id)


def update_import_status(
    database_path: str | Path,
    imported_file_id: int,
    import_status: str,
    import_error_message: str | None,
) -> ImportedFile | None:
    return imported_file_repository.update_import_status(
        database_path,
        imported_file_id,
        import_status,
        import_error_message,
    )


def upload_import_file(
    database_path: str | Path,
    upload_directory: str | Path,
    original_filename: str,
    file_stream: BinaryIO,
) -> ImportFileUploadResult:
    sanitized_filename = sanitize_filename(original_filename)
    file_type = _validate_filename(sanitized_filename)
    file_content = file_stream.read()
    file_hash = hashlib.sha256(file_content).hexdigest()

    existing_file = imported_file_repository.get_imported_file_by_hash(
        database_path,
        file_hash,
    )
    if existing_file is not None:
        return ImportFileUploadResult(imported_file=existing_file, is_duplicate=True)

    upload_path = Path(upload_directory)
    stored_path = upload_path / f"{file_hash}.{file_type}"
    if not is_path_relative_to(stored_path, upload_path):
        raise ImportFileValidationError({"file": "נתיב הקובץ אינו תקין."})

    upload_path.mkdir(parents=True, exist_ok=True)
    if not stored_path.exists():
        stored_path.write_bytes(file_content)

    imported_file = imported_file_repository.create_imported_file(
        database_path,
        NewImportedFile(
            original_filename=sanitized_filename,
            stored_path=str(stored_path),
            file_hash=file_hash,
            file_type=file_type,
        ),
    )
    return ImportFileUploadResult(imported_file=imported_file, is_duplicate=False)


def _validate_filename(filename: str) -> str:
    if not filename:
        raise ImportFileValidationError({"file": "חובה לבחור קובץ לייבוא."})

    if "." not in filename:
        raise ImportFileValidationError({"file": "סוג הקובץ אינו נתמך."})

    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ImportFileValidationError({"file": "סוג הקובץ אינו נתמך."})

    return extension
