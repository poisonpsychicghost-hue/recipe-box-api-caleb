from .models import create_recipe_model, get_recipe_row_by_id, delete_recipe_row_by_id
from .todict import recipe_to_dict

def create_recipe_service(role, title, ingredients, instructions, is_public, owner_id):
    if role == "guest":
         raise PermissionError
    else:
        recipe_dict = recipe_to_dict(create_recipe_model(title, ingredients, instructions, is_public, owner_id))
        return recipe_dict

def delete_recipe_service(role, user_id, recipe_id):
    if role == "guest":
        raise PermissionError

    is_admin = (role == "admin")

    recipe = get_recipe_row_by_id(recipe_id)
    if recipe is None:
        raise LookupError

    is_owner = str(recipe["owner_id"]) == str(user_id)

    if not (is_owner or is_admin):
        raise AssertionError

    rowcount = delete_recipe_row_by_id(recipe_id)
    return rowcount