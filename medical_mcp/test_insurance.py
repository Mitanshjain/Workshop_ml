
# ==========================================
# INSURANCE MCP - INTEGRATION TEST
# ==========================================

import asyncio

from fastmcp import Client

from medical_mcp.auth.jwt_handler import create_access_token


async def main():

    # ======================================
    # TEST 1: VALID PATIENT ACCESS
    # ======================================

    token = create_access_token(
        user_id=1,
        role="user"
    )

    async with Client(
        "http://127.0.0.1:8005/mcp",
        auth=token
    ) as client:

        tools = await client.list_tools()

        print("Available tools:")
        print([tool.name for tool in tools])

        result = await client.call_tool(
            "insurance_details",
            {"patient_id": 1}
        )

        print("\nTEST 1: Valid Patient")
        print(result.data)

        assert result.data["success"] is True
        assert result.data["insurance"]["patient_id"] == 1

    # ======================================
    # TEST 2: ACCESS ANOTHER PATIENT
    # ======================================

    async with Client(
        "http://127.0.0.1:8005/mcp",
        auth=token
    ) as client:

        result = await client.call_tool(
            "insurance_details",
            {"patient_id": 2}
        )

        print("\nTEST 2: Another Patient")
        print(result.data)

        assert result.data["success"] is False

    # ======================================
    # TEST 3: ADMIN ACCESS
    # ======================================

    admin_token = create_access_token(
        user_id=999,
        role="admin"
    )

    async with Client(
        "http://127.0.0.1:8005/mcp",
        auth=admin_token
    ) as client:

        result = await client.call_tool(
            "insurance_details",
            {"patient_id": 2}
        )

        print("\nTEST 3: Admin Access")
        print(result.data)

        assert result.data["success"] is True

    print("\nAll Insurance MCP tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
