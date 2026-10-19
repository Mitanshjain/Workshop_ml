from .groq_client import (
    ask_groq,
    ask_groq_with_image
)

from .database import (
    get_patient_history,
    get_patient_appointments,
    get_doctors_by_specialization,
    get_available_doctors,
    book_appointment,
    cancel_appointment,
    reschedule_appointment
)

import re

from datetime import (
    date,
    datetime,
    timedelta
)

from calendar import (
    month_name,
    month_abbr
)


# =========================================================
# PATIENT-SPECIFIC CHATBOT STATE
# =========================================================

patient_states = {}


def get_patient_state(patient_id):

    if patient_id not in patient_states:

        patient_states[patient_id] = {
            "conversation_history": [],

            # Booking
            "available_slot_options": [],
            "pending_appointment": None,
            "last_requested_date": None,

            # Cancellation
            "pending_cancellation": None,
            "pending_cancellation_options": [],

            # Reschedule
            "pending_reschedule": None
        }

    return patient_states[patient_id]


# =========================================================
# DOCTOR NAME FORMAT
# =========================================================

def format_doctor_name(name):

    name = str(name).strip()

    if name.lower().startswith("dr. "):
        return name

    if name.lower().startswith("dr "):
        return "Dr. " + name[3:].strip()

    return f"Dr. {name}"


# =========================================================
# SAVE CONVERSATION
# =========================================================

def save_conversation(
    state,
    message,
    response
):

    state["conversation_history"].append({
        "role": "user",
        "content": message
    })

    state["conversation_history"].append({
        "role": "assistant",
        "content": response
    })


# =========================================================
# DATE DETECTION
# =========================================================
#
# Supports:
#
# 25 September
# 25 September 2026
# 25 Sept
# 25 Sept 2026
# 25/09/2026
# 25-09-2026
# 2026-09-25
# 27
# today
# tomorrow
#
# IMPORTANT:
# A past month/day date is NOT silently moved to next year.
#
# Example:
# Today = 29 September 2026
#
# "27 September"
# becomes:
# 2026-09-27
#
# Then the booking logic can clearly tell the patient
# that this date has already passed.
# =========================================================

def detect_date(
    message,
    allow_day_only=True
):

    text = str(message).strip().lower()

    today = date.today()


    # -----------------------------------------------------
    # TODAY
    # -----------------------------------------------------

    if text == "today":

        return today.isoformat()


    # -----------------------------------------------------
    # TOMORROW
    # -----------------------------------------------------

    if text == "tomorrow":

        tomorrow = (
            today +
            timedelta(days=1)
        )

        return tomorrow.isoformat()


    # -----------------------------------------------------
    # YYYY-MM-DD
    #
    # Example:
    # 2026-10-02
    # -----------------------------------------------------

    match = re.search(
        r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b",
        text
    )

    if match:

        try:

            selected_date = date(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3))
            )

            return selected_date.isoformat()

        except ValueError:

            return None


    # -----------------------------------------------------
    # DD/MM/YYYY
    # DD-MM-YYYY
    #
    # Examples:
    # 25/09/2026
    # 25-09-2026
    # -----------------------------------------------------

    match = re.search(
        r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b",
        text
    )

    if match:

        try:

            selected_date = date(
                int(match.group(3)),
                int(match.group(2)),
                int(match.group(1))
            )

            return selected_date.isoformat()

        except ValueError:

            return None


    # -----------------------------------------------------
    # MONTH NAME MAPPING
    # -----------------------------------------------------

    months = {}

    for index, name in enumerate(month_name):

        if name:

            months[name.lower()] = index


    for index, name in enumerate(month_abbr):

        if name:

            months[name.lower()] = index


    # -----------------------------------------------------
    # DD MONTH
    # DD MONTH YYYY
    #
    # Examples:
    #
    # 25 September
    # 25 September 2026
    # 25 Sept
    # 25 Sept 2026
    # 2 October
    # -----------------------------------------------------

    match = re.search(
        r"\b(\d{1,2})\s+([a-z]+)(?:\s+(\d{4}))?\b",
        text
    )

    if match:

        day = int(match.group(1))

        month_text = match.group(2)

        year_text = match.group(3)

        month = months.get(month_text)

        if month:

            try:

                if year_text:

                    year = int(year_text)

                else:

                    year = today.year


                selected_date = date(
                    year,
                    month,
                    day
                )


                # IMPORTANT:
                #
                # Do NOT automatically change a past date
                # to next year.
                #
                # Example:
                #
                # Today = 29 September 2026
                # User = 27 September
                #
                # Result = 2026-09-27
                #
                # The booking logic will then tell the
                # patient that the date has passed.

                return selected_date.isoformat()

            except ValueError:

                return None


    # -----------------------------------------------------
    # DAY ONLY
    #
    # Example:
    #
    # 30
    #
    # This uses the current month first.
    # If that date does not exist, it tries next month.
    # -----------------------------------------------------

    if allow_day_only:

        match = re.fullmatch(
            r"\d{1,2}",
            text
        )

        if match:

            day = int(match.group())

            if 1 <= day <= 31:

                # -----------------------------------------
                # CURRENT MONTH
                # -----------------------------------------

                try:

                    selected_date = date(
                        today.year,
                        today.month,
                        day
                    )

                    return selected_date.isoformat()

                except ValueError:

                    pass


                # -----------------------------------------
                # NEXT MONTH
                # -----------------------------------------

                if today.month == 12:

                    next_month = 1

                    next_year = (
                        today.year + 1
                    )

                else:

                    next_month = (
                        today.month + 1
                    )

                    next_year = today.year


                try:

                    selected_date = date(
                        next_year,
                        next_month,
                        day
                    )

                    return selected_date.isoformat()

                except ValueError:

                    return None


    return None


# =========================================================
# CHECK PAST DATE
# =========================================================

def is_past_date(date_string):

    try:

        selected_date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        ).date()

        return selected_date < date.today()

    except (
        ValueError,
        TypeError
    ):

        return False


# =========================================================
# FORMAT DATE FOR CHAT
# =========================================================

def format_date_for_chat(date_string):

    try:

        selected_date = datetime.strptime(
            str(date_string),
            "%Y-%m-%d"
        )

        return selected_date.strftime(
            "%d %B %Y"
        )

    except (
        ValueError,
        TypeError
    ):

        return str(date_string)


# =========================================================
# FORMAT TIME FOR CHAT
# =========================================================

def format_time_for_chat(time_value):

    if time_value is None:

        return ""


    # datetime.time / datetime.datetime

    if hasattr(time_value, "strftime"):

        try:

            return time_value.strftime(
                "%I:%M %p"
            ).lstrip("0")

        except Exception:

            pass


    text = str(time_value).strip()


    # -----------------------------------------
    # HH:MM:SS
    # -----------------------------------------

    for time_format in (
        "%H:%M:%S",
        "%H:%M"
    ):

        try:

            parsed_time = datetime.strptime(
                text,
                time_format
            )

            return parsed_time.strftime(
                "%I:%M %p"
            ).lstrip("0")

        except ValueError:

            pass


    # -----------------------------------------
    # Numeric seconds
    #
    # Example:
    # 57600 = 16:00
    # -----------------------------------------

    try:

        seconds = int(float(text))

        if 0 <= seconds < 86400:

            hours = seconds // 3600

            minutes = (
                seconds % 3600
            ) // 60

            parsed_time = datetime(
                2000,
                1,
                1,
                hours,
                minutes
            )

            return parsed_time.strftime(
                "%I:%M %p"
            ).lstrip("0")

    except (
        ValueError,
        TypeError
    ):

        pass


    return text


# =========================================================
# AVAILABILITY SEARCH REQUEST
# =========================================================

def is_availability_search_request(
    message_lower
):

    phrases = [

        "which date is available",
        "which dates are available",

        "which date is free",
        "which dates are free",

        "which slot is available",
        "which slots are available",

        "which slot is free",
        "which slots are free",

        "next available",
        "next available slot",
        "next available slots",

        "next available date",
        "next available dates",

        "show available dates",
        "show available slots",

        "show me available dates",
        "show me available slots",

        "let me know which date",
        "let me know which dates",

        "let me know which slot",
        "let me know which slots",

        "then let me know which date",
        "then let me know which dates",

        "then let me know which slot",
        "then let me know which slots",

        "then let me know which date is available",

        "then let me know which date or slot are free",

        "let me know which date or slot are free",

        "what date is available",
        "what dates are available",

        "what date is free",
        "what dates are free",

        "what slots are available",
        "what slot is available",

        "find me a slot",
        "find a slot",

        "find an available slot",
        "find available slots",

        "find me an available slot",
        "find me available slots"
    ]

    return any(
        phrase in message_lower
        for phrase in phrases
    )


# =========================================================
# FIND NEXT AVAILABLE APPOINTMENTS
# =========================================================

def find_next_available_slots(
    specialization,
    start_date=None,
    days_to_check=30,
    max_results=5
):

    if start_date is None:

        start_date = (
            date.today()
            + timedelta(days=1)
        )


    # Convert string date to date object

    if isinstance(
        start_date,
        str
    ):

        try:

            start_date = datetime.strptime(
                start_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            start_date = (
                date.today()
                + timedelta(days=1)
            )


    results = []


    # -----------------------------------------------------
    # Check each future date against the REAL database
    # -----------------------------------------------------

    for day_offset in range(
        days_to_check
    ):

        check_date = (
            start_date
            + timedelta(days=day_offset)
        )


        slots = get_available_doctors(
            specialization,
            check_date.isoformat()
        )


        if slots:

            for slot in slots:

                results.append(slot)


                if (
                    len(results)
                    >= max_results
                ):

                    return results


    return results


# =========================================================
# NUMBER DETECTION
# =========================================================

def detect_number(message_lower):

    if message_lower in [
        "1",
        "slot 1",
        "option 1",
        "appointment 1",
        "appointment number 1"
    ]:

        return 1


    if message_lower in [
        "2",
        "slot 2",
        "option 2",
        "appointment 2",
        "appointment number 2"
    ]:

        return 2


    if message_lower in [
        "3",
        "slot 3",
        "option 3",
        "appointment 3",
        "appointment number 3"
    ]:

        return 3


    if message_lower in [
        "4",
        "slot 4",
        "option 4",
        "appointment 4",
        "appointment number 4"
    ]:

        return 4


    if message_lower in [
        "5",
        "slot 5",
        "option 5",
        "appointment 5",
        "appointment number 5"
    ]:

        return 5


    return None


# =========================================================
# BOOKING CONFIRMATION
# =========================================================

def is_booking_confirmation(
    message_lower
):

    return message_lower in [
        "yes",
        "yes please",
        "yes book",
        "yes book it",
        "book it",
        "book this",
        "confirm",
        "confirm it",
        "please book"
    ]


# =========================================================
# CANCELLATION CONFIRMATION
# =========================================================

def is_cancel_confirmation(
    message_lower
):

    return message_lower in [
        "yes",
        "yes cancel",
        "cancel it",
        "confirm",
        "confirm cancellation",
        "confirm cancel"
    ]


# =========================================================
# RESCHEDULE CONFIRMATION
# =========================================================

def is_reschedule_confirmation(
    message_lower
):

    return message_lower in [
        "yes",
        "yes please",
        "yes reschedule",
        "reschedule it",
        "confirm",
        "confirm reschedule",
        "please reschedule"
    ]


# =========================================================
# SPECIALIZATION DETECTION
# =========================================================

def detect_specialization(
    message_lower
):

    if "neurologist" in message_lower:

        return "Neurologist"


    if "orthopedic" in message_lower:

        return "Orthopedic"


    if "general physician" in message_lower:

        return "General Physician"


    if "dermatologist" in message_lower:

        return "Dermatologist"


    return None


# =========================================================
# REMEMBER SPECIALIZATION
# =========================================================

def get_previous_specialization(
    state
):

    conversation_history = (
        state["conversation_history"]
    )


    for item in reversed(
        conversation_history
    ):

        if item["role"] != "user":

            continue


        previous_message = (
            item["content"].lower()
        )


        specialization = (
            detect_specialization(
                previous_message
            )
        )


        if specialization:

            return specialization


    return None


# =========================================================
# IMAGE CHATBOT
# =========================================================

def chat_with_patient_image(
    message,
    patient_id,
    image_bytes,
    image_type
):

    if not patient_id:

        return (
            "Please login first before using "
            "the injury image feature."
        )


    try:

        response = ask_groq_with_image(
            message=message,
            image_bytes=image_bytes,
            image_type=image_type
        )

        return response


    except Exception:

        return (
            "I'm sorry, I couldn't analyze the image "
            "right now. Please describe the injury to me "
            "and I will try to help you."
        )


# =========================================================
# MAIN CHAT FUNCTION
# =========================================================

def chat_with_patient(
    message: str,
    patient_id: int = None
):

    # -----------------------------------------------------
    # Patient must be logged in
    # -----------------------------------------------------

    if not patient_id:

        return (
            "Please login first before using "
            "the clinic chatbot."
        )


    # -----------------------------------------------------
    # Get this patient's state only
    # -----------------------------------------------------

    state = get_patient_state(
        patient_id
    )

    conversation_history = (
        state["conversation_history"]
    )

    message_lower = (
        message.lower().strip()
    )


    # =====================================================
    # 1. GET PATIENT HISTORY
    # =====================================================

    patient_history = get_patient_history(
        patient_id
    )


    # =====================================================
    # 2. GET PATIENT APPOINTMENTS
    # =====================================================

    appointments = get_patient_appointments(
        patient_id
    )


    # =====================================================
    # 3. DETECT CANCEL REQUEST
    # =====================================================

    cancel_words = [
        "cancel appointment",
        "cancel my appointment",
        "cancel appointment please",
        "i want to cancel",
        "i want to cancel my appointment"
    ]

    cancellation_request = any(
        word in message_lower
        for word in cancel_words
    )


    # =====================================================
    # 4. DETECT RESCHEDULE REQUEST
    # =====================================================

    reschedule_words = [
        "reschedule appointment",
        "reschedule my appointment",
        "i want to reschedule",
        "i want to reschedule my appointment",
        "change my appointment",
        "change appointment"
    ]

    reschedule_request = any(
        word in message_lower
        for word in reschedule_words
    )


    # =====================================================
    # 5. START CANCELLATION FLOW
    # =====================================================

    if cancellation_request:

        state["pending_appointment"] = None

        state["available_slot_options"] = []

        state["pending_reschedule"] = None

        state["pending_cancellation"] = None

        state["pending_cancellation_options"] = []


        booked_appointments = [
            appointment
            for appointment in appointments
            if appointment["status"] == "booked"
        ]


        # -------------------------------------------------
        # NO APPOINTMENTS
        # -------------------------------------------------

        if not booked_appointments:

            response = (
                "You currently do not have any booked "
                "appointments to cancel."
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        # -------------------------------------------------
        # ONE APPOINTMENT
        # -------------------------------------------------

        if len(booked_appointments) == 1:

            state["pending_cancellation"] = (
                booked_appointments[0]
            )

            appointment = (
                state["pending_cancellation"]
            )

            response = (
                "You have one booked appointment:\n\n"

                f"Doctor: "
                f"{format_doctor_name(appointment['doctor_name'])}\n"

                f"Specialization: "
                f"{appointment['specialization']}\n"

                f"Date: "
                f"{appointment['appointment_date']}\n"

                f"Time: "
                f"{format_time_for_chat(appointment['start_time'])} "
                f"to "
                f"{format_time_for_chat(appointment['end_time'])}\n\n"

                "Would you like me to cancel "
                "this appointment?"
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        # -------------------------------------------------
        # MULTIPLE APPOINTMENTS
        # -------------------------------------------------

        state["pending_cancellation_options"] = (
            booked_appointments
        )

        response = (
            "You have the following booked "
            "appointments:\n\n"
        )


        for index, appointment in enumerate(
            booked_appointments,
            start=1
        ):

            response += (
                f"{index}. "
                f"{format_doctor_name(appointment['doctor_name'])} | "
                f"{appointment['specialization']} | "
                f"{appointment['appointment_date']} | "
                f"{format_time_for_chat(appointment['start_time'])} - "
                f"{format_time_for_chat(appointment['end_time'])}\n"
            )


        response += (
            "\nPlease enter the NUMBER of the "
            "appointment you would like to cancel."
        )


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 6. CANCEL APPOINTMENT NUMBER
    # =====================================================

    pending_cancellation_options = (
        state["pending_cancellation_options"]
    )


    if pending_cancellation_options:

        appointment_number = detect_number(
            message_lower
        )


        if appointment_number is None:

            response = (
                "Please enter the NUMBER of the "
                "appointment you would like to cancel."
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        if (
            appointment_number < 1
            or appointment_number >
            len(pending_cancellation_options)
        ):

            response = (
                "That appointment number is not valid. "
                "Please select one of the appointments "
                "listed above."
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        selected_appointment = (
            pending_cancellation_options[
                appointment_number - 1
            ]
        )


        state["pending_cancellation"] = (
            selected_appointment
        )

        state["pending_cancellation_options"] = []


        response = (
            f"You selected appointment "
            f"number {appointment_number}:\n\n"

            f"Doctor: "
            f"{format_doctor_name(selected_appointment['doctor_name'])}\n"

            f"Specialization: "
            f"{selected_appointment['specialization']}\n"

            f"Date: "
            f"{selected_appointment['appointment_date']}\n"

            f"Time: "
            f"{format_time_for_chat(selected_appointment['start_time'])} "
            f"to "
            f"{format_time_for_chat(selected_appointment['end_time'])}\n\n"

            "Would you like me to cancel "
            "this appointment?"
        )


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 7. CONFIRM CANCELLATION
    # =====================================================

    pending_cancellation = (
        state["pending_cancellation"]
    )


    if (
        pending_cancellation is not None
        and is_cancel_confirmation(
            message_lower
        )
    ):

        appointment_id = (
            pending_cancellation["id"]
        )


        cancelled = cancel_appointment(
            patient_id,
            appointment_id
        )


        if cancelled:

            response = (
                "✅ Your appointment has been "
                "cancelled successfully.\n\n"

                f"Doctor: "
                f"{format_doctor_name(pending_cancellation['doctor_name'])}\n"

                f"Specialization: "
                f"{pending_cancellation['specialization']}\n"

                f"Date: "
                f"{pending_cancellation['appointment_date']}\n"

                f"Time: "
                f"{format_time_for_chat(pending_cancellation['start_time'])} "
                f"to "
                f"{format_time_for_chat(pending_cancellation['end_time'])}"
            )

        else:

            response = (
                "Sorry, I could not cancel this "
                "appointment. It may already be "
                "cancelled or unavailable."
            )


        state["pending_cancellation"] = None

        state["pending_cancellation_options"] = []


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 8. START RESCHEDULE FLOW
    # =====================================================

    if reschedule_request:

        state["pending_appointment"] = None

        state["available_slot_options"] = []

        state["pending_cancellation"] = None

        state["pending_cancellation_options"] = []


        booked_appointments = [
            appointment
            for appointment in appointments
            if appointment["status"] == "booked"
        ]


        if not booked_appointments:

            response = (
                "You currently do not have any booked "
                "appointments to reschedule."
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        state["pending_reschedule"] = {
            "stage": "select_appointment",
            "appointment": None,
            "new_date": None,
            "available_slots": [],
            "slot": None
        }


        response = (
            "You have the following booked "
            "appointments:\n\n"
        )


        for index, appointment in enumerate(
            booked_appointments,
            start=1
        ):

            response += (
                f"{index}. "
                f"{format_doctor_name(appointment['doctor_name'])} | "
                f"{appointment['specialization']} | "
                f"{appointment['appointment_date']} | "
                f"{format_time_for_chat(appointment['start_time'])} - "
                f"{format_time_for_chat(appointment['end_time'])}\n"
            )


        response += (
            "\nPlease enter the NUMBER of the "
            "appointment you would like to reschedule."
        )


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 9. RESCHEDULE - SELECT OLD APPOINTMENT
    # =====================================================

    pending_reschedule = (
        state["pending_reschedule"]
    )


    if (
        pending_reschedule is not None
        and pending_reschedule["stage"]
        == "select_appointment"
    ):

        appointment_number = detect_number(
            message_lower
        )


        if appointment_number is None:

            response = (
                "Please enter the NUMBER of the "
                "appointment you would like to reschedule."
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        booked_appointments = [
            appointment
            for appointment in appointments
            if appointment["status"] == "booked"
        ]


        if (
            appointment_number < 1
            or appointment_number >
            len(booked_appointments)
        ):

            response = (
                "That appointment number is not valid. "
                "Please select one of the appointments "
                "listed."
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        selected_appointment = (
            booked_appointments[
                appointment_number - 1
            ]
        )


        pending_reschedule["appointment"] = (
            selected_appointment
        )

        pending_reschedule["stage"] = (
            "select_date"
        )


        response = (
            f"You selected appointment "
            f"number {appointment_number}:\n\n"

            f"Doctor: "
            f"{format_doctor_name(selected_appointment['doctor_name'])}\n"

            f"Specialization: "
            f"{selected_appointment['specialization']}\n"

            f"Date: "
            f"{selected_appointment['appointment_date']}\n"

            f"Time: "
            f"{format_time_for_chat(selected_appointment['start_time'])} "
            f"to "
            f"{format_time_for_chat(selected_appointment['end_time'])}\n\n"

            "Please tell me the NEW date you "
            "would like for this appointment."
        )


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 10. DETECT DATE
    # =====================================================

    appointment_date = detect_date(
        message_lower,
        allow_day_only=True
    )


    # =====================================================
    # 11. RESCHEDULE - SELECT NEW DATE
    # =====================================================

    pending_reschedule = (
        state["pending_reschedule"]
    )


    if (
        pending_reschedule is not None
        and pending_reschedule["stage"]
        == "select_date"
    ):

        if appointment_date is None:

            response = (
                "Please enter a valid appointment "
                "date, for example 2 October, "
                "5 October, or 2026-10-05."
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        if is_past_date(
            appointment_date
        ):

            response = (
                f"{format_date_for_chat(appointment_date)} "
                "has already passed.\n\n"
                "Please choose a future date."
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        selected_appointment = (
            pending_reschedule["appointment"]
        )


        specialization = (
            selected_appointment["specialization"]
        )


        available_slots = get_available_doctors(
            specialization,
            appointment_date
        )


        if not available_slots:

            response = (
                f"Sorry, there are no available "
                f"slots for {specialization} on "
                f"{format_date_for_chat(appointment_date)}.\n\n"
                "Please choose another date."
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        pending_reschedule["new_date"] = (
            appointment_date
        )

        pending_reschedule["available_slots"] = (
            available_slots
        )

        pending_reschedule["stage"] = (
            "select_slot"
        )


        response = (
            f"Here are the available slots for "
            f"{format_date_for_chat(appointment_date)}:\n\n"
        )


        for index, slot in enumerate(
            available_slots,
            start=1
        ):

            response += (
                f"{index}. "
                f"Doctor: "
                f"{format_doctor_name(slot['name'])} | "
                f"{format_time_for_chat(slot['start_time'])} - "
                f"{format_time_for_chat(slot['end_time'])}\n"
            )


        response += (
            "\nPlease select a slot by entering "
            "its number."
        )


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 12. RESCHEDULE - SELECT NEW SLOT
    # =====================================================

    pending_reschedule = (
        state["pending_reschedule"]
    )


    if (
        pending_reschedule is not None
        and pending_reschedule["stage"]
        == "select_slot"
    ):

        slot_number = detect_number(
            message_lower
        )


        if slot_number is None:

            response = (
                "Please enter the NUMBER of the "
                "available slot you would like."
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        available_slots = (
            pending_reschedule[
                "available_slots"
            ]
        )


        if (
            slot_number < 1
            or slot_number > len(
                available_slots
            )
        ):

            response = (
                "That slot number is not available. "
                "Please select one of the available slots."
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        selected_slot = (
            available_slots[
                slot_number - 1
            ]
        )


        pending_reschedule["slot"] = (
            selected_slot
        )

        pending_reschedule["stage"] = (
            "confirm"
        )


        response = (
            "You selected:\n\n"

            f"Doctor: "
            f"{format_doctor_name(selected_slot['name'])}\n"

            f"Specialization: "
            f"{selected_slot['specialization']}\n"

            f"Date: "
            f"{format_date_for_chat(selected_slot['available_date'])}\n"

            f"Time: "
            f"{format_time_for_chat(selected_slot['start_time'])} "
            f"to "
            f"{format_time_for_chat(selected_slot['end_time'])}\n\n"

            "Would you like me to reschedule "
            "your appointment to this slot?"
        )


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 13. RESCHEDULE CONFIRMATION
    # =====================================================

    pending_reschedule = (
        state["pending_reschedule"]
    )


    if (
        pending_reschedule is not None
        and pending_reschedule["stage"]
        == "confirm"
        and is_reschedule_confirmation(
            message_lower
        )
    ):

        selected_appointment = (
            pending_reschedule["appointment"]
        )


        selected_slot = (
            pending_reschedule["slot"]
        )


        # -------------------------------------------------
        # CHECK SLOT AGAIN
        # -------------------------------------------------

        current_slots = get_available_doctors(
            selected_slot["specialization"],
            selected_slot["available_date"]
        )


        slot_still_available = False


        for slot in current_slots:

            if (
                slot["id"] ==
                selected_slot["id"]

                and str(slot["start_time"]) ==
                str(selected_slot["start_time"])

                and str(slot["end_time"]) ==
                str(selected_slot["end_time"])
            ):

                slot_still_available = True

                selected_slot = slot

                break


        if not slot_still_available:

            state["pending_reschedule"] = None

            response = (
                "Sorry, that slot has just been "
                "booked.\n\n"
                "Please start the reschedule process "
                "again and choose another available slot."
            )

            save_conversation(
                state,
                message,
                response
            )

            return response


        # -------------------------------------------------
        # PERFORM RESCHEDULE
        # -------------------------------------------------

        success = reschedule_appointment(
            patient_id=patient_id,
            appointment_id=selected_appointment["id"],
            doctor_id=selected_slot["id"],
            appointment_date=selected_slot[
                "available_date"
            ],
            start_time=selected_slot[
                "start_time"
            ],
            end_time=selected_slot[
                "end_time"
            ]
        )


        if success:

            response = (
                "✅ Your appointment has been "
                "rescheduled successfully.\n\n"

                f"Doctor: "
                f"{format_doctor_name(selected_slot['name'])}\n"

                f"Specialization: "
                f"{selected_slot['specialization']}\n"

                f"Date: "
                f"{format_date_for_chat(selected_slot['available_date'])}\n"

                f"Time: "
                f"{format_time_for_chat(selected_slot['start_time'])} "
                f"to "
                f"{format_time_for_chat(selected_slot['end_time'])}\n\n"

                f"Appointment ID: "
                f"{selected_appointment['id']}"
            )

        else:

            response = (
                "Sorry, I could not reschedule "
                "the appointment. The selected slot "
                "may no longer be available."
            )


        state["pending_reschedule"] = None


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 14. SPECIALIZATION
    # =====================================================

    specialization = detect_specialization(
        message_lower
    )


    # =====================================================
    # 15. REMEMBER SPECIALIZATION
    # =====================================================

    if specialization is None:

        specialization = (
            get_previous_specialization(
                state
            )
        )


    # =====================================================
    # 16. FIND NEXT AVAILABLE DATE / SLOT
    # =====================================================

    if (
        specialization
        and is_availability_search_request(
            message_lower
        )
    ):

        last_requested_date = (
            state.get("last_requested_date")
        )


        # -----------------------------------------------
        # Decide search starting date
        # -----------------------------------------------

        if last_requested_date:

            try:

                search_start_date = (
                    datetime.strptime(
                        last_requested_date,
                        "%Y-%m-%d"
                    ).date()
                    + timedelta(days=1)
                )

            except ValueError:

                search_start_date = (
                    date.today()
                    + timedelta(days=1)
                )

        else:

            search_start_date = (
                date.today()
                + timedelta(days=1)
            )


        # -----------------------------------------------
        # Search REAL database
        # -----------------------------------------------

        next_available_slots = (
            find_next_available_slots(
                specialization=specialization,
                start_date=search_start_date,
                days_to_check=30,
                max_results=5
            )
        )


        # -----------------------------------------------
        # SLOTS FOUND
        # -----------------------------------------------

        if next_available_slots:

            state["available_slot_options"] = (
                next_available_slots
            )

            state["pending_appointment"] = None


            response = (
                "I found the following available "
                "appointments:\n\n"
            )


            for index, slot in enumerate(
                next_available_slots,
                start=1
            ):

                response += (
                    f"{index}. "
                    f"{format_doctor_name(slot['name'])}\n"

                    f"   Specialization: "
                    f"{slot['specialization']}\n"

                    f"   Date: "
                    f"{format_date_for_chat(str(slot['available_date']))}\n"

                    f"   Time: "
                    f"{format_time_for_chat(slot['start_time'])} "
                    f"to "
                    f"{format_time_for_chat(slot['end_time'])}\n\n"
                )


            response += (
                "Please select a slot by "
                "entering its number."
            )


            save_conversation(
                state,
                message,
                response
            )

            return response


        # -----------------------------------------------
        # NO FUTURE SLOTS
        # -----------------------------------------------

        response = (
            f"I could not find any available "
            f"{specialization} appointments "
            f"in the next 30 days.\n\n"
            "Please try another date."
        )


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 17. BOOKING SLOT NUMBER
    # =====================================================

    selected_slot_number = detect_number(
        message_lower
    )


    # =====================================================
    # 18. BOOKING SLOT SELECTION
    # =====================================================

    available_slot_options = (
        state["available_slot_options"]
    )


    if (
        selected_slot_number is not None
        and available_slot_options
    ):

        if (
            selected_slot_number >= 1
            and selected_slot_number <=
            len(available_slot_options)
        ):

            state["pending_appointment"] = (
                available_slot_options[
                    selected_slot_number - 1
                ]
            )


            selected = (
                state["pending_appointment"]
            )


            response = (
                "You selected:\n\n"

                f"Doctor: "
                f"{format_doctor_name(selected['name'])}\n"

                f"Specialization: "
                f"{selected['specialization']}\n"

                f"Date: "
                f"{format_date_for_chat(selected['available_date'])}\n"

                f"Time: "
                f"{format_time_for_chat(selected['start_time'])} "
                f"to "
                f"{format_time_for_chat(selected['end_time'])}\n\n"

                "Would you like to book "
                "this appointment?"
            )


            save_conversation(
                state,
                message,
                response
            )

            return response


        response = (
            "That slot number is not available. "
            "Please select one of the available slots."
        )


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 19. BOOKING CONFIRMATION
    # =====================================================

    pending_appointment = (
        state["pending_appointment"]
    )


    if (
        is_booking_confirmation(
            message_lower
        )
        and pending_appointment is not None
    ):

        selected_slot = (
            pending_appointment
        )


        # -------------------------------------------------
        # CHECK SLOT AGAIN
        # -------------------------------------------------

        current_slots = get_available_doctors(
            selected_slot["specialization"],
            selected_slot["available_date"]
        )


        slot_still_available = False


        for slot in current_slots:

            if (
                slot["id"] ==
                selected_slot["id"]

                and str(slot["start_time"]) ==
                str(selected_slot["start_time"])

                and str(slot["end_time"]) ==
                str(selected_slot["end_time"])
            ):

                slot_still_available = True

                selected_slot = slot

                break


        if not slot_still_available:

            state["pending_appointment"] = None

            state["available_slot_options"] = []


            response = (
                "Sorry, this appointment slot has "
                "already been booked.\n\n"
                "Please choose another available slot "
                "or another date."
            )


            save_conversation(
                state,
                message,
                response
            )

            return response


        # -------------------------------------------------
        # PAYMENT REQUIRED
        # -------------------------------------------------
        #
        # Appointment is NOT booked yet.
        #
        # Booking happens after Payment Done
        # in the chatbot.
        # -------------------------------------------------

        state["pending_appointment"] = (
            selected_slot
        )


        response = (
            "Your appointment slot is available.\n\n"

            f"Doctor: "
            f"{format_doctor_name(selected_slot['name'])}\n"

            f"Specialization: "
            f"{selected_slot['specialization']}\n"

            f"Date: "
            f"{format_date_for_chat(selected_slot['available_date'])}\n"

            f"Time: "
            f"{format_time_for_chat(selected_slot['start_time'])} "
            f"to "
            f"{format_time_for_chat(selected_slot['end_time'])}\n\n"

            "Please complete the payment before I "
            "book your appointment."
        )


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 20. YES WITHOUT PENDING BOOKING
    # =====================================================

    if is_booking_confirmation(
        message_lower
    ):

        response = (
            "Please select an available appointment "
            "slot first."
        )


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 21. NORMAL BOOKING DATE
    # =====================================================

    appointment_date = detect_date(
        message_lower,
        allow_day_only=True
    )


    # =====================================================
    # 22. REMEMBER REQUESTED DATE
    # =====================================================

    if appointment_date:

        state["last_requested_date"] = (
            appointment_date
        )


    # =====================================================
    # 23. NORMAL BOOKING AVAILABILITY
    # =====================================================

    available_slots = []


    # -----------------------------------------------------
    # CHECK PAST DATE
    # -----------------------------------------------------

    if (
        specialization
        and appointment_date
        and is_past_date(
            appointment_date
        )
    ):

        formatted_date = (
            format_date_for_chat(
                appointment_date
            )
        )


        response = (
            f"{formatted_date} has already passed.\n\n"
            "Please choose a future date, or "
            "ask me to find the next available "
            "appointment."
        )


        save_conversation(
            state,
            message,
            response
        )

        return response


    if (
        specialization
        and appointment_date
    ):

        available_slots = (
            get_available_doctors(
                specialization,
                appointment_date
            )
        )


    # =====================================================
    # 24. SAVE AVAILABLE BOOKING SLOTS
    # =====================================================

    if (
        specialization
        and appointment_date
    ):

        state["available_slot_options"] = (
            available_slots
        )


        # -------------------------------------------------
        # NO SLOTS
        # -------------------------------------------------

        if not available_slots:

            state["pending_appointment"] = None


            formatted_date = (
                format_date_for_chat(
                    appointment_date
                )
            )


            response = (
                f"Sorry, there are no available "
                f"slots for {specialization} on "
                f"{formatted_date}.\n\n"
                "If you want, I can find the "
                "next available dates and slots "
                "for you."
            )


            save_conversation(
                state,
                message,
                response
            )

            return response


        # -------------------------------------------------
        # ONE SLOT
        # -------------------------------------------------

        if len(available_slots) == 1:

            state["pending_appointment"] = (
                available_slots[0]
            )


            slot = available_slots[0]


            response = (
                f"Great! We have an open slot with "
                f"{format_doctor_name(slot['name'])} on "
                f"{format_date_for_chat(slot['available_date'])} "
                f"from "
                f"{format_time_for_chat(slot['start_time'])} "
                f"to "
                f"{format_time_for_chat(slot['end_time'])}.\n\n"

                "Would you like to book this appointment?"
            )


            save_conversation(
                state,
                message,
                response
            )

            return response


        # -------------------------------------------------
        # MULTIPLE SLOTS
        # -------------------------------------------------

        state["pending_appointment"] = None


        response = (
            f"Here are the available slots for "
            f"{format_date_for_chat(appointment_date)}:\n\n"
        )


        for index, slot in enumerate(
            available_slots,
            start=1
        ):

            response += (
                f"{index}. "
                f"{format_doctor_name(slot['name'])} | "
                f"{format_time_for_chat(slot['start_time'])} - "
                f"{format_time_for_chat(slot['end_time'])}\n"
            )


        response += (
            "\nPlease select a slot by entering "
            "its number."
        )


        save_conversation(
            state,
            message,
            response
        )

        return response


    # =====================================================
    # 25. HISTORY CONTEXT
    # =====================================================

    history_context = ""


    if patient_history:

        history_context = (
            "Previous patient history:\n"
        )


        for history in patient_history:

            history_context += (
                f"Doctor: "
                f"{format_doctor_name(history['doctor_name'])}\n"

                f"Problem: "
                f"{history['problem']}\n"

                f"Treatment: "
                f"{history['treatment']}\n"

                f"Visit Date: "
                f"{history['visit_date']}\n\n"
            )


    # =====================================================
    # 26. APPOINTMENT CONTEXT
    # =====================================================

    appointment_context = ""


    if appointments:

        appointment_context = (
            "Current patient appointments:\n"
        )


        for appointment in appointments:

            appointment_context += (
                f"Appointment ID: "
                f"{appointment['id']}\n"

                f"Doctor: "
                f"{format_doctor_name(appointment['doctor_name'])}\n"

                f"Specialization: "
                f"{appointment['specialization']}\n"

                f"Date: "
                f"{appointment['appointment_date']}\n"

                f"Start Time: "
                f"{appointment['start_time']}\n"

                f"End Time: "
                f"{appointment['end_time']}\n"

                f"Status: "
                f"{appointment['status']}\n\n"
            )


    # =====================================================
    # 27. DOCTOR CONTEXT
    # =====================================================

    doctor_context = ""


    if specialization:

        doctors = (
            get_doctors_by_specialization(
                specialization
            )
        )


        if doctors:

            doctor_context = (
                "Matching doctors:\n"
            )


            for doctor in doctors:

                doctor_context += (
                    f"Doctor: "
                    f"{format_doctor_name(doctor['name'])}\n"

                    f"Specialization: "
                    f"{doctor['specialization']}\n"

                    f"Experience: "
                    f"{doctor['experience']} years\n\n"
                )


    # =====================================================
    # 28. AVAILABILITY CONTEXT
    # =====================================================

    availability_context = ""


    if (
        specialization
        and appointment_date
    ):

        if available_slots:

            availability_context = (
                "ACTUAL AVAILABLE SLOTS "
                "FROM DATABASE:\n"
            )


            for index, slot in enumerate(
                available_slots,
                start=1
            ):

                availability_context += (
                    f"Slot {index}:\n"

                    f"Doctor: "
                    f"{format_doctor_name(slot['name'])}\n"

                    f"Specialization: "
                    f"{slot['specialization']}\n"

                    f"Date: "
                    f"{slot['available_date']}\n"

                    f"Start Time: "
                    f"{slot['start_time']}\n"

                    f"End Time: "
                    f"{slot['end_time']}\n\n"
                )

        else:

            availability_context = (
                "ACTUAL DATABASE RESULT:\n"

                f"No available slots for "
                f"{specialization} on "
                f"{appointment_date}.\n"
            )


    # =====================================================
    # 29. CURRENT DATABASE CONTEXT
    # =====================================================

    current_context = (
        history_context
        + appointment_context
        + doctor_context
        + availability_context
    )


    # =====================================================
    # 30. SYSTEM MESSAGE
    # =====================================================

    if not conversation_history:

        conversation_history.append({

            "role": "system",

            "content": (

                "You are a friendly clinic assistant. "

                "Help patients with their questions, "
                "symptoms, and appointment requests. "

                "Use a warm, natural and friendly tone. "

                "You can use simple emojis when appropriate. "

                "Do not claim to be a doctor or provide "
                "a definite diagnosis. "

                "For serious or emergency symptoms, advise "
                "the patient to seek appropriate medical care. "

                "When a patient describes an injury, "
                "be empathetic and helpful. "

                "If an injury appears serious or needs "
                "professional examination, recommend "
                "visiting the hospital or clinic and "
                "offer to help with an appointment.\n\n"

                "IMPORTANT APPOINTMENT RULES:\n"

                "1. Use only appointment information "
                "provided by the database.\n"

                "2. Never invent doctors, dates, "
                "or time slots.\n"

                "3. Never claim an appointment was booked "
                "unless the database confirms it.\n"

                "4. Never say a slot is available if the "
                "database says it is unavailable.\n"

                "5. Booking, cancellation, and rescheduling "
                "are handled by application code.\n"

                "6. Never confuse booking confirmation "
                "with cancellation confirmation.\n"

                "7. When the application provides available "
                "slots, use those slots only.\n"

                "8. Do not invent appointment IDs.\n"

                "9. For cancellation, the patient selects "
                "an appointment by its displayed list number. "
                "The application internally uses the real "
                "database appointment ID.\n"

                "10. For rescheduling, the patient first "
                "selects an existing appointment, then a "
                "new date, then an available slot, and "
                "finally confirms the reschedule.\n"

                "11. Appointment dates are dynamic. "
                "Never assume that only specific dates "
                "are available. Always use the date supplied "
                "by the patient and check the database "
                "for availability.\n"

                "12. If the patient asks for the next "
                "available appointment, available dates, "
                "or available slots, use the actual "
                "database results provided by the application. "
                "Never guess availability.\n"

                "13. Never invent future appointment dates "
                "or times.\n"
            )
        })


    # =====================================================
    # 31. DATABASE INFORMATION
    # =====================================================

    if current_context:

        conversation_history.append({

            "role": "system",

            "content": (
                "CURRENT DATABASE INFORMATION:\n\n"
                + current_context
            )
        })


    # =====================================================
    # 32. PATIENT MESSAGE
    # =====================================================

    conversation_history.append({

        "role": "user",
        "content": message
    })


    # =====================================================
    # 33. ASK GROQ
    # =====================================================

    try:

        response = ask_groq(
            conversation_history
        )

    except Exception:

        # Remove the user message if Groq failed

        if (
            conversation_history
            and conversation_history[-1]["role"]
            == "user"
        ):

            conversation_history.pop()


        return (
            "I'm sorry, I'm having trouble connecting "
            "to the clinic assistant right now. "
            "Please try again."
        )


    # =====================================================
    # 34. SAVE ASSISTANT RESPONSE
    # =====================================================

    conversation_history.append({

        "role": "assistant",
        "content": response
    })


    return response