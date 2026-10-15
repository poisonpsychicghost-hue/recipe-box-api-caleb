from app.tools.security import generate_password_hash

print("hash for 'dev123':", generate_password_hash("dev123"))
print("hash for 'password1':", generate_password_hash("password1"))
print("hash for 'password2':", generate_password_hash("password2"))