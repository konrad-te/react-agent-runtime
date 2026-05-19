MAX_STEPS = 5
MAX_HISTORY = 20

BLOCKED_COMMANDS = [
    "rm",
    "rmdir",
    "del",
    "shutdown",
    "reboot"
]

system_prompt = """
You're SWE agent. When you want to execute a bash command, respond EXACTLY in this format:

ACTION: bash
COMMAND: <command>

If you want to answer normally, repsond like this:

FINAL ANSWER: <your answer>

Only use bash commands when necessary.
"""