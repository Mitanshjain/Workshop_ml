import os

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")

if not api_key:
    raise ValueError(
        "ELEVENLABS_API_KEY not found in .env"
    )


# ==========================================
# CREATE ELEVENLABS CLIENT
# ==========================================

client = ElevenLabs(
    api_key=api_key
)


# ==========================================
# OPEN INPUT AUDIO
# ==========================================

print("Reading input audio...")

with open("sts_input.mp4", "rb") as audio_file:

    print("Converting speech to speech...")

    audio = client.speech_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        audio=audio_file,
        model_id="eleven_multilingual_sts_v2",
        output_format="mp3_44100_128"
    )


    # ==========================================
    # SAVE CONVERTED AUDIO
    # ==========================================

    with open(
        "sanjeevani_sts_output.mp3",
        "wb"
    ) as output_file:

        for chunk in audio:

            if chunk:
                output_file.write(chunk)


print("Speech-to-Speech successful!")

print(
    "Audio saved as "
    "sanjeevani_sts_output.mp3"
)