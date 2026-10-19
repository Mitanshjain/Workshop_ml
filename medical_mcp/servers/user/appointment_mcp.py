
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth import JWTVerifier
from fastmcp.server.dependencies import get_access_token

from medical_mcp.database import book_appointment
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
    "Appointment Booking MCP Server",
    auth=jwt_verifier
)

logger.info("Appointment MCP Server initialized successfully")


# ==========================================
# TOOL 1: BOOK APPOINTMENT
# ==========================================

@mcp.tool()
def book_doctor_appointment(
    patient_id: int,
    doctor_id: int,
    appointment_date: str,
    appointment_time: str
):

    try:

        # ==========================================
        # VERIFY JWT
        # ==========================================

        access_token = get_access_token()

        if access_token is None:

            logger.warning("Missing verified JWT")

            return {
                "success": False,
                "message": "Unauthorized access.",
                "appointment_id": None
            }

        claims = access_token.claims

        role = claims.get("role")
        user_id = claims.get("sub")

        # ==========================================
        # CHECK RBAC
        # ==========================================

        if not check_permission(role, "appointment_mcp"):

            logger.warning("RBAC permission denied")

            return {
                "success": False,
                "message": "Access denied: Insufficient permissions.",
                "appointment_id": None
            }

        # ==========================================
        # VERIFY PATIENT OWNERSHIP
        # ==========================================

        if role == "user":

            if str(patient_id) != str(user_id):

                logger.warning(
                    "Appointment booking ownership mismatch"
                )

                return {
                    "success": False,
                    "message": "Access denied: Patient ownership mismatch.",
                    "appointment_id": None
                }

        # ==========================================
        # BOOK APPOINTMENT IN DATABASE
        # ==========================================

        result = book_appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )

        logger.info(
            f"Appointment booking result: {result['success']}"
        )

        return result

    except Exception as e:

        logger.error(f"Appointment MCP error: {e}")

        raise CustomException(e, sys)


# ==========================================
# START MCP SERVER
# ==========================================

if __name__ == "__main__":

    logger.info(
        "Starting Appointment MCP Server on 127.0.0.1:8003"
    )

    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8003
    )
