from agent import run_agent
from runtime_control import handle_console_command

while True:

    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        break
    
    if user_input.startswith("/"):
        print(handle_console_command(user_input))
        continue

    run_agent(user_input)