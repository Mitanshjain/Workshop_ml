
import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from medical_mcp.auth.jwt_handler import create_access_token


# ==========================================
# UNIFIED MCP CONFIGURATION
# ==========================================

MCP_URL = "http://127.0.0.1:8011/mcp"


# ==========================================
# TEST UNIFIED MCP SERVER
# ==========================================

async def main():

    # Local development testing only.
    # Use a real admin ID from your database.
    token = create_access_token(
        user_id=1,
        role="admin"
    )

    transport = StreamableHttpTransport(
        url=MCP_URL,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    async with Client(transport) as client:

        tools = await client.list_tools()

        print("\n========== UNIFIED MCP TOOLS ==========")
        print(f"Total tools: {len(tools)}")

        for tool in tools:
            print(f" - {tool.name}")

        print("\nUnified MCP tool discovery successful!")


if __name__ == "__main__":
    asyncio.run(main())
