
from datetime import date, timedelta

from medical_mcp.database import book_appointment


# ==========================================
# GENERATE FUTURE APPOINTMENT DATE
# ==========================================

appointment_date = (
    date.today() + timedelta(days=7)
).isoformat()

appointment_time = "10:00"


# ==========================================
# TEST 1: BOOK AN APPOINTMENT
# ==========================================

print("\nTEST 1: Book Appointment")

result = book_appointment(
    patient_id=1,
    doctor_id=1,
    appointment_date=appointment_date,
    appointment_time=appointment_time
)

print(result)

assert result["success"] is True

print("TEST 1 PASSED: Appointment booked!")


# ==========================================
# TEST 2: PREVENT DOUBLE BOOKING
# ==========================================

print("\nTEST 2: Duplicate Doctor Slot")

result = book_appointment(
    patient_id=2,
    doctor_id=1,
    appointment_date=appointment_date,
    appointment_time=appointment_time
)

print(result)

assert result["success"] is False

print("TEST 2 PASSED: Duplicate booking prevented!")


# ==========================================
# FINAL RESULT
# ==========================================

print("\nAll appointment database tests passed!")
