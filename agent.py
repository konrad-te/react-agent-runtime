from tools import execute_bash, read_file, write_file, delete_file
from config import MAX_STEPS, SYSTEM_PROMPT, MAX_HISTORY
from memory import save_history, load_history

from google import genai
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

        if not assistant_text:
            print("Empty response from model")
            break

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
            
        if "ACTION: read_file" in assistant_text:

            file = (
                assistant_text
                .split("FILE:")[1]
                .strip()
            )

            print("\nReading the following file:")
            print(file)

            file_output = read_file(file)

            print("\nFile output:")
            print(file_output)
            
            conversation_history.append(
                f"Tool output: {file_output}"
            )
            save_history(conversation_history)

        if "ACTION: write_file" in assistant_text:

            if "FILE:" not in assistant_text:
                print("Invalid format")
                break

            file_name = (
                assistant_text
                .split("FILE:")[1]
                .split("CONTENT:")[0]
                .strip()
            )

            content = (
                assistant_text
                .split("CONTENT:")[1]
                .strip()
            )

            print("\nCreating a file:")
            print(file_name)

            file_output = write_file(file_name, content)

            print("\nFile output:")
            print(file_output)

            conversation_history.append(
                f"Tool output: {file_output}"
            )
            save_history(conversation_history)

        if "ACTION: delete_file" in assistant_text:

            filename = (
                assistant_text
                .split("FILE:")[1]
                .strip()
            )

            print("\nRemove the following file")
            print(filename)

            file_output = delete_file(filename)

            print("\nFile output:")
            print(file_output)

            conversation_history.append(
                f"Tool output: {file_output}"
            )
            save_history(conversation_history)

        else:
            break
