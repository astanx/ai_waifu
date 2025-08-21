from . import ai_terminal
from . import ai_waifu
from prompts.prompt_type import system_prompt
from .ollama import chat



async def send_message(text):
    try:
        messages = system_prompt.copy()
        content = chat(messages, text).strip()
        if content not in ["1", "0"]:
            print(f"Unexpected response: {content}. Expected '1' or '0'.")
            raise ValueError("Response must be '1' or '0'")
        if content == "1":
            return ai_terminal.send_message(text)
        else:
            return await ai_waifu.send_message(text)
        
    except Exception as e:
        print(f"Error with Ollama: {e}")
        raise