import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load variables from .env
load_dotenv()

# Get ElevenLabs API key
api_key = os.getenv("ELEVENLABS_API_KEY")

if not api_key:
    raise ValueError("ELEVENLABS_API_KEY not found in .env")

# Create ElevenLabs client
client = ElevenLabs(
    api_key=api_key
)

# Text that we want to convert into speech
text = "Hello, welcome to Sanjeevani Clinic. How can I help you today?"

print("Generating speech...")

# Convert text to speech
audio = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    output_format="mp3_44100_128",
    text=text,
    model_id="eleven_multilingual_v2",
)

# Save generated audio
with open("sanjeevani_tts.mp3", "wb") as file:
    for chunk in audio:
        if chunk:
            file.write(chunk)

print("TTS successful!")
print("Audio saved as sanjeevani_tts.mp3")