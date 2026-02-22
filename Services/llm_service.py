from sarvamai import SarvamAI
import os
from dotenv import load_dotenv
from Services.prompt_builder import build_prompt
load_dotenv()

client = SarvamAI(api_subscription_key=os.getenv("SARVAM_API_KEY"))

def summarize(text: str) -> str:
    response = client.chat.completions(
        messages=[{
            "role": "user",
            "content": f'''
            extract the core concepts from this content.
            remove formatting, repetition and irrelevant text
            {text}'''
        }]
    )

    return response.choices[0].message.content

def explain(summary: str, style: str, langauge: str) -> str:
    prompt = build_prompt(summary, style, langauge)

    response = client.chat.completions(
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    return response.choices[0].message.content