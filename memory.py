import json




def save_history(history):
    with open('history.json', 'w') as f:
        json.dump(history, f, indent=4)

def load_history():
    try:
        with open('history.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []