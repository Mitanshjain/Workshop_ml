
import sqlite3
import getpass

from medical_mcp.database import DB_NAME, init_db
from medical_mcp.auth.password_handler import hash_password


# ==========================================
# CREATE FIRST ADMIN
# ==========================================

def create_admin():

    init_db()

    username = input("Enter admin username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    password = getpass.getpass("Enter admin password: ")

    if len(password) < 12:
        print("Password must contain at least 12 characters.")
        return

    confirm_password = getpass.getpass("Confirm admin password: ")

    if password != confirm_password:
        print("Passwords do not match.")
        return

    password_hash = hash_password(password)

    con = sqlite3.connect(DB_NAME)

    try:
        con.execute("""
            INSERT INTO admins (username, password_hash, is_active)
            VALUES (?, ?, 1)
        """, (username, password_hash))

        con.commit()

        print("Admin account created successfully!")

    except sqlite3.IntegrityError:
        con.rollback()
        print("Admin username already exists.")

    finally:
        con.close()


if __name__ == "__main__":
    create_admin()
