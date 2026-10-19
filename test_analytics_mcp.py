
# ==========================================
# TEST CLINIC ANALYTICS MCP SERVER
# ==========================================

import asyncio

from fastmcp import Client
from medical_mcp.auth.jwt_handler import create_access_token


# ==========================================
# TEST ADMIN ACCESS
# ==========================================

async def test_analytics():

    # Create JWT token for admin
    admin_token = create_access_token(
        user_id=1,
        role="admin"
    )

    # Connect to Analytics MCP Server
    async with Client(
        "http://127.0.0.1:8008/mcp",
        auth=admin_token
    ) as client:

        result = await client.call_tool(
            "view_clinic_analytics",
            {}
        )

        print("\nCLINIC ANALYTICS RESULT:")
        print(result.data)


# ==========================================
# RUN TEST
# ==========================================

if __name__ == "__main__":
    asyncio.run(test_analytics())
