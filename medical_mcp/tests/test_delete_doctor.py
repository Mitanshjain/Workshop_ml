
import asyncio

from fastmcp import Client
from medical_mcp.auth.jwt_handler import create_access_token


# ==========================================
# TEST DELETE DOCTOR MCP TOOL
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
    # TEST 1: CHECK TOOL REGISTRATION
    # ======================================

    async with Client(mcp_url, auth=admin_token) as client:

        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]

        print("REGISTERED TOOLS:")
        for name in tool_names:
            print("-", name)

        if "delete_doctor_record" not in tool_names:
            print("\nERROR: Delete doctor tool is not registered.")
            return

        # ==================================
        # TEST 2: ADMIN DELETE REQUEST
        # ==================================

        result = await client.call_tool(
            "delete_doctor_record",
            {"doctor_id": 99999}
        )

        print("\nADMIN DELETE RESULT:")
        print(result.data)

    # ======================================
    # TEST 3: PATIENT DELETE REQUEST
    # ======================================

    async with Client(mcp_url, auth=patient_token) as client:

        result = await client.call_tool(
            "delete_doctor_record",
            {"doctor_id": 99999}
        )

        print("\nPATIENT DELETE RESULT:")
        print(result.data)


if __name__ == "__main__":
    asyncio.run(main())
