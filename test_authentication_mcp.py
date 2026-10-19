
import asyncio

from fastmcp import Client

from medical_mcp.auth.jwt_handler import create_access_token


# ==========================================
# TEST AUTHENTICATION MCP
# ==========================================

async def test_authentication():

    # Generate admin JWT token
    admin_token = create_access_token(
        user_id=1,
        role="admin"
    )

    # Connect to Authentication MCP Server
    async with Client(
        "http://127.0.0.1:8009/mcp",
        auth=admin_token
    ) as client:

        # TEST 1: Verify user identity
        user_result = await client.call_tool(
            "verify_user",
            {}
        )

        print("\nTEST 1: VERIFY USER")
        print(user_result.data)

        # TEST 2: Verify admin access
        admin_result = await client.call_tool(
            "verify_admin_access",
            {}
        )

        print("\nTEST 2: VERIFY ADMIN ACCESS")
        print(admin_result.data)

        
# ==========================================
# TEST PATIENT ROLE AUTHORIZATION
# ==========================================

async def test_patient_authorization():

    patient_token = create_access_token(
        user_id=2,
        role="patient"
    )

    async with Client(
        "http://127.0.0.1:8009/mcp",
        auth=patient_token
    ) as client:

        user_result = await client.call_tool(
            "verify_user",
            {}
        )

        print("\nTEST 3: PATIENT USER VERIFICATION")
        print(user_result.data)

        admin_result = await client.call_tool(
            "verify_admin_access",
            {}
        )

        print("\nTEST 4: PATIENT ADMIN ACCESS")
        print(admin_result.data)


        
# ==========================================
# TEST INVALID JWT TOKEN
# ==========================================

async def test_invalid_token():

    fake_token = "invalid.fake.jwt.token"

    print("\nTEST 5: INVALID JWT TOKEN")

    try:
        async with Client(
            "http://127.0.0.1:8009/mcp",
            auth=fake_token
        ) as client:

            result = await client.call_tool(
                "verify_admin_access",
                {}
            )

            print("Unexpected response:", result.data)
            raise AssertionError(
                "Security test failed: invalid token was accepted."
            )

    except AssertionError:
        raise

    except Exception as error:
        print("Invalid token rejected successfully!")
        print("Error:", type(error).__name__)






if __name__ == "__main__":

    asyncio.run(test_authentication())

    asyncio.run(test_patient_authorization())

    asyncio.run(test_invalid_token())


