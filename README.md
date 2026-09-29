# recipe-box-api – Backend

A backend service for storing and sharing recipes with support for both public and private entries.

Built with Flask, SQLite, and JWT-based auth to explore secure access to personal recipe data.

---

## Project Purpose

- Provide a simple online repository for users to store their recipes.
- Support both public recipes and private “secret” recipes.
- Expose a clear API for future frontend or third‑party integrations.
- Practice secure patterns around auth, data access, and role-based behavior.

---

## Tech Stack

- **Language:** Python
- **Framework:** Flask
- **Database:** SQLite3
- **Auth/Security:** JSON Web Tokens (JWT), password hashing with Werkzeug
- **Other:** (fill in if you use Blueprints, Marshmallow, etc.)

---

## Setup Instructions

1. **Clone and install dependencies**

   ```bash
   git clone <repo-url>
   cd recipe-box-api
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**

   Create a `.env` file (or configure env vars) with values such as:

   ```env
   DATABASE_URL=sqlite:///recipes.db
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   ```

3. **Initialize the database**

   ```bash
   python init_db.py   # or whatever script/Flask CLI command you use
   ```

4. **(Optional) Seed demo data**

   ```bash
   python seed_demo.py
   ```

---

## Running the Backend

```bash
flask run
# or
python app.py

## Run it

```
python init_db.py
python app.py
```

Requires Python 3.10+ and Flask (`pip install -r requirements.txt`).

## Try it

```
curl http://127.0.0.1:5000/recipes
curl http://127.0.0.1:5000/recipes/1
curl -X POST http://127.0.0.1:5000/recipes -H "Content-Type: application/json" \
     -d '{"title": "Toast", "ingredients": "bread"}'
curl -X DELETE http://127.0.0.1:5000/recipes/1
```

## Endpoints

| Method | Path | Success | Errors |
|---|---|---|---|
| GET | /recipes | 200 | |
| GET | /recipes/&lt;id&gt; | 200 | 404 |
| POST | /recipes | 201 | 400 bad body · 409 duplicate title |
| PATCH | /recipes/&lt;id&gt; | 200 | 400 · 404 · 409 |
| DELETE | /recipes/&lt;id&gt; | 204 | 404 |

`is_public` is stored on every recipe but nothing enforces it yet - by the end
of Unit 3, private recipes will only be visible to their owners.

Note: This is Caleb's fork for the authentication course
