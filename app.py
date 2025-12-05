import os, base64, hashlib, aiohttp, gradio as gr
from pathlib import Path
from openai import AsyncOpenAI
import PyPDF2
from docx import Document

# === CONFIG ===
client = AsyncOpenAI(api_key="os.getenv('OPENAI_API_KEY')")
MODEL = "gpt-4o-mini"
SYS = "You are BriAI — warm, expressive, friendly, and conversational. Always be helpful."

# === CACHE ===
cache = {}

# === HELPERS ===
def read_text(f):
    p = Path(f.name)
    if p.suffix.lower() == ".pdf":
        return "\n".join(page.extract_text() or "" for page in PyPDF2.PdfReader(f).pages)
    if p.suffix.lower() == ".docx":
        return "\n".join(p.text for p in Document(f).paragraphs)
    return p.read_text(encoding="utf-8", errors="ignore")

def encode_image(f):
    return base64.b64encode(f.read_bytes()).decode()

async def fetch_url(url):
    key = hashlib.md5(url.encode()).hexdigest()
    if key in cache: return cache[key]
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=10) as r:
                text = await r.text() if r.status == 200 else ""
                cache[key] = text[:5000]
                return cache[key]
    except:
        return "[Could not load webpage]"

# === CHAT STREAM ===
async def chat_stream(message, history, files, image, url):
    system_setup = [{"role": "system", "content": SYS}]

    # Attach FILES
    for f in files or []:
        name = Path(f.name).name
        if name.lower().endswith(('.png','.jpg','.jpeg','.webp')):
            system_setup.append({"role": "system","content":[{"type":"image_url","image_url":{"url":f"data:image;base64,{encode_image(f)}"}}]})
        else:
            try: text = read_text(f)[:3000]
            except: text = "[Unreadable file]"
            system_setup.append({"role": "system", "content": f"FILE ({name}):\n{text}"})

    # Attach pasted image
    if image:
        system_setup.append({"role": "system","content":[{"type":"image_url","image_url":{"url":f"data:image;base64,{encode_image(Path(image))}"}}]})

    # Attach webpage content
    if url:
        web = await fetch_url(url)
        system_setup.append({"role": "system", "content": f"WEBPAGE ({url}):\n{web}"})

    msgs = system_setup + history
    if message:
        msgs.append({"role": "user", "content": message})

    full = ""
    async for chunk in await client.chat.completions.create(
        model=MODEL, messages=msgs, stream=True
    ):
        if chunk.choices[0].delta.content:
            full += chunk.choices[0].delta.content
            yield history + [{"role":"user","content":message},{"role":"assistant","content":full}], ""

    yield history + [{"role":"user","content":message},{"role":"assistant","content":full}], ""

# === UI CSS (ChatGPT Style) ===
css = """
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
    display: flex;
    height: 100vh;
    flex-direction: column;
    font-family: Inter, sans-serif;
    background: #f7f8fa !important;
}

.gr-chatbot {
    background: white !important;
    border-radius: 14px !important;
    border: 1px solid #dcdcdc !important;
    padding: 14px !important;
    overflow-y: auto !important;
    height: 78vh !important;
}

.gr-chatbot-message.user {
    background: #2563eb !important;
    color: #ffffff !important;
    border-radius: 14px 14px 4px 14px !important;
    padding: 12px 16px !important;
    max-width: 72%;
    margin-left: auto !important;
}

.gr-chatbot-message.bot {
    background: #eceef1 !important;
    color: #111827 !important;
    border-radius: 14px 14px 14px 4px !important;
    padding: 12px 16px !important;
    max-width: 72%;
    margin-right: auto !important;
}

textarea {
    border-radius: 12px !important;
    border: 1px solid #ccd1d7 !important;
    padding: 14px !important;
    font-size: 1.05rem !important;
}

button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
}

.fullscreen-btn {
    position: fixed;
    bottom: 20px; right: 20px;
    width: 55px; height: 55px;
    border-radius: 50%;
    background: #6C5CE7;
    color: white; font-size: 1.6em;
    display: flex; justify-content: center; align-items: center;
    cursor: pointer;
    box-shadow: 0 6px 16px rgba(0,0,0,0.25);
}
"""

# === UI ===
# === UI ===
with gr.Blocks(title="BriAI") as demo:
    gr.HTML(f"<style>{css}</style>")

    gr.HTML("<h1 style='text-align:center;'>🤖 BriAI</h1>")

    chatbot = gr.Chatbot(
        avatar_images=(
            "https://i.imgur.com/MtGX2bg.png",
            "https://i.imgur.com/lX4gG2Z.png"
        )
    )

    msg = gr.Textbox(placeholder="Ask BriAI something...")
    files = gr.File(file_count="multiple", type="filepath", label="Attach Files")
    img = gr.Image(type="filepath", label="Paste/Upload Image")
    url = gr.Textbox(label="Web Link (optional)")
    submit = gr.Button("Send")

    # === EVENTS (✅ MUST BE INSIDE BLOCKS) ===
    submit.click(
        chat_stream,
        inputs=[msg, chatbot, files, img, url],
        outputs=[chatbot, msg]
    )

    msg.submit(
        chat_stream,
        inputs=[msg, chatbot, files, img, url],
        outputs=[chatbot, msg]
    )

demo.launch(theme=gr.themes.Soft(), share=True)
