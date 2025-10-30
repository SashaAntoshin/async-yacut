from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """Создаем приложение."""
    app = Flask(
        __name__, template_folder="../templates", static_folder="../static"
    )
    app.config.from_object("settings.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    from .api_views import api_bp
    from .error_handlers import init_error_handlers
    from .views import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    init_error_handlers(app)
    return app


app = create_app()
