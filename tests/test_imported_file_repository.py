import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.model.imported_file import NewImportedFile
from my_fitness_app.model.imported_file_repository import (
    create_imported_file,
    get_imported_file,
    get_imported_file_by_hash,
    list_imported_files,
    update_import_status,
)


class TestImportedFileRepository(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        initialize_database(self.database_path)

    def test_create_and_get_imported_file(self):
        created = create_imported_file(
            self.database_path,
            NewImportedFile(
                original_filename="activity.csv",
                stored_path="instance/uploads/abc123.csv",
                file_hash="abc123",
                file_type="csv",
            ),
        )

        loaded = get_imported_file(self.database_path, created.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, created.id)
        self.assertEqual(loaded.original_filename, "activity.csv")
        self.assertEqual(loaded.stored_path, "instance/uploads/abc123.csv")
        self.assertEqual(loaded.file_hash, "abc123")
        self.assertEqual(loaded.file_type, "csv")
        self.assertEqual(loaded.import_status, "not_imported")
        self.assertIsNone(loaded.import_error_message)
        self.assertTrue(loaded.imported_at)
        self.assertTrue(loaded.created_at)
        self.assertTrue(loaded.updated_at)

    def test_list_imported_files_orders_newest_first(self):
        first = create_imported_file(
            self.database_path,
            NewImportedFile(
                original_filename="first.csv",
                stored_path="instance/uploads/111.csv",
                file_hash="111",
                file_type="csv",
            ),
        )
        second = create_imported_file(
            self.database_path,
            NewImportedFile(
                original_filename="second.gpx",
                stored_path="instance/uploads/222.gpx",
                file_hash="222",
                file_type="gpx",
            ),
        )

        imported_files = list_imported_files(self.database_path)

        self.assertEqual(
            [imported_file.id for imported_file in imported_files],
            [second.id, first.id],
        )

    def test_get_by_hash_returns_existing_imported_file(self):
        created = create_imported_file(
            self.database_path,
            NewImportedFile(
                original_filename="activity.tcx",
                stored_path="instance/uploads/hash.tcx",
                file_hash="hash",
                file_type="tcx",
            ),
        )

        loaded = get_imported_file_by_hash(self.database_path, "hash")

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, created.id)

    def test_missing_imported_file_returns_none(self):
        self.assertIsNone(get_imported_file(self.database_path, 999))
        self.assertIsNone(get_imported_file_by_hash(self.database_path, "missing"))

    def test_update_import_status_updates_existing_file(self):
        created = create_imported_file(
            self.database_path,
            NewImportedFile(
                original_filename="activity.csv",
                stored_path="instance/uploads/hash.csv",
                file_hash="hash",
                file_type="csv",
            ),
        )

        updated = update_import_status(
            self.database_path,
            created.id,
            "partial_failure",
            "Row 3: bad duration",
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated.import_status, "partial_failure")
        self.assertEqual(updated.import_error_message, "Row 3: bad duration")

    def test_update_import_status_returns_none_for_missing_file(self):
        updated = update_import_status(
            self.database_path,
            999,
            "failed",
            "Missing file",
        )

        self.assertIsNone(updated)
