from ..extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, server_default='user')
    comments = db.relationship("Comment", back_populates="poster")
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
    comments = db.relationship("Comment", back_populates="recipe")
    owner = db.relationship("User", back_populates="recipes")

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    comment_text = db.Column(db.String(320), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    poster = db.relationship("User", back_populates="comments")
    recipe = db.relationship("Recipe", back_populates="comments")
