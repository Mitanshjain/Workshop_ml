
import asyncio
from datetime import date, timedelta

from fastmcp import Client
from medical_mcp.auth.jwt_handler import create_access_token


MCP_SERVER_URL = "http://127.0.0.1:8003/mcp"

# Use a different slot from the previous database test.
# This test will insert one demo appointment.
appointment_date = (
    date.today() + timedelta(days=9)
).isoformat()

appointment_time = "11:00"


async def test_appointment_mcp():

    # ==========================================
    # TEST 1: VALID USER BOOKING
    # ==========================================

    print("\nTEST 1: Valid User Appointment Booking")

    user_token = create_access_token(
        user_id=1,
        role="user"
    )

    async with Client(
        MCP_SERVER_URL,
        auth=user_token
    ) as client:

        result = await client.call_tool(
            "book_doctor_appointment",
            {
                "patient_id": 1,
                "doctor_id": 1,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time
            }
        )

        print(result.data)

        assert result.data["success"] is True

    print("TEST 1 PASSED!")


    # ==========================================
    # TEST 2: PATIENT OWNERSHIP DENIED
    # ==========================================

    print("\nTEST 2: Another Patient Booking")

    async with Client(
        MCP_SERVER_URL,
        auth=user_token
    ) as client:

        result = await client.call_tool(
            "book_doctor_appointment",
            {
                "patient_id": 2,
                "doctor_id": 1,
                "appointment_date": appointment_date,
                "appointment_time": "12:00"
            }
        )

        print(result.data)

        assert result.data["success"] is False
        assert "ownership mismatch" in result.data["message"]

    print("TEST 2 PASSED: Ownership denied!")


    # ==========================================
    # TEST 3: SYSTEM ROLE DENIED
    # ==========================================

    print("\nTEST 3: System Role Booking")

    system_token = create_access_token(
        user_id=20,
        role="system"
    )

    async with Client(
        MCP_SERVER_URL,
        auth=system_token
    ) as client:

        result = await client.call_tool(
            "book_doctor_appointment",
            {
                "patient_id": 1,
                "doctor_id": 1,
                "appointment_date": appointment_date,
                "appointment_time": "12:00"
            }
        )

        print(result.data)

        assert result.data["success"] is False
        assert "Access denied" in result.data["message"]

    print("TEST 3 PASSED: System role denied!")


    # ==========================================
    # TEST 4: MISSING JWT
    # ==========================================

    print("\nTEST 4: Missing JWT")

    try:
        async with Client(MCP_SERVER_URL) as client:
            await client.call_tool(
                "book_doctor_appointment",
                {
                    "patient_id": 1,
                    "doctor_id": 1,
                    "appointment_date": appointment_date,
                    "appointment_time": "12:00"
                }
            )

    except Exception as e:
        print("Access denied:", type(e).__name__)

    else:
        raise AssertionError(
            "Missing JWT was unexpectedly accepted"
        )

    print("TEST 4 PASSED: Missing JWT rejected!")


    # ==========================================
    # TEST 5: DUPLICATE BOOKING
    # ==========================================

    print("\nTEST 5: Duplicate Doctor Slot")

    async with Client(
        MCP_SERVER_URL,
        auth=user_token
    ) as client:

        result = await client.call_tool(
            "book_doctor_appointment",
            {
                "patient_id": 1,
                "doctor_id": 1,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time
            }
        )

        print(result.data)

        assert result.data["success"] is False

    print("TEST 5 PASSED: Duplicate booking prevented!")


    # ==========================================
    # TEST 6: ADMIN ROLE BOOKING
    # ==========================================

    print("\nTEST 6: Admin Role Appointment Booking")

    admin_token = create_access_token(
        user_id=99,
        role="admin"
    )

    async with Client(
        MCP_SERVER_URL,
        auth=admin_token
    ) as client:

        result = await client.call_tool(
            "book_doctor_appointment",
            {
                "patient_id": 2,
                "doctor_id": 2,
                "appointment_date": appointment_date,
                "appointment_time": "17:00"
            }
        )

        print(result.data)

        assert result.data["success"] is True

    print("TEST 6 PASSED: Admin booking allowed!")


    # ==========================================
    # TEST 7: INVALID JWT
    # ==========================================

    print("\nTEST 7: Invalid JWT")

    try:
        async with Client(
            MCP_SERVER_URL,
            auth="invalid.jwt.token"
        ) as client:

            await client.call_tool(
                "book_doctor_appointment",
                {
                    "patient_id": 1,
                    "doctor_id": 1,
                    "appointment_date": appointment_date,
                    "appointment_time": "13:00"
                }
            )

    except Exception as e:
        print("Access denied:", type(e).__name__)

    else:
        raise AssertionError(
            "Invalid JWT was unexpectedly accepted"
        )

    print("TEST 7 PASSED: Invalid JWT rejected!")



    print("\nAll Appointment MCP tests passed!")


if __name__ == "__main__":
    asyncio.run(test_appointment_mcp())
