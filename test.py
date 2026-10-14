from backend.app.__init__ import create_app
from backend.init_db import init_db

app = create_app("test")
init_db(app.config["DATABASE_PATH"], seed=False)
client = app.test_client()

# 1) Login to get the token
resp_login = client.post(
    "/login",
    json={"email": "test1@email.ext", "password": "testpw1"},
)
print("login:", resp_login.status_code, resp_login.json)

token = resp_login.json["token"]
print("token from login:", repr(token))

# 2) Call /recipes with Authorization header
resp_recipes = client.get(
    "/recipes",
    headers={"Authorization": f"Bearer {token}"},
)
print("recipes:", resp_recipes.status_code, resp_recipes.json)