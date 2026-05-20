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
from my_fitness_app.services.garmin_gpx_import_service import (
    GarminGpxImportError,
    import_garmin_gpx,
    parse_gpx_file,
)
from my_fitness_app.services.workout_service import list_workouts

FIXTURE_DIR = Path(__file__).parent / "fixtures"


class TestGarminGpxImportService(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root_path = Path(self.temp_dir.name)
        self.database_path = self.root_path / "fitness.db"
        self.upload_directory = self.root_path / "uploads"
        self.upload_directory.mkdir()
        initialize_database(self.database_path)

    def test_valid_gpx_fixture_imports_expected_workout_fields(self):
        imported_file = self._create_imported_file_from_fixture("garmin_valid.gpx")

        result = import_garmin_gpx(self.database_path, imported_file.id)

        workouts = list_workouts(self.database_path)
        self.assertIsNotNone(result)
        self.assertEqual(result.rows_read, 3)
        self.assertEqual(result.workouts_created, 1)
        self.assertEqual(result.duplicate_rows_skipped, 0)
        self.assertEqual(result.import_status, IMPORT_STATUS_IMPORTED)
        self.assertEqual(result.imported_file.import_status, IMPORT_STATUS_IMPORTED)
        self.assertIsNone(result.imported_file.import_error_message)
        self.assertEqual(len(workouts), 1)
        self.assertEqual(workouts[0].workout_date, "2026-05-18")
        self.assertEqual(workouts[0].workout_type, "Walking")
        self.assertEqual(workouts[0].duration_minutes, 30)
        self.assertEqual(workouts[0].source, "garmin_gpx")
        self.assertIn("Garmin GPX start time: 07:30", workouts[0].notes)
        self.assertIn("Distance meters:", workouts[0].notes)
        self.assertIn("Point count: 3", workouts[0].notes)
        self.assertIn("Segment count: 1", workouts[0].notes)
        self.assertIn("Elevation gain meters: 4.00", workouts[0].notes)

    def test_gpx_multiple_track_segments_imports_segment_metadata(self):
        imported_file = self._create_imported_file_from_fixture("garmin_multi_segment.gpx")

        result = import_garmin_gpx(self.database_path, imported_file.id)

        workouts = list_workouts(self.database_path)
        self.assertIsNotNone(result)
        self.assertEqual(result.rows_read, 4)
        self.assertEqual(result.import_status, IMPORT_STATUS_IMPORTED)
        self.assertEqual(len(workouts), 1)
        self.assertEqual(workouts[0].workout_type, "Cycling")
        self.assertEqual(workouts[0].duration_minutes, 30)
        self.assertIn("Point count: 4", workouts[0].notes)
        self.assertIn("Segment count: 2", workouts[0].notes)

    def test_gpx_missing_times_updates_status_with_error(self):
        imported_file = self._create_imported_file_from_fixture("garmin_missing_times.gpx")

        result = import_garmin_gpx(self.database_path, imported_file.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.import_status, IMPORT_STATUS_FAILED)
        self.assertIn("timestamps", result.imported_file.import_error_message)
        self.assertEqual(list_workouts(self.database_path), [])

    def test_gpx_malformed_xml_updates_status_with_error(self):
        imported_file = self._create_imported_file_from_fixture("garmin_malformed.gpx")

        result = import_garmin_gpx(self.database_path, imported_file.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.import_status, IMPORT_STATUS_FAILED)
        self.assertIn("Malformed GPX XML", result.imported_file.import_error_message)
        self.assertEqual(list_workouts(self.database_path), [])

    def test_gpx_insufficient_data_updates_status_with_error(self):
        imported_file = self._create_imported_file_from_fixture("garmin_insufficient.gpx")

        result = import_garmin_gpx(self.database_path, imported_file.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.import_status, IMPORT_STATUS_FAILED)
        self.assertIn("at least two track points", result.imported_file.import_error_message)
        self.assertEqual(list_workouts(self.database_path), [])

    def test_gpx_duplicate_import_skips_existing_workout(self):
        imported_file = self._create_imported_file_from_fixture("garmin_valid.gpx")
        first_result = import_garmin_gpx(self.database_path, imported_file.id)

        second_result = import_garmin_gpx(self.database_path, imported_file.id)

        self.assertIsNotNone(first_result)
        self.assertIsNotNone(second_result)
        self.assertEqual(first_result.workouts_created, 1)
        self.assertEqual(second_result.workouts_created, 0)
        self.assertEqual(second_result.duplicate_rows_skipped, 1)
        self.assertEqual(second_result.import_status, IMPORT_STATUS_IMPORTED)
        self.assertEqual(len(list_workouts(self.database_path)), 1)

    def test_parse_gpx_file_rejects_missing_track(self):
        file_path = self.upload_directory / "empty.gpx"
        file_path.write_text("<gpx></gpx>", encoding="utf-8")

        with self.assertRaises(GarminGpxImportError) as context:
            parse_gpx_file(file_path)

        self.assertIn("track", str(context.exception))

    def test_import_missing_file_returns_none(self):
        self.assertIsNone(import_garmin_gpx(self.database_path, 999))

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
                file_type="gpx",
            ),
        )
