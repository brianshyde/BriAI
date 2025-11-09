from openai import OpenAI
import os

# Load API Key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

while True:
    user = input("You: ")
    if user.lower() == "exit":
        break

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user}]
    )

    print("AI:", response.choices[0].message.content)
