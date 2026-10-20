from flask import Blueprint, jsonify, request, g
from ..tools.require import require_token
from ..tools.todict import recipe_to_dict
from ..tools.recipe_services import create_recipe_service, delete_recipe_service, list_recipes_service, get_recipes_service, update_recipe_service, list_my_recipes_service
from sqlalchemy.exc import IntegrityError
from ..extensions import cache

recipes_bp = Blueprint("recipes", __name__, url_prefix="/")



def list_recipes():
    user_id = g.user_id
    role = g.role
    recipes = list_recipes_service(role, user_id)
    return jsonify(recipes), 200


def get_recipe(recipe_id):
    user_id = g.user_id
    role = g.role
    try:
        recipe = get_recipes_service(role, user_id, recipe_id)
    except LookupError:
        return jsonify({"error": "recipe not found"}), 404
    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    return jsonify(recipe), 200


def create_recipe():
    # 1. HTTP translation + validation (exactly as you have)
    data = request.get_json(silent=True)
    if not data or not data.get("title") or not data.get("ingredients"):
        return jsonify({"error": "title and ingredients are required"}), 400

    user_id = g.user_id
    role = g.role
    # 2. Business rule: default/public flag still lives here for now
    is_public = 1 if data.get("is_public", True) else 0

    # 3. Data access delegated
    title = data["title"]
    ingredients = data["ingredients"]
    instructions = data.get("instructions", "")
    owner_id = user_id
    try:
        recipe_dict = create_recipe_service(role, title, ingredients, instructions, is_public, owner_id)
    except PermissionError:
        return jsonify({"error": "Guests Allowed Read-Only Access"})
    except IntegrityError:
        # SAME behavior you already had
        return jsonify({"error": "a recipe with that title already exists"}), 409

    # 4. Domain mapping + HTTP response (unchanged)
    return jsonify(recipe_dict), 201

def update_recipe(recipe_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400
    
    user_id = g.user_id
    role = g.role
    try:
        recipe = update_recipe_service(role, user_id, recipe_id, data)
    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403
    except LookupError:
        return jsonify({"error": "Recipe Not Found"}), 404
    except Exception:
        return jsonify({"error": "nothing to update"}), 400
    except IntegrityError:
        return jsonify({"error": "a recipe with that title already exists"}), 409
    return jsonify(recipe_to_dict(recipe))


def delete_recipe(recipe_id):

    user_id = g.user_id
    role = g.role
    try:
        rowcount = delete_recipe_service(role, user_id, recipe_id)
    except PermissionError:
        return jsonify({"error": "Guests Allowed Read-Only Access"}), 403
    except LookupError:
        return jsonify({"error": "Recipe Not Found"}), 404
    except AssertionError:
        return jsonify({"error": "Forbidden"}), 403
    if rowcount == 0:
        return jsonify({"error": "recipe not found"}), 404
    return "", 204

@cache.cached(timeout=30)
def list_my_recipes():
    user_id = g.user_id
    role = g.role
    try:
        recipes = list_my_recipes_service(role, user_id)
    except PermissionError:
        return jsonify({"error": "Guests Allowed Read-Only Access"}), 403
    except LookupError:
        return jsonify({"error": "No Recipes Found."}), 404
    return jsonify(recipes), 200

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
    "/recipes",
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

recipes_bp.add_url_rule(
    "/recipes/mine",
    view_func=require_token(list_my_recipes),
    methods=["GET"],
)
