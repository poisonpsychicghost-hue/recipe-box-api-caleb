import os
from dotenv import load_dotenv
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")
class Config:
    DEBUG = False
    CORS_ORIGIN = os.environ.get("CORS_ORIGIN")
    JWT_SECRET = os.environ.get("JWT_SECRET")
    DATABASE_PATH = os.environ.get("DATABASE_PATH")

    missing = [name for name, value in [
    ("JWT_SECRET", JWT_SECRET),
    ("DATABASE_PATH", DATABASE_PATH),
    ] if not value]

    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = "test_recipes.db"

class ProductionConfig(Config):
    DATABASE_PATH = "product_recipes.db"
    CORS_ORIGIN = "" #fill out at deployment. 