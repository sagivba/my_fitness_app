import hashlib
import tempfile
from io import BytesIO
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.services.import_file_service import (
    ALLOWED_EXTENSIONS,
    ImportFileValidationError,
    get_imported_file,
    list_imported_files,
    upload_import_file,
)


class TestImportFileService(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root_path = Path(self.temp_dir.name)
        self.database_path = self.root_path / "fitness.db"
        self.upload_directory = self.root_path / "uploads"
        initialize_database(self.database_path)

    def test_allowed_extensions_are_limited_to_raw_activity_file_types(self):
        self.assertEqual(ALLOWED_EXTENSIONS, {"csv", "tcx", "gpx", "fit"})

    def test_upload_import_file_stores_file_by_sha256_and_metadata(self):
        file_content = b"activity data"
        expected_hash = hashlib.sha256(file_content).hexdigest()

        result = upload_import_file(
            self.database_path,
            self.upload_directory,
            "Morning Ride.GPX",
            BytesIO(file_content),
        )

        imported_file = result.imported_file
        stored_path = Path(imported_file.stored_path)
        self.assertFalse(result.is_duplicate)
        self.assertEqual(imported_file.original_filename, "Morning_Ride.gpx")
        self.assertEqual(imported_file.file_hash, expected_hash)
        self.assertEqual(imported_file.file_type, "gpx")
        self.assertEqual(stored_path, self.upload_directory / f"{expected_hash}.gpx")
        self.assertEqual(stored_path.read_bytes(), file_content)

    def test_upload_import_file_sanitizes_path_traversal_filename(self):
        result = upload_import_file(
            self.database_path,
            self.upload_directory,
            "../../secret/../activity.fit",
            BytesIO(b"fit data"),
        )

        imported_file = result.imported_file
        stored_path = Path(imported_file.stored_path)
        self.assertEqual(imported_file.original_filename, "activity.fit")
        self.assertEqual(stored_path.parent, self.upload_directory)
        self.assertTrue(stored_path.exists())
        self.assertFalse((self.root_path / "activity.fit").exists())

    def test_upload_import_file_rejects_unsupported_extension(self):
        with self.assertRaises(ImportFileValidationError) as context:
            upload_import_file(
                self.database_path,
                self.upload_directory,
                "activity.txt",
                BytesIO(b"not supported"),
            )

        self.assertEqual(context.exception.errors, {"file": "סוג הקובץ אינו נתמך."})
        self.assertFalse(self.upload_directory.exists())

    def test_upload_import_file_rejects_missing_filename(self):
        with self.assertRaises(ImportFileValidationError) as context:
            upload_import_file(
                self.database_path,
                self.upload_directory,
                "",
                BytesIO(b"content"),
            )

        self.assertEqual(context.exception.errors, {"file": "חובה לבחור קובץ לייבוא."})
        self.assertFalse(self.upload_directory.exists())

    def test_upload_import_file_detects_duplicate_hash_without_new_row_or_file(self):
        first_result = upload_import_file(
            self.database_path,
            self.upload_directory,
            "first.csv",
            BytesIO(b"same content"),
        )

        second_result = upload_import_file(
            self.database_path,
            self.upload_directory,
            "second.csv",
            BytesIO(b"same content"),
        )

        imported_files = list_imported_files(self.database_path)
        stored_files = list(self.upload_directory.iterdir())
        self.assertFalse(first_result.is_duplicate)
        self.assertTrue(second_result.is_duplicate)
        self.assertEqual(second_result.imported_file.id, first_result.imported_file.id)
        self.assertEqual(len(imported_files), 1)
        self.assertEqual(len(stored_files), 1)

    def test_get_imported_file_returns_none_for_missing_id(self):
        self.assertIsNone(get_imported_file(self.database_path, 999))
