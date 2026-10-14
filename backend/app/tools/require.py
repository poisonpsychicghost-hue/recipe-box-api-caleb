from flask import jsonify, g, current_app, request
import jwt
from functools import wraps 

def require_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header[len("Bearer "):].strip()

        try:
            claims = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            g.user_id = claims.get("sub")
            g.role = claims.get("role")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token Has Expired. Please Log In."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)
    return wrapper

