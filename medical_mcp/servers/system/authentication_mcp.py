
# ==========================================
# SYSTEM AUTHENTICATION MCP SERVER
# ==========================================

import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token


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
# INITIALIZE MCP SERVER
# ==========================================

mcp = FastMCP(
    "System Authentication MCP Server",
    auth=auth
)


# ==========================================
# VERIFY CURRENT USER
# ==========================================

@mcp.tool()
def verify_user() -> dict:

    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    return {
        "success": True,
        "authenticated": True,
        "user_id": token.claims.get("sub"),
        "role": token.claims.get("role")
    }


# ==========================================
# VERIFY ADMIN ACCESS
# ==========================================

@mcp.tool()
def verify_admin_access() -> dict:

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

    return {
        "success": True,
        "authorized": True,
        "role": "admin"
    }


# ==========================================
# RUN MCP SERVER
# ==========================================

if __name__ == "__main__":

    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8009
    )
