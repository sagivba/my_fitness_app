import tempfile
from io import BytesIO
from pathlib import Path
from unittest import TestCase

from my_fitness_app.app import create_app
from my_fitness_app.config import AppConfig
from my_fitness_app.services.import_file_service import list_imported_files
from my_fitness_app.services.workout_service import list_workouts

FIXTURE_DIR = Path(__file__).parent / "fixtures"


class TestImportRoutes(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root_path = Path(self.temp_dir.name)
        self.database_path = self.root_path / "fitness.db"
        self.upload_directory = self.root_path / "uploads"
        self.app = create_app(
            AppConfig(
                project_name="Test Project",
                database_path=self.database_path,
                upload_directory=self.upload_directory,
            )
        )
        self.client = self.app.test_client()

    def test_home_page_links_to_imports(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("ייבוא קבצים".encode(), response.data)
        self.assertIn(b'href="/imports/"', response.data)

    def test_import_list_shows_empty_state(self):
        response = self.client.get("/imports/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("עדיין אין קבצי ייבוא שמורים.".encode(), response.data)

    def test_new_import_page_shows_upload_form(self):
        response = self.client.get("/imports/new")

        self.assertEqual(response.status_code, 200)
        self.assertIn("העלאת קובץ ייבוא".encode(), response.data)
        self.assertIn(b'enctype="multipart/form-data"', response.data)
        self.assertIn(b'name="file"', response.data)
        self.assertIn(b'accept=".csv,.tcx,.gpx,.fit"', response.data)

    def test_post_valid_import_redirects_to_detail_and_stores_file(self):
        response = self.client.post(
            "/imports/",
            data={"file": (BytesIO(b"activity data"), "activity.csv")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.headers["Location"], r"/imports/\d+$")

        imported_files = list_imported_files(self.database_path)
        self.assertEqual(len(imported_files), 1)
        imported_file = imported_files[0]
        self.assertEqual(imported_file.original_filename, "activity.csv")
        self.assertTrue(Path(imported_file.stored_path).exists())

        detail_response = self.client.get(response.headers["Location"])
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn(b"activity.csv", detail_response.data)
        self.assertIn(b"SHA-256", detail_response.data)
        self.assertIn("סטטוס ייבוא".encode(), detail_response.data)
        self.assertIn(b"not_imported", detail_response.data)
        self.assertIn("נוצר בתאריך".encode(), detail_response.data)
        self.assertIn(imported_file.created_at.encode(), detail_response.data)
        self.assertIn("עודכן בתאריך".encode(), detail_response.data)
        self.assertIn(imported_file.updated_at.encode(), detail_response.data)
        self.assertIn("ייבוא Garmin CSV".encode(), detail_response.data)

    def test_post_garmin_csv_import_runs_import_and_renders_summary(self):
        fixture_content = (FIXTURE_DIR / "garmin_supported.csv").read_bytes()
        upload_response = self.client.post(
            "/imports/",
            data={"file": (BytesIO(fixture_content), "garmin_supported.csv")},
            content_type="multipart/form-data",
        )
        imported_file = list_imported_files(self.database_path)[0]

        response = self.client.post(f"/imports/{imported_file.id}/garmin-csv-import")

        workouts = list_workouts(self.database_path)
        self.assertEqual(upload_response.status_code, 302)
        self.assertEqual(response.status_code, 200)
        self.assertIn("סיכום ייבוא".encode(), response.data)
        self.assertIn("שורות שנקראו".encode(), response.data)
        self.assertIn("אימונים שנוצרו".encode(), response.data)
        self.assertIn("כפילויות שדולגו".encode(), response.data)
        self.assertIn("שורות שגויות".encode(), response.data)
        self.assertIn("סטטוס סופי".encode(), response.data)
        self.assertIn(b"imported", response.data)
        self.assertEqual(len(workouts), 2)

    def test_post_garmin_csv_import_reports_malformed_rows(self):
        fixture_content = (FIXTURE_DIR / "garmin_malformed.csv").read_bytes()
        self.client.post(
            "/imports/",
            data={"file": (BytesIO(fixture_content), "garmin_malformed.csv")},
            content_type="multipart/form-data",
        )
        imported_file = list_imported_files(self.database_path)[0]

        response = self.client.post(f"/imports/{imported_file.id}/garmin-csv-import")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"failed", response.data)
        self.assertIn(b"Row 2", response.data)
        self.assertIn(b"Row 3", response.data)
        self.assertEqual(list_workouts(self.database_path), [])

    def test_post_garmin_csv_import_missing_file_returns_404(self):
        response = self.client.post("/imports/999/garmin-csv-import")

        self.assertEqual(response.status_code, 404)

    def test_post_duplicate_import_redirects_to_existing_detail(self):
        first_response = self.client.post(
            "/imports/",
            data={"file": (BytesIO(b"same content"), "first.gpx")},
            content_type="multipart/form-data",
        )
        second_response = self.client.post(
            "/imports/",
            data={"file": (BytesIO(b"same content"), "second.gpx")},
            content_type="multipart/form-data",
        )

        imported_files = list_imported_files(self.database_path)
        stored_files = list(self.upload_directory.iterdir())
        self.assertEqual(first_response.status_code, 302)
        self.assertEqual(second_response.status_code, 302)
        self.assertIn("?duplicate=1", second_response.headers["Location"])
        self.assertEqual(len(imported_files), 1)
        self.assertEqual(len(stored_files), 1)

        detail_response = self.client.get(second_response.headers["Location"])
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("הקובץ כבר נשמר בעבר. לא נוצר עותק נוסף.".encode(), detail_response.data)

    def test_post_rejected_extension_returns_form_with_error(self):
        response = self.client.post(
            "/imports/",
            data={"file": (BytesIO(b"not supported"), "activity.txt")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("סוג הקובץ אינו נתמך.".encode(), response.data)
        self.assertEqual(list_imported_files(self.database_path), [])
        self.assertFalse(self.upload_directory.exists())

    def test_post_missing_file_returns_form_with_error(self):
        response = self.client.post(
            "/imports/",
            data={},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("חובה לבחור קובץ לייבוא.".encode(), response.data)

    def test_detail_missing_import_returns_404(self):
        response = self.client.get("/imports/999")

        self.assertEqual(response.status_code, 404)
