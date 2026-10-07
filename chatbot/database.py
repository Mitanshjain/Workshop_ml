import mysql.connector


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mitansh@636782",
        database="sanjeevani_clinic"
    )

    return connection


# =========================================================
# PATIENT HISTORY
# =========================================================

def get_patient_history(patient_id: int):

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            doctor_name,
            problem,
            treatment,
            visit_date
        FROM patient_history
        WHERE patient_id = %s
        ORDER BY visit_date DESC
    """

    cursor.execute(
        query,
        (patient_id,)
    )

    history = cursor.fetchall()

    cursor.close()
    connection.close()

    return history


# =========================================================
# AVAILABLE DOCTORS / SLOTS FOR A SPECIFIC DATE
# =========================================================

def get_available_doctors(
    specialization,
    available_date
):

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            d.id,
            d.name,
            d.specialization,
            da.available_date,
            da.start_time,
            da.end_time
        FROM doctors d
        INNER JOIN doctor_availability da
            ON d.id = da.doctor_id
        WHERE LOWER(TRIM(d.specialization))
              = LOWER(TRIM(%s))

        AND DATE(da.available_date)
            = DATE(%s)

        AND da.is_available = TRUE

        AND NOT EXISTS (
            SELECT 1
            FROM appointments a
            WHERE a.doctor_id = d.id

            AND DATE(a.appointment_date)
                = DATE(da.available_date)

            AND a.start_time = da.start_time
            AND a.end_time = da.end_time

            AND a.status = 'booked'
        )

        ORDER BY
            da.start_time ASC
    """

    cursor.execute(
        query,
        (
            specialization,
            available_date
        )
    )

    doctors = cursor.fetchall()

    cursor.close()
    connection.close()

    return doctors


# =========================================================
# NEXT AVAILABLE DOCTORS / SLOTS
# =========================================================
#
# This is the important new function.
#
# It searches the REAL database for future availability.
#
# Example:
#
# Neurologist
# start date = 2026-09-30
#
# MySQL checks all future availability and returns
# the next available slots.
# =========================================================

def get_next_available_doctors(
    specialization,
    start_date,
    days_to_check=30,
    max_results=5
):

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            d.id,
            d.name,
            d.specialization,
            da.available_date,
            da.start_time,
            da.end_time

        FROM doctors d

        INNER JOIN doctor_availability da
            ON d.id = da.doctor_id

        WHERE LOWER(TRIM(d.specialization))
              = LOWER(TRIM(%s))

        AND DATE(da.available_date)
            >= DATE(%s)

        AND DATE(da.available_date)
            <= DATE_ADD(
                DATE(%s),
                INTERVAL %s DAY
            )

        AND da.is_available = TRUE

        AND NOT EXISTS (
            SELECT 1
            FROM appointments a

            WHERE a.doctor_id = d.id

            AND DATE(a.appointment_date)
                = DATE(da.available_date)

            AND a.start_time = da.start_time
            AND a.end_time = da.end_time

            AND a.status = 'booked'
        )

        ORDER BY
            da.available_date ASC,
            da.start_time ASC

        LIMIT %s
    """

    cursor.execute(
        query,
        (
            specialization,
            start_date,
            start_date,
            days_to_check,
            max_results
        )
    )

    doctors = cursor.fetchall()

    cursor.close()
    connection.close()

    return doctors


# =========================================================
# DOCTORS BY SPECIALIZATION
# =========================================================

def get_doctors_by_specialization(
    specialization
):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    query = """
        SELECT
            id,
            name,
            specialization,
            experience,
            phone
        FROM doctors
        WHERE LOWER(TRIM(specialization))
              = LOWER(TRIM(%s))
    """

    cursor.execute(
        query,
        (specialization,)
    )

    doctors = cursor.fetchall()

    cursor.close()
    connection.close()

    return doctors


# =========================================================
# BOOK APPOINTMENT
# =========================================================

def book_appointment(
    patient_id,
    doctor_id,
    appointment_date,
    start_time,
    end_time
):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    # -----------------------------------------------------
    # 1. Check whether slot is already booked
    # -----------------------------------------------------

    check_slot_query = """
        SELECT id
        FROM appointments
        WHERE doctor_id = %s

        AND appointment_date = %s
        AND start_time = %s
        AND end_time = %s

        AND status = 'booked'
    """

    cursor.execute(
        check_slot_query,
        (
            doctor_id,
            appointment_date,
            start_time,
            end_time
        )
    )

    existing_slot = cursor.fetchone()

    if existing_slot:

        cursor.close()
        connection.close()

        return None

    # -----------------------------------------------------
    # 2. Check duplicate appointment for same patient
    # -----------------------------------------------------

    duplicate_query = """
        SELECT id
        FROM appointments

        WHERE patient_id = %s
        AND doctor_id = %s
        AND appointment_date = %s
        AND start_time = %s
        AND end_time = %s

        AND status = 'booked'
    """

    cursor.execute(
        duplicate_query,
        (
            patient_id,
            doctor_id,
            appointment_date,
            start_time,
            end_time
        )
    )

    duplicate_appointment = (
        cursor.fetchone()
    )

    if duplicate_appointment:

        cursor.close()
        connection.close()

        return None

    # -----------------------------------------------------
    # 3. Insert appointment
    # -----------------------------------------------------

    insert_query = """
        INSERT INTO appointments
        (
            patient_id,
            doctor_id,
            appointment_date,
            start_time,
            end_time
        )

        VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        patient_id,
        doctor_id,
        appointment_date,
        start_time,
        end_time
    )

    cursor.execute(
        insert_query,
        values
    )

    connection.commit()

    appointment_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return appointment_id


# =========================================================
# PATIENT APPOINTMENTS
# =========================================================

def get_patient_appointments(
    patient_id: int
):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    query = """
        SELECT
            a.id,
            d.name AS doctor_name,
            d.specialization,
            a.appointment_date,
            a.start_time,
            a.end_time,
            a.status

        FROM appointments a

        INNER JOIN doctors d
            ON a.doctor_id = d.id

        WHERE a.patient_id = %s

        ORDER BY
            a.appointment_date DESC,
            a.start_time DESC
    """

    cursor.execute(
        query,
        (patient_id,)
    )

    appointments = cursor.fetchall()

    cursor.close()
    connection.close()

    return appointments


# =========================================================
# CANCEL APPOINTMENT
# =========================================================

def cancel_appointment(
    patient_id,
    appointment_id
):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    # -----------------------------------------------------
    # Check appointment belongs to patient
    # -----------------------------------------------------

    check_query = """
        SELECT id
        FROM appointments

        WHERE id = %s
        AND patient_id = %s
        AND status = 'booked'
    """

    cursor.execute(
        check_query,
        (
            appointment_id,
            patient_id
        )
    )

    appointment = cursor.fetchone()

    if not appointment:

        cursor.close()
        connection.close()

        return False

    # -----------------------------------------------------
    # Cancel appointment
    # -----------------------------------------------------

    update_query = """
        UPDATE appointments

        SET status = 'cancelled'

        WHERE id = %s
        AND patient_id = %s
    """

    cursor.execute(
        update_query,
        (
            appointment_id,
            patient_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return True


# =========================================================
# RESCHEDULE APPOINTMENT
# =========================================================

def reschedule_appointment(
    patient_id,
    appointment_id,
    doctor_id,
    appointment_date,
    start_time,
    end_time
):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    # -----------------------------------------------------
    # 1. Check existing appointment
    # -----------------------------------------------------

    check_query = """
        SELECT id
        FROM appointments

        WHERE id = %s
        AND patient_id = %s
        AND status = 'booked'
    """

    cursor.execute(
        check_query,
        (
            appointment_id,
            patient_id
        )
    )

    appointment = cursor.fetchone()

    if not appointment:

        cursor.close()
        connection.close()

        return False

    # -----------------------------------------------------
    # 2. Check new slot exists
    # -----------------------------------------------------

    availability_query = """
        SELECT id

        FROM doctor_availability

        WHERE doctor_id = %s
        AND available_date = %s
        AND start_time = %s
        AND end_time = %s
        AND is_available = TRUE
    """

    cursor.execute(
        availability_query,
        (
            doctor_id,
            appointment_date,
            start_time,
            end_time
        )
    )

    available_slot = cursor.fetchone()

    if not available_slot:

        cursor.close()
        connection.close()

        return False

    # -----------------------------------------------------
    # 3. Check whether new slot is already booked
    # -----------------------------------------------------

    slot_query = """
        SELECT id

        FROM appointments

        WHERE doctor_id = %s
        AND appointment_date = %s
        AND start_time = %s
        AND end_time = %s

        AND status = 'booked'

        AND id != %s
    """

    cursor.execute(
        slot_query,
        (
            doctor_id,
            appointment_date,
            start_time,
            end_time,
            appointment_id
        )
    )

    existing_slot = cursor.fetchone()

    if existing_slot:

        cursor.close()
        connection.close()

        return False

    # -----------------------------------------------------
    # 4. Update appointment
    # -----------------------------------------------------

    update_query = """
        UPDATE appointments

        SET
            doctor_id = %s,
            appointment_date = %s,
            start_time = %s,
            end_time = %s

        WHERE id = %s
        AND patient_id = %s
        AND status = 'booked'
    """

    cursor.execute(
        update_query,
        (
            doctor_id,
            appointment_date,
            start_time,
            end_time,
            appointment_id,
            patient_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return True


# =========================================================
# TEST DATABASE
# =========================================================

if __name__ == "__main__":

    print("\n===================================")
    print("TESTING SPECIFIC DATE")
    print("===================================\n")

    doctors = get_available_doctors(
        "Neurologist",
        "2026-09-30"
    )

    print("Available Doctors:")
    print(doctors)


    print("\n===================================")
    print("TESTING NEXT AVAILABLE")
    print("===================================\n")

    next_doctors = get_next_available_doctors(
        "Neurologist",
        "2026-09-30",
        days_to_check=30,
        max_results=5
    )

    print("Next Available Doctors:")

    for doctor in next_doctors:

        print(
            doctor["name"],
            "|",
            doctor["specialization"],
            "|",
            doctor["available_date"],
            "|",
            doctor["start_time"],
            "-",
            doctor["end_time"]
        )