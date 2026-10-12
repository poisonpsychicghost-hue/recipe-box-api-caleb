from __init__ import create_app

dev_app = create_app("dev")
test_app = create_app("test")

print("dev DEBUG:", dev_app.config["DEBUG"])
print("test DEBUG:", test_app.config["DEBUG"])
print("dev DB:", dev_app.config["DATABASE_PATH"])
print("test DB:", test_app.config["DATABASE_PATH"])
print("dev CORS", dev_app.config["CORS_ORIGIN"])
print("dev CORS", test_app.config["CORS_ORIGIN"])