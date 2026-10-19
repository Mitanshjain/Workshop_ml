
import asyncio

from fastmcp import Client
from medical_mcp.auth.jwt_handler import create_access_token


# ==========================================
# TEST UPDATE DOCTOR MCP TOOL
# ==========================================

async def main():

    mcp_url = "http://127.0.0.1:8006/mcp"

    admin_token = create_access_token(
        user_id=1,
        role="admin"
    )

    patient_token = create_access_token(
        user_id=1,
        role="user"
    )

    # ======================================
    # TEST 1: ADMIN UPDATES DOCTOR
    # ======================================

    async with Client(mcp_url, auth=admin_token) as client:

        tools = await client.list_tools()

        print("REGISTERED TOOLS:")
        for tool in tools:
            print("-", tool.name)

        if "update_doctor_details" not in [
            tool.name for tool in tools
        ]:
            print("ERROR: Update doctor tool not registered.")
            return

        result = await client.call_tool(
            "update_doctor_details",
            {
                "doctor_id": 3,
                "name": "Dr. Test Updated",
                "specialization": "Neurologist",
                "timing": "12 PM - 4 PM"
            }
        )

        print("\nADMIN UPDATE RESULT:")
        print(result.data)

    # ======================================
    # TEST 2: PATIENT CANNOT UPDATE DOCTOR
    # ======================================

    async with Client(mcp_url, auth=patient_token) as client:

        result = await client.call_tool(
            "update_doctor_details",
            {
                "doctor_id": 3,
                "name": "Dr. Unauthorized",
                "specialization": "Cardiologist",
                "timing": "9 AM - 1 PM"
            }
        )

        print("\nPATIENT UPDATE RESULT:")
        print(result.data)


if __name__ == "__main__":
    asyncio.run(main())
