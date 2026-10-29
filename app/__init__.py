import os

from flask import Flask

from .database import Database
from .routes import bp


def create_app(db_path=None):
    app = Flask(__name__)
    app.secret_key = "medicare-dev-secret"
    Database.configure(db_path or os.environ.get("MEDICARE_DB", "medicare.db"))
    Database.getInstance()
    app.register_blueprint(bp)
    return app
