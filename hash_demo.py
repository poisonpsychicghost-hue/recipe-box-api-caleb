from werkzeug.security import generate_password_hash, check_password_hash

password = "test-password-123" #fake password

password_hash = generate_password_hash(password)

print("Password hash: ", password_hash)

print("Correct candidate matches: ", check_password_hash(password_hash, "test-password-123"))

print("Wrong candidate matchse: ", check_password_hash(password_hash, "not-the-password"))

test_input = input('Type Password (Enter to Submit): ')
print("Test_Input Matches (True|False): ", check_password_hash(password_hash, test_input))