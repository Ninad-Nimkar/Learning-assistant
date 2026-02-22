from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import base64

from Services.ocr_service import extract_text
from utils.text_cleaner import clean_text
from Services.llm_service import summarize, explain
from Services.tts_service import generate_audio

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-and-explain")
async def upload_and_explain(
    file: UploadFile = File(...),
    style: str = Form("simple"),
    language: str = Form("hindi")
):
    file_bytes = await file.read()

    # 1. OCR
    raw_text = extract_text(file_bytes, file.filename)

    if not raw_text.strip():
        return JSONResponse(content={"error": "No text extracted from the file."}, status_code=400)

    # 2. Clean text
    cleaned_text = clean_text(raw_text)

    # 3. Summarize
    summary = summarize(cleaned_text)
    summary = clean_text(summary)

    # 4. Explain
    explanation = explain(summary, style, language)

    # 5. TTS
    audio_bytes = generate_audio(explanation)

    # Return both audio (base64) and transcript text
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    return JSONResponse(content={
        "audio": audio_b64,
        "transcript": explanation
    })

# Serve frontend static files (must be after API routes)
app.mount("/", StaticFiles(directory=str(BASE_DIR / "static"), html=True), name="static")