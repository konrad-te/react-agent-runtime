import time
from config import AGENT_NAME
from agent import run_agent
from chat_adapter import fetch_messages, send_message
from chat_policy import should_respond

POLL_SECONDS = 5
seen_message_ids = set()

def get_message_id(message):
    """gets a stable id from a chat message"""
    if isinstance(message, dict):
        return str(
            message.get("id")
            or message.get("seq")
            or message.get("sequence")
            or message.get("timestamp")
            or message.get("created_at")
            or message
        )

    return str(message)

def get_message_text(message):
    """gets text from a chat message"""
    if not isinstance(message, dict):
        return str(message)

    return (
        message.get("message")
        or message.get("text")
        or message.get("content")
        or message.get("body")
        or ""
    )

def get_message_agent(message):
    """gets sender name from a chat message"""
    if not isinstance(message, dict):
        return ""

    return (
        message.get("agent")
        or message.get("sender")
        or message.get("author")
        or message.get("name")
        or ""
    )

def normalize_name(name):
    """normalizes a name so comparisons are easier"""
    return name.strip().lower()

def is_own_message(message):
    """checks if the message came from this agent"""
    sender = normalize_name(get_message_agent(message))
    agent_name = normalize_name(AGENT_NAME)

    return sender == agent_name

def remember_existing_messages():
    """marks old messages as seen before the agent starts"""
    messages = fetch_messages()

    for message in messages:
        seen_message_ids.add(get_message_id(message))

    print(f"remembered {len(seen_message_ids)} existing messages")

def handle_message(message):
    """handles one group chat message if it needs an answer"""
    message_id = get_message_id(message)

    if message_id in seen_message_ids:
        return

    seen_message_ids.add(message_id)

    if is_own_message(message):
        return

    text = get_message_text(message)
    should_answer, reason = should_respond(text)

    if not should_answer:
        return

    print(f"responding because: {reason}")
    answer = run_agent(text)

    if answer:
        send_message(AGENT_NAME, answer)

def run_group_chat_loop():
    """runs the agent inside the shared group chat"""
    remember_existing_messages()

    while True:
        try:
            messages = fetch_messages()

            for message in messages:
                handle_message(message)

        except Exception as e:
            print(f"group chat error: {e}")

        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    run_group_chat_loop()
