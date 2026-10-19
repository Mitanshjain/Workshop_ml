
# ==========================================
# SANJEEVANI - UNIFIED MCP SERVER
# ==========================================

import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier

from medical_mcp.servers.admin.doctor_management_mcp import (
    mcp as doctor_management_mcp
)
from medical_mcp.servers.admin.analytics_mcp import (
    mcp as analytics_mcp
)

from medical_mcp.servers.admin.appointment_management_mcp import (
    mcp as appointment_management_mcp
)

from medical_mcp.servers.admin.security_audit_mcp import (
    mcp as security_audit_mcp,
    initialize_audit_table
)

from medical_mcp.servers.admin.authentication_mcp import (
    mcp as admin_authentication_mcp
)

from medical_mcp.servers.system.security_mcp import (
    mcp as system_security_mcp
)

from medical_mcp.servers.user.patient_mcp import (
    mcp as patient_mcp
)

from medical_mcp.servers.user.doctor_mcp import (
    mcp as doctor_search_mcp
)

from medical_mcp.servers.user.appointment_mcp import (
    mcp as appointment_booking_mcp
)

from medical_mcp.servers.user.medical_llm_mcp import (
    mcp as medical_llm_mcp
)

from medical_mcp.servers.user.insurance_mcp import (
    mcp as insurance_mcp
)


# ==========================================
# AUTHENTICATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "medical_mcp" / ".env")

JWT_SECRET = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET_KEY is missing.")

auth = JWTVerifier(
    public_key=JWT_SECRET,
    algorithm="HS256"
)

# ==========================================
# MAIN MCP SERVER
# ==========================================

mcp = FastMCP(
    "Sanjeevani Unified MCP Server",
    auth=auth
)

# ==========================================
# MOUNT MCP SERVERS
# ==========================================

mcp.mount(
    doctor_management_mcp,
    namespace="doctor_management"
)

mcp.mount(
    analytics_mcp,
    namespace="analytics"
)

# ==========================================
# APPOINTMENT MANAGEMENT MCP
# ==========================================

mcp.mount(
    appointment_management_mcp,
    namespace="appointment_management"
)

# ==========================================
# SECURITY AUDIT MCP
# ==========================================

mcp.mount(
    security_audit_mcp,
    namespace="security_audit"
)

# ==========================================
# ADMIN AUTHENTICATION MCP
# ==========================================

mcp.mount(
    admin_authentication_mcp,
    namespace="admin_authentication"
)

mcp.mount(
    system_security_mcp,
    namespace="system_security"
)

# ==========================================
# PATIENT MCP
# ==========================================

mcp.mount(
    patient_mcp,
    namespace="patient"
)

# ==========================================
# DOCTOR SEARCH MCP
# ==========================================

mcp.mount(
    doctor_search_mcp,
    namespace="doctor_search"
)

# ==========================================
# APPOINTMENT BOOKING MCP
# ==========================================

mcp.mount(
    appointment_booking_mcp,
    namespace="appointment_booking"
)

# ==========================================
# MEDICAL LLM MCP
# ==========================================

mcp.mount(
    medical_llm_mcp,
    namespace="medical_llm"
)

mcp.mount(
    insurance_mcp,
    namespace="insurance"
)

# ==========================================
# RUN UNIFIED MCP SERVER
# ==========================================

if __name__ == "__main__":

    # Initialize audit database table
    initialize_audit_table()

    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8011
    )
