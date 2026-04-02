from flask import Flask
from .config import Config
from .db import close_db
from .routes.main import main_bp
from .routes.auth import auth_bp
from .routes.api import api_bp
from .routes.admin import admin_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    app.teardown_appcontext(close_db)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,  url_prefix='/auth')
    app.register_blueprint(api_bp,   url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app