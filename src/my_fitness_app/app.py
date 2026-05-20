from flask import Flask

from my_fitness_app.config import AppConfig
from my_fitness_app.routes.api import api_bp
from my_fitness_app.routes.web import web_bp


def create_app(config: AppConfig | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder="../../templates",
        static_folder="../../static",
    )

    app_config = config or AppConfig.from_env()
    app.config["PROJECT_NAME"] = app_config.project_name
    app.config["DATABASE_PATH"] = str(app_config.database_path)

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
