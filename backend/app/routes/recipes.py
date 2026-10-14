from flask import Blueprint, jsonify, request, g
from ..tools.security import check_password_hash
from ..tools.require import require_token
from ..tools.todict import recipe_to_dict
from ..tools.databasegetter import get_db
import sqlite3


recipes_bp = Blueprint("recipes", __name__, url_prefix="/")

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


recipes_bp.add_url_rule(
    "/recipes",
    view_func=require_token(list_recipes),
    methods=["GET"],
)

recipes_bp.add_url_rule(
    "/recipes/<int:recipe_id>",
    view_func=require_token(get_recipe),
    methods=["GET"],
)

recipes_bp.add_url_rule(
    "/recipes/<int:recipe_id>",
    view_func=require_token(create_recipe),
    methods=["POST"],
)

recipes_bp.add_url_rule(
    "/recipes/<int:recipe_id>",
    view_func=require_token(update_recipe),
    methods=["PATCH"],
)

recipes_bp.add_url_rule(
    "/recipes/<int:recipe_id>",
    view_func=require_token(delete_recipe),
    methods=["DELETE"],
)
