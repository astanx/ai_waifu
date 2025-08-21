import waifu.tts as tts
from config import weights_path
import waifu.stt as stt
import waifu.ollama as ai
import waifu.memory as memory
import asyncio

placeholder = "\nSay something (press Enter to use voice) or type 'exit': "

async def start_pipeline():    
    process = None
    try:
        process = await tts.run_sovits_api()
        if not process:
            raise Exception("Failed to start SoVITS API")
        
        await tts.change_sovits_model(weights_path)
        
        print("Welcome to the AI Waifu chat!")

        while True:
            text = await asyncio.to_thread(stt.user_input, placeholder)
            
            if text.lower() == "exit":
                break

            try:
                print(f"You: {text}")
                response = await ai.send_message(text) 
                print(f"AI: {response}")
            except Exception as e:
                print(f"Error processing message or TTS: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        memory.save_conversation()
        if process:
            await tts.stop_sovits_api(process)
        print("Goodbye!")
