
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth import JWTVerifier
from fastmcp.server.dependencies import get_access_token

from medical_mcp.database import get_patient
from medical_mcp.auth.rbac import check_permission

from src.logger import get_logger
from src.exception import CustomException


# ==========================================
# INITIALIZE LOGGER
# ==========================================

logger = get_logger(__name__)


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
    "Patient Details MCP Server",
    auth=jwt_verifier
)

logger.info("Patient MCP Server initialized successfully")


# ==========================================
# TOOL 1: GET PATIENT DETAILS
# ==========================================

@mcp.tool()
def patient_details(patient_id: int):

    try:

        # Get verified JWT
        access_token = get_access_token()

        if access_token is None:
            logger.warning("Access denied: Missing verified JWT")

            return {
                "success": False,
                "message": "Unauthorized access.",
                "patient": None
            }

        claims = access_token.claims

        role = claims.get("role")
        user_id = claims.get("sub")

        # ==========================================
        # CHECK RBAC PERMISSION
        # ==========================================

        if not check_permission(role, "patient_mcp"):

            logger.warning("Patient MCP RBAC access denied")

            return {
                "success": False,
                "message": "Access denied: Insufficient permissions.",
                "patient": None
            }

        # ==========================================
        # CHECK PATIENT OWNERSHIP
        # ==========================================

        # Demo assumption:
        # JWT user ID matches the patient ID in SQLite.
        # Replace with a verified account-patient
        # mapping when integrating real login.

        if role == "user":

            if str(patient_id) != str(user_id):

                logger.warning(
                    "Patient ownership verification failed"
                )

                return {
                    "success": False,
                    "message": "Access denied: Patient ownership mismatch.",
                    "patient": None
                }

        # ==========================================
        # FETCH PATIENT FROM DATABASE
        # ==========================================

        patient = get_patient(patient_id)

        if not patient:

            logger.warning("Patient not found in database")

            return {
                "success": False,
                "message": "Patient details not available in database.",
                "patient": None
            }

        logger.info("Patient details retrieved successfully")

        return {
            "success": True,
            "patient": {
                "id": patient[0],
                "name": patient[1],
                "age": patient[2],
                "city": patient[3],
                "blood_group": patient[4]
            }
        }

    except Exception as e:

        logger.error(f"Patient MCP error: {e}")

        raise CustomException(e, sys)


# ==========================================
# START MCP SERVER
# ==========================================

if __name__ == "__main__":

    logger.info(
        "Starting Patient MCP Server on 127.0.0.1:8002"
    )

    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8002
    )
