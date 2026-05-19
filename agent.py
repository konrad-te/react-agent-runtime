from tools import execute_bash
from config import MAX_STEPS, SYSTEM_PROMPT, MAX_HISTORY
from memory import save_history, load_history

import google.genai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("gemini_api")

client = genai.Client(api_key=api_key)



def run_agent(user_input):
    conversation_history = load_history()
    conversation_history.append(f"User: {user_input}")
    save_history(conversation_history)

    for step in range(MAX_STEPS):
        conversation_history = conversation_history[-MAX_HISTORY:]

        full_prompt = (
            SYSTEM_PROMPT
            + "\n\n"
            + "\n".join(conversation_history)
        )

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
            )

        except Exception as e:

            print("\nAPI Error:")
            print(e)

            break

        assistant_text = response.text

        print("\nAI:")
        print(assistant_text)

        conversation_history.append(
            f"Assistant: {assistant_text}"
        )
        save_history(conversation_history)
        

        if "FINAL ANSWER:" in assistant_text:
            break

        if "ACTION: bash" in assistant_text:

            command = (
                assistant_text
                .split("COMMAND:")[1]
                .strip()
            )

            print("\nExecuting command:")
            print(command)

            command_output = execute_bash(command)

            print("\nCommand output:")
            print(command_output)

            conversation_history.append(
                f"Tool output: {command_output}"
            )
            save_history(conversation_history)
            