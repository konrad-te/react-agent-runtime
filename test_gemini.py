import google.genai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("gemini_api")

client = genai.Client(api_key=api_key)

messages = []


while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    messages.append(
        {
            "role": "user",
            "parts": [{"text": user_input}]
        }
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages
    )

    assistant_text= response.text

    print("\nAI:", assistant_text)

    messages.append(
        {
            "role": "model",
            "parts": [{"text": assistant_text}]
        }
    )

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say Hello"
)

print(response.text)