
import sqlite3
import os


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DB_NAME = os.path.join(
    os.path.dirname(__file__),
    "clinic.db"
)


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def init_db():

    con = sqlite3.connect(DB_NAME)

    try:
        con.execute("PRAGMA foreign_keys = ON")

        cur = con.cursor()

        # ==========================================
        # DOCTORS TABLE
        # ==========================================

        cur.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY,
                name TEXT,
                specialization TEXT,
                timing TEXT
            )
        """)

        # ==========================================
        # PATIENTS TABLE
        # ==========================================

        cur.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER,
                city TEXT,
                blood_group TEXT
            )
        """)

        # ==========================================
        # APPOINTMENTS TABLE
        # ==========================================

        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'booked',

                FOREIGN KEY (patient_id)
                    REFERENCES patients(id),

                FOREIGN KEY (doctor_id)
                    REFERENCES doctors(id),

                UNIQUE (
                    doctor_id,
                    appointment_date,
                    appointment_time
                )
            )
        """)

        
        # ==========================================
        # INSURANCE POLICIES TABLE
        # ==========================================

        cur.execute("""
            CREATE TABLE IF NOT EXISTS insurance_policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                provider TEXT NOT NULL,
                policy_number TEXT NOT NULL UNIQUE,
                coverage_amount REAL NOT NULL,
                status TEXT NOT NULL,
                expiry_date TEXT NOT NULL,

                FOREIGN KEY (patient_id)
                    REFERENCES patients(id)
            )
        """)

        
        # ==========================================
        # ADMINS TABLE
        # ==========================================

        cur.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        """)



        # ==========================================
        # INSERT SAMPLE DOCTORS
        # ==========================================

        cur.execute("SELECT COUNT(*) FROM doctors")

        if cur.fetchone()[0] == 0:

            cur.executemany(
                """
                INSERT INTO doctors (
                    id,
                    name,
                    specialization,
                    timing
                )
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        1,
                        "Dr.Sharma",
                        "General Physician",
                        "10 AM - 2 PM"
                    ),
                    (
                        2,
                        "Dr.Mehta",
                        "Cardiologist",
                        "4 PM - 8 PM"
                    )
                ]
            )

        # ==========================================
        # INSERT SAMPLE PATIENTS
        # ==========================================

        cur.execute("SELECT COUNT(*) FROM patients")

        if cur.fetchone()[0] == 0:

            cur.executemany(
                """
                INSERT INTO patients (
                    id,
                    name,
                    age,
                    city,
                    blood_group
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        1,
                        "Rahul Sharma",
                        32,
                        "Jaipur",
                        "B+"
                    ),
                    (
                        2,
                        "Priya Verma",
                        28,
                        "Jaipur",
                        "O+"
                    ),
                    (
                        3,
                        "Amit Singh",
                        45,
                        "Ajmer",
                        "A+"
                    )
                ]
            )

            
        # ==========================================
        # INSERT SAMPLE INSURANCE POLICIES
        # ==========================================

        cur.execute(
            "SELECT COUNT(*) FROM insurance_policies"
        )

        if cur.fetchone()[0] == 0:

            cur.executemany(
                """
                INSERT INTO insurance_policies (
                    patient_id,
                    provider,
                    policy_number,
                    coverage_amount,
                    status,
                    expiry_date
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        1,
                        "Demo Health Insurance",
                        "DEMO-POL-1001",
                        500000,
                        "Active",
                        "2027-12-31"
                    ),
                    (
                        2,
                        "Demo Care Insurance",
                        "DEMO-POL-1002",
                        300000,
                        "Active",
                        "2027-06-30"
                    ),
                    (
                        3,
                        "Demo Secure Insurance",
                        "DEMO-POL-1003",
                        200000,
                        "Expired",
                        "2025-12-31"
                    )
                ]
            )


        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


# ==========================================
# GET DOCTOR DETAILS
# ==========================================

def get_doctor(name: str):

    con = sqlite3.connect(DB_NAME)

    try:
        cur = con.cursor()

        cur.execute(
            """
            SELECT
                id,
                name,
                specialization,
                timing
            FROM doctors
            WHERE LOWER(name) = LOWER(?)
            """,
            (name,)
        )

        result = cur.fetchone()

        return result

    finally:
        con.close()


# ==========================================
# GET PATIENT DETAILS
# ==========================================

def get_patient(patient_id: int):

    con = sqlite3.connect(DB_NAME)

    try:
        cur = con.cursor()

        cur.execute(
            """
            SELECT
                id,
                name,
                age,
                city,
                blood_group
            FROM patients
            WHERE id = ?
            """,
            (patient_id,)
        )

        result = cur.fetchone()

        return result

    finally:
        con.close()


# ==========================================
# BOOK DOCTOR APPOINTMENT
# ==========================================

def book_appointment(
    patient_id: int,
    doctor_id: int,
    appointment_date: str,
    appointment_time: str
):

    con = sqlite3.connect(DB_NAME)

    try:
        # Enable foreign key validation
        con.execute("PRAGMA foreign_keys = ON")

        cur = con.cursor()

        # ==========================================
        # INSERT APPOINTMENT
        # ==========================================

        cur.execute(
            """
            INSERT INTO appointments (
                patient_id,
                doctor_id,
                appointment_date,
                appointment_time
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                patient_id,
                doctor_id,
                appointment_date,
                appointment_time
            )
        )

        con.commit()

        return {
            "success": True,
            "message": "Appointment booked successfully.",
            "appointment_id": cur.lastrowid
        }

    except sqlite3.IntegrityError:

        con.rollback()

        return {
            "success": False,
            "message": (
                "Booking failed. Doctor slot may already "
                "be booked, or patient/doctor ID is invalid."
            ),
            "appointment_id": None
        }

    finally:
        con.close()


# ==========================================
# GET INSURANCE DETAILS
# ==========================================

def get_insurance(patient_id: int):

    con = sqlite3.connect(DB_NAME)

    try:
        cur = con.cursor()

        cur.execute(
            """
            SELECT
                id,
                patient_id,
                provider,
                policy_number,
                coverage_amount,
                status,
                expiry_date
            FROM insurance_policies
            WHERE patient_id = ?
            """,
            (patient_id,)
        )

        result = cur.fetchone()

        return result

    finally:
        con.close()


# ==========================================
# GET ADMIN BY USERNAME
# ==========================================

def get_admin_by_username(username: str):

    con = sqlite3.connect(DB_NAME)

    try:
        con.row_factory = sqlite3.Row

        cur = con.cursor()

        cur.execute(
            """
            SELECT
                id,
                username,
                password_hash,
                is_active
            FROM admins
            WHERE username = ?
            """,
            (username,)
        )

        admin = cur.fetchone()

        if admin is None:
            return None

        return dict(admin)

    finally:
        con.close()



# ==========================================
# ADD DOCTOR
# ==========================================

def add_doctor(
    name: str,
    specialization: str,
    timing: str
) -> dict:

    name = name.strip()
    specialization = specialization.strip()
    timing = timing.strip()

    # Validate doctor information
    if not name or not specialization or not timing:
        return {
            "success": False,
            "message": "All doctor fields are required."
        }

    con = sqlite3.connect(DB_NAME)

    try:
        cur = con.cursor()

        cur.execute(
            """
            INSERT INTO doctors (
                name,
                specialization,
                timing
            )
            VALUES (?, ?, ?)
            """,
            (name, specialization, timing)
        )

        con.commit()

        return {
            "success": True,
            "message": "Doctor added successfully.",
            "doctor_id": cur.lastrowid
        }

    except sqlite3.Error:
        con.rollback()
        return {
            "success": False,
            "message": "Unable to add doctor."
        }

    finally:
        con.close()



# ==========================================
# GET ALL DOCTORS
# ==========================================

def get_all_doctors() -> dict:

    con = sqlite3.connect(DB_NAME)

    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute(
            """
            SELECT
                id,
                name,
                specialization,
                timing
            FROM doctors
            ORDER BY id
            """
        )

        doctors = [
            dict(row)
            for row in cur.fetchall()
        ]

        return {
            "success": True,
            "total_doctors": len(doctors),
            "doctors": doctors
        }

    except sqlite3.Error:
        return {
            "success": False,
            "message": "Unable to retrieve doctors."
        }

    finally:
        con.close()



# ==========================================
# UPDATE DOCTOR DETAILS
# ==========================================

def update_doctor(
    doctor_id: int,
    name: str,
    specialization: str,
    timing: str
) -> dict:

    # Validate input
    if doctor_id <= 0:
        return {
            "success": False,
            "message": "Invalid doctor ID."
        }

    name = name.strip()
    specialization = specialization.strip()
    timing = timing.strip()

    if not name or not specialization or not timing:
        return {
            "success": False,
            "message": "All doctor fields are required."
        }

    con = sqlite3.connect(DB_NAME)

    try:
        cur = con.cursor()

        # Check doctor exists
        cur.execute(
            "SELECT id FROM doctors WHERE id = ?",
            (doctor_id,)
        )

        if cur.fetchone() is None:
            return {
                "success": False,
                "message": "Doctor not found."
            }

        # Update doctor information
        cur.execute(
            """
            UPDATE doctors
            SET name = ?,
                specialization = ?,
                timing = ?
            WHERE id = ?
            """,
            (name, specialization, timing, doctor_id)
        )

        con.commit()

        return {
            "success": True,
            "message": "Doctor updated successfully.",
            "doctor_id": doctor_id
        }

    except sqlite3.Error:
        con.rollback()

        return {
            "success": False,
            "message": "Unable to update doctor."
        }

    finally:
        con.close()



# ==========================================
# DELETE DOCTOR
# ==========================================

def delete_doctor(doctor_id: int) -> dict:

    if doctor_id <= 0:
        return {
            "success": False,
            "message": "Invalid doctor ID."
        }

    con = sqlite3.connect(DB_NAME)

    try:
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()

        # Check doctor exists
        cur.execute(
            "SELECT id FROM doctors WHERE id = ?",
            (doctor_id,)
        )

        if cur.fetchone() is None:
            return {
                "success": False,
                "message": "Doctor not found."
            }

        # Check existing appointments
        cur.execute(
            """
            SELECT COUNT(*)
            FROM appointments
            WHERE doctor_id = ?
            """,
            (doctor_id,)
        )

        appointment_count = cur.fetchone()[0]

        if appointment_count > 0:
            return {
                "success": False,
                "message": "Cannot delete doctor with existing appointments."
            }

        # Delete doctor
        cur.execute(
            "DELETE FROM doctors WHERE id = ?",
            (doctor_id,)
        )

        con.commit()

        return {
            "success": True,
            "message": "Doctor deleted successfully.",
            "doctor_id": doctor_id
        }

    except sqlite3.Error:
        con.rollback()

        return {
            "success": False,
            "message": "Unable to delete doctor."
        }

    finally:
        con.close()



# ==========================================
# APPOINTMENT MANAGEMENT
# VIEW ALL APPOINTMENTS
# ==========================================

def get_all_appointments():

    con = sqlite3.connect(DB_NAME)

    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute("""
            SELECT
                a.id AS appointment_id,
                a.patient_id,
                a.doctor_id,
                d.name AS doctor_name,
                a.appointment_date,
                a.appointment_time,
                a.status
            FROM appointments AS a
            JOIN doctors AS d
                ON a.doctor_id = d.id
            ORDER BY
                a.appointment_date DESC,
                a.appointment_time DESC
        """)

        appointments = [
            dict(row)
            for row in cur.fetchall()
        ]

        return {
            "success": True,
            "total_appointments": len(appointments),
            "appointments": appointments
        }

    except sqlite3.Error as error:

        return {
            "success": False,
            "message": "Unable to retrieve appointments."
        }

    finally:
        con.close()


# ==========================================
# UPDATE APPOINTMENT STATUS
# ==========================================

def update_appointment_status(
    appointment_id: int,
    status: str
) -> dict:

    allowed_statuses = {
        "booked",
        "completed",
        "cancelled"
    }

    status = status.strip().lower()

    # Validate status
    if status not in allowed_statuses:
        return {
            "success": False,
            "message": "Invalid appointment status."
        }

    if appointment_id <= 0:
        return {
            "success": False,
            "message": "Invalid appointment ID."
        }

    con = None

    try:
        con = sqlite3.connect(DB_NAME)

        con.execute("PRAGMA foreign_keys = ON")

        cur = con.cursor()

        # Check appointment exists
        cur.execute(
            """
            SELECT status
            FROM appointments
            WHERE id = ?
            """,
            (appointment_id,)
        )

        appointment = cur.fetchone()

        if appointment is None:
            return {
                "success": False,
                "message": "Appointment not found."
            }

        old_status = appointment[0]

        # Avoid unnecessary updates
        if old_status == status:
            return {
                "success": True,
                "message": "Appointment already has this status."
            }

        # Prevent reopening finalized appointments
        if old_status in ("completed", "cancelled"):
            return {
                "success": False,
                "message": "Finalized appointments cannot be changed."
            }

        # Update status
        cur.execute(
            """
            UPDATE appointments
            SET status = ?
            WHERE id = ?
            """,
            (status, appointment_id)
        )

        con.commit()

        return {
            "success": True,
            "message": "Appointment status updated successfully.",
            "appointment_id": appointment_id,
            "old_status": old_status,
            "new_status": status
        }

    except sqlite3.Error as error:

        if con is not None:
            con.rollback()

        return {
            "success": False,
            "message": str(error)
        }

    finally:
        if con is not None:
            con.close()



# ==========================================
# CLINIC ANALYTICS - DATABASE FUNCTION
# ==========================================

def get_clinic_analytics() -> dict:

    con = None

    try:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        # Total doctors
        cur.execute("SELECT COUNT(*) FROM doctors")
        total_doctors = cur.fetchone()[0]

        # Total patients
        cur.execute("SELECT COUNT(*) FROM patients")
        total_patients = cur.fetchone()[0]

        # Total appointments
        cur.execute("SELECT COUNT(*) FROM appointments")
        total_appointments = cur.fetchone()[0]

        # Appointments grouped by status
        cur.execute("""
            SELECT status, COUNT(*)
            FROM appointments
            GROUP BY status
        """)

        status_counts = {
            status: count
            for status, count in cur.fetchall()
        }

        return {
            "success": True,
            "analytics": {
                "total_doctors": total_doctors,
                "total_patients": total_patients,
                "total_appointments": total_appointments,
                "booked_appointments": status_counts.get("booked", 0),
                "completed_appointments": status_counts.get("completed", 0),
                "cancelled_appointments": status_counts.get("cancelled", 0)
            }
        }

    except sqlite3.Error as error:
        return {
            "success": False,
            "message": str(error)
        }

    finally:
        if con is not None:
            con.close()
