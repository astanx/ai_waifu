import aiohttp
import asyncio
import os
import subprocess
import time
import re
from config import api_url, base_path

ref_audio_path = f"{base_path}/waifu/tts/reference.wav"

async def run_sovits_api():
    print("Starting SoVITS API...")
    sovits_path = f"{base_path}/GPT-SoVITS"
    if not os.path.exists(sovits_path):
        raise FileNotFoundError(f"SoVITS directory not found: {sovits_path}")
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

async def tts(text, text_lang, prompt_lang, propmt_text):
    text = text.strip()
    
    # Validate inputs
    if not os.path.exists(ref_audio_path):
        raise FileNotFoundError(f"Reference audio file not found: {ref_audio_path}")
    if not text or re.fullmatch(r"[^\w]+", text):
        print("Text input cannot be empty")
        return
    
    params = {
        "text": text,
        "text_lang": text_lang,
        "ref_audio_path": ref_audio_path,
        "prompt_lang": prompt_lang,
        "prompt_text": propmt_text,
        "streaming_mode": True
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/tts", json=params) as response:
            try:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"TTS failed: {error_data}")

                print("🔊 Live streaming...")

                ffplay = subprocess.Popen(
                    ["ffplay", "-nodisp", "-autoexit", "-"],
                    stdin=subprocess.PIPE
                )

                async for chunk in response.content.iter_chunked(4096):
                    if chunk:
                        ffplay.stdin.write(chunk)
                        ffplay.stdin.flush()

                ffplay.stdin.close()
                await asyncio.sleep(0.1)
            except aiohttp.ClientError as e:
                raise Exception(f"Network error during TTS request: {e}")
        
