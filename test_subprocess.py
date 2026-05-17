import subprocess

command = input("Enter command: ")

try:
    result = subprocess.run(
        command.split(),
        capture_output=True,
        text=True
    )
except Exception as e:
    print(e)
    
print("STDOUT:")
print(result.stdout)

print("STDERR:")
print(result.stderr)

print("RETURN CODE:")
print(result.returncode)

print(result)