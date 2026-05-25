import subprocess
import shlex
from config import BLOCKED_FILES, ALLOWED_COMMANDS, MAX_TOOL_OUTPUT
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()

def execute_bash(command):
    try:
        parsed_command = shlex.split(command)
        base_command = parsed_command[0]
        arguments = parsed_command[1:]
        if base_command not in ALLOWED_COMMANDS:
            return f"Command not allowed: {base_command}"

        for argument in arguments:
            if is_blocked_file(argument):
                return "Access denied"
        
        result = subprocess.run(
            parsed_command,
            cwd = PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout or result.stderr
        return limit_output(output)
    
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e: 
        return str(e)
    
def read_file(filename):
    if is_blocked_file(filename):
        return "Access denied"
    try:
        with open(filename, "r") as file:
            return limit_output(file.read())
        
    except FileNotFoundError:
        return "File not found"

def write_file(filename, content):
        try:
            with open(filename, "w") as file:
                file.write(content)
            return "File written successfully"
        except Exception as e:
            return str(e)
        
def delete_file(filename):
    try:
        if is_blocked_file(filename):
            return "Access denied"
        os.remove(filename)
        return f"{filename} removed successfully"
    except FileNotFoundError:
        return "File not found"
    
def replace_in_file(filename, old_text, new_text):
    if is_blocked_file(filename):
        return "Access denied"
    
    try:
        with open(filename, "r") as file:
            content = file.read()
        
        count = content.count(old_text)
        if count == 0:
            return "Text to replace was not found"
        
        if count > 1:
            return "Text to replace appears multiple times"
        
        updated_content = content.replace(old_text, new_text, 1)

        with open(filename, "w") as file:
            file.write(updated_content)

        return "File section replaced successfully"
    
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return str(e)

### Helper function compares real path against the real path of every blocked file

def is_blocked_file(path_text):
    try:
        requested_path = (PROJECT_ROOT / path_text).resolve()
    except Exception:
        return False
    
    for blocked_file in BLOCKED_FILES:
        blocked_path = (PROJECT_ROOT / blocked_file).resolve()
        if requested_path == blocked_path:
            return True
        
    return False

### Helper function to cut output

def limit_output(output):
    if output is None:
        return ""
    
    if len(output) <= MAX_TOOL_OUTPUT:
        return output
    
    return output[:MAX_TOOL_OUTPUT] + "\n\n[Tool output truncated]"
