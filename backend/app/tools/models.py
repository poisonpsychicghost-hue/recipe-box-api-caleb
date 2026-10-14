from .databasegetter import get_db
import sqlite3
from flask import jsonify, g

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

def delete_recipe_row_by_id(recipe_id):
    db = get_db()
    cur = db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    db.commit()
    rowcount = cur.rowcount
    return rowcount
