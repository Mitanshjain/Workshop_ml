
# ==========================================
# APPOINTMENT MANAGEMENT MCP SERVER
# ==========================================

import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token

from medical_mcp.database import (
    get_all_appointments,
    update_appointment_status as db_update_appointment_status,
)


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(
    PROJECT_ROOT / "medical_mcp" / ".env"
)

JWT_SECRET = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing."
    )


# ==========================================
# JWT AUTHENTICATION
# ==========================================

auth = JWTVerifier(
    public_key=JWT_SECRET,
    algorithm="HS256"
)


# ==========================================
# CREATE MCP SERVER
# ==========================================

mcp = FastMCP(
    "Appointment Management MCP Server",
    auth=auth
)


# ==========================================
# VIEW ALL APPOINTMENTS TOOL
# ==========================================

@mcp.tool()
def view_all_appointments() -> dict:

    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    if token.claims.get("role") != "admin":
        return {
            "success": False,
            "message": "Admin access required."
        }

    return get_all_appointments()


# ==========================================
# UPDATE APPOINTMENT STATUS MCP TOOL
# ==========================================

@mcp.tool()
def change_appointment_status(
    appointment_id: int,
    status: str
) -> dict:

    # Get authenticated access token
    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    # Only admin can update appointments
    if token.claims.get("role") != "admin":
        return {
            "success": False,
            "message": "Admin access required."
        }

    # Validate allowed appointment statuses
    allowed_statuses = {
        "booked",
        "completed",
        "cancelled"
    }

    status = status.strip().lower()

    if status not in allowed_statuses:
        return {
            "success": False,
            "message": "Invalid appointment status."
        }

    # Update appointment in SQLite
    return db_update_appointment_status(
        appointment_id=appointment_id,
        status=status
    )



# ==========================================
# RUN MCP SERVER
# ==========================================

if __name__ == "__main__":

    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8007
    )
