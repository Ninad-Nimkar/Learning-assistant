from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from fastapi import UploadFile, File
from sarvamai import SarvamAI
import pdfplumber
import pytesseract
from PIL import Image
import io
from sarvamai.play import save
import base64
from fastapi.responses import StreamingResponse

load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
client = SarvamAI(api_subscription_key=SARVAM_API_KEY) 

app = FastAPI()

@app.post("/upload-and-explain")
async def upload_and_explain(file: UploadFile = File(...), style = "simple"):

    file_bytes = await file.read()
    extracted_text = ""

    #extract text
    if file.filename.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() or ""

    extracted_text = extracted_text[:4000]

    prompt = f"""
    you are a friendly Indian educational assistant.

    Explain the topic in {style} style.

    Important:
    - keep sentence short.
    - Use conversationa tone.
    - Make it sound natural when spoken.
    - Avoid bullet points.
    - Avoid markdown fomatting
    - If Target language is regional language, use simple language Vocabulary.

    Topic: {extracted_text}
    """
        
            
    chat_response = client.chat.completions(
        messages=[{
            "content": prompt,
            "role": "user"
        }]
    )
        
    explanation = chat_response.choices[0].message.content

    audio = client.text_to_speech.convert(
        target_language_code = "hi-IN",
        text = explanation,
        model = "bulbul:v3",
        speaker = "ishita"
    )

    audio_base64 = audio.audios[0]
    audio_bytes = base64.b64decode(audio_base64)

    with open("output.wav", "wb") as f:
        f.write(audio_bytes)


    return StreamingResponse(
        audio_bytes,
        media_type = "audio/wav"
    )