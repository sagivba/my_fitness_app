from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for

from my_fitness_app.services import strength_service, workout_service
from my_fitness_app.services.strength_service import (
    StrengthValidationError,
    StrengthWorkoutNotFoundError,
)
from my_fitness_app.services.workout_service import WorkoutValidationError

workouts_bp = Blueprint("workouts", __name__, url_prefix="/workouts")


@workouts_bp.get("/")
def list_workouts():
    workouts = workout_service.list_workouts(current_app.config["DATABASE_PATH"])
    return render_template("workouts/list.html", workouts=workouts)


@workouts_bp.get("/new")
def new_workout():
    return render_template("workouts/new.html", errors={}, values={})


@workouts_bp.post("/")
def create_workout():
    values = request.form.to_dict()
    try:
        workout = workout_service.create_workout(current_app.config["DATABASE_PATH"], values)
    except WorkoutValidationError as error:
        return (
            render_template("workouts/new.html", errors=error.errors, values=values),
            400,
        )

    return redirect(url_for("workouts.get_workout", workout_id=workout.id))


@workouts_bp.get("/<int:workout_id>")
def get_workout(workout_id: int):
    workout = workout_service.get_workout(current_app.config["DATABASE_PATH"], workout_id)
    if workout is None:
        abort(404)
    return _render_workout_detail(workout)


@workouts_bp.post("/<int:workout_id>/strength-sets")
def create_strength_set(workout_id: int):
    values = request.form.to_dict()
    try:
        strength_service.add_strength_set(
            current_app.config["DATABASE_PATH"],
            workout_id,
            values,
        )
    except StrengthWorkoutNotFoundError:
        abort(404)
    except StrengthValidationError as error:
        workout = workout_service.get_workout(current_app.config["DATABASE_PATH"], workout_id)
        if workout is None:
            abort(404)
        return (
            _render_workout_detail(
                workout,
                strength_errors=error.errors,
                strength_values=values,
            ),
            400,
        )

    return redirect(url_for("workouts.get_workout", workout_id=workout_id))


def _render_workout_detail(
    workout,
    strength_errors: dict[str, str] | None = None,
    strength_values: dict[str, str] | None = None,
):
    exercises = strength_service.list_strength_exercises(
        current_app.config["DATABASE_PATH"],
        workout.id,
    )
    summary = strength_service.summarize_strength_exercises(exercises)
    return render_template(
        "workouts/detail.html",
        workout=workout,
        strength_exercises=exercises,
        strength_summary=summary,
        strength_errors=strength_errors or {},
        strength_values=strength_values or {},
    )
