from flask import Blueprint, current_app, render_template

from my_fitness_app.services import dashboard_service

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.get("/")
def show_dashboard():
    summary = dashboard_service.get_workout_dashboard_summary(current_app.config["DATABASE_PATH"])
    return render_template("dashboard/index.html", summary=summary)
