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

    @property
    def ABSOLUTE_DATABASE_PATH(self):
        # If env var is relative, join it to BACKEND_DIR
        db_path = Path(self.DATABASE_PATH)
        if not db_path.is_absolute():
            db_path = BACKEND_DIR / db_path
        return str(db_path)

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"sqlite:///{self.ABSOLUTE_DATABASE_PATH}"
    
class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_PATH = "recipes.db"

class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = "backend/test_recipes.db"

class ProductionConfig(Config):
    DATABASE_PATH = "backend/product_recipes.db"
    CORS_ORIGIN = "" #fill out at deployment. 