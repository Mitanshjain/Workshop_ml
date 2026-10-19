from fastmcp import FastMCP

from medical_mcp.database import get_doctor
from src.logger import get_logger
from src.exception import CustomException

import sys

from fastmcp.server.dependencies import get_access_token
from medical_mcp.auth.rbac import check_permission

import os
from pathlib import Path
from dotenv import load_dotenv
from fastmcp.server.auth import JWTVerifier


# Initialize Logger
logger = get_logger(__name__)


# Create Doctor MCP Server
# ==========================================
# LOAD JWT CONFIGURATION
# ==========================================

load_dotenv(
    Path(__file__).resolve().parents[2] / ".env"
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing")


# ==========================================
# CONFIGURE JWT AUTHENTICATION
# ==========================================

jwt_verifier = JWTVerifier(
    public_key=JWT_SECRET_KEY,
    algorithm="HS256"
)

mcp = FastMCP(
    "Doctor Search MCP Server",
    auth=jwt_verifier
)

logger.info("Doctor Search MCP Server initialized successfully")


# Tool 1: Get verified doctor details
@mcp.tool()
def doctor_details(name: str):

    try:

                # ==========================================
        # JWT + RBAC AUTHORIZATION
        # ==========================================

        access_token = get_access_token()

        if access_token is None:
            logger.warning("Access denied: No verified JWT")
            return {
                "success": False,
                "message": "Unauthorized access.",
                "doctor": None
            }

        # Read role from the verified JWT claims
        claims = access_token.claims
        role = claims.get("role")

        if not check_permission(role, "doctor_mcp"):
            logger.warning(
                f"RBAC access denied for role: {role}"
            )

            return {
                "success": False,
                "message": "Access denied: Insufficient permissions.",
                "doctor": None
            }

        logger.info(f"Doctor search requested for: {name}")

        # Search doctor in actual database
        doctor = get_doctor(name)

        # Hallucination Control
        if not doctor:

            logger.warning(
                f"Doctor not found in database: {name}"
            )

            return {
                "success": False,
                "message": "Doctor details not available in database.",
                "doctor": None
            }

        # Doctor Found
        logger.info(
            f"Doctor verified successfully from database: {doctor[1]}"
        )

        return {
            "success": True,
            "doctor": {
                "id": doctor[0],
                "name": doctor[1],
                "specialization": doctor[2],
                "timing": doctor[3]
            }
        }

    except Exception as e:

        logger.error(
            f"Error while fetching doctor details: {e}"
        )

        raise CustomException(e, sys)


# Start MCP Server
if __name__ == "__main__":

    logger.info(
        "Starting Doctor Search MCP Server on 127.0.0.1:8001"
    )

    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8001
    )