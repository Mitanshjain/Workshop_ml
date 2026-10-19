
import asyncio

from fastmcp import Client

from medical_mcp.auth.jwt_handler import create_access_token


# ==========================================
# TEST DOCTOR MANAGEMENT MCP
# ==========================================

async def main():

    mcp_url = "http://127.0.0.1:8006/mcp"

    # ======================================
    # GENERATE TEST JWT TOKENS
    # ======================================

    admin_token = create_access_token(
        user_id=1,
        role="admin"
    )

    patient_token = create_access_token(
        user_id=1,
        role="user"
    )

    # ======================================
    # TEST 0: CHECK REGISTERED MCP TOOLS
    # ======================================

    async with Client(mcp_url, auth=admin_token) as client:

        tools = await client.list_tools()

        registered_tools = [tool.name for tool in tools]

        print("\nREGISTERED MCP TOOLS:")

        for tool_name in registered_tools:
            print("-", tool_name)

    # ======================================
    # TEST 1: ADMIN ACCESS
    # ======================================

    async with Client(mcp_url, auth=admin_token) as client:

        result = await client.call_tool(
            "check_admin_access",
            {}
        )

        print("\nADMIN RESULT:")
        print(result.data)

    # ======================================
    # TEST 2: PATIENT ACCESS
    # ======================================

    async with Client(mcp_url, auth=patient_token) as client:

        result = await client.call_tool(
            "check_admin_access",
            {}
        )

        print("\nPATIENT RESULT:")
        print(result.data)

    # ======================================
    # CHECK ADD DOCTOR TOOL AVAILABILITY
    # ======================================

    if "add_new_doctor" not in registered_tools:

        print("\nERROR: add_new_doctor tool is not registered.")
        print("Check doctor_management_mcp.py.")
        print("Restart the MCP server on port 8006.")

        return

    # ======================================
    # TEST 3: ADMIN ADDS A DOCTOR
    # ======================================

    async with Client(mcp_url, auth=admin_token) as client:

        result = await client.call_tool(
            "add_new_doctor",
            {
                "name": "Dr. Kumar",
                "specialization": "Dermatologist",
                "timing": "10 AM - 2 PM"
            }
        )

        print("\nADMIN ADD DOCTOR RESULT:")
        print(result.data)

    # ======================================
    # TEST 4: PATIENT CANNOT ADD A DOCTOR
    # ======================================

    async with Client(mcp_url, auth=patient_token) as client:

        result = await client.call_tool(
            "add_new_doctor",
            {
                "name": "Dr. Unauthorized",
                "specialization": "Cardiologist",
                "timing": "4 PM - 8 PM"
            }
        )

        print("\nPATIENT ADD DOCTOR RESULT:")
        print(result.data)


        
    # ======================================
    # TEST 5: ADMIN VIEWS ALL DOCTORS
    # ======================================

    async with Client(mcp_url, auth=admin_token) as client:

        result = await client.call_tool(
            "view_all_doctors",
            {}
        )

        print("\nADMIN VIEW ALL DOCTORS:")
        print(result.data)

    # ======================================
    # TEST 6: PATIENT CANNOT VIEW ADMIN TOOL
    # ======================================

    async with Client(mcp_url, auth=patient_token) as client:

        result = await client.call_tool(
            "view_all_doctors",
            {}
        )

        print("\nPATIENT VIEW ALL DOCTORS:")
        print(result.data)



# ==========================================
# RUN TESTS
# ==========================================

if __name__ == "__main__":
    asyncio.run(main())
