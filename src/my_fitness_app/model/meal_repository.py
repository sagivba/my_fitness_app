import sqlite3
from pathlib import Path

from my_fitness_app.model.database import connect
from my_fitness_app.model.meal import Meal, NewMeal


def create_meal(database_path: str | Path, meal: NewMeal) -> Meal:
    connection = connect(database_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO meal (
                meal_date, meal_type, description, calories, protein_grams, carbs_grams,
                fat_grams, fiber_grams, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                meal.meal_date,
                meal.meal_type,
                meal.description,
                meal.calories,
                meal.protein_grams,
                meal.carbs_grams,
                meal.fat_grams,
                meal.fiber_grams,
                meal.notes,
            ),
        )
        connection.commit()
        created_id = cursor.lastrowid
        if created_id is None:
            raise RuntimeError("Failed to create meal")
        created_meal = get_meal(database_path, created_id)
        if created_meal is None:
            raise RuntimeError("Created meal could not be loaded")
        return created_meal
    finally:
        connection.close()


def list_meals(database_path: str | Path) -> list[Meal]:
    connection = connect(database_path)
    try:
        rows = connection.execute(
            """
            SELECT id, meal_date, meal_type, description, calories, protein_grams,
                   carbs_grams, fat_grams, fiber_grams, source, notes, created_at, updated_at
            FROM meal
            ORDER BY meal_date DESC, id DESC
            """
        ).fetchall()
    finally:
        connection.close()

    return [_meal_from_row(row) for row in rows]


def get_meal(database_path: str | Path, meal_id: int) -> Meal | None:
    connection = connect(database_path)
    try:
        row = connection.execute(
            """
            SELECT id, meal_date, meal_type, description, calories, protein_grams,
                   carbs_grams, fat_grams, fiber_grams, source, notes, created_at, updated_at
            FROM meal
            WHERE id = ?
            """,
            (meal_id,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None
    return _meal_from_row(row)


def update_meal(database_path: str | Path, meal_id: int, meal: NewMeal) -> Meal | None:
    connection = connect(database_path)
    try:
        cursor = connection.execute(
            """
            UPDATE meal
            SET meal_date = ?,
                meal_type = ?,
                description = ?,
                calories = ?,
                protein_grams = ?,
                carbs_grams = ?,
                fat_grams = ?,
                fiber_grams = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                meal.meal_date,
                meal.meal_type,
                meal.description,
                meal.calories,
                meal.protein_grams,
                meal.carbs_grams,
                meal.fat_grams,
                meal.fiber_grams,
                meal.notes,
                meal_id,
            ),
        )
        connection.commit()
        if cursor.rowcount == 0:
            return None
    finally:
        connection.close()

    return get_meal(database_path, meal_id)


def _meal_from_row(row: sqlite3.Row) -> Meal:
    return Meal(
        id=row["id"],
        meal_date=row["meal_date"],
        meal_type=row["meal_type"],
        description=row["description"],
        calories=row["calories"],
        protein_grams=row["protein_grams"],
        carbs_grams=row["carbs_grams"],
        fat_grams=row["fat_grams"],
        fiber_grams=row["fiber_grams"],
        source=row["source"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
