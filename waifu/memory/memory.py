import json
from config import base_path

messages = None
conversation_path = f"{base_path}/waifu/memory/conversation.json"

def save_conversation():
    global messages
    if not messages:
        print("No conversation to save.")
        return
    print("Saving conversation...")
    try:
        with open(conversation_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Error writing to file: {e}")
        raise


def load_conversation(system_prompt):
    global messages
    try:
        with open(conversation_path, "r", encoding="utf-8") as f:
            content = f.read()
            if content.strip() == "":
                messages = system_prompt
                return messages

            f.seek(0)
            messages = json.load(f)
            return messages
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading conversation: {e}")
        messages = system_prompt
        return messages