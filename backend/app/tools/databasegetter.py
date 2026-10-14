import sqlite3
from flask import g 
import os


import sqlite3
from flask import g, current_app

def get_db():
    if "db" not in g:
        db_path = current_app.config["DATABASE_PATH"]
        print("CONNECTING TO DB:", repr(db_path))
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

