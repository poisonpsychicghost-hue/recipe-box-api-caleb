from .models import create_recipe_model_orm, list_recipes_model_orm, list_recipes_for_owner_orm_model, get_recipe_object_by_id, update_recipe_model_orm, delete_recipe_object_by_id, create_recipe_comment_main
from .todict import recipe_to_dict
from .alch_models import User


def create_recipe_service(role, title, ingredients, instructions, is_public, owner_id):
    if role == "guest":
         raise PermissionError

    owner = User.query.get(owner_id)
    if owner is None:
        raise LookupError
    recipe_dict = recipe_to_dict(create_recipe_model_orm(title, ingredients, instructions, is_public, owner))
    return recipe_dict

def delete_recipe_service(role, user_id, recipe_id):
    if role == "guest":
        raise PermissionError

    is_admin = (role == "admin")

    recipe = get_recipe_object_by_id(recipe_id)
    is_owner = str(recipe.owner_id) == str(user_id)
    if not (is_owner or is_admin):
        raise AssertionError

    recipe = delete_recipe_object_by_id(recipe_id)
    return recipe

def list_recipes_service(role, user_id):
    rows = list_recipes_model_orm()
    recipes = []
    for row in rows:
        recipe = recipe_to_dict(row)
        is_owner = str(recipe["owner_id"]) == str(user_id)
        is_admin = role == 'admin'
        if (is_owner or is_admin or recipe["is_public"]):
            recipes.append(recipe)
    return recipes

def get_recipes_service(role, user_id, recipe_id):
    row = get_recipe_object_by_id(recipe_id)
    if row is None:
        raise LookupError
    is_guest = role == 'guest'
    is_admin = role == 'admin'
    is_owner = str(row.owner.id) == str(user_id)
    is_public = bool(row.is_public)

    if is_guest and not is_public:
        raise PermissionError
    if is_admin:
        return recipe_to_dict(row)
    if not is_public and not is_owner:
        raise PermissionError
    return recipe_to_dict(row)

def update_recipe_service(role, user_id, recipe_id, data):
    row = get_recipe_object_by_id(recipe_id)
    if row is None:
        raise LookupError
    if role == 'guest':
        raise PermissionError
    is_admin = role == 'admin'
    is_owner = str(row.owner_id) == str(user_id)
    fields = ["title", "ingredients", "instructions", "is_public"]
    if not any(field in data for field in fields):
        raise Exception
    if not (is_owner or is_admin):
        raise PermissionError
    recipe = update_recipe_model_orm(recipe_id, data)
    return recipe_to_dict(recipe)

def list_my_recipes_service(role, user_id):
    if role == "guest":
        raise PermissionError
    recipes = []
    rows = list_recipes_for_owner_orm_model(user_id)
    if len(rows) == 0:
        raise LookupError
    for row in rows:
        recipe = recipe_to_dict(row)
        recipes.append(recipe)
    return recipes

def create_recipe_comment_service(role, recipe_id, comment_text, user_id):
    if role == "guest":
        raise PermissionError
    recipe = get_recipe_object_by_id(recipe_id)
    
    if recipe is None:
        raise LookupError
    owner_id = recipe.owner_id
    if recipe.is_public == False and owner_id != user_id:
        raise LookupError
    comment = create_recipe_comment_main(recipe_id, comment_text, user_id)
    return comment


