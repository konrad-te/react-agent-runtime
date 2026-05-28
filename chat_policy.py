from config import AGENT_NAME

def should_respond(message_text):
    """Decides if this agent should answer a group chat message."""
    text = message_text.lower()
    agent_name = AGENT_NAME.lower()

    if f"@{agent_name}" in text:
        return True, "Agent was directly mentioned"

    if agent_name in text:
        return True, "Agent name was mentioned"

    if "all agents" in text or "@everyone" in text:
        return True, "Team-wide request"

    if "can someone" in text or "anyone" in text:
        return True, "Open team request"

    if "who can" in text or "need help" in text:
        return True, "Help request"

    if "please claim" in text or "claim one small task" in text:
        return True, "Task claim request"

    return False, "No response needed"
