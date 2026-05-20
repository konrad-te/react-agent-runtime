import subprocess
import shlex
from config import BLOCKED_COMMANDS, BLOCKED_FILES

def execute_bash(command):
    try:
        parsed_command = shlex.split(command)
        base_command = parsed_command[0]
        arguments = parsed_command[1:]
        for argument in arguments:
            if argument in BLOCKED_FILES:
                return "Access denied"
        if base_command in BLOCKED_COMMANDS:
            return "Command blocked for safety"
        
        result = subprocess.run(
            parsed_command,
            capture_output=True,
            text=True
        )
        return result.stdout or result.stderr
    
    except Exception as e: 
        return str(e)
    
def read_file(filename):
    if filename in BLOCKED_FILES:
        return "Access denied"
    try:
        with open(filename, "r") as file:
            return file.read()
    except FileNotFoundError:
        return "File not found"

def write_file(filename, content):
        try:
            with open(filename, "w") as file:
                file.write(content)
            return "File written successfully"
        except Exception as e:
            return str(e)
