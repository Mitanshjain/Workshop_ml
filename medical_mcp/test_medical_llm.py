
# ==========================================
# MEDICAL LLM MCP - INTEGRATION TEST
# ==========================================

import asyncio

from fastmcp import Client
from medical_mcp.auth.jwt_handler import create_access_token


async def main():

    # Generate a test JWT
    token = create_access_token(
        user_id=1,
        role="user"
    )

    # Connect to Medical LLM MCP
    async with Client(
        "http://127.0.0.1:8004/mcp",
        auth=token
    ) as client:

        # Check registered tools
        tools = await client.list_tools()

        print("Available tools:")
        print([tool.name for tool in tools])

        # Test Groq LLM response
        result = await client.call_tool(
            "medical_llm_chat",
            {
                "message": "What are common symptoms of fever?"
            }
        )

        print("\nMedical LLM Response:")
        print(result.data)


if __name__ == "__main__":
    asyncio.run(main())
