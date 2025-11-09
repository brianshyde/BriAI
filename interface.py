import gradio as gr
import openai
from dotenv import load_dotenv
import json
import os

# -------------------------
# Load API Key
# -------------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

MEMORY_FILE = "conversation_memory.json"


# -------------------------------------------------------
# ✅ Load or Create Memory File
# -------------------------------------------------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_memory(history):
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


# -------------------------------------------------------
# ✅ Chatbot Logic (With Persistent Memory)
# -------------------------------------------------------
def chatbot(user_input, history):

    if history is None or history == "":
        history = load_memory()

    # Append new user message
    history.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",    # ✅ faster + better model
            messages=history
        )

        reply = response.choices[0].message.content

        # Append assistant reply
        history.append({"role": "assistant", "content": reply})

        # Save memory
        save_memory(history)

        return reply, history

    except Exception as e:
        return f"⚠️ Error: {str(e)}", history


# -------------------------------------------------------
# ✅ UI IMPROVEMENTS
# -------------------------------------------------------
custom_css = """
#chatbot {
    height: 600px !important;
}
.gradio-container {
    background: linear-gradient(135deg, #e8f1ff 0%, #ffffff 100%);
}
#title {
    text-align: center;
    font-size: 2.3rem;
    font-weight: bold;
    margin-bottom: 10px;
    color: #1a3d7c;
}
#subtitle {
    text-align: center;
    font-size: 1.1rem;
    color: #333;
    margin-bottom: 25px;
}
"""


with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:

    gr.Markdown("<div id='title'>🧊 BrainIce ML — Personal Smart AI</div>")
    gr.Markdown("<div id='subtitle'>Your always-learning AI assistant powered by persistent memory.</div>")

    with gr.Row():
        model_choice = gr.Dropdown(
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            value="gpt-4o-mini",
            label="Model"
        )
        clear_memory_btn = gr.Button("🧹 Clear Memory", variant="stop")

    chatbotUI = gr.ChatInterface(
        fn=chatbot,
        title="BrianTechAI",
        retry_btn="🔁 Retry",
        undo_btn="↩ Undo",
        clear_btn="🧽 Clear Chat",
        chatbot=gr.Chatbot(
            height=600,
            avatar_images=("https://i.imgur.com/4M34hi2.png", 
                           "https://i.imgur.com/Qb7Vop2.png")
        ),
        additional_inputs=[model_choice],
    )

    # Clear memory button event
    def clear_memory():
        save_memory([])
        return gr.Info("✅ Memory cleared successfully!")

    clear_memory_btn.click(clear_memory)


# -------------------------------------------------------
# ✅ Launch App
# -------------------------------------------------------
demo.launch(share=True)

