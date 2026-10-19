import sqlite3
import getpass

from medical_mcp.database import DB_NAME
from medical_mcp.auth.password_handler import hash_password # Verify import location

# Connect to existing admin database
con = sqlite3.connect(DB_NAME)

try:
    cur = con.cursor()

    # Display existing admin usernames
    cur.execute("SELECT username FROM admins")
    admins = cur.fetchall()

    if not admins:
        print("No admin accounts found.")
    else:
        print("Available admins:")
        for admin in admins:
            print("-", admin[0])

        username = input("Enter admin username: ").strip()

        cur.execute(
            "SELECT id FROM admins WHERE username = ?",
            (username,)
        )

        if cur.fetchone() is None:
            print("Admin not found.")
        else:
            password = getpass.getpass("Enter new password: ")
            confirm = getpass.getpass("Confirm new password: ")

            if len(password) < 12:
                print("Password must contain at least 12 characters.")
            elif password != confirm:
                print("Passwords do not match.")
            else:
                password_hash = hash_password(password)

                cur.execute(
                    """
                    UPDATE admins
                    SET password_hash = ?
                    WHERE username = ?
                    """,
                    (password_hash, username)
                )

                con.commit()
                print("Admin password reset successfully!")

finally:
    con.close()