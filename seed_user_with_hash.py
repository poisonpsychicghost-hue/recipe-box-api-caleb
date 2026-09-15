import sqlite3
from security import hash_password, verify_password

DB_PATH = "recipes.db"

def main():
    username = "hash_demo_user"
    email = "fake.user@email.ext"
    plain_password = "fake-password-123"

    password_hash = hash_password(plain_password)
    print('Generated hash: ', password_hash)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Insert Test
    cur.execute(
        """
        INSERT INTO users (username, password_hash, email)
        VALUES (?, ?, ?)
        """,
        (username, password_hash, email),
    )
    conn.commit()

    # Confirm with Read
    cur.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    )
    row = cur.fetchone()
    print("Row from DB: ", row)

    stored_hash = row[2]

    # Test/Verify correct + incorect candidates w/ helper
    print("Correct candidate matches:",
          verify_password(stored_hash, plain_password))

    print("Incorrect candidate matches: ", 
          verify_password(stored_hash, "not-the-password"))
    
    test_input_password = input("Enter a Test Password (enter to submit): ")
    print("Input Password Matches (True|False): ", 
          verify_password(stored_hash, test_input_password))

    conn.close()

if __name__ == "__main__":
    main()