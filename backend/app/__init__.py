"""Recipe Box API — BE104 course skeleton.

A working Flask + SQLite CRUD API for recipes. It stores data perfectly —
and it trusts everyone. There is no authentication and no authorization yet.
That is the point: you will add both, lesson by lesson, in Units 2 and 3.
"""

import sqlite3
from functools import wraps
from flask import Flask, g, jsonify, request, current_app
from flask_cors import CORS
from .security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import jwt
import datetime
from .config import Config, DevelopmentConfig, TestingConfig



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

    app.teardown_appcontext(close_db)
    #list
    app.add_url_rule(
        "/recipes",
        view_func=require_token(list_recipes),
        methods=["GET"],
    )
    #get
    app.add_url_rule(
        "/recipes/<int:recipe_id>",
        view_func=require_token(get_recipe),
        methods=["GET"],
    )
    #create
    app.add_url_rule(
        "/recipes",
        view_func=require_token(create_recipe),
        methods=["POST"],
    )
    #update
    app.add_url_rule(
        "/recipes/<int:recipe_id>",
        view_func=require_token(update_recipe),
        methods=["PATCH"],
    )
    #delete
    app.add_url_rule(
        "/recipes/<int:recipe_id>",
        view_func=require_token(delete_recipe),
        methods=["DELETE"],
    )

    return app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, 'recipes.db')


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

from .routes.auth import auth_bp

def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def recipe_to_dict(row):
    result = {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
        "owner_id": row["owner_id"],
    }

    # safely include owner_username if it’s present in this query
    if "owner_username" in row.keys():
        result["owner_username"] = row["owner_username"]

    return result

def require_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header[len("Bearer "):].strip()

        try:
            claims = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            g.user_id = claims.get("sub")
            g.role = claims.get("role")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token Has Expired. Please Log In."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)
    return wrapper



def hello():
    return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})



@require_token
def list_recipes():
    db = get_db()
    user_id = g.user_id
    role = g.role

    base_query = """
        SELECT
            r.id,
            r.title,
            r.ingredients,
            r.instructions,
            r.is_public,
            r.owner_id,
            u.username AS owner_username
        FROM recipes AS r
        JOIN users AS u ON r.owner_id = u.id
    """

    params = ()
    where_clauses = []

    if role == "admin":
        # admin sees everything
        query = base_query
    elif role == "guest":
        # guest: only public recipes
        where_clauses.append("r.is_public = 1")
        query = base_query + " WHERE " + " AND ".join(where_clauses)
    else:
        # regular user: public recipes OR their own (even if private)
        where_clauses.append("(r.is_public = 1 OR r.owner_id = ?)")
        params = (user_id,)
        query = base_query + " WHERE " + " AND ".join(where_clauses)

    rows = db.execute(query, params).fetchall()

    recipes = []
    for row in rows:
        recipes.append({
            "id": row["id"],
            "title": row["title"],
            "ingredients": row["ingredients"],
            "instructions": row["instructions"],
            "is_public": bool(row["is_public"]),
            "owner_id": row["owner_id"],
            "owner_username": row["owner_username"],
        })

    return jsonify(recipes), 200


@require_token
def get_recipe(recipe_id):
    user_id = g.user_id
    role = g.role
    db = get_db()
    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()
    if row is None:
        return jsonify({"error": "recipe not found"}), 404
    if role == "guest" and row["is_public"] == 0:
        return jsonify({"error": "Forbidden"}), 403
    if role == "admin":
        return jsonify(recipe_to_dict(row))
    if row["is_public"] == 0 and str(user_id) != str(row["owner_id"]):
        return jsonify({"error": "Forbidden"}), 403
   
      
    return jsonify(recipe_to_dict(row))



@require_token
def create_recipe():
    data = request.get_json(silent=True)
    if not data or not data.get("title") or not data.get("ingredients"):
        return jsonify({"error": "title and ingredients are required"}), 400

    user_id = g.user_id
    role = g.role
    if role == "guest":
        return jsonify({"error": "Guests Allowed Read-Only Access"})
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO recipes (title, ingredients, instructions, is_public, owner_id)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                data["title"],
                data["ingredients"],
                data.get("instructions", ""),
                1 if data.get("is_public", True) else 0,
                user_id,
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "a recipe with that title already exists"}), 409
    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return jsonify(recipe_to_dict(row)), 201



@require_token
def update_recipe(recipe_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400
    
    user_id = g.user_id
    role = g.role
    if role == "guest":
        return jsonify({"error": "Guests Allowed Read-Only Access"}), 403
    db = get_db()
    recipe = db.execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()
    if recipe is None:
            return jsonify({"error": "Recipe Not Found"}), 404
    is_owner = str(recipe["owner_id"]) == str(user_id)
    is_admin = role == "admin"
    if not (is_owner or is_admin):
        return jsonify({"error": "Forbidden"}), 403

    
    fields, values = [], []
    for column in ("title", "ingredients", "instructions"):
        if column in data:
            fields.append(f"{column} = ?")
            values.append(data[column])
    if "is_public" in data:
        fields.append("is_public = ?")
        values.append(1 if data["is_public"] else 0)
    if not fields:
        return jsonify({"error": "nothing to update"}), 400
    values.append(recipe_id)
    try:
        cur = db.execute(
            f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?", values
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "a recipe with that title already exists"}), 409
    if cur.rowcount == 0:
        return jsonify({"error": "recipe not found"}), 404
    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()
    return jsonify(recipe_to_dict(row))



@require_token
def delete_recipe(recipe_id):

    user_id = g.user_id
    role = g.role
    db = get_db()
    if role == "guest":
        return jsonify({"error": "Guests Allowed Read-Only Access"}), 403
    recipe = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()
    if recipe is None:
        return jsonify({"error": "Recipe Not Found"}), 404
    is_owner = str(recipe["owner_id"]) == str(user_id)
    is_admin = role == "admin"
    if not (is_owner or is_admin):
        return jsonify({"error": "Forbidden"}), 403
    cur = db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "recipe not found"}), 404
    return "", 204





if __name__ == "__main__":
    app.run(debug=True)
