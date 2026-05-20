import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.app import create_app
from my_fitness_app.config import AppConfig
from my_fitness_app.model.workout import NewWorkout
from my_fitness_app.model.workout_repository import create_workout as create_workout_record
from my_fitness_app.services.workout_service import create_workout


class TestWorkoutRoutes(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        self.app = create_app(
            AppConfig(
                project_name="Test Project",
                database_path=self.database_path,
            )
        )
        self.client = self.app.test_client()

    def test_workout_list_shows_empty_state(self):
        response = self.client.get("/workouts/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("עדיין אין אימונים שמורים.".encode(), response.data)

    def test_workout_list_shows_existing_workouts(self):
        create_workout(
            self.database_path,
            {
                "workout_date": "2026-05-20",
                "workout_type": "Walking",
                "duration_minutes": "45",
                "notes": "",
            },
        )

        response = self.client.get("/workouts/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"2026-05-20", response.data)
        self.assertIn(b"Walking", response.data)
        self.assertIn("טבלת אימונים חכמה".encode(), response.data)
        self.assertIn("45 דק׳ (ידני)".encode(), response.data)

    def test_workout_table_renders_structured_garmin_metrics(self):
        create_workout_record(
            self.database_path,
            NewWorkout(
                workout_date="2026-05-20",
                workout_type="Running",
                duration_minutes=40,
                notes="Distance meters: 999999.00",
                source="garmin_tcx",
                start_time="2026-05-20T06:45:00Z",
                duration_seconds=2400,
                distance_meters=6200,
                calories=410,
                average_heart_rate=146,
                max_heart_rate=173,
            ),
        )

        response = self.client.get("/workouts/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"06:45", response.data)
        self.assertIn(b"Garmin TCX", response.data)
        self.assertIn("40 דק׳ (מקובץ Garmin)".encode(), response.data)
        self.assertIn("6.20 ק״מ".encode(), response.data)
        self.assertIn(b"410", response.data)
        self.assertIn(b"146", response.data)
        self.assertIn(b"173", response.data)
        self.assertNotIn(b"999999", response.data)

    def test_workout_table_shows_missing_metrics_as_dash(self):
        create_workout(
            self.database_path,
            {
                "workout_date": "2026-05-20",
                "workout_type": "Mobility",
                "duration_minutes": "",
                "notes": "",
            },
        )

        response = self.client.get("/workouts/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Mobility", response.data)
        self.assertIn("ידני".encode(), response.data)
        self.assertGreaterEqual(response.data.count(b">-<"), 5)

    def test_new_workout_page_shows_form(self):
        response = self.client.get("/workouts/new")

        self.assertEqual(response.status_code, 200)
        self.assertIn("הוספת אימון".encode(), response.data)
        self.assertIn(b'name="workout_date"', response.data)
        self.assertIn(b'name="workout_type"', response.data)

    def test_post_valid_workout_redirects_to_detail(self):
        response = self.client.post(
            "/workouts/",
            data={
                "workout_date": "2026-05-20",
                "workout_type": "Walking",
                "duration_minutes": "45",
                "notes": "Easy pace",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.headers["Location"], r"/workouts/\d+$")

        detail_response = self.client.get(response.headers["Location"])
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn(b"Walking", detail_response.data)
        self.assertIn(b"Easy pace", detail_response.data)
        self.assertIn("אימון כוח".encode(), detail_response.data)

    def test_post_invalid_workout_returns_form_with_errors(self):
        response = self.client.post(
            "/workouts/",
            data={
                "workout_date": "",
                "workout_type": "",
                "duration_minutes": "0",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("חובה להזין תאריך אימון.".encode(), response.data)
        self.assertIn("חובה להזין סוג אימון.".encode(), response.data)
        self.assertIn("משך האימון חייב להיות מספר שלם חיובי.".encode(), response.data)

    def test_missing_workout_returns_404(self):
        response = self.client.get("/workouts/999")

        self.assertEqual(response.status_code, 404)

    def test_workout_detail_shows_strength_section_and_existing_sets(self):
        workout = create_workout(
            self.database_path,
            {
                "workout_date": "2026-05-20",
                "workout_type": "Gym",
                "duration_minutes": "45",
                "notes": "",
            },
        )
        self.client.post(
            f"/workouts/{workout.id}/strength-sets",
            data={
                "exercise_name": "Squat",
                "reps": "5",
                "weight_kg": "80",
                "perceived_effort": "8",
                "notes": "Heavy",
            },
        )

        response = self.client.get(f"/workouts/{workout.id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("אימון כוח".encode(), response.data)
        self.assertIn(b"Squat", response.data)
        self.assertIn(b"80.0", response.data)
        self.assertIn("400.00 ק״ג".encode(), response.data)

    def test_workout_table_shows_strength_summary(self):
        workout = create_workout(
            self.database_path,
            {
                "workout_date": "2026-05-20",
                "workout_type": "Gym",
                "duration_minutes": "45",
                "notes": "",
            },
        )
        self.client.post(
            f"/workouts/{workout.id}/strength-sets",
            data={
                "exercise_name": "Squat",
                "reps": "5",
                "weight_kg": "80",
                "perceived_effort": "",
                "notes": "",
            },
        )

        response = self.client.get("/workouts/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("1 תרגילים · 1 סטים · 5 חזרות · 400.00 ק״ג".encode(), response.data)

    def test_workout_detail_organizes_garmin_metrics_and_source_info(self):
        workout = create_workout_record(
            self.database_path,
            NewWorkout(
                workout_date="2026-05-20",
                workout_type="Running",
                duration_minutes=40,
                notes=None,
                source="garmin_gpx",
                start_time="2026-05-20T06:45:00Z",
                end_time="2026-05-20T07:25:00Z",
                duration_seconds=2400,
                distance_meters=6200,
                calories=410,
                average_heart_rate=146,
                max_heart_rate=173,
                external_activity_id="activity-1",
            ),
        )

        response = self.client.get(f"/workouts/{workout.id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("פרטים בסיסיים".encode(), response.data)
        self.assertIn("מדדי Garmin".encode(), response.data)
        self.assertIn("מקור וייבוא".encode(), response.data)
        self.assertIn(b"Garmin GPX", response.data)
        self.assertIn(b"activity-1", response.data)
        self.assertIn("6.20 ק״מ".encode(), response.data)
        self.assertIn("40 דק׳ (מקובץ Garmin)".encode(), response.data)

    def test_post_valid_strength_set_creates_record_and_redirects(self):
        workout = create_workout(
            self.database_path,
            {
                "workout_date": "2026-05-20",
                "workout_type": "Gym",
                "duration_minutes": "",
                "notes": "",
            },
        )

        response = self.client.post(
            f"/workouts/{workout.id}/strength-sets",
            data={
                "exercise_name": "Bench Press",
                "reps": "8",
                "weight_kg": "60",
                "perceived_effort": "7",
                "notes": "Solid",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.headers["Location"], rf"/workouts/{workout.id}$")

        detail_response = self.client.get(response.headers["Location"])
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn(b"Bench Press", detail_response.data)
        self.assertIn(b"Solid", detail_response.data)

    def test_post_valid_strength_set_reuses_existing_exercise(self):
        workout = create_workout(
            self.database_path,
            {
                "workout_date": "2026-05-20",
                "workout_type": "Gym",
                "duration_minutes": "",
                "notes": "",
            },
        )
        self.client.post(
            f"/workouts/{workout.id}/strength-sets",
            data={
                "exercise_name": "Bench   Press",
                "reps": "8",
                "weight_kg": "60",
                "perceived_effort": "",
                "notes": "",
            },
        )

        response = self.client.post(
            f"/workouts/{workout.id}/strength-sets",
            data={
                "exercise_name": " bench press ",
                "reps": "6",
                "weight_kg": "",
                "perceived_effort": "",
                "notes": "",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.count(b"Bench   Press"), 1)
        self.assertIn(b">2<", response.data)

    def test_post_invalid_strength_set_returns_detail_with_errors(self):
        workout = create_workout(
            self.database_path,
            {
                "workout_date": "2026-05-20",
                "workout_type": "Gym",
                "duration_minutes": "",
                "notes": "",
            },
        )

        response = self.client.post(
            f"/workouts/{workout.id}/strength-sets",
            data={
                "exercise_name": "",
                "reps": "0",
                "weight_kg": "-1",
                "perceived_effort": "11",
                "notes": "Keep this",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("חובה להזין שם תרגיל.".encode(), response.data)
        self.assertIn("חובה להזין מספר חזרות חיובי.".encode(), response.data)
        self.assertIn("משקל חייב להיות מספר לא שלילי.".encode(), response.data)
        self.assertIn("מאמץ נתפס חייב להיות מספר שלם בין 1 ל-10.".encode(), response.data)
        self.assertIn(b"Keep this", response.data)

    def test_post_strength_set_for_missing_workout_returns_404(self):
        response = self.client.post(
            "/workouts/999/strength-sets",
            data={
                "exercise_name": "Squat",
                "reps": "5",
                "weight_kg": "",
                "perceived_effort": "",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 404)
