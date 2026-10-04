"""Recipe Box API — BE104 course skeleton.

A working Flask + SQLite CRUD API for recipes. It stores data perfectly —
and it trusts everyone. There is no authentication and no authorization yet.
That is the point: you will add both, lesson by lesson, in Units 2 and 3.
"""

import sqlite3
from functools import wraps
from flask import Flask, g, jsonify, request
from .security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import jwt
import datetime

DATABASE = "backend/recipes.db"

app = Flask(__name__)
load_dotenv()
app.config["JWT_SECRET"] = os.getenv("JWT_SECRET")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def recipe_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
        "owner_id": row["owner_id"]
    }


def require_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header[len("Bearer "):].strip()

        try:
            claims = jwt.decode(token, app.config["JWT_SECRET"], algorithms=["HS256"])
            g.user_id = claims.get("sub")
            g.role = claims.get("role")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token Has Expired. Please Log In."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)
    return wrapper


@app.get("/")
def hello():
    return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})


@app.get("/recipes")
@require_token
def list_recipes():
    db = get_db()
    user_id = g.user_id
    role = g.role
    if role == "guest":
        rows = db.execute("SELECT * FROM recipes WHERE is_public = 1")
    if role == "admin":
        rows = db.execute("SELECT * FROM recipes")
    else:
        rows = db.execute("SELECT * FROM recipes WHERE is_public = 1 OR owner_id = ? ORDER BY id", (user_id,)).fetchall()
    return jsonify([recipe_to_dict(r) for r in rows])


@app.get("/recipes/<int:recipe_id>")
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


@app.post("/recipes")
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


@app.patch("/recipes/<int:recipe_id>")
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


@app.delete("/recipes/<int:recipe_id>")
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


@app.post("/users")
def create_user():
    if not request.is_json:
        return jsonify({"error": "Bad Request: Request Should Be in JSON"}), 400
    data = request.get_json()
    WL = ["username", "email", "password"]
    if not data:
        return jsonify({"error": "Bad Request: Request Empty"}), 400
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not isinstance(username, str) or username.strip() == "":
        return jsonify({"error": "Bad Request: username required"}), 400
    if not isinstance(email, str) or email.strip() == "":
        return jsonify({"error": "Bad Request: email required"}), 400
    if not isinstance(password, str) or password.strip() == "":
        return jsonify({"error": "Bad Request: password required"}), 400

    password_hash = generate_password_hash(password)

    db = get_db()
    try:
        cur = db.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """, (username, email, password_hash))
        db.commit()
    except sqlite3.IntegrityError as e:
        msg = str(e)
        if "users.username" in msg:
            return jsonify({"error": "username already taken"}), 409
        if "users.email" in msg:
            return jsonify({"error": "email already taken"}), 409
        return jsonify({"error": "account conflict"}), 409

    user_id = cur.lastrowid
    return_body = {"message": "User Creation Successful", "username": username, "email": email, "id": user_id}

    return jsonify(return_body), 201


@app.post("/login")
def validate_login():
    if not request.is_json:
        return {"error": "Bad Request: Request must be JSON"}, 400
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return {"error": "username and password are required"}, 400

    db = get_db()
    row = db.execute("""
        SELECT id, username, password_hash, role FROM users WHERE username = ?
    """, (username,)).fetchone()


    if row is None or not check_password_hash(row["password_hash"], password):
        return {"error": "Invalid credentials"}, 401

    payload = {
        "sub": str(row["id"]),
        "username": row["username"],
        "role": row["role"],
       "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
    }

    token = jwt.encode(
        payload,
        app.config["JWT_SECRET"],
        algorithm="HS256"
    )

    return jsonify({
        "id": row["id"],
        "username": row["username"],
        "token": token
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
