from .databasegetter import get_db
import sqlite3
from flask import jsonify, g, session
from .alch_models import Recipe
from sqlalchemy import select

def create_recipe_model(title, ingredients, instructions, is_public, owner_id):
    db = get_db()
    cur = db.execute(
        "INSERT INTO recipes (title, ingredients, instructions, is_public, owner_id)"
        " VALUES (?, ?, ?, ?, ?)",
        (title, ingredients, instructions, is_public, owner_id),
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return row

def get_recipe_row_by_id(recipe_id):
    db = get_db()
    recipe = db.execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
            ).fetchone()
    if recipe is None:
        return None
    return recipe

def get_recipe_object_by_id(recipe_id):
    return Recipe.query.get(recipe_id)


def delete_recipe_row_by_id(recipe_id):
    db = get_db()
    cur = db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    db.commit()
    rowcount = cur.rowcount
    return rowcount

def list_recipes_model():
    db = get_db()
    recipes = db.execute("""
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
        WHERE r.is_public = 1
    """
    ).fetchall()
    return recipes

def list_recipes_model_orm():
    query = Recipe.query
    return query.all()

def update_recipe_row(recipe_id, fields, values):
    db = get_db()
    cur = db.execute(f"UPDATE recipes SET  {', '.join(fields)} WHERE id = ?", values + [recipe_id])
    db.commit()
    return cur.rowcount

def list_recipes_for_owner_model(owner_id):
    db = get_db()
    recipes = db.execute(
        """SELECT r.*, u.username AS owner_username FROM recipes AS r JOIN users AS u ON r.owner_id = u.id WHERE r.owner_id = ?""", (owner_id,)
    ).fetchall()
    return recipes

