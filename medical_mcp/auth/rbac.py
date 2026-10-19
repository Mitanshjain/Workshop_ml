
import sys

from src.logger import get_logger
from src.exception import CustomException

logger = get_logger(__name__)


# ==========================================
# ROLE BASED ACCESS CONTROL
# ==========================================

ROLE_PERMISSIONS = {

    "user": [
        "patient_mcp",
        "doctor_mcp",
        "appointment_mcp",
        "medical_llm_mcp",
        "insurance_mcp"
    ],

    "admin": [
        "patient_mcp",
        "doctor_mcp",
        "appointment_mcp",
        "medical_llm_mcp",
        "insurance_mcp",
        "doctor_management_mcp",
        "appointment_management_mcp",
        "analytics_mcp"
    ],

    "system": [
        "authentication_mcp",
        "security_mcp"
    ]
}


# ==========================================
# CHECK ROLE PERMISSION
# ==========================================

def check_permission(role: str, mcp_server: str):

    try:

        logger.info(
            f"Checking RBAC permission | "
            f"Role: {role} | MCP Server: {mcp_server}"
        )

        allowed_servers = ROLE_PERMISSIONS.get(
            role,
            []
        )

        if mcp_server in allowed_servers:

            logger.info(
                f"Access granted | Role: {role}"
            )

            return True

        logger.warning(
            f"Access denied | Role: {role} | "
            f"MCP Server: {mcp_server}"
        )

        return False

    except Exception as e:

        logger.error(
            f"RBAC permission check failed: {e}"
        )

        raise CustomException(e, sys)
