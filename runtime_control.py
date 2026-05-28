import time
from config import (
    DEFAULT_PAUSED,
    DEFAULT_RATE_LIMIT_SECONDS,
    DEFAULT_MAX_MODEL_CALLS_PER_SESSION,
    DEFAULT_MAX_TOOL_CALLS_PER_SESSION,
    DEFAULT_MAX_TOKEN_BUDGET,
)

state = {
    "paused": DEFAULT_PAUSED,
    "rate_limit_seconds": DEFAULT_RATE_LIMIT_SECONDS,
    "max_model_calls": DEFAULT_MAX_MODEL_CALLS_PER_SESSION,
    "max_tool_calls": DEFAULT_MAX_TOOL_CALLS_PER_SESSION,
    "max_token_budget": DEFAULT_MAX_TOKEN_BUDGET,
    "model_calls_used": 0,
    "tool_calls_used": 0,
    "tokens_used": 0,
    "last_response_time": 0,
}

def estimate_tokens(text):
    """estimates token usage in a simple way for budget control"""
    if not text:
        return 0

    return max(1, len(text) // 4)

def can_respond():
    """checks if the agent is allowed to answer right now"""
    if state["paused"]:
        return False, "Agent is paused"

    elapsed = time.time() - state["last_response_time"]

    if elapsed < state["rate_limit_seconds"]:
        wait_time = int(state["rate_limit_seconds"] - elapsed) + 1
        return False, (
            f"Rate limit active. Try again in {wait_time} seconds "
            "or change it with /rate <seconds>."
        )

    if state["model_calls_used"] >= state["max_model_calls"]:
        return False, "Model call budget exhausted"

    if state["tokens_used"] >= state["max_token_budget"]:
        return False, "Token budget exhausted"

    return True, "OK"

def record_response():
    """stores when the agent last answered for rate limiting"""
    state["last_response_time"] = time.time()

def can_call_model():
    """checks if one more model/API call is allowed."""
    if state["model_calls_used"] >= state["max_model_calls"]:
        return False, "Model call budget exhausted"

    return True, "OK"

def record_model_call():
    """counts one model/API call"""
    state["model_calls_used"] += 1

def can_spend_tokens(text):
    """checks if sending this text would stay inside the token budget"""
    estimated_tokens = estimate_tokens(text)

    if state["tokens_used"] + estimated_tokens > state["max_token_budget"]:
        return False, "Token budget would be exceeded"

    return True, "OK"

def record_token_usage(text):
    """Adds estimated token usage to the session total."""
    state["tokens_used"] += estimate_tokens(text)

def can_use_tool():
    """Checks if the agent can still use another tool."""
    if state["tool_calls_used"] >= state["max_tool_calls"]:
        return False, "Tool call budget exhausted"

    return True, "OK"

def record_tool_call():
    """Counts one tool call."""
    state["tool_calls_used"] += 1

def reset_usage():
    """Resets counters but keeps current limits."""
    state["model_calls_used"] = 0
    state["tool_calls_used"] = 0
    state["tokens_used"] = 0
    state["last_response_time"] = 0

def parse_positive_int(value):
    """Turns command text into a positive number if possible."""
    try:
        number = int(value)
    except ValueError:
        return None

    if number < 0:
        return None

    return number

def handle_console_command(command):
    """Handles local slash commands for live agent control."""
    parts = command.strip().split()

    if not parts:
        return "No command"

    if parts[0] == "/help":
        return (
            "Commands: /help, /status, /pause, /resume, /rate <seconds>, "
            "/model-budget <count>, /tool-budget <count>, "
            "/token-budget <tokens>, /reset-usage"
        )

    if parts[0] == "/pause":
        state["paused"] = True
        return "Agent paused"

    if parts[0] == "/resume":
        state["paused"] = False
        return "Agent resumed"

    if parts[0] == "/rate":
        if len(parts) != 2:
            return "Usage: /rate <seconds>"

        seconds = parse_positive_int(parts[1])

        if seconds is None:
            return "Rate limit must be a positive number"

        state["rate_limit_seconds"] = seconds
        return f"Rate limit set to {parts[1]} seconds"

    if parts[0] == "/model-budget":
        if len(parts) != 2:
            return "Usage: /model-budget <count>"

        count = parse_positive_int(parts[1])

        if count is None:
            return "Model budget must be a positive number"

        state["max_model_calls"] = count
        return f"Model call budget set to {parts[1]}"

    if parts[0] == "/tool-budget":
        if len(parts) != 2:
            return "Usage: /tool-budget <count>"

        count = parse_positive_int(parts[1])

        if count is None:
            return "Tool budget must be a positive number"

        state["max_tool_calls"] = count
        return f"Tool call budget set to {parts[1]}"

    if parts[0] == "/token-budget":
        if len(parts) != 2:
            return "Usage: /token-budget <tokens>"

        tokens = parse_positive_int(parts[1])

        if tokens is None:
            return "Token budget must be a positive number"

        state["max_token_budget"] = tokens
        return f"Token budget set to {parts[1]}"

    if parts[0] == "/reset-usage":
        reset_usage()
        return "Usage counters reset"

    if parts[0] == "/status":
        return str(state)

    return "Unknown command"
