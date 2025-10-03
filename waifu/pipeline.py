import waifu.tts as tts
from config import weights_path
import waifu.stt as stt
import waifu.ollama as ai
import waifu.animations as animations
import asyncio
import json

placeholder = "\nSay something (or type 'exit'): "

async def start_pipeline():    
    frontend_process = None
    sovits_process = None
    try:
        frontend_process = await animations.start_frontend()
        if not frontend_process:
            raise Exception("Failed to start frontend server")
        
        asyncio.create_task(animations.start_websocket_server())
        sovits_process = await tts.run_sovits_api()
        if not sovits_process:
            raise Exception("Failed to start SoVITS API")
        
        await tts.change_sovits_model(weights_path)
        mode = input("Select STT mode ('cpu' or 'gpu'): ").strip().lower()
        
        print("Welcome to the AI Waifu chat!")

        while True:
            text = await get_user_input(placeholder, mode)
            
            if text.lower() == "exit":
                break

            try:
                print(f"You: {text}")
                request = json.dumps({"from": "user", "content" : text})    
                await ai.send_message(request) 
            except Exception as e:
                print(f"Error processing message or TTS: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        ai.waifu_save_conversation()
        await animations.stop_websocket_server()
        if sovits_process:
            await tts.stop_sovits_api(sovits_process)
        await animations.stop_frontend(frontend_process)
        
        print("Goodbye!")
        
        
async def get_user_input(prompt, mode="gpu"):
    return await asyncio.to_thread(stt.user_input, prompt, mode)