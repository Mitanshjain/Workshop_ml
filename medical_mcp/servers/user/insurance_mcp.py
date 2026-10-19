
# ==========================================
# SANJEEVANI - INSURANCE MCP SERVER
# ==========================================

import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token

from medical_mcp.database import get_insurance


# ==========================================
# ENVIRONMENT CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / "medical_mcp" / ".env")

JWT_SECRET = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET_KEY is missing.")


# ==========================================
# LOGGING
# ==========================================

logger = logging.getLogger(__name__)


# ==========================================
# JWT AUTHENTICATION
# ==========================================

auth = JWTVerifier(
    public_key=JWT_SECRET,
    algorithm="HS256"
)


# ==========================================
# FASTMCP SERVER
# ==========================================

mcp = FastMCP(
    "Insurance MCP Server",
    auth=auth
)


# ==========================================
# INSURANCE DETAILS TOOL
# ==========================================

@mcp.tool()
def insurance_details(patient_id: int) -> dict:

    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required.",
            "insurance": None
        }

    role = token.claims.get("role")
    user_id = token.claims.get("sub")

    if role not in ("user", "admin"):
        return {
            "success": False,
            "message": "Access denied.",
            "insurance": None
        }

    # A user may only access their own record.
    # Admin access is for trusted testing only.
    if role == "user" and str(patient_id) != str(user_id):
        return {
            "success": False,
            "message": "Access denied for this patient.",
            "insurance": None
        }

    try:
        record = get_insurance(patient_id)

        if record is None:
            return {
                "success": False,
                "message": "Insurance policy not found.",
                "insurance": None
            }

        return {
            "success": True,
            "insurance": {
                "id": record[0],
                "patient_id": record[1],
                "provider": record[2],
                "policy_number": record[3],
                "coverage_amount": record[4],
                "status": record[5],
                "expiry_date": record[6]
            }
        }

    except Exception:
        logger.exception("Insurance lookup failed.")

        return {
            "success": False,
            "message": "Unable to retrieve insurance details.",
            "insurance": None
        }


# ==========================================
# RUN MCP SERVER
# ==========================================

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8005
    )
