from flask import Blueprint, current_app, render_template

from my_fitness_app.services.example_service import get_welcome_message

web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def index():
    message = get_welcome_message(current_app.config["PROJECT_NAME"])
    return render_template("index.html", message=message)
