from flask import Blueprint, request, jsonify, current_app
from .. import get_db
from ..security import check_password_hash, generate_password_hash
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

def create_user():
    if not request.is_json:
        return jsonify({"error": "Bad Request: Request Should Be in JSON"}), 400
    data = request.get_json()
    WL = ["username", "email", "password"]
    if not data:
        return jsonify({"error": "Bad Request: Request Empty"}), 400
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not isinstance(username, str) or username.strip() == "":
        return jsonify({"error": "Bad Request: username required"}), 400
    if not isinstance(email, str) or email.strip() == "":
        return jsonify({"error": "Bad Request: email required"}), 400
    if not isinstance(password, str) or password.strip() == "":
        return jsonify({"error": "Bad Request: password required"}), 400

    password_hash = generate_password_hash(password)

    db = get_db()
    try:
        cur = db.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """, (username, email, password_hash))
        db.commit()
    except sqlite3.IntegrityError as e:
        msg = str(e)
        if "users.username" in msg:
            return jsonify({"error": "username already taken"}), 409
        if "users.email" in msg:
            return jsonify({"error": "email already taken"}), 409
        return jsonify({"error": "account conflict"}), 409

    user_id = cur.lastrowid
    return_body = {"message": "User Creation Successful", "username": username, "email": email, "id": user_id}

    return jsonify(return_body), 201





auth_bp.add_url_rule(
    "/users",
    view_func=create_user,
    methods=["POST"]
)

auth_bp.add_url_rule(

        "/login",
        view_func=validate_login,
        methods=["POST"]
        )

