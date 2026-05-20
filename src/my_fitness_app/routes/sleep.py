from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for

from my_fitness_app.services import sleep_service
from my_fitness_app.services.sleep_service import SleepValidationError

sleep_bp = Blueprint("sleep", __name__, url_prefix="/sleep")


@sleep_bp.get("/")
def list_sleep_logs():
    sleep_logs = sleep_service.list_sleep_logs(current_app.config["DATABASE_PATH"])
    return render_template("sleep/list.html", sleep_logs=sleep_logs)


@sleep_bp.get("/new")
def new_sleep_log():
    return render_template("sleep/new.html", errors={}, values={})


@sleep_bp.post("/")
def create_sleep_log():
    values = request.form.to_dict()
    try:
        sleep_log = sleep_service.create_sleep_log(current_app.config["DATABASE_PATH"], values)
    except SleepValidationError as error:
        return (
            render_template("sleep/new.html", errors=error.errors, values=values),
            400,
        )

    return redirect(url_for("sleep.get_sleep_log", sleep_log_id=sleep_log.id))


@sleep_bp.get("/<int:sleep_log_id>")
def get_sleep_log(sleep_log_id: int):
    sleep_log = sleep_service.get_sleep_log(current_app.config["DATABASE_PATH"], sleep_log_id)
    if sleep_log is None:
        abort(404)
    return render_template("sleep/detail.html", sleep_log=sleep_log)
