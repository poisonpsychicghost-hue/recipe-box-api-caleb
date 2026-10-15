import os
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL DEFAULT '',
    is_public INTEGER NOT NULL DEFAULT 1,
    owner_id INTEGER NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
);
"""

USERS_SEED = [
    ("guest", "guest@email.ext", "scrypt:32768:8:1$grkkZZCov9U8Rqwv$871fde769eeb05128135767d0a99e2df49e9589296df9be9cd361c6b2e14c70a188e6c411a1a8393c5acca59f0ef6acd00266a62e91d2d2900fcd24fa5f6c4fb", "guest"),
    ("dev", "thomas.barnard@students.maestrocollege.edu", "scrypt:32768:8:1$kjKnCjY78EFmAlRI$4a2aff29eddf10aaf93cf6c3d67cfce3d9a805a929084426c06d3aa273e72d429b5e19d10947fe60fd3b6069c2bf185266dafd27ad5c5ba0dfa8a0bbee52d220", "admin"),
    ("carlos", "carlos@email.ext", "scrypt:32768:8:1$iinLYN0Vhw9vwHgV$3ede7f5b22b7deacedecb67fc3d91d229649cdc540029576b241f09caed49ec5fb7f771a9010385d4bfc8be664c4c5b58b2bff2c93ea7a7717a7a40fe384e935", "user"),
]

def init_db(db_path: str, *, seed: bool = True) -> None:
    """
    Initialize the SQLite database at db_path.

    - Always ensures tables exist.
    - Optionally seeds users/recipes when seed=True and tables are empty.
    """
    # Ensure parent directory exists (e.g. "backend/")
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    connection = sqlite3.connect(db_path)
    try:
        connection.executescript(SCHEMA)

        if not seed:
            # For a pure testing DB, you might skip seeding entirely
            print(f"Initialized schema in {db_path} (no seed).")
            return

        # 1) Seed users if needed
        existing_users = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing_users == 0:
            connection.executemany(
                "INSERT INTO users (username, email, password_hash, role)"
                " VALUES (?, ?, ?, ?)",
                USERS_SEED,
            )
            connection.commit()

        # 2) Look up dev_id AFTER users are seeded
        dev_row = connection.execute(
            "SELECT id FROM users WHERE username = ?", ("dev",)
        ).fetchone()
        dev_id = dev_row[0]

        # 3) Build recipe seed using dev_id
        RECIPES_SEED = [
            (
                "Shakshuka",
                "eggs, tomatoes, peppers, onion, cumin, paprika",
                "Simmer the sauce, crack in the eggs, cover until just set.",
                1,
                dev_id,
            ),
            (
                "Overnight oats",
                "rolled oats, milk, yogurt, chia seeds, honey",
                "Stir everything together and refrigerate overnight.",
                1,
                dev_id,
            ),
            (
                "Secret family hot sauce",
                "habaneros, garlic, vinegar, a secret ingredient",
                "If we wrote it down here, it wouldn't be a secret.",
                0,
                dev_id,
            ),
        ]

        # 4) Seed recipes if needed
        existing_recipes = connection.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
        if existing_recipes == 0:
            connection.executemany(
                "INSERT INTO recipes (title, ingredients, instructions, is_public, owner_id)"
                " VALUES (?, ?, ?, ?, ?)",
                RECIPES_SEED,
            )
            connection.commit()
            print(f"Created {db_path} and seeded {len(RECIPES_SEED)} recipes.")
        else:
            print(f"{db_path} already has {existing_recipes} recipes - nothing to do.")
    finally:
        connection.close()


if __name__ == "__main__":
    # Default behavior when run as a script:
    # initialize the *development* database with seed data.
    init_db("backend/recipes.db", seed=True)