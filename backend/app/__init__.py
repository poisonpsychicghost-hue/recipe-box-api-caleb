"""Recipe Box API — BE104 course skeleton.

A working Flask + SQLite CRUD API for recipes. It stores data perfectly —
and it trusts everyone. There is no authentication and no authorization yet.
That is the point: you will add both, lesson by lesson, in Units 2 and 3.
"""

from flask import Flask
from dotenv import load_dotenv
from .config import Config, DevelopmentConfig, TestingConfig
from .extensions import db

config_map = {
    "main": Config,
    "dev": DevelopmentConfig,
    "test": TestingConfig
}

def create_app(config_name):
    app = Flask(__name__)
    load_dotenv()
    config_class = config_map[config_name]
    config_obj = config_class()
    app.config.from_object(config_obj)

    # Use the config’s DATABASE_PATH as the runtime DATABASE
    app.config["DATABASE"] = app.config["DATABASE_PATH"]
    app.config["SQLALCHEMY_DATATBASE_URI"] = config_obj.SQLALCHEMY_DATABASE_URI
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(recipes_bp)
    print("DEBUG DATABASE_PATH:", repr(app.config.get("DATABASE_PATH")))
    print("DEBUG ABSOLUTE_DATABASE_PATH:", repr(app.config.get("ABSOLUTE_DATABASE_PATH", None)))
    print("DEBUG ORM URI:", repr(app.config.get("SQLALCHEMY_DATABASE_URI")))


    return app
def create_app_dev():
    # or "main" if that's your usual config name
    return create_app("dev")

from .routes.auth import auth_bp
from .routes.recipes import recipes_bp
