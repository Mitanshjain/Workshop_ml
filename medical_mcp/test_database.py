from medical_mcp.database import (
    DB_NAME,
    get_doctor,
    init_db
)

print("Database Path:", DB_NAME)

# Initialize database and sample records
init_db()

# Check existing doctor
doctor = get_doctor("Dr. Sharma")

print("Doctor Found:", doctor)