# app.py — BriAI: Your Friendly AI Companion (PWA + Gradio + OpenAI)

import os
import gradio as gr
from openai import OpenAI

# ========================================
# 1. OpenAI Setup
# ========================================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ========================================
# 2. AI Personality
# ========================================
PERSONALITY = """
You are BriAI — a warm, friendly, expressive AI companion.
You speak clearly, use natural human tone, avoid robotic answers.
Encourage, uplift, and be genuinely helpful.
"""

# ========================================
# 3. Generate Reply (expects [[user, bot], ...])
# ========================================
def generate_reply(history: list) -> str:
    messages = [{"role": "system", "content": PERSONALITY}]
    for user_msg, bot_msg in history:
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if bot_msg:
            messages.append({"role": "assistant", "content": bot_msg})
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return resp.choices[0].message.content

# ========================================
# 4. Gradio → OpenAI Bridge
# ========================================
def respond(message: str, chat_history: list[dict]) -> tuple[list[dict], str]:
    # Convert Gradio dicts → [[user, bot]]
    openai_hist = []
    for msg in chat_history:
        if msg["role"] == "user":
            openai_hist.append([msg["content"], None])
        else:
            openai_hist.append([None, msg["content"]])
    openai_hist.append([message, None])

    reply = generate_reply(openai_hist)

    # Append in Gradio format
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": reply})

    return chat_history, ""

# ========================================
# 5. Custom CSS
# ========================================
custom_css = """
#chatbot {height: 560px !important; border-radius: 12px; overflow: hidden;}
.gr-chatbot-message.user {background: #2563eb !important; color: white !important; border-radius: 12px; margin: 6px;}
.gr-chatbot-message.bot   {background: #1f2937 !important; color: #e5e7eb !important; border-radius: 12px; margin: 6px;}
body {background: linear-gradient(135deg, #111827, #1f2937); margin: 0; font-family: 'Segoe UI', sans-serif;}
#center-header {text-align: center; padding: 20px 10px;}
"""

# ========================================
# 6. Gradio UI
# ========================================
with gr.Blocks(css=custom_css, theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate")) as demo:

    # Header
    with gr.Column(elem_id="header"):
        with gr.Row():
            gr.HTML("""
            <div id="center-header">
                <h1 style="color:white; font-size:40px; font-weight:800; margin:0;">BriAI</h1>
                <p style="color:#9CA3AF; font-size:18px; margin:5px 0;">Your friendly AI companion</p>
            </div>
            """)

    # Chatbot
    chatbot = gr.Chatbot(elem_id="chatbot", type="messages", label="BriAI Chat Window", height=560)

    # Input
    with gr.Row():
        txt = gr.Textbox(
            placeholder="Say something to BriAI...",
            label="Message",
            scale=8,
            container=False
        )
        btn = gr.Button("Send", variant="primary", scale=1)

    # Events
    btn.click(respond, [txt, chatbot], [chatbot, txt])
    txt.submit(respond, [txt, chatbot], [chatbot, txt])

# ========================================
# 7. Launch as PWA (with custom icons & manifest)
# ========================================
demo.launch(
    share=True,
    pwa={
        "name": "BriAI - AI Companion",
        "short_name": "BriAI",
        "description": "A warm, friendly AI chat companion powered by GPT.",
        "start_url": ".",
        "display": "standalone",
        "background_color": "#111827",
        "theme_color": "#2563eb",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": "icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
)
