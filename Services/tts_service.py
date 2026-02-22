from sarvamai import SarvamAI
import os
from dotenv import load_dotenv
import base64
load_dotenv()

client = SarvamAI(api_subscription_key = os.getenv("SARVAM_API_KEY"))

def generate_audio(text: str):
    audio = client.text_to_speech.convert(
        target_language_code="en-IN",
        text = text,
        model = "bulbul:v3",
        speaker="ritu"
    )

    combined_audio = "".join(audio.audios)
    audio_bytes = base64.b64decode(combined_audio)

    with open("output.wav", "wb") as f:
        f.write(audio_bytes)

    return audio_bytes