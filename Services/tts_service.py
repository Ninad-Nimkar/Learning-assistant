from sarvamai import SarvamAI
import os
from dotenv import load_dotenv
import base64
from Services.prompt_builder import SPEAKER_BY_LANGAUGE
load_dotenv()

client = SarvamAI(api_subscription_key = os.getenv("SARVAM_API_KEY"))

def generate_audio(text: str, language: str):

    config = SPEAKER_BY_LANGAUGE.get(language, SPEAKER_BY_LANGAUGE["hindi"])

    audio = client.text_to_speech.convert(
        target_language_code = config["target_language_code"],
        text = text,
        model = "bulbul:v3",
        speaker = config["speaker"]
    )

    combined_audio = "".join(audio.audios)
    audio_bytes = base64.b64decode(combined_audio)

    with open("output.wav", "wb") as f:
        f.write(audio_bytes)

    return audio_bytes