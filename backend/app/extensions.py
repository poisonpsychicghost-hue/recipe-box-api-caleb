from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache

migrate = Migrate()
cache = Cache()
db = SQLAlchemy()
