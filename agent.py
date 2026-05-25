from tools import execute_bash, read_file, write_file, delete_file, replace_in_file
from config import MAX_STEPS, SYSTEM_PROMPT, MAX_HISTORY
from memory import save_history, load_history

from google import genai
import os
import json
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

        try:
            assistant_data = json.loads(assistant_text)
        except json.JSONDecodeError:
            print("Invalid JSON response from model")
            break

        response_type = assistant_data.get("type")

        if response_type == "final":
            print("\nFinal answer:")
            print(assistant_data.get("message", ""))
            break

        if response_type != "tool_call":
            print("Invalid response type")
            break

        tool = assistant_data.get("tool")

        if tool == "bash":
            command = assistant_data.get("command", "")

            print("\nExecuting command:")
            print(command)

            tool_output = execute_bash(command)

        elif tool == "read_file":
            filename = assistant_data.get("file", "")

            print("\nReading the following file:")
            print(filename)

            tool_output = read_file(filename)

        elif tool == "write_file":
            filename = assistant_data.get("file", "")
            content = assistant_data.get("content", "")

            print("\nCreating a file:")
            print(filename)

            tool_output = write_file(filename, content)

        elif tool == "replace_in_file":
            filename = assistant_data.get("file", "")
            old_text = assistant_data.get("old", "")
            new_text = assistant_data.get("new", "")

            print("\nReplacing text in file:")
            print(filename)

            tool_output = replace_in_file(filename, old_text, new_text)

        elif tool == "delete_file":
            filename = assistant_data.get("file", "")

            print("\nRemove the following file")
            print(filename)

            tool_output = delete_file(filename)

        else:
            tool_output = f"Unknown tool: {tool}"

        print("\nTool output:")
        print(tool_output)

        conversation_history.append(
            f"Tool output: {tool_output}"
        )
        save_history(conversation_history)
