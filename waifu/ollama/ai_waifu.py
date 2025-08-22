from .ollama import chat, chat_stream
import waifu.tts as voice
from waifu.memory import load_conversation
from prompts.waifu import system_prompt
from prompts.comment import system_prompt as comment_system_prompt


# Flag to indicate if the AI Waifu is initialized
not_initialized = True

# Global variable to hold the conversation messages
messages = None
comment_messages = comment_system_prompt.copy()

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

async def comment_action(text):
    global comment_messages
    try:
        content = ""
        print(f"AI Comment: ", end="", flush=True)
        async for chunk in chat_stream(comment_messages, text):
            print(f"{chunk}", end="", flush=True)
            content += chunk
        print('\n')
        
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