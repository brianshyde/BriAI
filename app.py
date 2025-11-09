import gradio as gr
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PERSONALITY = """You are BriAI — warm, friendly, expressive.
Speak naturally, uplift, and help the user."""

def reply(hist):
    msgs = [{"role": "system", "content": PERSONALITY}]
    for user, bot in hist:
        if user: msgs.append({"role": "user", "content": user})
        if bot: msgs.append({"role": "assistant", "content": bot})
    return client.chat.completions.create(
        model="gpt-4o-mini", messages=msgs
    ).choices[0].message.content

def chat(msg, history):
    history.append([msg, None])
    bot_msg = reply(history)
    history[-1][1] = bot_msg
    return history, ""

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# BriAI")
    gr.Markdown("Your friendly AI companion")
    chatbot = gr.Chatbot(height=500)
    txt = gr.Textbox(placeholder="Talk to BriAI...", label="Message")
    txt.submit(chat, [txt, chatbot], [chatbot, txt])

demo.launch()
