import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.model.imported_file import NewImportedFile
from my_fitness_app.model.imported_file_repository import create_imported_file
from my_fitness_app.services.garmin_csv_import_service import (
    IMPORT_STATUS_FAILED,
    IMPORT_STATUS_IMPORTED,
)
from my_fitness_app.services.garmin_tcx_import_service import (
    GarminTcxImportError,
    import_garmin_tcx,
    parse_tcx_file,
)
from my_fitness_app.services.workout_service import list_workouts

FIXTURE_DIR = Path(__file__).parent / "fixtures"


class TestGarminTcxImportService(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root_path = Path(self.temp_dir.name)
        self.database_path = self.root_path / "fitness.db"
        self.upload_directory = self.root_path / "uploads"
        self.upload_directory.mkdir()
        initialize_database(self.database_path)

    def test_valid_tcx_fixture_imports_expected_workout_fields(self):
        imported_file = self._create_imported_file_from_fixture("garmin_valid.tcx")

        result = import_garmin_tcx(self.database_path, imported_file.id)

        workouts = list_workouts(self.database_path)
        self.assertIsNotNone(result)
        self.assertEqual(result.rows_read, 1)
        self.assertEqual(result.workouts_created, 1)
        self.assertEqual(result.duplicate_rows_skipped, 0)
        self.assertEqual(result.import_status, IMPORT_STATUS_IMPORTED)
        self.assertEqual(result.imported_file.import_status, IMPORT_STATUS_IMPORTED)
        self.assertIsNone(result.imported_file.import_error_message)
        self.assertEqual(len(workouts), 1)
        self.assertEqual(workouts[0].workout_date, "2026-05-18")
        self.assertEqual(workouts[0].workout_type, "Running")
        self.assertEqual(workouts[0].duration_minutes, 30)
        self.assertEqual(workouts[0].source, "garmin_tcx")
        self.assertEqual(workouts[0].start_time, "2026-05-18T07:30:00Z")
        self.assertEqual(workouts[0].duration_seconds, 1800.0)
        self.assertEqual(workouts[0].distance_meters, 5000.0)
        self.assertEqual(workouts[0].calories, 320)
        self.assertEqual(workouts[0].average_heart_rate, 142)
        self.assertEqual(workouts[0].max_heart_rate, 168)
        self.assertEqual(workouts[0].external_activity_id, "2026-05-18T07:30:00Z")
        self.assertIn("Garmin TCX start time: 07:30", workouts[0].notes)
        self.assertIn("Distance meters: 5000.00", workouts[0].notes)
        self.assertIn("Calories: 320", workouts[0].notes)
        self.assertIn("Average heart rate bpm: 142", workouts[0].notes)
        self.assertIn("Max heart rate bpm: 168", workouts[0].notes)

    def test_tcx_missing_optional_hr_fields_imports_with_missing_metadata_note(self):
        imported_file = self._create_imported_file_from_fixture("garmin_missing_hr.tcx")

        result = import_garmin_tcx(self.database_path, imported_file.id)

        workouts = list_workouts(self.database_path)
        self.assertIsNotNone(result)
        self.assertEqual(result.import_status, IMPORT_STATUS_IMPORTED)
        self.assertEqual(len(workouts), 1)
        self.assertEqual(workouts[0].workout_type, "Walking")
        self.assertIsNone(workouts[0].average_heart_rate)
        self.assertIsNone(workouts[0].max_heart_rate)
        self.assertIn(
            "Missing optional fields: average heart rate, max heart rate",
            workouts[0].notes,
        )

    def test_tcx_malformed_xml_updates_status_with_error(self):
        imported_file = self._create_imported_file_from_fixture("garmin_malformed.tcx")

        result = import_garmin_tcx(self.database_path, imported_file.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.import_status, IMPORT_STATUS_FAILED)
        self.assertIn("Malformed TCX XML", result.imported_file.import_error_message)
        self.assertEqual(list_workouts(self.database_path), [])

    def test_tcx_unsupported_incomplete_structure_updates_status_with_error(self):
        imported_file = self._create_imported_file_from_fixture("garmin_unsupported.tcx")

        result = import_garmin_tcx(self.database_path, imported_file.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.import_status, IMPORT_STATUS_FAILED)
        self.assertIn("at least one Lap", result.imported_file.import_error_message)
        self.assertEqual(list_workouts(self.database_path), [])

    def test_tcx_duplicate_import_skips_existing_workout(self):
        imported_file = self._create_imported_file_from_fixture("garmin_valid.tcx")
        first_result = import_garmin_tcx(self.database_path, imported_file.id)

        second_result = import_garmin_tcx(self.database_path, imported_file.id)

        self.assertIsNotNone(first_result)
        self.assertIsNotNone(second_result)
        self.assertEqual(first_result.workouts_created, 1)
        self.assertEqual(second_result.workouts_created, 0)
        self.assertEqual(second_result.duplicate_rows_skipped, 1)
        self.assertEqual(second_result.import_status, IMPORT_STATUS_IMPORTED)
        self.assertEqual(len(list_workouts(self.database_path)), 1)

    def test_parse_tcx_file_rejects_missing_activity(self):
        file_path = self.upload_directory / "empty.tcx"
        file_path.write_text("<root></root>", encoding="utf-8")

        with self.assertRaises(GarminTcxImportError) as context:
            parse_tcx_file(file_path)

        self.assertIn("Activity", str(context.exception))

    def test_import_missing_file_returns_none(self):
        self.assertIsNone(import_garmin_tcx(self.database_path, 999))

    def _create_imported_file_from_fixture(self, fixture_name: str):
        source_path = FIXTURE_DIR / fixture_name
        stored_path = self.upload_directory / fixture_name
        shutil.copyfile(source_path, stored_path)
        return create_imported_file(
            self.database_path,
            NewImportedFile(
                original_filename=fixture_name,
                stored_path=str(stored_path),
                file_hash=fixture_name,
                file_type="tcx",
            ),
        )
