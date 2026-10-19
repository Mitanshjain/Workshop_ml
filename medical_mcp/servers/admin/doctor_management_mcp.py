
# ==========================================
# DOCTOR MANAGEMENT MCP SERVER
# ==========================================

import os
from pathlib import Path



from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token


from medical_mcp.database import add_doctor as db_add_doctor

from medical_mcp.database import get_all_doctors as db_get_all_doctors

from medical_mcp.database import update_doctor as db_update_doctor

from medical_mcp.database import delete_doctor as db_delete_doctor

# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / "medical_mcp" / ".env")

JWT_SECRET = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET_KEY is missing.")


# ==========================================
# JWT AUTHENTICATION
# ==========================================

auth = JWTVerifier(
    public_key=JWT_SECRET,
    algorithm="HS256"
)


# ==========================================
# INITIALIZE FASTMCP
# ==========================================

mcp = FastMCP(
    "Doctor Management MCP Server",
    auth=auth
)


# ==========================================
# ADMIN ACCESS TEST
# ==========================================

@mcp.tool()
def check_admin_access() -> dict:

    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    role = token.claims.get("role")

    if role != "admin":
        return {
            "success": False,
            "message": "Admin access required."
        }

    return {
        "success": True,
        "message": "Doctor Management MCP admin access verified."
    }



# ==========================================
# ADD DOCTOR MCP TOOL
# ==========================================

@mcp.tool()
def add_new_doctor(
    name: str,
    specialization: str,
    timing: str
) -> dict:

    # Get authenticated JWT
    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    # Check admin role
    if token.claims.get("role") != "admin":
        return {
            "success": False,
            "message": "Admin access required."
        }

    # Validate input
    if not name.strip() or not specialization.strip() or not timing.strip():
        return {
            "success": False,
            "message": "All doctor fields are required."
        }

    # Insert doctor into SQLite
    result = db_add_doctor(
        name=name,
        specialization=specialization,
        timing=timing
    )

    return result



# ==========================================
# GET ALL DOCTORS MCP TOOL
# ==========================================

@mcp.tool()
def view_all_doctors() -> dict:

    # Get authenticated JWT
    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    # Only admin can access this tool
    if token.claims.get("role") != "admin":
        return {
            "success": False,
            "message": "Admin access required."
        }

    # Retrieve doctors from SQLite
    return db_get_all_doctors()




# ==========================================
# UPDATE DOCTOR MCP TOOL
# ==========================================

@mcp.tool()
def update_doctor_details(
    doctor_id: int,
    name: str,
    specialization: str,
    timing: str
) -> dict:

    # Get authenticated JWT
    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    # Only admin can update doctors
    if token.claims.get("role") != "admin":
        return {
            "success": False,
            "message": "Admin access required."
        }

    # Update doctor information in SQLite
    return db_update_doctor(
        doctor_id=doctor_id,
        name=name,
        specialization=specialization,
        timing=timing
    )


# ==========================================
# DELETE DOCTOR MCP TOOL
# ==========================================

@mcp.tool()
def delete_doctor_record(doctor_id: int) -> dict:

    # Get authenticated JWT
    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    # Only admin can delete doctors
    if token.claims.get("role") != "admin":
        return {
            "success": False,
            "message": "Admin access required."
        }

    # Delete doctor from SQLite
    return db_delete_doctor(doctor_id)





# ==========================================
# RUN MCP SERVER
# ==========================================

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8006
    )
