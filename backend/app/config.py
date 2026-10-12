class Config:
    DEBUG = False
    DATABASE_PATH = "recipes.db"
    CORS_ORIGIN = 'http://127.0.0.1:5173'

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = "test_recipes.db"

class ProductionConfig(Config):
    DATABASE_PATH = "product_recipes.db"
    CORS_ORIGIN = "" #fill out at deployment. 