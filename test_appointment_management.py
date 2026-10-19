
# ==========================================
# TEST APPOINTMENT STATUS MCP TOOL
# ==========================================

import asyncio

from fastmcp import Client

from medical_mcp.auth.jwt_handler import create_access_token


async def main():

    admin_token = create_access_token(
        user_id=1,
        role="admin"
    )

    patient_token = create_access_token(
        user_id=1,
        role="patient"
    )

    mcp_url = "http://127.0.0.1:8007/mcp"

    # ======================================
    # TEST 1: INVALID APPOINTMENT STATUS
    # ======================================

    async with Client(mcp_url, auth=admin_token) as client:

        result = await client.call_tool(
            "change_appointment_status",
            {
                "appointment_id": 1,
                "status": "invalid_status"
            }
        )

        print("\nTEST 1 - Invalid Status:")
        print(result.data)

    # ======================================
    # TEST 2: APPOINTMENT DOES NOT EXIST
    # ======================================

        result = await client.call_tool(
            "change_appointment_status",
            {
                "appointment_id": -1,
                "status": "completed"
            }
        )

        print("\nTEST 2 - Invalid Appointment ID:")
        print(result.data)

    # ======================================
    # TEST 3: PATIENT ACCESS DENIED
    # ======================================

    async with Client(mcp_url, auth=patient_token) as client:

        result = await client.call_tool(
            "change_appointment_status",
            {
                "appointment_id": 1,
                "status": "completed"
            }
        )

        print("\nTEST 3 - Patient Access:")
        print(result.data)


if __name__ == "__main__":
    asyncio.run(main())
