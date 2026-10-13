# recipe-box-api — Backend Code Review

**Reviewer:** Code Reviewer
**Date:** 2026-05-30
**Scope:** `backend/` (Flask + SQLite + JWT). Frontend (`recipe-box-ui/`) read only for contract/consistency checks.
**Commit reviewed:** working tree at `05ddb42` + uncommitted changes (`app/routes/`, `config.py`, `__init__.py`, `requirements.txt`)

---

## 0. Bottom line

The auth layer that was just added is mostly correct — `require_token` is applied to every `/recipes` route, ownership checks exist on PATCH/DELETE, guests are read-only, and passwords are scrypt-hashed. That is real progress over the documented anonymous-CRUD state.

But **the app cannot start as committed**, and there are three defects that will silently break behaviour once it does:

1. `flask_cors` is imported and never used, is not in `requirements.txt`, and is not installed → `create_app()` raises `ModuleNotFoundError` on every entry point.
2. `DATABASE_PATH` from `.env` is read into config and then ignored — `get_db()` hardcodes a path next to `app/__init__.py`. Every config (`test`, `prod`) points at the same database.
3. `create_recipe()` returns `200` with a JSON error body for guests instead of `403`, and `update_recipe()`/`delete_recipe()` return `403` for guests *after* confirming the row exists — an existence oracle.

Plus one latent time bomb: `datetime.datetime.utcnow()` in the login payload is deprecated and will raise in a future Python.

Details, evidence and patches below.

---

## 1. Critical — the application does not start

### 1.1 `flask_cors` is imported but not installed or declared

`backend/app/__init__.py:11`

```python
from flask_cors import CORS
```

- `CORS` is never referenced again anywhere in the file (verified with `grep -rn "CORS" --include=*.py`).
- `backend/requirements.txt` is `flask` + `python-dotenv==1.2.4` — no `flask-cors`.
- Neither `backend/venv` nor the root `.venv-1` has it installed.

Reproduced:

```
$ backend/venv/bin/python -c "from app import create_app; create_app('dev')"
ModuleNotFoundError: No module named 'flask_cors'
```

This means `wsgi.py`, `python app.py`, `flask run`, and `app/test.py` all fail at import time. `app/test.py` has presumably never run.

**Fix — pick one:**

Option A (dead import, delete it):

```python
# backend/app/__init__.py — remove line 11
-from flask_cors import CORS
```

Option B (you actually want CORS, since the Vue dev server runs on `:5173` and the API on `:5000`):

```python
from flask_cors import CORS

def create_app(config_name):
    app = Flask(__name__)
    ...
    CORS(app, origins=[app.config["CORS_ORIGIN"]], supports_credentials=False)
```

Then add `flask-cors` to `requirements.txt`.

Option A is only safe if the frontend is proxied (e.g. Vite `server.proxy`). It currently is not — `recipe-box-ui/src/tools/useApiClient.ts` and `useAuth.ts` fetch `http://127.0.0.1:5000` cross-origin directly, so **the browser will block every request** without CORS headers. Given that, Option B is the correct fix unless you add a Vite proxy.

Also note the `.env` line has spaces around the `=`:

```
CORS_ORIGIN = 'http://127.0.0.1:5173'
```

`python-dotenv` tolerates this, but the quotes become part of the value in some parsers. Write it unquoted and unspaced: `CORS_ORIGIN=http://127.0.0.1:5173`.

### 1.2 `DATABASE_PATH` is validated then ignored

`backend/app/config.py` reads and *requires* `DATABASE_PATH`:

```python
DATABASE_PATH = os.environ.get("DATABASE_PATH")
missing = [... ("DATABASE_PATH", DATABASE_PATH) ...]
if missing:
    raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
```

But `backend/app/__init__.py:78` hardcodes its own:

```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'recipes.db')
```

Consequences:

- `TestingConfig.DATABASE_PATH = "test_recipes.db"` and `ProductionConfig.DATABASE_PATH = "product_recipes.db"` are decorative. `create_app("test")` writes to the dev database.
- Setting `DATABASE_PATH` in `.env` changes nothing.
- The config guard gives a false sense of safety: you can be told `JWT_SECRET` is missing but never that your DB path is wrong.

Note the resolved path is `backend/app/recipes.db`, *not* `backend/recipes.db` where `init_db.py` creates and seeds the schema. Confirmed: `backend/recipes.db` has **no tables** (`sqlite3 recipes.db ".tables"` → empty), while `backend/app/recipes.db` is a 24 KB file. So the DB the server opens is not the one the setup script builds.

**Fix:**

```python
# backend/app/__init__.py
def get_db():
    if "db" not in g:
        path = current_app.config["DATABASE_PATH"]
        g.db = sqlite3.connect(path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db
```

Resolve relative paths against a single known root (the repo's `backend/` dir) so `init_db.py`, `seed_user_with_hash.py` and the app agree:

```python
# backend/app/config.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/

def _db_path(value: str | None) -> str:
    if not value:
        return os.path.join(BASE_DIR, "recipes.db")
    return value if os.path.isabs(value) else os.path.join(BASE_DIR, value)
```

Then `DATABASE_PATH=recipes.db` in `.env` resolves to `backend/recipes.db` — the seeded one. Delete the stray `backend/app/recipes.db` and `backend/recipes_fake.db` once migrated.

---

## 2. High — authorization defects

### 2.1 Guest creation returns `200`, not `403`

`backend/app/__init__.py:224`

```python
if role == "guest":
    return jsonify({"error": "Guests Allowed Read-Only Access"})   # ← defaults to 200
```

Every other guard in the file returns a status code; this one does not. The frontend's `useApiClient.request()` treats `response.ok` as success, so a guest "creating" a recipe gets a green toast and `recipes.value.push(...)` never runs — the UI silently does nothing while claiming success. `RegisterModal`/`AddRecipeView` hit the same path.

**Fix:** `return jsonify({"error": "Guests Allowed Read-Only Access"}), 403`

### 2.2 Existence oracle on PATCH/DELETE

`update_recipe` (line ~257) and `delete_recipe` (line ~301) both do:

```python
recipe = db.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
if recipe is None:
    return jsonify({"error": "Recipe Not Found"}), 404
is_owner = str(recipe["owner_id"]) == str(user_id)
if not (is_owner or is_admin):
    return jsonify({"error": "Forbidden"}), 403
```

A guest or a non-owner can distinguish "recipe 7 exists but is private" (`403`) from "recipe 7 does not exist" (`404`). Combined with `id` being an autoincrement integer, that is a trivial enumeration oracle over the whole table, including other users' private recipes. Note this contradicts the course's own acceptance test, which expects `403` for a non-owner regardless.

`get_recipe` has the same shape but at least checks `role == "guest"` first — still, a guest probing a private recipe gets `403` and a missing one gets `404`.

**Fix — check permission against a scoped query, and return 404 for both:**

```python
def _load_owned(db, recipe_id, user_id, role):
    """Return the row if the caller may mutate it, else None."""
    if role == "admin":
        return db.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    return db.execute(
        "SELECT * FROM recipes WHERE id = ? AND owner_id = ?",
        (recipe_id, user_id),
    ).fetchone()
```

Then in PATCH/DELETE:

```python
recipe = _load_owned(db, recipe_id, user_id, role)
if recipe is None:
    return jsonify({"error": "Recipe Not Found"}), 404
```

404-for-everything is the right call for private data: it leaks nothing. If the course rubric insists on `403` for a known-but-forbidden row, gate it behind an explicit test config flag, not by default.

### 2.3 Ownership comparison via string coercion

`str(recipe["owner_id"]) == str(user_id)` appears three times. It works today because `g.user_id` is set from `claims.get("sub")`, which login stores as `str(row["id"])`, and because SQLite is loosely typed. It is fragile: the moment anything sets `g.user_id` to an `int` (or a JWT is issued with an int `sub` by another service), the comparison still passes but for the wrong reason, and a `None` `sub` would compare as `"None"` against a `NULL` owner.

**Fix:** normalise once at the auth boundary:

```python
# in require_token, after decode
sub = claims.get("sub")
if sub is None:
    return jsonify({"error": "Unauthorized"}), 401
try:
    g.user_id = int(sub)
except (TypeError, ValueError):
    return jsonify({"error": "Unauthorized"}), 401
g.role = claims.get("role")
```

and compare `recipe["owner_id"] == g.user_id` as ints.

### 2.4 `require_token` accepts tokens with no `sub` and unknown roles

`claims.get("sub")` and `claims.get("role")` are unvalidated. A token signed with the same secret but carrying `{"role": "admin"}` — or no role at all — lands in the `else` branch of `list_recipes`, which treats unknown roles as regular users (fail-open there, but `get_recipe` would `Forbidden` for a missing role on private rows while allowing public ones). Add explicit validation:

```python
role = claims.get("role")
if role not in {"guest", "user", "admin"}:
    return jsonify({"error": "Unauthorized"}), 401
```

---

## 3. Medium

### 3.1 `datetime.datetime.utcnow()` is deprecated and will break

`backend/app/routes/auth.py`

```python
"exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
```

`utcnow()` returns a naive datetime and is deprecated since 3.12; it emits a `DeprecationWarning` today and is slated for removal. PyJWT encodes a naive datetime as a UTC epoch, so it currently works — but it is the classic trap. Use:

```python
"exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2),
```

Also consider making the TTL a config value (`JWT_TTL_HOURS`) rather than a literal, since the frontend's session-expiry flow is documented in `design_document.md` §4.5.

### 3.2 No token revocation / logout is client-side only

`logout()` in `useAuth.ts` just clears memory. A stolen token stays valid for its full 2 hours. For a course project this is acceptable, but document it — `SECURITY_NOTES.md` currently only records the anonymous-CRUD finding and is now stale (the app *does* enforce auth on `/recipes`).

### 3.3 `SECURITY_NOTES.md` is out of date

It describes the pre-refactor state (anonymous PATCH/DELETE/GET returning 200). Update it to reflect: token required on all `/recipes`, guest read-only, ownership enforced, and the two remaining gaps above (no revocation, existence oracle if left unfixed).

### 3.4 `JWT_SECRET` is committed in `.env`

`backend/.env` contains a real-looking secret and is gitignored (good) — but confirm it never entered history:

```bash
git log --all --oneline -- backend/.env
```

If it did, rotate the secret; a 2-hour JWT with a known signing key is a full auth bypass.

### 3.5 `config.py` class-body `RuntimeError` is a footgun

The `missing` check runs at import time of the config module, so *any* import of `app` — including a future migration tool or a test that only wants `app.security` — requires both env vars to be present. `seed_user_with_hash.py` and `hash_demo.py` currently import through `backend.app.security`, which triggers `app/__init__.py` → `flask_cors` → boom. Move validation into a factory called from `create_app()`:

```python
def _validate(cfg):
    missing = [k for k in ("JWT_SECRET", "DATABASE_PATH") if not cfg.get(k)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
```

---

## 4. Low / cleanup

| # | Location | Issue |
|---|---|---|
| 4.1 | `app/__init__.py:76` | `BASE_DIR`/`DATABASE` are module-level dead constants once 1.2 is fixed. Remove. |
| 4.2 | `app/__init__.py` `hello()` | Defined, never registered. Delete or add a `/` route. |
| 4.3 | `app/__init__.py` bottom | `if __name__ == "__main__": app.run(debug=True)` references a name `app` that does not exist in this module (it is local to `create_app`). Dead code — delete it; `app.py`/`wsgi.py` are the entry points. |
| 4.4 | `app/__init__.py` `list_recipes` | The dict-building loop duplicates `recipe_to_dict()` and includes `owner_username` unconditionally, while `recipe_to_dict` includes it only if present. The frontend masks the leak client-side (`ownerName = isAdmin \|\| isOwner ? r.owner_username : 'Public'`), but the API still ships other users' usernames to everyone. Return `owner_username` only for admin/self, or use a single shaping function. |
| 4.5 | `app/__init__.py` `create_recipe` | Does not validate that `title`/`ingredients` are strings; a JSON `{"title": 1, "ingredients": []}` is accepted by the truthiness check and stored. Add `isinstance(..., str)` like `create_user` does. |
| 4.6 | `app/__init__.py` `create_recipe` | `is_public` accepts any truthy JSON value (`"false"` → `True`). Coerce explicitly: `if not isinstance(data.get("is_public", True), bool): return 400`. |
| 4.7 | `app/__init__.py` `update_recipe` | The `fields` list is built by string interpolation of column names — safe *today* because the names are hardcoded, but it is the pattern that becomes SQL injection the first time someone adds a dynamic field. Prefer a fixed mapping: `{"title": "title", ...}` and reject unknown keys explicitly. |
| 4.8 | `app/__init__.py` `update_recipe` | `cur.rowcount == 0` after a successful `SELECT` of the row is unreachable (the row exists, so the UPDATE matched). Harmless but dead. |
| 4.9 | `app/__init__.py` `delete_recipe` | Returns `"", 204`; the frontend `request<void>` tries `response.json()` on an empty body and falls back to `null`. Fine, but `jsonify({})` would be kinder to generic clients. |
| 4.10 | `app/routes/auth.py:2` | `from .. import get_db` (relative) next to `from app.security import ...` (absolute). Pick one style; absolute is safer if `app` is ever renamed. |
| 4.11 | `app/routes/auth.py` | `auth_bp` is created with `url_prefix="/"` and a single rule. Fine, but the docstring/`REFACTOR_PLAN.md` says routes move to `router/router.py`; keep the plan and the code in sync. |
| 4.12 | `app/routes/auth.py` `validate_login` | `data.get("email")` on a non-dict JSON body (e.g. `[1,2]`) raises `AttributeError` → 500. Guard with `if not isinstance(data, dict): return 400`. Same in `create_user`. |
| 4.13 | `app/routes/auth.py` | On failed login, an unknown email and a wrong password both return `401 Invalid credentials` — good. Keep it that way. |
| 4.14 | `app/routes/auth.py` | No rate limiting on `/login`. A 4-char password is accepted at registration; add a minimum length. |
| 4.15 | `app/security.py` | Defines `hash_password`/`verify_password`, but `app/__init__.py` imports `generate_password_hash`/`check_password_hash` from `werkzeug.security` directly and uses those. Two names for one thing. Route everything through `app.security`. |
| 4.16 | `app/security.py` header | `# security,py` typo. |
| 4.17 | `init_db.py` | `CREATE TABLE IF NOT EXISTS recipes` omits `owner_id`, which the API requires on INSERT. Re-running `init_db.py` on a fresh clone produces a schema the app cannot write to. Make the schema a single source of truth (a `schema.sql` or a `flask db-init` CLI command) shared with the test setup. |
| 4.18 | `init_db.py` | Seeds recipes with no `owner_id`; the API's `JOIN users` then drops them from `list_recipes`. Seed a user too. |
| 4.19 | `seed_user_with_hash.py` | Imports `from backend.app.security import ...` — only works if CWD is the repo root and `backend` is a package (it has no `__init__.py`). Run from `backend/` it fails. Use `from app.security import ...`. |
| 4.20 | `seed_user_with_hash.py`, `hash_demo.py` | Both call `input()` in their `main`. Delete `hash_demo.py`; it is a scratch file. |
| 4.21 | `app/test.py` | Top-level `print()`s in a module under `app/`. It is collected by pytest if it ever runs and imports two apps at import time. Move to `tests/` and convert to real assertions. |
| 4.22 | `backend/recipes_fake.db` | Tracked? `.gitignore` has `*.db`, but the file exists on disk with real-looking user rows (three scrypt hashes, one admin). Delete it, and verify it was never committed. |
| 4.23 | `package-lock.json` (repo root) | An empty npm lockfile at the root of a Python repo. Delete. |
| 4.24 | Two venvs | `backend/venv/` and root `.venv-1/` are both present; `flask_cors` is in neither. Consolidate to one and document it in the README. |
| 4.25 | `requirements.txt` | Unpinned `flask` alongside pinned `python-dotenv`, and missing `flask-cors` (see 1.1), `PyJWT`, and `Werkzeug`. Pin all four: `flask-cors` is a direct dependency, `PyJWT` is imported as `jwt`, and `Werkzeug` provides the hashing. |

---

## 5. Suggested priority order

1. **Unbreak startup** — decide on CORS (1.1), fix `requirements.txt`.
2. **Wire `DATABASE_PATH` through `get_db()`** and reconcile the three database files (1.2).
3. **Fix the guest `200` → `403`** (2.1) — it is a one-line bug with a user-visible wrong outcome.
4. **Close the existence oracle** (2.2) and normalise `user_id` (2.3, 2.4).
5. **Replace `utcnow()`** (3.1) before it becomes a runtime error.
6. **Reconcile the schema** between `init_db.py` and the API (4.17–4.19), then re-seed so `list_recipes` returns rows again.
7. Cleanup pass (section 4) — most of it is deletion.

---

## 6. What is already right

Worth stating, because the course docs still describe the old broken state:

- `require_token` wraps all five `/recipes` routes; the anonymous-CRUD findings in `SECURITY_NOTES.md` are resolved.
- JWT validation distinguishes expired from invalid and returns `401` for both.
- Passwords use Werkzeug's scrypt with per-hash salt (`scrypt:32768:8:1$…`, 16-byte salt) — not the old `sha256`-only default.
- Login returns a uniform `401 Invalid credentials` for both unknown email and bad password, so it does not leak account existence.
- `create_user` validates types and maps `IntegrityError` to specific `409`s.
- `list_recipes` correctly scopes by role: admin → all, guest → public only, user → public OR own.
- SQL is parameterised everywhere; the only interpolation is the hardcoded column list in `update_recipe` (4.7).
