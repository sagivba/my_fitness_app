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
    IMPORT_STATUS_PARTIAL_FAILURE,
    GarminCsvImportError,
    import_garmin_csv,
    map_garmin_csv_headers,
    parse_garmin_csv_file,
)
from my_fitness_app.services.workout_service import list_workouts

FIXTURE_DIR = Path(__file__).parent / "fixtures"


class TestGarminCsvImportService(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root_path = Path(self.temp_dir.name)
        self.database_path = self.root_path / "fitness.db"
        self.upload_directory = self.root_path / "uploads"
        self.upload_directory.mkdir()
        initialize_database(self.database_path)

    def test_header_mapping_supports_documented_fixture_columns(self):
        header_mapping = map_garmin_csv_headers(
            ["activity_date", "start_time", "activity_type", "duration_minutes", "notes"]
        )

        self.assertEqual(header_mapping["workout_date"], "activity_date")
        self.assertEqual(header_mapping["start_time"], "start_time")
        self.assertEqual(header_mapping["workout_type"], "activity_type")
        self.assertEqual(header_mapping["duration_minutes"], "duration_minutes")
        self.assertEqual(header_mapping["notes"], "notes")

    def test_header_mapping_supports_optional_metric_columns(self):
        header_mapping = map_garmin_csv_headers(
            [
                "activity_date",
                "start_time",
                "activity_type",
                "duration_minutes",
                "distance_meters",
                "calories",
                "avg_hr",
                "max_hr",
                "activity_id",
            ]
        )

        self.assertEqual(header_mapping["distance_meters"], "distance_meters")
        self.assertEqual(header_mapping["calories"], "calories")
        self.assertEqual(header_mapping["average_heart_rate"], "avg_hr")
        self.assertEqual(header_mapping["max_heart_rate"], "max_hr")
        self.assertEqual(header_mapping["external_activity_id"], "activity_id")

    def test_header_mapping_supports_garmin_style_aliases(self):
        header_mapping = map_garmin_csv_headers(
            ["Activity Date", "Start Time", "Activity Type", "Duration Minutes"]
        )

        self.assertEqual(header_mapping["workout_date"], "Activity Date")
        self.assertEqual(header_mapping["start_time"], "Start Time")
        self.assertEqual(header_mapping["workout_type"], "Activity Type")
        self.assertEqual(header_mapping["duration_minutes"], "Duration Minutes")

    def test_header_mapping_rejects_missing_required_columns(self):
        with self.assertRaises(GarminCsvImportError) as context:
            map_garmin_csv_headers(["activity_date", "activity_type"])

        self.assertIn("duration_minutes", str(context.exception))
        self.assertIn("start_time", str(context.exception))

    def test_parse_supported_fixture_returns_valid_rows(self):
        parse_result = parse_garmin_csv_file(FIXTURE_DIR / "garmin_supported.csv")

        self.assertEqual(parse_result.rows_read, 2)
        self.assertEqual(parse_result.errors, [])
        self.assertEqual(len(parse_result.workout_rows), 2)
        self.assertEqual(parse_result.workout_rows[0].workout_date, "2026-05-18")
        self.assertEqual(parse_result.workout_rows[0].start_time, "07:30")
        self.assertEqual(parse_result.workout_rows[0].workout_type, "Walking")
        self.assertEqual(parse_result.workout_rows[0].duration_minutes, 45)
        self.assertEqual(parse_result.workout_rows[0].start_timestamp, "2026-05-18T07:30:00")
        self.assertEqual(parse_result.workout_rows[0].duration_seconds, 2700)
        self.assertEqual(parse_result.workout_rows[0].notes, "Morning walk")

    def test_parse_metric_fixture_returns_optional_structured_metrics(self):
        parse_result = parse_garmin_csv_file(FIXTURE_DIR / "garmin_metrics.csv")
        workout_row = parse_result.workout_rows[0]

        self.assertEqual(parse_result.errors, [])
        self.assertEqual(workout_row.start_timestamp, "2026-05-20T06:45:00")
        self.assertEqual(workout_row.end_time, "2026-05-20T07:25:00")
        self.assertEqual(workout_row.duration_seconds, 2400)
        self.assertEqual(workout_row.distance_meters, 6200.5)
        self.assertEqual(workout_row.calories, 410)
        self.assertEqual(workout_row.average_heart_rate, 146)
        self.assertEqual(workout_row.max_heart_rate, 173)
        self.assertEqual(workout_row.external_activity_id, "csv-activity-1")

    def test_parse_malformed_fixture_reports_row_errors(self):
        parse_result = parse_garmin_csv_file(FIXTURE_DIR / "garmin_malformed.csv")

        self.assertEqual(parse_result.rows_read, 2)
        self.assertEqual(len(parse_result.workout_rows), 0)
        self.assertEqual(len(parse_result.errors), 2)
        self.assertIn("Row 2: start_time must use HH:MM", parse_result.errors[0])
        self.assertIn("Row 3: duration_minutes must be a positive integer", parse_result.errors[1])

    def test_valid_fixture_import_creates_workouts_and_updates_status(self):
        imported_file = self._create_imported_file_from_fixture("garmin_supported.csv")

        result = import_garmin_csv(self.database_path, imported_file.id)

        workouts = list_workouts(self.database_path)
        self.assertIsNotNone(result)
        self.assertEqual(result.rows_read, 2)
        self.assertEqual(result.workouts_created, 2)
        self.assertEqual(result.duplicate_rows_skipped, 0)
        self.assertEqual(result.malformed_rows, 0)
        self.assertEqual(result.import_status, IMPORT_STATUS_IMPORTED)
        self.assertEqual(result.imported_file.import_status, IMPORT_STATUS_IMPORTED)
        self.assertIsNone(result.imported_file.import_error_message)
        self.assertEqual(len(workouts), 2)
        self.assertEqual(workouts[1].workout_date, "2026-05-18")
        self.assertEqual(workouts[1].workout_type, "Walking")
        self.assertEqual(workouts[1].duration_minutes, 45)
        self.assertEqual(workouts[1].start_time, "2026-05-18T07:30:00")
        self.assertEqual(workouts[1].duration_seconds, 2700)
        self.assertEqual(workouts[1].source, "garmin_csv")
        self.assertIn("Garmin CSV start time: 07:30", workouts[1].notes)

    def test_metric_fixture_import_stores_structured_metrics(self):
        imported_file = self._create_imported_file_from_fixture("garmin_metrics.csv")

        result = import_garmin_csv(self.database_path, imported_file.id)

        workouts = list_workouts(self.database_path)
        self.assertIsNotNone(result)
        self.assertEqual(result.import_status, IMPORT_STATUS_IMPORTED)
        self.assertEqual(len(workouts), 1)
        self.assertEqual(workouts[0].start_time, "2026-05-20T06:45:00")
        self.assertEqual(workouts[0].end_time, "2026-05-20T07:25:00")
        self.assertEqual(workouts[0].duration_seconds, 2400)
        self.assertEqual(workouts[0].distance_meters, 6200.5)
        self.assertEqual(workouts[0].calories, 410)
        self.assertEqual(workouts[0].average_heart_rate, 146)
        self.assertEqual(workouts[0].max_heart_rate, 173)
        self.assertEqual(workouts[0].external_activity_id, "csv-activity-1")

    def test_partial_malformed_import_creates_valid_rows_and_updates_status(self):
        imported_file = self._create_imported_file_from_fixture("garmin_partial_malformed.csv")

        result = import_garmin_csv(self.database_path, imported_file.id)

        workouts = list_workouts(self.database_path)
        self.assertIsNotNone(result)
        self.assertEqual(result.rows_read, 2)
        self.assertEqual(result.workouts_created, 1)
        self.assertEqual(result.malformed_rows, 1)
        self.assertEqual(result.import_status, IMPORT_STATUS_PARTIAL_FAILURE)
        self.assertEqual(result.imported_file.import_status, IMPORT_STATUS_PARTIAL_FAILURE)
        self.assertIn("Row 3", result.imported_file.import_error_message)
        self.assertEqual(len(workouts), 1)

    def test_failed_import_creates_no_workouts_and_updates_status(self):
        imported_file = self._create_imported_file_from_fixture("garmin_malformed.csv")

        result = import_garmin_csv(self.database_path, imported_file.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.rows_read, 2)
        self.assertEqual(result.workouts_created, 0)
        self.assertEqual(result.malformed_rows, 2)
        self.assertEqual(result.import_status, IMPORT_STATUS_FAILED)
        self.assertEqual(result.imported_file.import_status, IMPORT_STATUS_FAILED)
        self.assertIn("Row 2", result.imported_file.import_error_message)
        self.assertEqual(list_workouts(self.database_path), [])

    def test_duplicate_workout_detection_skips_existing_garmin_csv_rows(self):
        imported_file = self._create_imported_file_from_fixture("garmin_supported.csv")
        first_result = import_garmin_csv(self.database_path, imported_file.id)

        second_result = import_garmin_csv(self.database_path, imported_file.id)

        self.assertIsNotNone(first_result)
        self.assertIsNotNone(second_result)
        self.assertEqual(first_result.workouts_created, 2)
        self.assertEqual(second_result.workouts_created, 0)
        self.assertEqual(second_result.duplicate_rows_skipped, 2)
        self.assertEqual(second_result.import_status, IMPORT_STATUS_IMPORTED)
        self.assertEqual(len(list_workouts(self.database_path)), 2)

    def test_import_non_csv_file_updates_status_with_error(self):
        source_path = self.upload_directory / "activity.gpx"
        source_path.write_text("<gpx></gpx>", encoding="utf-8")
        imported_file = create_imported_file(
            self.database_path,
            NewImportedFile(
                original_filename="activity.gpx",
                stored_path=str(source_path),
                file_hash="activity-gpx",
                file_type="gpx",
            ),
        )

        result = import_garmin_csv(self.database_path, imported_file.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.import_status, IMPORT_STATUS_FAILED)
        self.assertIn("Only CSV", result.imported_file.import_error_message)

    def test_import_missing_file_returns_none(self):
        self.assertIsNone(import_garmin_csv(self.database_path, 999))

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
                file_type="csv",
            ),
        )
