"""Recipe Box API — BE104 course skeleton.

A working Flask + SQLite CRUD API for recipes. It stores data perfectly —
and it trusts everyone. There is no authentication and no authorization yet.
That is the point: you will add both, lesson by lesson, in Units 2 and 3.
"""


from functools import wraps
from flask import Flask, g, jsonify
from flask_cors import CORS
from .tools.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from .config import Config, DevelopmentConfig, TestingConfig
from .tools.databasegetter import get_db, close_db


config_map = {
    "main": Config,
    "dev": DevelopmentConfig,
    "test": TestingConfig
}

def create_app(config_name):
    app = Flask(__name__)
    load_dotenv()
    config_class = config_map[config_name]
    app.config.from_object(config_class)

    app.register_blueprint(auth_bp)
    app.register_blueprint(recipes_bp)

    app.teardown_appcontext(close_db)

    return app


from .routes.auth import auth_bp
from .routes.recipes import recipes_bp


def hello():
    return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})





if __name__ == "__main__":
    app.run(debug=True)
