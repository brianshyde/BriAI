from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Load OpenAI Client using ENV variable key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
# Serve UI (interface folder)
app.mount("/interface", StaticFiles(directory="interface"), name="interface")

@app.get("/")
def home():
    return FileResponse("interface/index.html")

class Message(BaseModel):
    text: str

@app.post("/chat")
def chat_endpoint(message: Message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message.text}]
    )
    reply_text = response.choices[0].message.content
    return {"reply": reply_text}
