
# ==========================================
# CLINIC ANALYTICS MCP SERVER
# ==========================================

import os
from pathlib import Path

from dotenv import load_dotenv

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token

from medical_mcp.database import get_clinic_analytics


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
# CREATE ANALYTICS MCP SERVER
# ==========================================

mcp = FastMCP(
    "Clinic Analytics MCP Server",
    auth=auth
)


# ==========================================
# VIEW CLINIC ANALYTICS TOOL
# ==========================================

@mcp.tool()
def view_clinic_analytics() -> dict:

    # Get authenticated JWT
    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    # Allow admins only
    if token.claims.get("role") != "admin":
        return {
            "success": False,
            "message": "Admin access required."
        }

    # Retrieve statistics from SQLite
    return get_clinic_analytics()


# ==========================================
# RUN ANALYTICS MCP SERVER
# ==========================================

if __name__ == "__main__":

    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8008
    )
