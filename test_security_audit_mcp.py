
import asyncio

from fastmcp import Client

from medical_mcp.auth.jwt_handler import create_access_token


# ==========================================
# TEST SECURITY & AUDIT MCP
# ==========================================

async def test_security_audit():

    # STEP 1: Generate admin JWT token
    admin_token = create_access_token(
        user_id=1,
        role="admin"
    )

    # STEP 2: Connect to Security & Audit MCP
    async with Client(
        "http://127.0.0.1:8010/mcp",
        auth=admin_token
    ) as client:

        # STEP 3: Record an audit event
        record_result = await client.call_tool(
            "record_audit_event",
            {
                "action": "ADMIN_LOGIN_SUCCESS",
                "details": "Admin authentication test completed."
            }
        )

        print("\nTEST 1: RECORD AUDIT EVENT")
        print(record_result.data)

        # STEP 4: Retrieve audit history
        history_result = await client.call_tool(
            "view_audit_logs",
            {
                "limit": 10
            }
        )

        print("\nTEST 2: VIEW AUDIT LOGS")
        print(history_result.data)


        
# ==========================================
# TEST PATIENT ACCESS RESTRICTIONS
# ==========================================

async def test_patient_audit_access():

    patient_token = create_access_token(
        user_id=2,
        role="patient"
    )

    async with Client(
        "http://127.0.0.1:8010/mcp",
        auth=patient_token
    ) as client:

        # TEST 3: Patient attempts to record an event
        record_result = await client.call_tool(
            "record_audit_event",
            {
                "action": "UNAUTHORIZED_TEST",
                "details": "Patient attempting to create an audit log."
            }
        )

        print("\nTEST 3: PATIENT RECORD AUDIT EVENT")
        print(record_result.data)

        # TEST 4: Patient attempts to view audit history
        history_result = await client.call_tool(
            "view_audit_logs",
            {
                "limit": 10
            }
        )

        print("\nTEST 4: PATIENT VIEW AUDIT LOGS")
        print(history_result.data)

        # Verify both operations were denied
        assert record_result.data["success"] is False
        assert history_result.data["success"] is False

        print("\nSECURITY TEST PASSED: Patient access denied.")




if __name__ == "__main__":

    asyncio.run(test_security_audit())

    asyncio.run(test_patient_audit_access())

