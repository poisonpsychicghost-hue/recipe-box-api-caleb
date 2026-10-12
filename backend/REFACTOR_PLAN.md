REFACTOR PLAN for recipe-box-api

Current app.py Responsibilities (10/12/26):
    - 13: 
        -App Bootstrap
        -Configuration
        -CORS Policy
        -DB Connx
        -Data Shaping
        -JWT Parsing
        -JWT Authentication
        -JWT Issuance
        -Role Authorization
        -Database Queries
        -API Routing
        -Error Handling
        -Crud Logics

Target:
    —recipe_box/app.py - main app. Builds   itself, imports tools.
    -recipe_box/tools/jwt_utils.py - Houses JWT issuance, JWT Validation, & JWT parsing methods.
    -recipe_box/tools/error_handler - Houses HTTP Error processing, takes in raw errors, exports JSON, StatusCode.
    -recipe_box/tools/return_to_json.py - Houses the valid response processor, taking input raw data and aligning it to expected Public Shape.
    -recipe_box/tools/get_db.py - Houses the database connection open and close functions
    -recipe_box/router/router.py - Houses the API routes for the app.
    -recipe_box/auth/role_check.py - Houses the RoleCheck methods (is_guest, is_admin)
    -recipe_box/auth/owner_check.py - Houses the Ownership checker method
    -recipe_box/auth/register.py - Houses the '/register' POST logics
    -recipe_box/auth/login.py - Houses the '/login' POST logics
    -recipe_box/recipe/recipe_repository.py - Houses the '/recipes' CRUD logics.

Test Acceptance List:
    -POST /users —body: {username, email, password} -> 201 Created, JSON {id, username, email, ConfirmationMessage}

    -POST /recipes —body: {title, ingredients, ?instructions, ?is_public}, —auth: {token} -> 201 Created, JSON {id, title, ingredients, instructions, is_public, owner_id}

    -DELETE /recipes/<id> —body: {}, —auth: {token} -> 204 DELETED, JSON {}

    -PATCH /recipes/<id> -body: {?title, ?ingredients, ?instructions, ?is_public}, -auth: {token} -> 200 OK, JSON {id, title, ingredients, instructions, is_public, owner_id}

    -GET /recipes -body: {}, auth: {token} -> 200 OK, JSON {recipe: {id, title, ingredients, instructions, is_public, owner_id} for recipe in recipes}

    -GET /recipes/<id> -body: {}, auth: {token} -> 200 OK, JSON {id, title, ingredients, instructions, is_public, owner_id}

    -POST /login -body: {email, password} -> 200 OK, JSON {id, username, role, email, token}