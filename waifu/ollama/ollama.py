import ollama
from config import model

def chat(messages, text):
    messages.append({"role": "user", "content": text})
    response = ollama.chat(model=model, messages=messages)

    if "message" not in response or "content" not in response["message"]:
        raise ValueError("Unexpected response structure from Ollama")
        
    content = response["message"]["content"]
    messages.append({"role": "assistant", "content": content})
    return content