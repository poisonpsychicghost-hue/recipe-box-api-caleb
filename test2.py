import sqlite3

for path in ["backend/recipes.db", "backend/test_recipes.db"]:
    conn = sqlite3.connect(path)
    users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    recipes = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    conn.close()
    print(path, "users:", users, "recipes:", recipes)