# import os
# import sys
# import uvicorn
# from fastapi import FastAPI,Form,Request
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from chatbot.database import get_db_connection
# from src.logger import get_logger
# from src.exception import CustomException
# from chatbot.chatbot_logic import chat_with_patient
# logger = get_logger(__name__)
# from src.pipeline.predict_pipeline import CustomData,PredictPipeline

# from nlp_pretrained.ner_tagger import(get_pos_tags,extract_entities)
# from nlp_pretrained.embedding import(most_similar_word)
# from nlp_pretrained.sentiment_analyzer import analyze_sentiment
# from starlette.middleware.sessions import SessionMiddleware
# app = FastAPI(title="covid prediction clinic")

# app.add_middleware(
#     SessionMiddleware,
#     secret_key="sanjeevani-secret-key"
# )

# # Mounting the css file
# app.mount("/static",StaticFiles(directory="static"), name="static")

# # Set the templates folder
# templates = Jinja2Templates(directory="templates")

# @app.get("/",response_class=HTMLResponse)
# async def home(request:Request):
#     logger.info("Home page accessed...")
#     return templates.TemplateResponse(request,"index.html")

# @app.get("/predict",response_class=HTMLResponse)
# async def predict_form(request: Request):
#     logger.info("Predict form page accessed...")
#     return templates.TemplateResponse(request,"predict.html",{"result":None})


# @app.post("/predict",response_class=HTMLResponse)
# async def predict_result(
#     request:Request,
#     age:int = Form(...),
#     gender:str = Form(...),
#     fever : float = Form(...),
#     cough : str = Form(...),
#     city :str = Form(...)
# ):
#     try:
#         logger.info(f"Prediction request received :: age{age},gender{gender},fever{fever},cough{cough},city{city}")

#         custom_data = CustomData(age=age,gender=gender,fever=fever,cough=cough,city=city)

#         data_df = custom_data.get_data_as_dataframe()

#         predict_pipeline = PredictPipeline()
#         result,probability = predict_pipeline.predict(data_df)
#         return templates.TemplateResponse(
#             request,
#             "predict.html",
#             {
#                 "result":result,
#                 "probability": probability,
#                 "form_data":{
#                     "age":age,
#                     "gender":gender,
#                     "fever":fever,
#                     "cough":cough,
#                     "city":city
#                 }
#             }
#         )

#     except Exception as e:
#         raise CustomException(e,sys)

# @app.get("/health")
# async def health_check() -> dict[str, str]:
#     logger.info("Monitering alert....")
#     return{"status":"ok"}


# # NLP pretrained

# @app.get("/pretrained-nlp",response_class=HTMLResponse)
# async def pretrained_nlp_form(request:Request):
#     return templates.TemplateResponse(request,
#                                       "pretrained_nlp.html",
#                                       {
#                                           "result":None,
#                                           "Form_data":{
#                                               "query":""
#                                           },
#                                           "error":None
#                                       })

# @app.post("/pretrained-nlp",response_class=HTMLResponse)
# async def pretrained_nlp_analysis(
#     request:Request,
#     query:str = Form(...)
# ) -> None:
#     try:
#         # Text clean
#         query = query.strip()
#         if not query:
#             return templates.TemplateResponse(
#                 request,
#                 "pretrained_nlp.html",
#                 {
#                     "result":None,
#                     "form_data":{
#                         "query":""
#                     },
#                     "error":"Please some text..."
#                 }
#             )
#         # Pos tagging
#         pos_tags = get_pos_tags(query)

#         # NER
#         entities = extract_entities(query)

#         # Sentiment Analysis
#         sentiment = analyze_sentiment(query)

#         # Word Embeddings
#         similar_word = []
#         words = query.split()
#         first_word = words[0].lower()
#         if words:
#             try:
#                 similar_word = most_similar_word(first_word,topn = 5)
#             except Exception as e:
#                 logger.warning(f"Glove similarity failed for :", {first_word},"and the error is:",{e})
#                 similar_words = []

#         # Final result
#         result = {
#             "query":query,
#             "pos_tags":pos_tags,
#             "entities":entities,
#             "similar_words":similar_word,
#             "sentiment":sentiment
#         }
#         # Rendering the result
#         return templates.TemplateResponse(
#             request,
#             "pretrained_nlp.html",
#             {
#                 "result":result,
#                 "form_data":{
#                     "query":query
#                 },
#                 "error":None
#             }
#         )


#     except Exception as e:
#         logger.info("Error occured in pretrained nlp analysis")
#         return templates.TemplateResponse(
#             request,
#             "pretrained_nlp.html",
#             {
#                 "result":None,
#                 "form_data":{
#                     "query":query
#                 },
#                 "error":str(e)
#             }
#         )

# @app.post("/chat")
# async def chat(
#     request: Request,
#     message: str = Form(...)
# ):

#     patient_id = request.session.get("patient_id")
#     patient_name = request.session.get("patient_name")

#     response = chat_with_patient(message, patient_id)

#     return {
#         "message": message,
#         "response": response,
#         "patient_id": patient_id,
#         "patient_name": patient_name
#     }


# @app.get("/register", response_class=HTMLResponse)
# async def register_page(request: Request):

#     return templates.TemplateResponse(
#         request,
#         "register.html"
#     )

# @app.post("/register")
# async def register_patient(
#     name: str = Form(...),
#     email: str = Form(...),
#     password: str = Form(...)
# ):

#     connection = get_db_connection()
#     cursor = connection.cursor()

#     query = """
#         INSERT INTO patients (name, email, password)
#         VALUES (%s, %s, %s)
#     """

#     values = (name, email, password)

#     cursor.execute(query, values)

#     connection.commit()

#     cursor.close()
#     connection.close()

#     return {
#         "message": "Patient registered successfully!"
#     }

# @app.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request):

#     return templates.TemplateResponse(
#         request,
#         "login.html"
#     )

# @app.post("/login")
# async def login_patient(
#     request: Request,
#     email: str = Form(...),
#     password: str = Form(...)
# ):

#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)

#     query = """
#         SELECT id, name, email
#         FROM patients
#         WHERE email = %s AND password = %s
#     """

#     values = (email, password)

#     cursor.execute(query, values)

#     patient = cursor.fetchone()

#     cursor.close()
#     connection.close()

#     if patient is None:
#         return {
#             "message": "Invalid email or password"
#     }

#     request.session["patient_id"] = patient["id"]
#     request.session["patient_name"] = patient["name"]

#     return {
#         "message": "Login successful!",
#         "patient": patient
#     }

# @app.get("/patient-session")
# async def patient_session(request: Request):

#     patient_id = request.session.get("patient_id")
#     patient_name = request.session.get("patient_name")

#     return {
#         "patient_id": patient_id,
#         "patient_name": patient_name
#     }

# if __name__ == "__main__":
#     uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)

# ---------------------------------------------------------------Previous code ------------------------------------------------------------

# ---------------------------------------------------------------Current code -------------------------------------------------------------
import os

import sys

import uvicorn

from io import BytesIO

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from fastapi.responses import StreamingResponse


from pathlib import Path

from fastapi import (

    FastAPI,

    Form,

    Request,

    UploadFile,

    File

)

from fastapi.responses import (

    HTMLResponse,

    RedirectResponse,

    StreamingResponse

)

from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

from chatbot.database import (

    get_db_connection,

    get_available_doctors,

    book_appointment

)

from chatbot.chatbot_logic import (

    chat_with_patient,

    chat_with_patient_image,

    get_patient_state

)

from src.logger import get_logger

from src.exception import CustomException

from src.pipeline.predict_pipeline import (

    CustomData,

    PredictPipeline

)

from nlp_pretrained.ner_tagger import (

    get_pos_tags,

    extract_entities

)

from nlp_pretrained.embedding import (

    most_similar_word

)

from nlp_pretrained.sentiment_analyzer import (

    analyze_sentiment

)

from starlette.middleware.sessions import SessionMiddleware

# ==========================================

# LOGGER

# ==========================================

logger = get_logger(__name__)


# ==========================================
# ELEVENLABS
# ==========================================

load_dotenv()

elevenlabs_client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

# ==========================================

# FASTAPI APP

# ==========================================

app = FastAPI(

    title="covid prediction clinic"

)

# ==========================================

# SESSION

# ==========================================

app.add_middleware(

    SessionMiddleware,

    secret_key="sanjeevani-secret-key"

)

# ==========================================

# STATIC FILES

# ==========================================

app.mount(

    "/static",

    StaticFiles(directory="static"),

    name="static"

)

# ==========================================

# TEMPLATES

# ==========================================

templates = Jinja2Templates(

    directory="templates"

)

# ==========================================

# INJURY IMAGE UPLOAD FOLDER

# ==========================================

INJURY_UPLOAD_DIR = Path(

    "static/uploads/injuries"

)

INJURY_UPLOAD_DIR.mkdir(

    parents=True,

    exist_ok=True

)

# ==========================================

# HELPER FUNCTION

# ==========================================

def serialize_appointment(slot):

    if not slot:

        return None

    start_time = slot.get(

        "start_time"

    )

    end_time = slot.get(

        "end_time"

    )

    # Convert time object into HH:MM

    if hasattr(

        start_time,

        "strftime"

    ):

        start_time = start_time.strftime(

            "%H:%M"

        )

    # Convert time object into HH:MM

    if hasattr(

        end_time,

        "strftime"

    ):

        end_time = end_time.strftime(

            "%H:%M"

        )

    return {

        "id":

            slot.get("id"),

        "name":

            slot.get("name"),

        "specialization":

            slot.get("specialization"),

        "available_date":

            str(

                slot.get(

                    "available_date"

                )

            ),

        "start_time":

            str(start_time),

        "end_time":

            str(end_time)

    }

# ==========================================

# IMAGE → DOCTOR SPECIALIZATION

# ==========================================

def detect_specialization(

    image_response: str

) -> str | None:

    """

    Detect a suitable doctor specialization

    from the injury image analysis response.

    This is only an initial routing suggestion.

    It is not a medical diagnosis.

    """

    text = image_response.lower()

    # --------------------------------------

    # Orthopedic

    # --------------------------------------

    orthopedic_keywords = [

        "ankle",

        "foot",

        "wrist",

        "hand",

        "leg",

        "knee",

        "elbow",

        "shoulder",

        "bone",

        "joint",

        "sprain",

        "fracture",

        "swollen ankle",

        "swollen leg",

        "swollen foot"

    ]

    for keyword in orthopedic_keywords:

        if keyword in text:

            return "Orthopedic"

    # --------------------------------------

    # General Surgery

    # --------------------------------------

    surgery_keywords = [

        "cut",

        "deep cut",

        "wound",

        "open wound",

        "laceration",

        "bleeding"

    ]

    for keyword in surgery_keywords:

        if keyword in text:

            return "General Surgery"

    # --------------------------------------

    # Dermatology

    # --------------------------------------

    dermatology_keywords = [

        "rash",

        "skin irritation",

        "skin redness",

        "skin infection",

        "itching",

        "skin"

    ]

    for keyword in dermatology_keywords:

        if keyword in text:

            return "Dermatologist"

    # --------------------------------------

    # No specialization detected

    # --------------------------------------

    return None

# ==========================================

# ROOT ROUTE

# ==========================================

@app.get(

    "/",

    response_class=HTMLResponse

)

async def home(

    request: Request

):

    logger.info(

        "Root page accessed..."

    )

    return RedirectResponse(

        url="/register",

        status_code=303

    )

# ==========================================

# SCREENING + CHATBOT HOME PAGE

# ==========================================

@app.get(

    "/screening",

    response_class=HTMLResponse

)

async def screening_page(

    request: Request

):

    patient_id = request.session.get(

        "patient_id"

    )

    patient_name = request.session.get(

        "patient_name"

    )

    patient_email = request.session.get("patient_email")

    if not patient_id:

        return RedirectResponse(

            url="/register",

            status_code=303

        )

    logger.info(

        f"Screening page accessed by patient "

        f"{patient_id}"

    )

    return templates.TemplateResponse(

        request,

        "index.html",

        {

            "patient_id": patient_id,

            "patient_name": patient_name,

            "patient_email": patient_email

        }

    )

# ==========================================

# COMPLETE PAYMENT

#

# Payment is handled inside the chatbot.

#

# This endpoint is called when the patient

# clicks "Payment Done".

# ==========================================

@app.post("/payment/complete")

async def complete_payment(

    request: Request

):

    patient_id = request.session.get(

        "patient_id"

    )

    patient_name = request.session.get(

        "patient_name"

    )

    # --------------------------------------

    # Patient must be logged in

    # --------------------------------------

    if not patient_id:

        return {

            "success": False,

            "message": "Please login first."

        }

    # --------------------------------------

    # Get patient state

    # --------------------------------------

    state = get_patient_state(

        patient_id

    )

    # --------------------------------------

    # Get pending appointment

    # --------------------------------------

    pending_appointment = (

        state.get(

            "pending_appointment"

        )

    )

    if pending_appointment is None:

        return {

            "success": False,

            "message":

                "No pending appointment found."

        }

    selected_slot = pending_appointment

    # ======================================

    # CHECK SLOT AGAIN

    # ======================================

    try:

        current_slots = (

            get_available_doctors(

                selected_slot[

                    "specialization"

                ],

                selected_slot[

                    "available_date"

                ]

            )

        )

    except Exception as e:

        logger.error(

            f"Error checking appointment "

            f"availability: {e}"

        )

        return {

            "success": False,

            "message": (

                "Could not check appointment "

                "availability. Please try again."

            )

        }

    slot_still_available = False

    for slot in current_slots:

        if (

            str(slot["id"])

            ==

            str(selected_slot["id"])

            and

            str(

                slot["start_time"]

            )

            ==

            str(

                selected_slot["start_time"]

            )

            and

            str(

                slot["end_time"]

            )

            ==

            str(

                selected_slot["end_time"]

            )

        ):

            slot_still_available = True

            selected_slot = slot

            break

    # ======================================

    # SLOT NO LONGER AVAILABLE

    # ======================================

    if not slot_still_available:

        state[

            "pending_appointment"

        ] = None

        state[

            "available_slot_options"

        ] = []

        return {

            "success": False,

            "message": (

                "Sorry, this appointment slot "

                "is no longer available. "

                "Please choose another slot."

            )

        }

    # ======================================

    # BOOK APPOINTMENT

    # ======================================

    try:

        appointment_id = book_appointment(

            patient_id=patient_id,

            doctor_id=selected_slot[

                "id"

            ],

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

    except Exception as e:

        logger.error(

            f"Appointment booking error: {e}"

        )

        return {

            "success": False,

            "message": (

                "The appointment could not "

                "be booked. Please try again."

            )

        }

    # ======================================

    # FORMAT TIME

    # ======================================

    start_time = selected_slot[

        "start_time"

    ]

    end_time = selected_slot[

        "end_time"

    ]

    if hasattr(

        start_time,

        "strftime"

    ):

        start_time = start_time.strftime(

            "%H:%M"

        )

    if hasattr(

        end_time,

        "strftime"

    ):

        end_time = end_time.strftime(

            "%H:%M"

        )

    # ======================================

    # APPOINTMENT INFORMATION

    # ======================================

    appointment = {

        "id":

            appointment_id,

        "patient_name":

            patient_name,

        "name":

            selected_slot[

                "name"

            ],

        "specialization":

            selected_slot[

                "specialization"

            ],

        "available_date":

            str(

                selected_slot[

                    "available_date"

                ]

            ),

        "start_time":

            str(start_time),

        "end_time":

            str(end_time)

    }

    # ======================================

    # CLEAR PENDING APPOINTMENT

    # ======================================

    state[

        "pending_appointment"

    ] = None

    state[

        "available_slot_options"

    ] = []

    # ======================================

    # LOG

    # ======================================

    logger.info(

        f"Appointment booked successfully. "

        f"Appointment ID: {appointment_id}, "

        f"Patient ID: {patient_id}"

    )

    # ======================================

    # RESPONSE

    # ======================================

    return {

        "success":

            True,

        "message":

            "Payment successfully done.",

        "appointment":

            appointment

    }

# ==========================================

# PREDICTION PAGE

# ==========================================

@app.get(

    "/predict",

    response_class=HTMLResponse

)

async def predict_form(

    request: Request

):

    logger.info(

        "Predict form page accessed..."

    )

    return templates.TemplateResponse(

        request,

        "predict.html",

        {

            "result": None

        }

    )

# ==========================================

# PREDICTION

# ==========================================

@app.post(

    "/predict",

    response_class=HTMLResponse

)

async def predict_result(

    request: Request,

    age: int = Form(...),

    gender: str = Form(...),

    fever: float = Form(...),

    cough: str = Form(...),

    city: str = Form(...)

):

    try:

        logger.info(

            f"Prediction request received :: "

            f"age={age}, "

            f"gender={gender}, "

            f"fever={fever}, "

            f"cough={cough}, "

            f"city={city}"

        )

        custom_data = CustomData(

            age=age,

            gender=gender,

            fever=fever,

            cough=cough,

            city=city

        )

        data_df = (

            custom_data

            .get_data_as_dataframe()

        )

        predict_pipeline = (

            PredictPipeline()

        )

        result, probability = (

            predict_pipeline.predict(

                data_df

            )

        )

        return templates.TemplateResponse(

            request,

            "predict.html",

            {

                "result": result,

                "probability":

                    probability,

                "form_data": {

                    "age": age,

                    "gender": gender,

                    "fever": fever,

                    "cough": cough,

                    "city": city

                }

            }

        )

    except Exception as e:

        raise CustomException(

            e,

            sys

        )

# ==========================================

# HEALTH CHECK

# ==========================================

@app.get("/health")

async def health_check() -> dict[str, str]:

    logger.info(

        "Monitoring alert...."

    )

    return {

        "status": "ok"

    }

# ==========================================

# PRETRAINED NLP

# ==========================================

@app.get(

    "/pretrained-nlp",

    response_class=HTMLResponse

)

async def pretrained_nlp_form(

    request: Request

):

    return templates.TemplateResponse(

        request,

        "pretrained_nlp.html",

        {

            "result": None,

            "form_data": {

                "query": ""

            },

            "error": None

        }

    )

@app.post(

    "/pretrained-nlp",

    response_class=HTMLResponse

)

async def pretrained_nlp_analysis(

    request: Request,

    query: str = Form(...)

):

    try:

        # --------------------------------------

        # Text clean

        # --------------------------------------

        query = query.strip()

        if not query:

            return templates.TemplateResponse(

                request,

                "pretrained_nlp.html",

                {

                    "result": None,

                    "form_data": {

                        "query": ""

                    },

                    "error":

                        "Please enter some text..."

                }

            )

        # --------------------------------------

        # POS tagging

        # --------------------------------------

        pos_tags = get_pos_tags(

            query

        )

        # --------------------------------------

        # NER

        # --------------------------------------

        entities = extract_entities(

            query

        )

        # --------------------------------------

        # Sentiment

        # --------------------------------------

        sentiment = analyze_sentiment(

            query

        )

        # --------------------------------------

        # Word embeddings

        # --------------------------------------

        similar_word = []

        words = query.split()

        if words:

            first_word = (

                words[0].lower()

            )

            try:

                similar_word = (

                    most_similar_word(

                        first_word,

                        topn=5

                    )

                )

            except Exception as e:

                logger.warning(

                    f"Glove similarity failed "

                    f"for {first_word}: {e}"

                )

                similar_word = []

        # --------------------------------------

        # Final result

        # --------------------------------------

        result = {

            "query":

                query,

            "pos_tags":

                pos_tags,

            "entities":

                entities,

            "similar_words":

                similar_word,

            "sentiment":

                sentiment

        }

        # --------------------------------------

        # Render

        # --------------------------------------

        return templates.TemplateResponse(

            request,

            "pretrained_nlp.html",

            {

                "result":

                    result,

                "form_data": {

                    "query":

                        query

                },

                "error":

                    None

            }

        )

    except Exception as e:

        logger.info(

            "Error occurred in pretrained NLP analysis"

        )

        return templates.TemplateResponse(

            request,

            "pretrained_nlp.html",

            {

                "result":

                    None,

                "form_data": {

                    "query":

                        query

                },

                "error":

                    str(e)

            }

        )

# ==========================================
# ELEVENLABS TEXT TO SPEECH
# ==========================================

@app.post("/text-to-speech")
async def text_to_speech(
    request: Request
):
    try:
        # Get JSON data from frontend
        data = await request.json()

        text = data.get(
            "text",
            ""
        ).strip()

        # Check text
        if not text:
            return {
                "success": False,
                "message": "No text provided."
            }

        # Convert text into speech
        audio = elevenlabs_client.text_to_speech.convert(
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_multilingual_v2"
        )

        # Send audio back to browser
        return StreamingResponse(
            audio,
            media_type="audio/mpeg"
        )

    except Exception as e:

        logger.error(
            f"ElevenLabs TTS error: {e}"
        )

        return {
            "success": False,
            "message": "Could not generate speech."
        }


# ==========================================
# ELEVENLABS SPEECH TO SPEECH
# ==========================================

@app.post("/speech-to-speech")
async def speech_to_speech(
    audio: UploadFile = File(...)
):
    try:

        # Read uploaded audio
        audio_bytes = await audio.read()

        if not audio_bytes:
            return {
                "success": False,
                "message": "No audio provided."
            }

        # Convert speech using ElevenLabs
        converted_audio = elevenlabs_client.speech_to_speech.convert(
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            audio=audio_bytes,
            model_id="eleven_multilingual_sts_v2",
            output_format="mp3_44100_128"
        )

        # Return converted audio
        return StreamingResponse(
            converted_audio,
            media_type="audio/mpeg"
        )

    except Exception as e:

        logger.error(
            f"ElevenLabs STS error: {e}"
        )

        return {
            "success": False,
            "message": "Could not convert speech."
        }


# ==========================================
# ELEVENLABS SPEECH TO TEXT
# ==========================================

@app.post("/speech-to-text")
async def speech_to_text(
    audio: UploadFile = File(...)
):
    try:

        # Read uploaded recording
        audio_bytes = await audio.read()

        if not audio_bytes:
            return {
                "success": False,
                "message": "No audio provided."
            }


        # Convert bytes into file-like object
        audio_file = BytesIO(audio_bytes)

        audio_file.name = (
            audio.filename
            or "recording.webm"
        )


        # ======================================
        # ELEVENLABS TRANSCRIPTION
        # ======================================

        transcription = (
            elevenlabs_client
            .speech_to_text
            .convert(
                file=audio_file,

                # Medical / clinical STT model
                model_id="scribe_v2_medical",

                # We only need spoken text
                tag_audio_events=False,

                # Single patient speaking
                diarize=False
            )
        )


        # ======================================
        # GET TRANSCRIBED TEXT
        # ======================================

        text = transcription.text


        logger.info(
            f"STT transcription: {text}"
        )


        return {
            "success": True,
            "text": text
        }


    except Exception as e:

        logger.error(
            f"ElevenLabs STT error: {e}"
        )

        return {
            "success": False,
            "message":
                "Could not convert speech to text."
        }


# ==========================================

# CHATBOT + INJURY IMAGE UPLOAD

# ==========================================

@app.post("/chat")

async def chat(

    request: Request,

    message: str = Form(""),

    injury_image: UploadFile | None = File(None)

):

    patient_id = request.session.get(

        "patient_id"

    )

    patient_name = request.session.get(

        "patient_name"

    )

    # --------------------------------------

    # Default specialization

    # --------------------------------------

    specialization = None

    # --------------------------------------

    # Patient must be logged in

    # --------------------------------------

    if not patient_id:

        return {

            "message":

                message,

            "response":

                (

                    "Please login first "

                    "to use the chatbot."

                ),

            "patient_id":

                None,

            "patient_name":

                None,

            "image_url":

                None,

            "specialization":

                None,

            "payment_required":

                False,

            "pending_appointment":

                None

        }

    # --------------------------------------

    # Image URL

    # --------------------------------------

    image_url = None

    # --------------------------------------

    # Image bytes

    # --------------------------------------

    image_bytes = None

    image_type = None

    # ======================================

    # IF PATIENT UPLOADED AN IMAGE

    # ======================================

    if injury_image is not None:

        # ----------------------------------

        # Check filename

        # ----------------------------------

        if not injury_image.filename:

            return {

                "message":

                    message,

                "response":

                    (

                        "Please select an image."

                    ),

                "patient_id":

                    patient_id,

                "patient_name":

                    patient_name,

                "image_url":

                    None,

                "specialization":

                    None,

                "payment_required":

                    False,

                "pending_appointment":

                    None

            }

        # ----------------------------------

        # Allowed image types

        # ----------------------------------

        allowed_extensions = {

            ".jpg",

            ".jpeg",

            ".png",

            ".webp"

        }

        file_extension = Path(

            injury_image.filename

        ).suffix.lower()

        if (

            file_extension

            not in allowed_extensions

        ):

            return {

                "message":

                    message,

                "response":

                    (

                        "Please upload a JPG, "

                        "JPEG, PNG or WEBP image."

                    ),

                "patient_id":

                    patient_id,

                "patient_name":

                    patient_name,

                "image_url":

                    None,

                "specialization":

                    None,

                "payment_required":

                    False,

                "pending_appointment":

                    None

            }

        # ----------------------------------

        # Read image

        # ----------------------------------

        try:

            image_bytes = (

                await injury_image.read()

            )

            image_type = (

                injury_image.content_type

                or "image/jpeg"

            )

            if not image_bytes:

                return {

                    "message":

                        message,

                    "response":

                        (

                            "The uploaded image "

                            "is empty. Please try "

                            "another image."

                        ),

                    "patient_id":

                        patient_id,

                    "patient_name":

                        patient_name,

                    "image_url":

                        None,

                    "specialization":

                        None,

                    "payment_required":

                        False,

                    "pending_appointment":

                        None

                }

        except Exception as e:

            logger.error(

                f"Image reading error: {e}"

            )

            return {

                "message":

                    message,

                "response":

                    (

                        "I could not read the "

                        "image. Please try again."

                    ),

                "patient_id":

                    patient_id,

                "patient_name":

                    patient_name,

                "image_url":

                    None,

                "specialization":

                    None,

                "payment_required":

                    False,

                "pending_appointment":

                    None

            }

        # ----------------------------------

        # Create filename

        # ----------------------------------

        safe_filename = (

            f"patient_{patient_id}_"

            f"{injury_image.filename}"

        )

        file_path = (

            INJURY_UPLOAD_DIR /

            safe_filename

        )

        # ----------------------------------

        # Save image

        # ----------------------------------

        try:

            with open(

                file_path,

                "wb"

            ) as file:

                file.write(

                    image_bytes

                )

            logger.info(

                f"Injury image uploaded by "

                f"patient {patient_id}: "

                f"{safe_filename}"

            )

            image_url = (

                f"/static/uploads/injuries/"

                f"{safe_filename}"

            )

        except Exception as e:

            logger.error(

                f"Image save error: {e}"

            )

            return {

                "message":

                    message,

                "response":

                    (

                        "Image upload failed. "

                        "Please try again."

                    ),

                "patient_id":

                    patient_id,

                "patient_name":

                    patient_name,

                "image_url":

                    None,

                "specialization":

                    None,

                "payment_required":

                    False,

                "pending_appointment":

                    None

            }

    # ======================================

    # CHATBOT RESPONSE

    # ======================================

    response = ""

    # --------------------------------------

    # IMAGE + TEXT

    # --------------------------------------

    if image_bytes is not None:

        logger.info(

            f"Sending injury image to Groq "

            f"for patient {patient_id}"

        )

        try:

            result = (

                chat_with_patient_image(

                    message=message.strip(),

                    patient_id=patient_id,

                    image_bytes=image_bytes,

                    image_type=image_type

                )

            )

            # ----------------------------------

            # Get response from Groq

            # ----------------------------------

            response = result.get(

                "response",

                "I received your injury image."

            )

            # ----------------------------------

            # Get specialization

            # ----------------------------------

            specialization = result.get(

                "specialization",

                "None"

            )

            logger.info(

                f"Detected specialization: "

                f"{specialization}"

            )

            # ----------------------------------

            # Add appointment information

            # ----------------------------------

            if specialization != "None":

                response += (

                    f"\n\nBased on the area shown, "

                    f"an {specialization} doctor may "

                    f"be appropriate for an initial "

                    f"check. I can also help you check "

                    f"available appointments."

                )

        except Exception as e:

            logger.error(

                f"Image chatbot error: {e}"

            )

            response = (

                "I received your injury image, "

                "but I could not analyze it right now. "

                "Please try uploading it again."

            )

    # --------------------------------------

    # TEXT ONLY

    # --------------------------------------

    elif message.strip():

        try:

            response = (

                chat_with_patient(

                    message.strip(),

                    patient_id

                )

            )

        except Exception as e:

            logger.error(

                f"Chatbot error: {e}"

            )

            response = (

                "Sorry, I could not process your "

                "message right now. Please try again."

            )

    # --------------------------------------

    # Nothing uploaded / entered

    # --------------------------------------

    else:

        response = (

            "Please type a message or upload "

            "an injury image."

        )

    # ======================================

    # GET PATIENT STATE

    # ======================================

    state = get_patient_state(

        patient_id

    )

    # ======================================

    # CHECK PAYMENT REQUIREMENT

    # ======================================

    payment_required = False

    if (

        "Please complete the payment before "

        "I book your appointment."

    ) in response:

        payment_required = True

    # ======================================

    # GET PENDING APPOINTMENT

    # ======================================

    pending_appointment = None

    if payment_required:

        pending_appointment = (

            serialize_appointment(

                state.get(

                    "pending_appointment"

                )

            )

        )

    # ======================================

    # FINAL RESPONSE

    # ======================================

    return {

        "message":

            message,

        "response":

            response,

        "patient_id":

            patient_id,

        "patient_name":

            patient_name,

        "image_url":

            image_url,

        "specialization":

            specialization,

        "payment_required":

            payment_required,

        "pending_appointment":

            pending_appointment

    }

# ==========================================

# REGISTER PAGE

# ==========================================

@app.get(

    "/register",

    response_class=HTMLResponse

)

async def register_page(

    request: Request

):

    return templates.TemplateResponse(

        request,

        "register.html",

        {

            "error": None

        }

    )

# ==========================================

# REGISTER PATIENT

# ==========================================

@app.post("/register")

async def register_patient(

    request: Request,

    name: str = Form(...),

    email: str = Form(...),

    password: str = Form(...)

):

    connection = None

    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        # --------------------------------------

        # Check existing email

        # --------------------------------------

        check_query = """

            SELECT id

            FROM patients

            WHERE email = %s

        """

        cursor.execute(

            check_query,

            (email,)

        )

        existing_patient = (

            cursor.fetchone()

        )

        if existing_patient:

            return templates.TemplateResponse(

                request,

                "register.html",

                {

                    "error": (

                        "This email is already "

                        "registered. Please login."

                    )

                }

            )

        # --------------------------------------

        # Insert patient

        # --------------------------------------

        query = """

            INSERT INTO patients

            (

                name,

                email,

                password

            )

            VALUES

            (

                %s,

                %s,

                %s

            )

        """

        values = (

            name,

            email,

            password

        )

        cursor.execute(

            query,

            values

        )

        connection.commit()

        logger.info(

            f"Patient registered: {email}"

        )

        return RedirectResponse(

            url="/login",

            status_code=303

        )

    except Exception as e:

        logger.error(

            f"Registration error: {e}"

        )

        if connection:

            connection.rollback()

        return templates.TemplateResponse(

            request,

            "register.html",

            {

                "error": (

                    "Registration failed. "

                    "Please try again."

                )

            }

        )

    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()

# ==========================================

# LOGIN PAGE

# ==========================================

@app.get(

    "/login",

    response_class=HTMLResponse

)

async def login_page(

    request: Request

):

    return templates.TemplateResponse(

        request,

        "login.html",

        {

            "error": None

        }

    )

# ==========================================

# LOGIN PATIENT

# ==========================================

@app.post("/login")

async def login_patient(

    request: Request,

    email: str = Form(...),

    password: str = Form(...)

):

    connection = None

    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(

            dictionary=True

        )

        # --------------------------------------

        # Find patient

        # --------------------------------------

        query = """

            SELECT

                id,

                name,

                email

            FROM patients

            WHERE email = %s

            AND password = %s

        """

        values = (

            email,

            password

        )

        cursor.execute(

            query,

            values

        )

        patient = cursor.fetchone()

        # --------------------------------------

        # Invalid login

        # --------------------------------------

        if patient is None:

            return templates.TemplateResponse(

                request,

                "login.html",

                {

                    "error":

                        "Invalid email or password."

                }

            )

        # --------------------------------------

        # Save session

        # --------------------------------------

        request.session[

            "patient_id"

        ] = patient["id"]

        request.session[

            "patient_name"

        ] = patient["name"]

        request.session["patient_email"] = patient["email"]

        logger.info(

            f"Patient logged in: "

            f"{patient['id']}"

        )

        # --------------------------------------

        # Login successful

        # --------------------------------------

        return RedirectResponse(

            url="/screening",

            status_code=303

        )

    except Exception as e:

        logger.error(

            f"Login error: {e}"

        )

        return templates.TemplateResponse(

            request,

            "login.html",

            {

                "error":

                    "Login failed. "

                    "Please try again."

            }

        )

    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()

# ==========================================

# PATIENT SESSION

# ==========================================

@app.get("/patient-session")

async def patient_session(

    request: Request

):

    patient_id = request.session.get(

        "patient_id"

    )

    patient_name = request.session.get(

        "patient_name"

    )

    return {

        "patient_id":

            patient_id,

        "patient_name":

            patient_name

    }

# ==========================================

# LOGOUT

# ==========================================

@app.get("/logout")

async def logout(

    request: Request

):

    request.session.clear()

    return RedirectResponse(

        url="/register",

        status_code=303

    )

# ==========================================

# RUN APPLICATION

# ==========================================

if __name__ == "__main__":

    uvicorn.run(

        "main:app",

        host="0.0.0.0",

        port=8000,

        reload=True

    )