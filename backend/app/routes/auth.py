from flask import Blueprint, request, jsonify, current_app
from .. import get_db
from ..security import check_password_hash
import datetime, jwt 

auth_bp = Blueprint("auth", __name__, url_prefix="/")

def validate_login():
    if not request.is_json:
        return {"error": "Bad Request: Request must be JSON"}, 400
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return {"error": "email and password are required"}, 400

    db = get_db()
    row = db.execute("""
        SELECT id, username, password_hash, role, email FROM users WHERE email = ?
    """, (email,)).fetchone()


    if row is None or not check_password_hash(row["password_hash"], password):
        return {"error": "Invalid credentials"}, 401

    payload = {
        "sub": str(row["id"]),
        "username": row["username"],
        "role": row["role"],
       "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
       "email": row["email"]
    }

    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET"],
        algorithm="HS256"
    )

    return jsonify({
        "id": row["id"],
        "username": row["username"],
        "role": row["role"],
        "email": row["email"],
        "token": token
    }), 200


auth_bp.add_url_rule(
        "/login",
        view_func=validate_login,
        methods=["POST"]
        )