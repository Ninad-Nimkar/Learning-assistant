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
async def upload_and_explain(file: UploadFile = File(...), style = "simple", language = "Hindi"):

    file_bytes = await file.read()
    extracted_text = " "

    #extract text
    if file.filename.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() or ""

    extracted_text = extracted_text.replace("\n", " ")[:7000]

    prompt = f"""
-You are a smart best buddy.
-don't introduce the topic, directly start the explanation.
-translate in a ready to speech language.
-NO special characters.
-Mix English and {language} language for better understanding.
-Respond ONLY in {language}.
-Do NOT use English in case of regional language.
-Do NOT translate word by word.
-Explain the concept in naturally and daily simple spoken {language} language (we don't want pure regional langauge).
-Match the {style} vibe by using terms related to {style} and examples.

-The following content is only for understanding: {extracted_text}

Remember:
Your entire response must be in {language}.
"""
        
            
    chat_response = client.chat.completions(
        messages=[{
            "content": prompt,
            "role": "user"
        }]
    )
        
    explanation = chat_response.choices[0].message.content

    audio = client.text_to_speech.convert(
        target_language_code = "en-IN",
        text = explanation,
        model = "bulbul:v3",
        speaker = "suhani"
    )

    audio_base64 = audio.audios[0]
    audio_bytes = base64.b64decode(audio_base64)

    with open("output.wav", "wb") as f:
        f.write(audio_bytes)

    print(explanation)

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type = "audio/wav"
    )