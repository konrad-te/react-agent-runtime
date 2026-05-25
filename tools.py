import subprocess
import shlex
from config import BLOCKED_FILES, ALLOWED_COMMANDS
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()

def execute_bash(command):
    try:
        parsed_command = shlex.split(command)
        base_command = parsed_command[0]
        arguments = parsed_command[1:]
        for argument in arguments:
            if is_blocked_file(argument):
                return "Access deni"
            if base_command not in ALLOWED_COMMANDS:
                return f"Command not allowed: {command}"
        
        result = subprocess.run(
            parsed_command,
            cwd = PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        return result.stdout or result.stderr
    
    except Exception as e: 
        return str(e)
    
def read_file(filename):
    if is_blocked_file(filename):
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
        
def delete_file(filename):
    try:
        if is_blocked_file(filename):
            return "Access denied"
        os.remove(filename)
        return f"{filename} removed successfully"
    except FileNotFoundError:
        return "File not found"
    

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