import ollama
import waifu.memory as memory
from prompts.prompt import system_prompt
from config import model
import json
import re
from models.ai_response import AssistantResponse
from types import SimpleNamespace

client = ollama.Client()

messages = memory.load_conversation(system_prompt)

def chat(text: str) -> AssistantResponse:
    messages.append({"role": "user", "content": text})
    response = client.chat(model=model, messages=messages)

    if not hasattr(response, "message") or not hasattr(response.message, "content"):
        raise ValueError("Unexpected response structure from Ollama")
        
    content = response.message.content 
    messages.append({"role": "assistant", "content": content})
    cleaned_content = re.sub(r'^```json\n|\n```$', '', content.strip())
    cleaned_content = re.sub(r',(\s*[}\]])', r'\1', cleaned_content)  # Remove trailing commas
    print(f"Debug: Cleaned content: {cleaned_content}")
    return json.loads(cleaned_content, object_hook=lambda d: SimpleNamespace(**d))

def waifu_save_conversation():
    memory.save_conversation(messages)

'''
TODO rework
async def chat_stream(text: str):
    messages.append({"role": "user", "content": text})

    stream = client.chat(model=model, messages=messages, stream=True)

    full_response = ""
    for chunk in stream:
        if "message" in chunk and "content" in chunk["message"]:
            chunk_content = chunk["message"]["content"]
            yield chunk_content
            full_response += chunk_content
    messages.append({"role": "assistant", "content": full_response})
    '''