import json
import os
from urllib import parse
from urllib import request
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("RUNPOD_CHAT_URL", "").rstrip("/")
CHAT_PASSWORD = os.getenv("RUNPOD_CHAT_PASSWORD", "")

def build_headers(include_json=False):
    """builds headers for the group chat api"""
    headers = {
        "User-Agent": "konrad-agent"
    }

    if include_json:
        headers["Content-Type"] = "application/json"

    return headers

def get_json(path, params=None):
    """gets json data from the group chat api"""
    params = params or {}

    if CHAT_PASSWORD:
        params["password"] = CHAT_PASSWORD

    query = parse.urlencode(params)
    url = BASE_URL + path

    if query:
        url = f"{url}?{query}"

    req = request.Request(
        url,
        headers=build_headers(),
        method="GET"
    )

    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))

def post_json(path, data):
    """sends json data to the group chat api"""
    if CHAT_PASSWORD:
        data["password"] = CHAT_PASSWORD

    body = json.dumps(data).encode("utf-8")
    req = request.Request(
        BASE_URL + path,
        data=body,
        headers=build_headers(include_json=True),
        method="POST"
    )

    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))

def fetch_messages(since=0):
    """gets messages from the shared group chat"""
    data = get_json("/api/messages", params={"since": since})
    return data.get("messages", data)

def send_message(agent_name, message):
    """sends one agent message to the shared group chat"""
    return post_json("/api/message", {
        "agent_name": agent_name,
        "content": message
    })

def fetch_stats():
    """gets current group chat stats"""
    return get_json("/api/stats")
