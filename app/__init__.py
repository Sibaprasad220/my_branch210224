# app/__init__.py
from flask import Flask
from app.config.config import Config
from app.routes.routes import routes
from app.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Register routes blueprint after initializing db to avoid circular import
    app.register_blueprint(routes)

    return app
