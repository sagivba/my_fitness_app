from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for

from my_fitness_app.services import meal_service
from my_fitness_app.services.meal_service import MealValidationError

meals_bp = Blueprint("meals", __name__, url_prefix="/meals")


@meals_bp.get("/")
def list_meals():
    meals = meal_service.list_meals(current_app.config["DATABASE_PATH"])
    return render_template("meals/list.html", meals=meals)


@meals_bp.get("/new")
def new_meal():
    return render_template("meals/new.html", errors={}, values={})


@meals_bp.post("/")
def create_meal():
    values = request.form.to_dict()
    try:
        meal = meal_service.create_meal(current_app.config["DATABASE_PATH"], values)
    except MealValidationError as error:
        return (
            render_template("meals/new.html", errors=error.errors, values=values),
            400,
        )

    return redirect(url_for("meals.get_meal", meal_id=meal.id))


@meals_bp.get("/<int:meal_id>")
def get_meal(meal_id: int):
    meal = meal_service.get_meal(current_app.config["DATABASE_PATH"], meal_id)
    if meal is None:
        abort(404)
    return render_template("meals/detail.html", meal=meal)


@meals_bp.get("/<int:meal_id>/edit")
def edit_meal(meal_id: int):
    meal = meal_service.get_meal(current_app.config["DATABASE_PATH"], meal_id)
    if meal is None:
        abort(404)
    return render_template("meals/edit.html", meal=meal, errors={}, values={})


@meals_bp.post("/<int:meal_id>")
def update_meal(meal_id: int):
    values = request.form.to_dict()
    try:
        meal = meal_service.update_meal(current_app.config["DATABASE_PATH"], meal_id, values)
    except MealValidationError as error:
        existing_meal = meal_service.get_meal(current_app.config["DATABASE_PATH"], meal_id)
        if existing_meal is None:
            abort(404)
        return (
            render_template(
                "meals/edit.html",
                meal=existing_meal,
                errors=error.errors,
                values=values,
            ),
            400,
        )

    if meal is None:
        abort(404)

    return redirect(url_for("meals.get_meal", meal_id=meal.id))
