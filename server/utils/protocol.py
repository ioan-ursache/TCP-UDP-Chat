import json

def encode_message(msg_type, text, sender = None):
    # type \ text \ sender - format
    msg = {"type": msg_type, "text": text}
    if sender:
        msg["from"] = sender
    return json.dumps(msg) + "\n"

def decode_message(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None