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

async def chat_stream(messages, text):
    messages.append({"role": "user", "content": text})

    stream = ollama.chat(model=model, messages=messages, stream=True)

    full_response = ""
    for chunk in stream:
        if "message" in chunk and "content" in chunk["message"]:
            chunk_content = chunk["message"]["content"]
            yield chunk_content
            full_response += chunk_content

    messages.append({"role": "assistant", "content": full_response})