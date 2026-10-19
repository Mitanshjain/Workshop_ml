
from medical_mcp.auth.rbac import check_permission


# ==========================================
# TEST 1: USER ACCESS
# ==========================================

assert check_permission(
    "user", "doctor_mcp"
) is True

print("TEST 1 PASSED: User can access Doctor MCP")


# ==========================================
# TEST 2: USER CANNOT ACCESS ADMIN
# ==========================================

assert check_permission(
    "user", "doctor_management_mcp"
) is False

print("TEST 2 PASSED: User cannot access Admin MCP")


# ==========================================
# TEST 3: ADMIN ACCESS
# ==========================================

assert check_permission(
    "admin", "doctor_management_mcp"
) is True

print("TEST 3 PASSED: Admin can access Admin MCP")


# ==========================================
# TEST 4: SYSTEM ACCESS
# ==========================================

assert check_permission(
    "system", "security_mcp"
) is True

print("TEST 4 PASSED: System can access Security MCP")


# ==========================================
# TEST 5: INVALID ROLE
# ==========================================

assert check_permission(
    "unknown", "doctor_mcp"
) is False

print("TEST 5 PASSED: Unknown role denied")


print("\nAll RBAC tests passed successfully!")
