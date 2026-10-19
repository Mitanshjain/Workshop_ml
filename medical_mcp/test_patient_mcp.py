
import asyncio

from fastmcp import Client
from medical_mcp.auth.jwt_handler import create_access_token


MCP_SERVER_URL = "http://127.0.0.1:8002/mcp"


async def test_patient_mcp():

    # ==========================================
    # TEST 1: VALID USER + OWN PATIENT ID
    # ==========================================

    print("\nTEST 1: User Accessing Own Patient Details")

    user_token = create_access_token(
        user_id=1,
        role="user"
    )

    async with Client(
        MCP_SERVER_URL,
        auth=user_token
    ) as client:

        result = await client.call_tool(
            "patient_details",
            {"patient_id": 1}
        )

        print(result.data)

        assert result.data["success"] is True
        assert result.data["patient"]["id"] == 1

    print("TEST 1 PASSED!")


    # ==========================================
    # TEST 2: USER ACCESSING ANOTHER PATIENT
    # ==========================================

    print("\nTEST 2: User Accessing Another Patient")

    async with Client(
        MCP_SERVER_URL,
        auth=user_token
    ) as client:

        result = await client.call_tool(
            "patient_details",
            {"patient_id": 2}
        )

        print(result.data)

        assert result.data["success"] is False
        assert result.data["patient"] is None
        assert "ownership mismatch" in result.data["message"]

    print("TEST 2 PASSED: Unauthorized patient access denied!")

    # ==========================================
    # TEST 3: ADMIN ACCESS
    # ==========================================

    print("\nTEST 3: Admin Access")

    admin_token = create_access_token(
        user_id=10,
        role="admin"
    )

    async with Client(
        MCP_SERVER_URL,
        auth=admin_token
    ) as client:

        result = await client.call_tool(
            "patient_details",
            {"patient_id": 2}
        )

        print(result.data)

        assert result.data["success"] is True
        assert result.data["patient"]["id"] == 2

    print("TEST 3 PASSED: Admin access allowed!")


    # ==========================================
    # TEST 4: MISSING JWT TOKEN
    # ==========================================

    print("\nTEST 4: Missing JWT Token")

    try:
        async with Client(MCP_SERVER_URL) as client:
            await client.call_tool(
                "patient_details",
                {"patient_id": 1}
            )

    except Exception as e:
        print("Access denied:", type(e).__name__)

    else:
        raise AssertionError(
            "Missing JWT was unexpectedly accepted"
        )

    print("TEST 4 PASSED: Missing JWT rejected!")


    # ==========================================
    # TEST 5: SYSTEM ROLE DENIED
    # ==========================================

    print("\nTEST 5: System Role Access")

    system_token = create_access_token(
        user_id=20,
        role="system"
    )

    async with Client(
        MCP_SERVER_URL,
        auth=system_token
    ) as client:

        result = await client.call_tool(
            "patient_details",
            {"patient_id": 1}
        )

        print(result.data)

        assert result.data["success"] is False
        assert result.data["patient"] is None
        assert "Access denied" in result.data["message"]

    print("TEST 5 PASSED: System role denied!")

if __name__ == "__main__":
    asyncio.run(test_patient_mcp())
