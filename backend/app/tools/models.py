from flask import jsonify, g, session
from .alch_models import Recipe
from sqlalchemy import select
from ..extensions import db

def create_recipe_model_orm(title, ingredients, instructions, is_public, owner_id):
    recipe = Recipe(title=title, ingredients=ingredients, instructions=instructions, is_public=is_public, owner_id=owner_id)
    db.session.add(recipe)
    db.session.commit()
    return recipe

def get_recipe_object_by_id(recipe_id):
    return Recipe.query.get(recipe_id)

def delete_recipe_object_by_id(recipe_id):
    recipe = get_recipe_object_by_id(recipe_id)
    if recipe is None:
        raise LookupError
    db.session.delete(recipe)
    db.session.commit()
    return None

def list_recipes_model_orm():
    query = Recipe.query
    return query.all()

def update_recipe_model_orm(recipe_id, data):
    recipe = get_recipe_object_by_id(recipe_id)
    if recipe is None:
        raise LookupError
    if "title" in data:
        recipe.title = data["title"]
    if "ingredients" in data:
        recipe.ingredients = data["ingredients"]
    if "instructions" in data:
        recipe.instructions = data["instructions"]
    if "is_public" in data:
        if data["is_public"]:
            recipe.is_public = 1
        else:
            recipe.is_public = 0
    db.session.commit()
    return recipe

def list_recipes_for_owner_orm_model(owner_id):
    recipes = Recipe.query.filter_by(owner_id=owner_id).all()
    return recipes
