
import bcrypt


# ==========================================
# HASH PASSWORD
# ==========================================

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed_password.decode("utf-8")


# ==========================================
# VERIFY PASSWORD
# ==========================================

def verify_password(
    password: str,
    hashed_password: str
) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

# ==========================================
# AUTHENTICATE ADMIN
# ==========================================

def authenticate_admin(username: str, password: str):

    from medical_mcp.database import get_admin_by_username

    admin = get_admin_by_username(username)

    # Check whether admin exists
    if admin is None:
        return None

    # Check whether admin account is active
    if not admin["is_active"]:
        return None

    # Verify password using bcrypt
    if not verify_password(
        password,
        admin["password_hash"]
    ):
        return None

    # Return verified admin information
    return {
        "id": admin["id"],
        "username": admin["username"],
        "role": "admin"
    }

