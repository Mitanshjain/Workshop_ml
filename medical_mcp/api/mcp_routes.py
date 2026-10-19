# ==========================================
# FASTAPI → FASTMCP INTEGRATION
# ==========================================
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from fastmcp import Client
from medical_mcp.auth.jwt_handler import create_access_token
from medical_mcp.auth.password_handler import authenticate_admin
from medical_mcp.database import get_admin_by_username
from pathlib import Path
from typing import Literal
from fastapi.responses import FileResponse
import logging



logger = logging.getLogger(__name__)

# ==========================================
# UNIFIED MCP SERVER CONFIGURATION
# ==========================================

UNIFIED_MCP_URL = "http://127.0.0.1:8011/mcp"
# ==========================================
# ROUTER
# ==========================================
router = APIRouter(prefix="/api/mcp", tags=["Medical MCP"])
# ==========================================
# REQUEST MODEL
# ==========================================
class DoctorSearchRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
# ==========================================
# DOCTOR MCP API
# ==========================================
@router.post("/doctor")
async def search_doctor(
    data: DoctorSearchRequest,
    request: Request
):
    # Get patient identity from authenticated session
    patient_id = request.session.get("patient_id")
    if not patient_id:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )
    # Generate JWT on the trusted backend only
    token = create_access_token(
        user_id=int(patient_id),
        role="user"
    )
    try:
        # Connect FastAPI to Doctor FastMCP server
        async with Client(
            UNIFIED_MCP_URL,
            auth=token
        ) as client:
            result = await client.call_tool(
                "doctor_search_doctor_details",
                {"name": data.name.strip()}
            )
            return result.data
    except Exception as e:

        print(
            f"DOCTOR MCP ACTUAL ERROR: {type(e).__name__}: {e}",
            flush=True
        )

        logger.exception(
            "Unified Doctor MCP request failed"
        )

        raise HTTPException(
            status_code=503,
            detail="Doctor MCP server is unavailable."
        )
# ==========================================
# PATIENT MCP API
# ==========================================
@router.get("/patient")
async def get_patient_mcp_details(request: Request):
    # Logged-in patient identity
    patient_id = request.session.get("patient_id")
    if not patient_id:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )
    # JWT generated on trusted backend
    token = create_access_token(
        user_id=int(patient_id),
        role="user"
    )
    try:
        async with Client(
            UNIFIED_MCP_URL,
            auth=token
        ) as client:
            result = await client.call_tool(
                "patient_patient_details",
                {"patient_id": int(patient_id)}
            )
            return result.data
        
    except Exception as e:

        print(
                f"APPOINTMENT MCP ACTUAL ERROR: {type(e).__name__}: {e}",
                flush=True
            )

    logger.exception("Unified Appointment MCP connection failed")

    raise HTTPException(
        status_code=503,
        detail="Appointment MCP connection failed."
    )
# ==========================================
# APPOINTMENT MCP CONNECTION CHECK
# ==========================================
@router.get("/appointment/status")
async def check_appointment_mcp(request: Request):
    # Check logged-in patient
    patient_id = request.session.get("patient_id")
    if not patient_id:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )
    # Generate JWT for MCP authentication
    token = create_access_token(
        user_id=int(patient_id),
        role="user"
    )
    try:
        # Connect to Appointment MCP server
        async with Client(
            UNIFIED_MCP_URL,
            auth=token
        ) as client:

            tools = await client.list_tools()

        return {
            "success": True,
            "message": "Appointment MCP connected successfully.",
            "available_tools": [
                tool.name for tool in tools
            ]
        }
    except Exception as e:
        print(
            f"APPOINTMENT MCP ERROR: "
            f"{type(e).__name__}: {e}"
        )
        raise HTTPException(
            status_code=503,
            detail="Appointment MCP connection failed."
        )
# ==========================================
# MEDICAL LLM MCP API
# ==========================================
class MedicalLLMRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
@router.post("/medical-llm")
async def medical_llm_api(
    data: MedicalLLMRequest,
    request: Request
):
    # Verify logged-in patient
    patient_id = request.session.get("patient_id")
    if not patient_id:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )
    # Generate JWT for MCP authentication
    token = create_access_token(
        user_id=int(patient_id),
        role="user"
    )
    try:
        # Connect to Medical LLM MCP
        async with Client(
            UNIFIED_MCP_URL,
            auth=token
        ) as client:
            result = await client.call_tool(
                "medical_llm_medical_llm_chat",
                {
                    "message": data.message.strip()
                }
            )
            return result.data
    except Exception as e:
        print(
            f"MEDICAL LLM MCP ERROR: "
            f"{type(e).__name__}: {e}"
        )
        raise HTTPException(
            status_code=503,
            detail="Medical LLM MCP service unavailable."
        )
# ==========================================
# INSURANCE MCP API
# ==========================================
@router.get("/insurance")
async def get_insurance_mcp_details(request: Request):
    # Get logged-in patient
    patient_id = request.session.get("patient_id")
    if not patient_id:
        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )
    # IMPORTANT:
    # MySQL login IDs and SQLite demo patient IDs
    # are not verified to represent the same person.
    # Do not expose demo insurance records using
    # the MySQL session patient ID.
    raise HTTPException(
        status_code=403,
        detail=(
            "Insurance MCP is currently in demo mode. "
            "Patient identity mapping is not configured."
        )
    )
# ==========================================
# ADMIN LOGIN REQUEST MODEL
# ==========================================
class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1)
# ==========================================
# RECORD ADMIN LOGIN AUDIT EVENT
# ==========================================
async def record_admin_login_audit(admin_id: int):
    try:
        # Generate admin JWT token
        token = create_access_token(
            user_id=admin_id,
            role="admin"
        )
        # Connect to Security & Audit MCP
        async with Client(
            UNIFIED_MCP_URL,
            auth=token
        ) as client:
            await client.call_tool(
                "security_audit_record_audit_event",
                {
                    "action": "ADMIN_LOGIN_SUCCESS",
                    "details": "Admin logged in successfully."
                }
            )
    except Exception:
        # Audit server failure should not block login
        logger.warning(
            "Admin login audit logging failed.",
            exc_info=True
        )


        
# ==========================================
# REUSABLE ADMIN AUDIT LOGGING HELPER
# ==========================================

async def record_admin_action_audit(
    admin_id: int,
    action: str,
    details: str = ""
):
    try:
        token = create_access_token(
            user_id=admin_id,
            role="admin"
        )

        async with Client(
            UNIFIED_MCP_URL,
            auth=token
        ) as client:

            result = await client.call_tool(
                "security_audit_record_audit_event",
                {
                    "action": action,
                    "details": details
                }
            )

            if not result.data.get("success"):
                logger.warning(
                    "Audit event was not recorded: %s",
                    action
                )

    except Exception:
        logger.warning(
            "Failed to record admin audit event: %s",
            action,
            exc_info=True
        )


        # ==========================================
# ADMIN LOGIN HTML PAGE
# ==========================================

# ==========================================
# ADMIN LOGIN HTML PAGE
# ==========================================

@router.get("/admin/login")
async def admin_login_page():

    project_root = Path(__file__).resolve().parents[2]

    login_page = project_root / "templates" / "admin_login.html"

    return FileResponse(
        path=login_page,
        media_type="text/html"
    )

# ==========================================
# ADMIN LOGIN API
# ==========================================
@router.post("/admin/login")
async def admin_login(
    data: AdminLoginRequest,
    request: Request
):
    # Verify admin credentials
    admin = authenticate_admin(
        data.username.strip(),
        data.password
    )
    # Reject invalid credentials
    if admin is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin credentials."
        )
    # Clear any existing patient/admin session
    request.session.clear()
    # Create verified admin session
    request.session["admin_id"] = admin["id"]
    request.session["admin_username"] = admin["username"]
    request.session["role"] = "admin"

    # Record successful login without blocking authentication if audit is down.
    await record_admin_login_audit(admin["id"])
    return {
        "success": True,
        "message": "Admin login successful.",
        "admin": {
            "id": admin["id"],
            "username": admin["username"],
            "role": "admin"
        }
    }
# ==========================================
# ADMIN SESSION VERIFICATION
# ==========================================
@router.get("/admin/session")
async def admin_session(request: Request):
    admin_id = request.session.get("admin_id")
    role = request.session.get("role")
    if not admin_id or role != "admin":
        raise HTTPException(
            status_code=401,
            detail="Admin login required."
        )
    return {
        "success": True,
        "authenticated": True,
        "admin": {
            "id": admin_id,
            "username": request.session.get("admin_username"),
            "role": role
        }
    }
# ==========================================
# ADMIN LOGOUT
# ==========================================
@router.post("/admin/logout")
async def admin_logout(request: Request):
    admin_id = request.session.get("admin_id")
    if not admin_id or request.session.get("role") != "admin":
        raise HTTPException(
            status_code=401,
            detail="Admin login required."
        )
    request.session.clear()
    return {
        "success": True,
        "message": "Admin logged out successfully."
    }
# ==========================================
# ADMIN: VIEW ALL DOCTORS VIA MCP
# ==========================================
@router.get("/admin/doctors")
async def admin_view_doctors(request: Request):
    # Check authenticated admin session
    admin_id = request.session.get("admin_id")
    username = request.session.get("admin_username")
    if not admin_id or request.session.get("role") != "admin":
        raise HTTPException(
            status_code=401,
            detail="Admin login required."
        )
    # Verify admin still exists and is active
    admin = get_admin_by_username(username or "")
    if (
        admin is None
        or not admin["is_active"]
        or admin["id"] != admin_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Admin access denied."
        )
    # Generate server-side MCP token
    admin_token = create_access_token(
        user_id=admin["id"],
        role="admin"
    )
    # Call Doctor Management MCP
    async with Client(
        UNIFIED_MCP_URL,
        auth=admin_token
    ) as client:
        result = await client.call_tool(
            "doctor_management_view_all_doctors",
            {}
        )
    return result.data
# ==========================================
# ADMIN: ADD DOCTOR VIA MCP
# ==========================================
class AddDoctorRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    specialization: str = Field(min_length=1, max_length=100)
    timing: str = Field(min_length=1, max_length=100)
@router.post("/admin/doctors")
async def admin_add_doctor(
    data: AddDoctorRequest,
    request: Request
):
    # Check admin session
    admin_id = request.session.get("admin_id")
    username = request.session.get("admin_username")
    if not admin_id or request.session.get("role") != "admin":
        raise HTTPException(
            status_code=401,
            detail="Admin login required."
        )
    # Verify active admin in SQLite
    admin = get_admin_by_username(username or "")
    if (
        admin is None
        or not admin["is_active"]
        or admin["id"] != admin_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Admin access denied."
        )
    # Generate admin JWT on the server
    admin_token = create_access_token(
        user_id=admin["id"],
        role="admin"
    )
    # Call Doctor Management MCP
    async with Client(
        UNIFIED_MCP_URL,
        auth=admin_token
    ) as client:
        result = await client.call_tool(
            "doctor_management_add_new_doctor",
            {
                "name": data.name.strip(),
                "specialization": data.specialization.strip(),
                "timing": data.timing.strip()
            }
        )
    return result.data
# ==========================================
# ADMIN: UPDATE DOCTOR VIA MCP
# ==========================================
class UpdateDoctorRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    specialization: str = Field(min_length=1, max_length=100)
    timing: str = Field(min_length=1, max_length=100)
@router.put("/admin/doctors/{doctor_id}")
async def admin_update_doctor(
    doctor_id: int,
    data: UpdateDoctorRequest,
    request: Request
):
    # ======================================
    # CHECK ADMIN SESSION
    # ======================================
    admin_id = request.session.get("admin_id")
    username = request.session.get("admin_username")
    if not admin_id or request.session.get("role") != "admin":
        raise HTTPException(
            status_code=401,
            detail="Admin login required."
        )
    # ======================================
    # VERIFY ACTIVE ADMIN
    # ======================================
    admin = get_admin_by_username(username or "")
    if (
        admin is None
        or not admin["is_active"]
        or admin["id"] != admin_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Admin access denied."
        )
    # ======================================
    # GENERATE ADMIN JWT
    # ======================================
    admin_token = create_access_token(
        user_id=admin["id"],
        role="admin"
    )
    # ======================================
    # CALL DOCTOR MANAGEMENT MCP
    # ======================================
    async with Client(
        UNIFIED_MCP_URL,
        auth=admin_token
    ) as client:
        result = await client.call_tool(
            "doctor_management_update_doctor_details",
            {
                "doctor_id": doctor_id,
                "name": data.name.strip(),
                "specialization": data.specialization.strip(),
                "timing": data.timing.strip()
            }
        )
    return result.data
# ==========================================
# ADMIN: DELETE DOCTOR VIA MCP
# ==========================================
@router.delete("/admin/doctors/{doctor_id}")
async def admin_delete_doctor(
    doctor_id: int,
    request: Request
):
    # Check admin session
    admin_id = request.session.get("admin_id")
    username = request.session.get("admin_username")
    if not admin_id or request.session.get("role") != "admin":
        raise HTTPException(
            status_code=401,
            detail="Admin login required."
        )
    # Verify admin exists and is active
    admin = get_admin_by_username(username or "")
    if (
        admin is None
        or not admin["is_active"]
        or admin["id"] != admin_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Admin access denied."
        )
    # Generate server-side admin JWT
    admin_token = create_access_token(
        user_id=admin["id"],
        role="admin"
    )
    # Call Doctor Management MCP
    async with Client(
        UNIFIED_MCP_URL,
        auth=admin_token
    ) as client:
        result = await client.call_tool(
            "doctor_management_delete_doctor_record",
            {
                "doctor_id": doctor_id
            }
        )
    return result.data
# ==========================================
# ADMIN DASHBOARD HTML ROUTE
# ==========================================
@router.get("/admin/dashboard")
async def admin_dashboard(request: Request):
    # Check admin login session
    admin_id = request.session.get("admin_id")
    username = request.session.get("admin_username")
    if not admin_id or request.session.get("role") != "admin":
        raise HTTPException(
            status_code=401,
            detail="Admin login required."
        )
    # Verify admin exists and is active
    admin = get_admin_by_username(username or "")
    if (
        admin is None
        or not admin["is_active"]
        or admin["id"] != admin_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Admin access denied."
        )
    # Project root: Workshop_ml
    project_root = Path(__file__).resolve().parents[2]
    dashboard_path = (
        project_root / "templates" / "admin_dashboard.html"
    )
    return FileResponse(
        path=dashboard_path,
        media_type="text/html"
    )
# ==========================================
# ADMIN - VIEW ALL APPOINTMENTS
# FASTAPI -> APPOINTMENT MANAGEMENT MCP
# ==========================================
@router.get("/admin/appointments")
async def admin_view_appointments(request: Request):
    # Verify admin session
    admin_id = request.session.get("admin_id")
    username = request.session.get("admin_username")
    if (
        not admin_id
        or request.session.get("role") != "admin"
    ):
        raise HTTPException(
            status_code=401,
            detail="Admin login required."
        )
    # Verify admin exists and is active
    admin = get_admin_by_username(username or "")
    if (
        admin is None
        or not admin["is_active"]
        or admin["id"] != admin_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Admin access denied."
        )
    # Generate JWT from authenticated admin identity
    admin_token = create_access_token(
        user_id=admin["id"],
        role="admin"
    )
    # Connect to Appointment Management MCP
    async with Client(
        UNIFIED_MCP_URL,
        auth=admin_token
    ) as client:
        result = await client.call_tool(
            "appointment_management_view_all_appointments"
        )
    return result.data
# ==========================================
# ADMIN: UPDATE APPOINTMENT STATUS VIA MCP
# ==========================================
class AppointmentStatusUpdateRequest(BaseModel):
    status: Literal["booked", "completed", "cancelled"]
@router.put("/admin/appointments/{appointment_id}/status")
async def admin_update_appointment_status(
    appointment_id: int,
    payload: AppointmentStatusUpdateRequest,
    request: Request,
):
    # Require an authenticated admin session
    admin_id = request.session.get("admin_id")
    username = request.session.get("admin_username")
    if not admin_id or request.session.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Admin login required.")
    # Verify the admin still exists and is active
    admin = get_admin_by_username(username or "")
    if (
        admin is None
        or not admin["is_active"]
        or admin["id"] != admin_id
    ):
        raise HTTPException(status_code=403, detail="Admin access denied.")
    # Create an admin JWT on the trusted backend
    admin_token = create_access_token(user_id=admin["id"], role="admin")
    # Call Appointment Management MCP (port 8007)
    async with Client(
        UNIFIED_MCP_URL,
        auth=admin_token,
    ) as client:
        result = await client.call_tool(
            "appointment_management_change_appointment_status",
            {"appointment_id": appointment_id, "status": payload.status},
        )
    return result.data
# ==========================================
# ADMIN - CLINIC ANALYTICS API
# ==========================================
@router.get("/admin/analytics")
async def get_admin_analytics(request: Request):
    # Verify admin login session
    admin_id = request.session.get("admin_id")
    if not admin_id or request.session.get("role") != "admin":
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required."
        )
    # Verify admin is still active
    admin_username = request.session.get("admin_username")
    admin = get_admin_by_username(admin_username)
    if (
        not admin
        or not admin["is_active"]
        or admin["id"] != admin_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Admin access denied."
        )
    # Generate JWT for Analytics MCP
    admin_token = create_access_token(
        user_id=admin["id"],
        role="admin"
    )
    # Connect to Analytics MCP server
    async with Client(
        UNIFIED_MCP_URL,
        auth=admin_token
    ) as client:
        result = await client.call_tool(
            "analytics_view_clinic_analytics",
            {}
        )
        return result.data
# ==========================================
# AUTHENTICATION MCP - VERIFY ADMIN SESSION
# ==========================================
@router.get("/admin/verify-auth")
async def verify_admin_authentication(request: Request):
    # Check existing FastAPI session
    admin_id = request.session.get("admin_id")
    role = request.session.get("role")
    if not admin_id or role != "admin":
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required."
        )
    # Confirm the admin still exists and is active
    admin = get_admin_by_username(
        request.session.get("admin_username", "")
    )
    if (
        not admin
        or not admin.get("is_active")
        or str(admin["id"]) != str(admin_id)
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid or inactive admin."
        )
    # Generate JWT for the authenticated admin
    token = create_access_token(
        user_id=admin["id"],
        role="admin"
    )
    # Call Authentication MCP
    async with Client(
        UNIFIED_MCP_URL,
        auth=token
    ) as client:
        result = await client.call_tool(
            "admin_authentication_verify_admin_access",
            {}
        )
    data = result.data
    if not data.get("success") or not data.get("authorized"):
        raise HTTPException(
            status_code=403,
            detail="Admin access denied."
        )
    return {
        "success": True,
        "authenticated": True,
        "authorized": True,
        "role": "admin"
    }
# ==========================================
# SECURITY & AUDIT MCP - VIEW AUDIT LOGS
# ==========================================
@router.get("/admin/audit-logs")
async def get_admin_audit_logs(request: Request):
    # Check existing admin session
    admin_id = request.session.get("admin_id")
    role = request.session.get("role")
    if not admin_id or role != "admin":
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required."
        )
    # Verify active admin
    admin = get_admin_by_username(
        request.session.get("admin_username", "")
    )
    if (
        not admin
        or not admin.get("is_active")
        or str(admin["id"]) != str(admin_id)
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid or inactive admin."
        )
    # Generate JWT for Security & Audit MCP
    token = create_access_token(
        user_id=admin["id"],
        role="admin"
    )
    # Call Security & Audit MCP Server
    try:
        async with Client(
            UNIFIED_MCP_URL,
            auth=token
        ) as client:
            result = await client.call_tool(
                "security_audit_view_audit_logs",
                {"limit": 20}
            )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Security & Audit MCP service unavailable."
        )
    data = result.data
    if not data.get("success"):
        raise HTTPException(
            status_code=403,
            detail="Audit log access denied."
        )
    return data
