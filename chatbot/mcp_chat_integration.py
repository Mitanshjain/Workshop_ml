"""Safe, opt-in doctor-name MCP lookup for the existing Sanjeevani /chat route.

Call `await try_mcp_doctor_lookup(message, patient_id)` from the FastAPI
endpoint before the existing text-chat branch. None means continue the
existing booking/cancellation/rescheduling/chatbot flow unchanged.
"""

import re
from typing import Optional

from chatbot.mcp_router import search_doctor_by_name

# Explicit detail lookups only: don't hijack appointment workflows or
# specialization/availability searches.
_DOCTOR_QUERY = re.compile(
    r"^\s*(?:show(?:\s+me)?|find|search(?:\s+for)?|get|tell\s+me\s+about)"
    r"\s+(?:the\s+)?(?:details?|information|profile|info)\s+"
    r"(?:of|for|about|on)\s+(?P<name>dr\.?\s+[a-z][a-z .'-]{1,80})\s*[?.!]?\s*$",
    re.IGNORECASE,
)


async def try_mcp_doctor_lookup(message: str, patient_id: int | None) -> Optional[str]:
    """Return verified doctor details, a safe error, or None (not an MCP request)."""
    match = _DOCTOR_QUERY.fullmatch(message or "")
    if not match:
        return None
    if not patient_id:
        return "Please log in before searching doctor details."

    name = match.group("name").strip().rstrip("?.! ")
    result = await search_doctor_by_name(int(patient_id), name)
    if not result.get("success"):
        return "Doctor search is temporarily unavailable. Please try again later."

    payload = result.get("data")
    if not isinstance(payload, dict) or not payload.get("success"):
        return "I couldn't find verified details for that doctor in the clinic database."

    doctor = payload.get("doctor")
    if not isinstance(doctor, dict) or not doctor.get("name"):
        return "Verified doctor details are not available right now."

    # Show only verified fields returned by the MCP database tool.
    lines = [f"Doctor: {doctor['name']}"]
    for field, label in (("specialization", "Specialization"), ("timing", "Timing")):
        if doctor.get(field) is not None:
            lines.append(f"{label}: {doctor[field]}")
    lines.append("These details are from the clinic's doctor database; appointment availability must be checked separately.")
    return "\n".join(lines)
