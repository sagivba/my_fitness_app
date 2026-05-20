from dataclasses import dataclass


@dataclass(frozen=True)
class ImportedFile:
    id: int
    original_filename: str
    stored_path: str
    file_hash: str
    file_type: str
    imported_at: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class NewImportedFile:
    original_filename: str
    stored_path: str
    file_hash: str
    file_type: str
