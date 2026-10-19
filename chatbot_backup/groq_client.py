import os
import base64
import json

from dotenv import load_dotenv
from groq import Groq

from .prompt import SYSTEM_PROMPT


# ==========================================
# LOAD ENVIRONMENT
# ==========================================

load_dotenv()


# ==========================================
# GROQ API KEY
# ==========================================

api_key = os.getenv("GROQ_API_KEY")


# ==========================================
# GROQ CLIENT
# ==========================================

client = Groq(
    api_key=api_key
)


# ==========================================
# NORMAL TEXT CHAT
# ==========================================

def ask_groq(messages: list) -> str:

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            *messages
        ]
    )

    return (
        response
        .choices[0]
        .message
        .content
    )


# ==========================================
# INJURY IMAGE CHAT
# ==========================================

def ask_groq_with_image(
    message: str,
    image_bytes: bytes,
    image_type: str
):

    try:

        # --------------------------------------
        # Convert image to Base64
        # --------------------------------------

        base64_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")


        # --------------------------------------
        # System instruction
        # --------------------------------------

        image_system_prompt = """
You are Sanjeevani Assistant, a friendly
clinic assistant.

The patient has uploaded an injury photo.

Your job is to:

1. Look carefully at the image.

2. Identify the body area that appears
   to be affected.

3. Give a short, friendly and empathetic
   response to the patient.

4. Describe only what can reasonably be
   observed in the image.

5. Never give a definite medical diagnosis.

6. Never claim that the patient definitely
   has a fracture, infection, sprain, or
   another medical condition.

7. Ask how the injury happened when useful.

8. Ask about pain, swelling, bleeding,
   or difficulty moving the area when
   appropriate.

9. Recommend seeing a healthcare professional
   when an injury is visible.

10. Tell the patient that Sanjeevani can
    help them book a doctor appointment
    and potentially save waiting time.

11. Keep the response friendly, short,
    and conversational.

12. Never pretend to be a doctor.

13. Do not unnecessarily scare the patient.

14. This is only initial screening guidance
    and NOT a medical diagnosis.


IMPORTANT:

You must also identify the most appropriate
doctor specialization based on the affected
body area.

Use ONLY one of these specializations:

- Orthopedic
- Dermatologist
- General Physician
- Neurologist
- None


SPECIALIZATION GUIDELINES:

Use "Orthopedic" for injuries involving:

- hand
- wrist
- arm
- elbow
- shoulder
- leg
- knee
- ankle
- foot
- bones
- joints
- muscles
- visible physical injuries

Use "Dermatologist" mainly for:

- skin problems
- rashes
- skin irritation
- unusual skin lesions
- skin-related conditions

Use "Neurologist" when the image/context
strongly suggests a neurological concern.

Use "General Physician" when the affected
area/problem does not clearly belong to
another specialization.

Use "None" when the image does not show
a medical/injury concern or when you cannot
reasonably determine a specialization.


RETURN FORMAT:

Return ONLY valid JSON.

Use exactly this structure:

{
    "response": "friendly message for the patient",
    "specialization": "Orthopedic"
}


The "response" should sound natural and
friendly.

Example:

{
    "response": "Oh no! 😟 I can see that your ankle area looks swollen. How did this happen — did you twist your ankle, fall, or hurt it somehow? Since you've had an injury, it would be a good idea to have it checked by a doctor. 🏥 If you'd like, I can help you check available Orthopedic appointments so you can save some waiting time. This is only initial guidance and not a medical diagnosis.",
    "specialization": "Orthopedic"
}

Remember:

- Return ONLY JSON.
- Do not add markdown.
- Do not add ```json.
- Do not add explanations outside the JSON.
"""


        # --------------------------------------
        # User message
        # --------------------------------------

        if message.strip():

            user_text = message

        else:

            user_text = (
                "Please look carefully at this injury "
                "photo. Identify the affected body area, "
                "respond to the patient in a friendly "
                "way, and determine the most appropriate "
                "doctor specialization."
            )


        # --------------------------------------
        # Send image + text to Groq
        # --------------------------------------

        response = client.chat.completions.create(

            model="qwen/qwen3.8-27b",

            messages=[

                {
                    "role": "system",
                    "content": image_system_prompt
                },

                {
                    "role": "user",
                    "content": [

                        {
                            "type": "text",
                            "text": user_text
                        },

                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    f"data:{image_type};"
                                    f"base64,{base64_image}"
                                )
                            }
                        }

                    ]
                }

            ],

            temperature=0.7,

            max_completion_tokens=500
        )


        # --------------------------------------
        # Get Groq response
        # --------------------------------------

        raw_response = (
            response
            .choices[0]
            .message
            .content
        )


        # --------------------------------------
        # Convert JSON response
        # --------------------------------------

        try:

            result = json.loads(
                raw_response
            )

        except json.JSONDecodeError:

            # ----------------------------------
            # Fallback if Groq adds extra text
            # ----------------------------------

            start = raw_response.find("{")
            end = raw_response.rfind("}")

            if (
                start != -1
                and end != -1
                and end > start
            ):

                json_text = raw_response[
                    start:end + 1
                ]

                result = json.loads(
                    json_text
                )

            else:

                result = {
                    "response": raw_response,
                    "specialization": "None"
                }


        # --------------------------------------
        # Get response text
        # --------------------------------------

        chatbot_response = (
            result.get(
                "response",
                "I received your injury photo. "
                "It would be a good idea to have "
                "it checked by a healthcare "
                "professional."
            )
        )


        # --------------------------------------
        # Get specialization
        # --------------------------------------

        specialization = (
            result.get(
                "specialization",
                "None"
            )
        )


        # --------------------------------------
        # Validate specialization
        # --------------------------------------

        allowed_specializations = {

            "Orthopedic",
            "Dermatologist",
            "General Physician",
            "Neurologist",
            "None"
        }


        if specialization not in (
            allowed_specializations
        ):

            specialization = "None"


        # --------------------------------------
        # Return both values
        # --------------------------------------

        return {
            "response": chatbot_response,
            "specialization": specialization
        }


    except Exception as e:

        print(
            f"Groq injury image error: {e}"
        )

        return {

            "response": (
                "I can see that you've uploaded "
                "an injury photo. 😟 It would be "
                "a good idea to have the injury "
                "checked by a healthcare professional. "
                "🏥 If you'd like, I can also help "
                "you book an appointment and save "
                "some waiting time."
            ),

            "specialization": "None"
        }
