
# ==========================================
# SYSTEM SECURITY MCP SERVER
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
    "System Security MCP Server",
    auth=auth
)


# ==========================================
# CHECK USER PERMISSION
# ==========================================

@mcp.tool()
def check_user_permission(
    required_role: str
) -> dict:

    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    user_role = token.claims.get("role")

    allowed_roles = {
        "admin",
        "doctor",
        "patient"
    }

    required_role = required_role.strip().lower()

    if required_role not in allowed_roles:
        return {
            "success": False,
            "message": "Invalid required role."
        }

    if user_role != required_role:
        return {
            "success": False,
            "authorized": False,
            "message": "Permission denied."
        }

    return {
        "success": True,
        "authorized": True,
        "role": user_role
    }


# ==========================================
# VALIDATE INPUT
# ==========================================

@mcp.tool()
def validate_input(
    text: str,
    max_length: int = 500
) -> dict:

    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    if max_length < 1 or max_length > 10000:
        return {
            "success": False,
            "message": "Invalid maximum length."
        }

    cleaned_text = text.strip()

    if not cleaned_text:
        return {
            "success": False,
            "message": "Input cannot be empty."
        }

    if len(cleaned_text) > max_length:
        return {
            "success": False,
            "message": "Input exceeds allowed length."
        }

    return {
        "success": True,
        "valid": True,
        "cleaned_text": cleaned_text
    }


# ==========================================
# CHECK SECURITY STATUS
# ==========================================

@mcp.tool()
def check_security_status() -> dict:

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
        "authentication": "JWT",
        "algorithm": "HS256",
        "role_based_access": True,
        "security_server": "active"
    }


# ==========================================
# RUN MCP SERVER
# ==========================================

if __name__ == "__main__":

    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8012
    )
