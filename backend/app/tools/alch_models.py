from ..extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, server_default='user')
    recipes = db.relationship("Recipe", back_populates="owner")

class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    ingredients = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False, server_default='')
    example_image_link = db.Column(db.String(255), nullable=True, unique=True)
    is_public = db.Column(db.Integer, nullable=False, server_default='1')
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, ) #Make Related to User.id later
    owner = db.relationship("User", back_populates="recipes")

