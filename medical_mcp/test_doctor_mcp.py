
import asyncio

from fastmcp import Client

from medical_mcp.auth.jwt_handler import create_access_token


MCP_SERVER_URL = "http://127.0.0.1:8001/mcp"


async def test_doctor_mcp():

    # ==========================================
    # TEST 1: VALID JWT TOKEN
    # ==========================================

    token = create_access_token(
        user_id=1,
        role="user"
    )

    print("\nTEST 1: Valid JWT Token")

    async with Client(
        MCP_SERVER_URL,
        auth=token
    ) as client:

        result = await client.call_tool(
            "doctor_details",
            {"name": "Dr. Sharma"}
        )

        print(result.data)

        assert result.data["success"] is True

    print("TEST 1 PASSED!")


    # ==========================================
    # TEST 2: MISSING JWT TOKEN
    # ==========================================

    print("\nTEST 2: Missing JWT Token")

    try:

        async with Client(MCP_SERVER_URL) as client:

            await client.call_tool(
                "doctor_details",
                {"name": "Dr. Sharma"}
            )

        raise AssertionError(
            "Missing JWT token was unexpectedly accepted"
        )

    except AssertionError:
        raise

    except Exception as e:

        print("Access denied as expected")
        print("Error:", type(e).__name__)

    print("TEST 2 PASSED!")

    # ==========================================
    # TEST 3: INVALID JWT TOKEN
    # ==========================================

    print("\nTEST 3: Invalid JWT Token")

    try:

        async with Client(
            MCP_SERVER_URL,
            auth="invalid.jwt.token"
        ) as client:

            await client.call_tool(
                "doctor_details",
                {"name": "Dr. Sharma"}
            )

        raise AssertionError(
            "Invalid JWT token was unexpectedly accepted"
        )

    except AssertionError:
        raise

    except Exception as e:

        print("Invalid token rejected as expected")
        print("Error:", type(e).__name__)

    print("TEST 3 PASSED!")

    # ==========================================
    # TEST 4: SYSTEM ROLE ACCESS DENIED
    # ==========================================

    print("\nTEST 4: System Role Access")

    system_token = create_access_token(
        user_id=2,
        role="system"
    )

    async with Client(
        MCP_SERVER_URL,
        auth=system_token
    ) as client:

        result = await client.call_tool(
            "doctor_details",
            {"name": "Dr. Sharma"}
        )

        print(result.data)

        assert result.data["success"] is False
        assert result.data["doctor"] is None
        assert "Access denied" in result.data["message"]

    print("TEST 4 PASSED: System role denied!")

    # ==========================================
    # TEST 5: ADMIN ROLE ACCESS ALLOWED
    # ==========================================

    print("\nTEST 5: Admin Role Access")

    admin_token = create_access_token(
        user_id=3,
        role="admin"
    )

    async with Client(
        MCP_SERVER_URL,
        auth=admin_token
    ) as client:

        result = await client.call_tool(
            "doctor_details",
            {"name": "Dr. Sharma"}
        )

        print(result.data)

        assert result.data["success"] is True
        assert result.data["doctor"]["name"] == "Dr. Sharma"

    print("TEST 5 PASSED: Admin role allowed!")

if __name__ == "__main__":
    asyncio.run(test_doctor_mcp())
