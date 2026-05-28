import json
import os
from urllib import request
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("RUNPOD_CHAT_URL", "").rstrip("/")

def get_json(path):
    """gets json data from the group chat api"""
    with request.urlopen(BASE_URL + path, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))

def post_json(path, data):
    """sends json data to the group chat api"""
    body = json.dumps(data).encode("utf-8")
    req = request.Request(
        BASE_URL + path,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))

def fetch_messages():
    """gets messages from the shared group chat"""
    return get_json("/api/messages")

def send_message(agent_name, message):
    """sends one agent message to the shared group chat"""
    return post_json("/api/message", {
        "agent": agent_name,
        "message": message
    })

def fetch_stats():
    """gets current group chat stats"""
    return get_json("/api/stats")
