from tools import execute_bash, read_file, write_file, delete_file, replace_in_file
from config import MAX_STEPS, SYSTEM_PROMPT, MAX_HISTORY, PRIMARY_MODEL, FALLBACK_MODEL
from memory import save_history, load_history
from runtime_control import (
    can_respond,
    record_response,
    can_call_model,
    record_model_call,
    can_spend_tokens,
    record_token_usage,
    can_use_tool,
    record_tool_call
)

from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("gemini_api")

client = genai.Client(api_key=api_key)


def is_retryable_api_error(error):
    """Checks if an API error is temporary enough to try fallback."""
    error_text = str(error).lower()
    retryable_markers = [
        "503",
        "unavailable",
        "rate",
        "quota",
        "resource_exhausted",
    ]

    return any(marker in error_text for marker in retryable_markers)

def generate_with_fallback(full_prompt):
    """Calls the primary model first, then fallback once if needed."""
    last_error = None

    for model_name in [PRIMARY_MODEL, FALLBACK_MODEL]:
        can_call, reason = can_call_model()

        if not can_call:
            raise RuntimeError(reason)

        try:
            record_model_call()
            record_token_usage(full_prompt)

            if model_name == FALLBACK_MODEL:
                print(f"\nTrying fallback model: {model_name}")

            return client.models.generate_content(
                model=model_name,
                contents=full_prompt
            )

        except Exception as e:
            last_error = e

            if model_name == FALLBACK_MODEL or not is_retryable_api_error(e):
                raise

            print(f"\nPrimary model failed, trying fallback: {e}")

    raise last_error


def run_agent(user_input):
    """Runs one user request through the agent loop."""
    can_run, reason = can_respond()

    if not can_run:
        print(reason)
        return reason

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

        can_spend, reason = can_spend_tokens(full_prompt)

        if not can_spend:
            print(reason)
            record_response()
            return reason

        try:
            response = generate_with_fallback(full_prompt)

        except Exception as e:
            error_message = f"API Error: {e}"

            print("\nAPI Error:")
            print(e)

            return error_message

        assistant_text = response.text

        if not assistant_text:
            print("Empty response from model")
            record_response()
            return "Empty response from model"

        record_token_usage(assistant_text)

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
            return "Invalid JSON response from model"

        response_type = assistant_data.get("type")

        if response_type == "final":
            message = assistant_data.get("message", "")

            print("\nFinal answer:")
            print(message)
            record_response()
            return message

        if response_type != "tool_call":
            print("Invalid response type")
            return "Invalid response type"

        tool = assistant_data.get("tool")
        can_run_tool, reason = can_use_tool()

        if not can_run_tool:
            tool_output = reason

        elif tool == "bash":
            command = assistant_data.get("command", "")

            print("\nExecuting command:")
            print(command)

            record_tool_call()
            tool_output = execute_bash(command)

        elif tool == "read_file":
            filename = assistant_data.get("file", "")

            print("\nReading the following file:")
            print(filename)

            record_tool_call()
            tool_output = read_file(filename)

        elif tool == "write_file":
            filename = assistant_data.get("file", "")
            content = assistant_data.get("content", "")

            print("\nCreating a file:")
            print(filename)

            record_tool_call()
            tool_output = write_file(filename, content)

        elif tool == "replace_in_file":
            filename = assistant_data.get("file", "")
            old_text = assistant_data.get("old", "")
            new_text = assistant_data.get("new", "")

            print("\nReplacing text in file:")
            print(filename)

            record_tool_call()
            tool_output = replace_in_file(filename, old_text, new_text)

        elif tool == "delete_file":
            filename = assistant_data.get("file", "")

            print("\nRemove the following file")
            print(filename)

            record_tool_call()
            tool_output = delete_file(filename)

        else:
            tool_output = f"Unknown tool: {tool}"

        print("\nTool output:")
        print(tool_output)

        conversation_history.append(
            f"Tool output: {tool_output}"
        )
        save_history(conversation_history)

    return "Agent stopped before producing a final answer"
