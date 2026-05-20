from collections.abc import Mapping
from pathlib import Path

from my_fitness_app.model import meal_repository
from my_fitness_app.model.meal import Meal, NewMeal


class MealValidationError(ValueError):
    def __init__(self, errors: dict[str, str]):
        super().__init__("Invalid meal data")
        self.errors = errors


def create_meal(database_path: str | Path, form_data: Mapping[str, str]) -> Meal:
    meal = _validate_meal(form_data)
    return meal_repository.create_meal(database_path, meal)


def list_meals(database_path: str | Path) -> list[Meal]:
    return meal_repository.list_meals(database_path)


def get_meal(database_path: str | Path, meal_id: int) -> Meal | None:
    return meal_repository.get_meal(database_path, meal_id)


def update_meal(
    database_path: str | Path,
    meal_id: int,
    form_data: Mapping[str, str],
) -> Meal | None:
    meal = _validate_meal(form_data)
    return meal_repository.update_meal(database_path, meal_id, meal)


def _validate_meal(form_data: Mapping[str, str]) -> NewMeal:
    errors: dict[str, str] = {}

    meal_date = form_data.get("meal_date", "").strip()
    meal_type = form_data.get("meal_type", "").strip()
    description = form_data.get("description", "").strip()
    calories = _parse_optional_positive_int(
        form_data.get("calories", "").strip(),
        "calories",
        "קלוריות חייבות להיות מספר שלם חיובי.",
        errors,
    )
    protein_grams = _parse_optional_positive_float(
        form_data.get("protein_grams", "").strip(),
        "protein_grams",
        "חלבון חייב להיות מספר חיובי.",
        errors,
    )
    carbs_grams = _parse_optional_positive_float(
        form_data.get("carbs_grams", "").strip(),
        "carbs_grams",
        "פחמימות חייבות להיות מספר חיובי.",
        errors,
    )
    fat_grams = _parse_optional_positive_float(
        form_data.get("fat_grams", "").strip(),
        "fat_grams",
        "שומן חייב להיות מספר חיובי.",
        errors,
    )
    fiber_grams = _parse_optional_positive_float(
        form_data.get("fiber_grams", "").strip(),
        "fiber_grams",
        "סיבים חייבים להיות מספר חיובי.",
        errors,
    )
    notes = form_data.get("notes", "").strip() or None

    if not meal_date:
        errors["meal_date"] = "חובה להזין תאריך ארוחה."
    if not meal_type:
        errors["meal_type"] = "חובה להזין סוג ארוחה."
    if not description:
        errors["description"] = "חובה להזין תיאור ארוחה."

    if errors:
        raise MealValidationError(errors)

    return NewMeal(
        meal_date=meal_date,
        meal_type=meal_type,
        description=description,
        calories=calories,
        protein_grams=protein_grams,
        carbs_grams=carbs_grams,
        fat_grams=fat_grams,
        fiber_grams=fiber_grams,
        notes=notes,
    )


def _parse_optional_positive_int(
    value: str,
    field_name: str,
    error_message: str,
    errors: dict[str, str],
) -> int | None:
    if not value:
        return None

    try:
        parsed_value = int(value)
    except ValueError:
        errors[field_name] = error_message
        return None

    if parsed_value <= 0:
        errors[field_name] = error_message
        return None

    return parsed_value


def _parse_optional_positive_float(
    value: str,
    field_name: str,
    error_message: str,
    errors: dict[str, str],
) -> float | None:
    if not value:
        return None

    try:
        parsed_value = float(value)
    except ValueError:
        errors[field_name] = error_message
        return None

    if parsed_value <= 0:
        errors[field_name] = error_message
        return None

    return parsed_value
