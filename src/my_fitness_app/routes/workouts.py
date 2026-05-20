from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for

from my_fitness_app.services import workout_service
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
    return render_template("workouts/detail.html", workout=workout)
