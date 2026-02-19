from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class ExplainRequest(BaseModel):
    text: str
    style: str = "simple"

@app.get("/")
def root():
    return {"message": "AI Explainer Backen Running"}

@app.post("/explain")
def explain(request:ExplainRequest):

    prompt = f"""
    you are helpful educatrional assistant,
    Explain the following topic clearly and simply.
    
    Explain the following topic in {request.style} style.

    Make it:
    - Clear
    - Engaging
    - Easy to understand
    - Suitable for Indian students

    Topic: {request.text}
    """
        
    response = requests.post(
        "https://api.sarvam.ai/v1/chat/completions",
        headers = {
            "api-subscription-key": os.getenv("SARVAM_API_KEY")
        },
        json={
            "messages":[
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "model": "sarvam-m"
        }
    )
    
    return (response.json()["choices"][0]["message"]["content"])
