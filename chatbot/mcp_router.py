"""Patient-authorized MCP tool access for the Sanjeevani chatbot.

Step 1: Doctor Search by NAME only. Do not infer doctor availability,
specialization, or identity from this tool's result.
"""

import logging
from typing import Any

from fastmcp import Client
from medical_mcp.auth.jwt_handler import create_access_token

logger = logging.getLogger(__name__)
DOCTOR_MCP_URL = "http://127.0.0.1:8011/mcp"


async def search_doctor_by_name(patient_id: int, doctor_name: str) -> dict[str, Any]:
    """Search doctor MCP using a backend-issued patient JWT.

    Must only be called after FastAPI has verified the patient's session.
    Returns a structured result; callers must not fabricate missing data.
    """
    if not isinstance(patient_id, int) or patient_id <= 0:
        return {"success": False, "error": "Authentication required."}

    name = doctor_name.strip() if isinstance(doctor_name, str) else ""
    if not name or len(name) > 100:
        return {"success": False, "error": "Provide a doctor name (1–100 characters)."}

    try:
        token = create_access_token(user_id=patient_id, role="user")
        async with Client(DOCTOR_MCP_URL, auth=token) as client:
            result = await client.call_tool("doctor_search_doctor_details", {"name": name})

        if getattr(result, "is_error", False):
            return {"success": False, "error": "Doctor lookup failed."}

        data = getattr(result, "data", None)
        if data is None:
            return {"success": False, "error": "No doctor information was returned."}

        return {"success": True, "data": data}

    except Exception:
        logger.exception("Doctor MCP lookup failed")
        return {"success": False, "error": "Doctor search is temporarily unavailable."}
