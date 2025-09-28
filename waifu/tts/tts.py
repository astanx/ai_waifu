import aiohttp
import asyncio
import os
import subprocess
import re
from config import api_url, base_path
from waifu.animations.broadcast import send_talk_to_all

ref_audio_path = f"{base_path}/waifu/tts/reference.wav"
sovits_path = f"{base_path}/GPT-SoVITS"
reference_text = "Tea parties are a must for the well-mannered. If you'd like to learn the proper etiquette, I'd be happy to teach you."


if not os.path.exists(ref_audio_path):
    raise FileNotFoundError(f"Reference audio file not found: {ref_audio_path}")

if not os.path.exists(sovits_path):
    raise FileNotFoundError(f"SoVITS path not found: {sovits_path}")

async def run_sovits_api() -> None:
    print("Starting SoVITS API...")
    
    original_path = os.getcwd()
    try:
        os.chdir(sovits_path)
        proc = subprocess.Popen(
            ["python", "api_v2.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Waiting for SoVITS API to start...")
        try:
            async with aiohttp.ClientSession() as session:
                async with asyncio.timeout(30):
                    while True:
                        try:
                            async with session.get(f"{api_url}/ping") as response:
                                if response.status == 200:
                                    print("SoVITS API is running")
                                    break
                        except aiohttp.ClientConnectionError:
                            await asyncio.sleep(1)
        except asyncio.TimeoutError:
            print("SoVITS API didn't respond within 30 seconds")

        return proc
    finally:
        os.chdir(original_path)

async def stop_sovits_api(process):
    print("Stopping SoVITS API...")
    if process:
        process.terminate()
        process.wait()
        print("SoVITS API stopped")
    else:
        raise Exception("No SoVITS API process to stop")

async def change_sovits_model(weights_path):
    print(f"Changing SoVITS weights to {weights_path}...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_url}/set_sovits_weights?weights_path={weights_path}") as response:
            if response.status == 200:
                print("SoVITS weights changed successfully")
            else:
                raise Exception(f"Failed to change SoVITS weights: {await response.json()}")

async def tts(text: str, text_lang: str, prompt_lang: str) -> None:
    text = text.strip()
    
    # Validate inputs
    if not text or re.fullmatch(r"[^\w]+", text):
        print("Text input cannot be empty")
        return
    
    params = {
        "text": text,
        "text_lang": text_lang,
        "ref_audio_path": ref_audio_path,
        "prompt_lang": prompt_lang,
        "prompt_text": reference_text,
        "streaming_mode": True
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/tts", json=params) as response:
            try:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"TTS failed: {error_data}")

                print("Live streaming...")
                ffplay = subprocess.Popen(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-f", "wav", "-"],
                    stdin=subprocess.PIPE
                )

                asyncio.create_task(send_talk_to_all("start"))
                async for chunk in response.content.iter_chunked(4096):
                    if chunk:
                        ffplay.stdin.write(chunk)
                        ffplay.stdin.flush()
                await send_talk_to_all("stop")
                ffplay.stdin.close()
                
            except aiohttp.ClientError as e:
                raise Exception(f"Network error during TTS request: {e}")
        
