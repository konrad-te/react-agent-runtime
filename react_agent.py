import subprocess
import google.genai as genai
import os
from dotenv import load_dotenv
import shlex

load_dotenv()

api_key = os.getenv("gemini_api")

client = genai.Client(api_key=api_key)

conversation_history = []

system_prompt = """
You're SWE agent. When you want to execute a bash command, respond EXACTLY in this format:

ACTION: bash
COMMAND: <command>

If you want to answer normally, repsond like this:

FINAL ANSWER: <your answer>

Only use bash commands when necessary.
"""

MAX_STEPS = 5

BLOCKED_COMMANDS = [
    "rm",
    "rmdir",
    "del",
    "shutdown",
    "reboot"
]


while True:

    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        break

    conversation_history.append(f"User: {user_input}")

    for step in range(MAX_STEPS):

        full_prompt = system_prompt + "\n\n" + "\n".join(conversation_history)

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
            )
        
        except Exception as e:
            print("\nAPI Error>")
            print(e)
            break

        assistant_text = response.text

        print("\nAI:")
        print(assistant_text)

        conversation_history.append(f"Assistant: {assistant_text}")

        if "FINAL ANSWER:" in assistant_text:
            break

        if "ACTION: bash" in assistant_text:

            command = assistant_text.split("COMMAND:")[1].strip()

            print("\nExecuting command:")
            print(command)

            try:
                parsed_command = shlex.split(command)
                base_command = parsed_command

                if base_command in BLOCKED_COMMANDS:
                    command_output = "Command blocked for safety"
                    
                else:
                    result = subprocess.run(
                        parsed_command,
                        capture_output=True,
                        text=True
                    )
                    command_output = result.stdout or result.stderr

            except Exception as e:
                command_output = str(e)

            print("\nCommand output:")
            print(command_output)

            conversation_history.append(
                f"Tool output: {command_output}"
            )


    # user_input= input("\nYou: ")

    # if user_input.lower() == "exit":
    #     break

    # conversation_history.append(f"User: {user_input}")

    # full_prompt = system_prompt + "\n\n" + "\n".join(conversation_history)

    # response = client.models.generate_content(
    #     model="gemini-2.5-flash",
    #     contents=full_prompt
    # )

    # assistant_text = response.text
    # if "ACTION: bash" in assistant_text:

    #     command = assistant_text.split("COMMAND:")[1].strip()

    #     print("\nExecuting command:")
    #     print(command)

    #     try:
    #         result = subprocess.run(
    #             command.split(),
    #             capture_output=True,
    #             text=True
    #         )

    #         command_output = result.stdout

    #         print("Command output:\n")
    #         print(command_output)

    #         conversation_history.append(
    #             f"Tool output: {command_output}"
    #         )

    #         followup_response = client.models.generate_content(
    #             model="gemini-2.5-flash",
    #             contents=system_prompt + "\n\n" + "\n".join(conversation_history)
    #         )

    #         followup_text = followup_response.text

    #         print("\nAI:")
    #         print(followup_text)

    #         conversation_history.append(
    #             f"Assistant: {followup_text}"
    #         )
    #     except Exception as e:
    #         command_output = str(e)

    #         print("\nExecution error:")
    #         print(command_output)

    # print("\nAI:")
    # print(assistant_text)

    # conversation_history.append(f"Assistant: {assistant_text}")