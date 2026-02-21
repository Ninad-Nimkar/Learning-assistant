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
    you are helpful educatrional assistant,
    Explain the following topic clearly and simply.
    
    Explain the following topic in {style} style.

    Make it:
    - Clear
    - Engaging
    - Easy to understand
    - Suitable for Indian students

    Topic: {extracted_text}  
    """
        
            
    chat_response = client.chat.completions(
        messages=[{
            "content": prompt,
            "role": "user"
        }]
    )
        
    explanation = chat_response.choices[0].message.content
    return {
        "extracted_text": extracted_text[:4000],
        "explanation": explanation
    }
