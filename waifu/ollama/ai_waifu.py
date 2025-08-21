from .ollama import chat
import waifu.tts as voice
from waifu.memory import load_conversation
from prompts.waifu import system_prompt
from config import base_path

# Flag to indicate if the AI Waifu is initialized
not_initialized = True

# Global variable to hold the conversation messages
messages = None

reference_text = "Tea parties are a must for the well-mannered. If you'd like to learn the proper etiquette, I'd be happy to teach you."

async def send_message(text):
    global messages
    initialize()
    try:
        content = chat(messages, text)
        print(f"AI Waifu: {content}")

        await voice.tts(content, "en", "en", reference_text)
        return content
    except Exception as e:
        print(f"Error with Ollama: {e}")
        raise

def initialize():
    global not_initialized, messages
    if not_initialized:
        print("Initializing AI Waifu...")
        messages = load_conversation(system_prompt)
        if not messages:
            messages = system_prompt
        not_initialized = False
    return 