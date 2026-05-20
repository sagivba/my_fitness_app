from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for

from my_fitness_app.services import daily_log_service
from my_fitness_app.services.daily_log_service import DailyLogValidationError

daily_logs_bp = Blueprint("daily_logs", __name__, url_prefix="/daily-logs")


@daily_logs_bp.get("/")
def list_daily_logs():
    daily_logs = daily_log_service.list_daily_logs(current_app.config["DATABASE_PATH"])
    return render_template("daily_logs/list.html", daily_logs=daily_logs)


@daily_logs_bp.get("/new")
def new_daily_log():
    return render_template("daily_logs/new.html", errors={}, values={})


@daily_logs_bp.post("/")
def create_daily_log():
    values = request.form.to_dict()
    try:
        daily_log = daily_log_service.create_daily_log(current_app.config["DATABASE_PATH"], values)
    except DailyLogValidationError as error:
        return (
            render_template("daily_logs/new.html", errors=error.errors, values=values),
            400,
        )

    return redirect(url_for("daily_logs.get_daily_log", daily_log_id=daily_log.id))


@daily_logs_bp.get("/<int:daily_log_id>")
def get_daily_log(daily_log_id: int):
    daily_log = daily_log_service.get_daily_log(current_app.config["DATABASE_PATH"], daily_log_id)
    if daily_log is None:
        abort(404)
    return render_template("daily_logs/detail.html", daily_log=daily_log)
