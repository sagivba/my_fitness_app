from dataclasses import dataclass


@dataclass(frozen=True)
class Meal:
    id: int
    meal_date: str
    meal_type: str
    description: str
    calories: int | None
    protein_grams: float | None
    carbs_grams: float | None
    fat_grams: float | None
    fiber_grams: float | None
    source: str
    notes: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class NewMeal:
    meal_date: str
    meal_type: str
    description: str
    calories: int | None
    protein_grams: float | None
    carbs_grams: float | None
    fat_grams: float | None
    fiber_grams: float | None
    notes: str | None
