import sqlite3
from pathlib import Path

from my_fitness_app.model.database import connect
from my_fitness_app.model.strength import (
    NewStrengthExercise,
    NewStrengthSet,
    StrengthExercise,
    StrengthSet,
)

STRENGTH_EXERCISE_SELECT_COLUMNS = """
    id, workout_id, exercise_name, exercise_order, notes, created_at, updated_at
"""

STRENGTH_SET_SELECT_COLUMNS = """
    id, strength_exercise_id, set_number, reps, weight_kg, perceived_effort, notes,
    created_at, updated_at
"""

STRENGTH_SET_JOIN_SELECT_COLUMNS = """
    strength_set.id, strength_set.strength_exercise_id, strength_set.set_number,
    strength_set.reps, strength_set.weight_kg, strength_set.perceived_effort,
    strength_set.notes, strength_set.created_at, strength_set.updated_at
"""


def create_exercise(
    database_path: str | Path,
    exercise: NewStrengthExercise,
) -> StrengthExercise:
    connection = connect(database_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO strength_exercise (
                workout_id, exercise_name, exercise_order, notes
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                exercise.workout_id,
                exercise.exercise_name,
                exercise.exercise_order,
                exercise.notes,
            ),
        )
        connection.commit()
        created_id = cursor.lastrowid
        if created_id is None:
            raise RuntimeError("Failed to create strength exercise")
        created_exercise = get_exercise(database_path, created_id)
        if created_exercise is None:
            raise RuntimeError("Created strength exercise could not be loaded")
        return created_exercise
    finally:
        connection.close()


def create_set(database_path: str | Path, strength_set: NewStrengthSet) -> StrengthSet:
    connection = connect(database_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO strength_set (
                strength_exercise_id, set_number, reps, weight_kg, perceived_effort, notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                strength_set.strength_exercise_id,
                strength_set.set_number,
                strength_set.reps,
                strength_set.weight_kg,
                strength_set.perceived_effort,
                strength_set.notes,
            ),
        )
        connection.commit()
        created_id = cursor.lastrowid
        if created_id is None:
            raise RuntimeError("Failed to create strength set")
        created_set = get_set(database_path, created_id)
        if created_set is None:
            raise RuntimeError("Created strength set could not be loaded")
        return created_set
    finally:
        connection.close()


def get_exercise(database_path: str | Path, exercise_id: int) -> StrengthExercise | None:
    connection = connect(database_path)
    try:
        row = connection.execute(
            f"""
            SELECT {STRENGTH_EXERCISE_SELECT_COLUMNS}
            FROM strength_exercise
            WHERE id = ?
            """,
            (exercise_id,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None
    return _exercise_from_row(row)


def get_set(database_path: str | Path, strength_set_id: int) -> StrengthSet | None:
    connection = connect(database_path)
    try:
        row = connection.execute(
            f"""
            SELECT {STRENGTH_SET_SELECT_COLUMNS}
            FROM strength_set
            WHERE id = ?
            """,
            (strength_set_id,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None
    return _set_from_row(row)


def list_exercises_for_workout(
    database_path: str | Path,
    workout_id: int,
) -> list[StrengthExercise]:
    connection = connect(database_path)
    try:
        exercise_rows = connection.execute(
            f"""
            SELECT {STRENGTH_EXERCISE_SELECT_COLUMNS}
            FROM strength_exercise
            WHERE workout_id = ?
            ORDER BY exercise_order ASC, id ASC
            """,
            (workout_id,),
        ).fetchall()

        set_rows = connection.execute(
            f"""
            SELECT {STRENGTH_SET_JOIN_SELECT_COLUMNS}
            FROM strength_set
            JOIN strength_exercise
              ON strength_exercise.id = strength_set.strength_exercise_id
            WHERE strength_exercise.workout_id = ?
            ORDER BY strength_exercise.exercise_order ASC,
                     strength_exercise.id ASC,
                     strength_set.set_number ASC,
                     strength_set.id ASC
            """,
            (workout_id,),
        ).fetchall()
    finally:
        connection.close()

    sets_by_exercise_id: dict[int, list[StrengthSet]] = {}
    for row in set_rows:
        strength_set = _set_from_row(row)
        sets_by_exercise_id.setdefault(strength_set.strength_exercise_id, []).append(strength_set)

    exercises = []
    for row in exercise_rows:
        exercise = _exercise_from_row(row)
        exercises.append(
            StrengthExercise(
                id=exercise.id,
                workout_id=exercise.workout_id,
                exercise_name=exercise.exercise_name,
                exercise_order=exercise.exercise_order,
                notes=exercise.notes,
                created_at=exercise.created_at,
                updated_at=exercise.updated_at,
                sets=tuple(sets_by_exercise_id.get(exercise.id, [])),
            )
        )
    return exercises


def next_exercise_order(database_path: str | Path, workout_id: int) -> int:
    connection = connect(database_path)
    try:
        row = connection.execute(
            """
            SELECT COALESCE(MAX(exercise_order), 0) + 1 AS next_order
            FROM strength_exercise
            WHERE workout_id = ?
            """,
            (workout_id,),
        ).fetchone()
    finally:
        connection.close()

    return int(row["next_order"])


def next_set_number(database_path: str | Path, exercise_id: int) -> int:
    connection = connect(database_path)
    try:
        row = connection.execute(
            """
            SELECT COALESCE(MAX(set_number), 0) + 1 AS next_number
            FROM strength_set
            WHERE strength_exercise_id = ?
            """,
            (exercise_id,),
        ).fetchone()
    finally:
        connection.close()

    return int(row["next_number"])


def _exercise_from_row(row: sqlite3.Row) -> StrengthExercise:
    return StrengthExercise(
        id=row["id"],
        workout_id=row["workout_id"],
        exercise_name=row["exercise_name"],
        exercise_order=row["exercise_order"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _set_from_row(row: sqlite3.Row) -> StrengthSet:
    return StrengthSet(
        id=row["id"],
        strength_exercise_id=row["strength_exercise_id"],
        set_number=row["set_number"],
        reps=row["reps"],
        weight_kg=row["weight_kg"],
        perceived_effort=row["perceived_effort"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
