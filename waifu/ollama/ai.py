from .ollama import chat
import waifu.tts as voice
import asyncio
from waifu.stt import *
from waifu.animations.broadcast import send_emotions_to_all
from .browser import fetch_duckduckgo_search_results
from .terminal import open_terminal_and_ask
import json


command_attempt = 0

async def send_message(text: str) -> str :
    global command_attempt
    try:
        content = chat(text)
        
        
        if getattr(content, "animation", None):
            emotion = getattr(content.animation, "emotion", "neutral")
            value = float(getattr(content.animation,"value", 1.0))
            asyncio.create_task(send_emotions_to_all(emotion, value))
            
        if getattr(content, "comment", None):
            await voice.tts(content.comment, "en", "en")
            await send_emotions_to_all("neutral", 1.0)
        
        
        if content.type == "command":
            if content.dangerous == "1" or content.dangerous == 1:
                print("Warning: Command contains potentially dangerous operations.")

                confirm = open_terminal_and_ask(content.content)
                
                if confirm == 1:
                    await run_command(content.content)
                    return [content.content, getattr(content, "comment", None)]
                else:
                    print("Command is not safe to execute. Skipping.")
                    return None, None
                
            elif content.dangerous == "0" or content.dangerous == 0:
                await run_command(content.content)
                return [content.content, getattr(content, "comment", None)]
            else:
                print("Warning: Command marked as dangerous without confirmation. Skipping execution.")
                return None, None
        elif content.type == "waifu":
            await voice.tts(content.content, "en", "en")
            await send_emotions_to_all("neutral", 1.0)
        elif content.type == "browser":
            print(f"Browser action requested for query: {content.content}")
            query_results = fetch_duckduckgo_search_results(content.content)
            request = json.dumps({"from": "system", "content" : f"Thats results for '{content.content}': {query_results}"})
            content, comment = await send_message(request)
            return [content, comment]
        else:
            print(f"Unknown response type: {content.type}")
            raise ValueError(f"Unknown response type: {content.type}")
        return [content.content, getattr(content, "comment", None)]
        
        
    except Exception as e:
        print(f"Error with Ollama: {e}")
        raise e
    
async def run_command(content):
    global command_attempt
    print(f"Executing command: {content}")

    proc = await asyncio.create_subprocess_shell(
        content,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )   
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        error_msg = stderr.decode('utf-8', errors='ignore').strip()
        print(f"Error executing command: {error_msg}")
        
        # Prompt AI for a retry command
        retry_prompt = f"Command failed with output: {error_msg}. Please suggest a fixed command to retry. Also inform user about the error."
        
        command_attempt += 1
        if command_attempt > 3:
            print("Maximum command retry attempts reached. Aborting.")
            request = json.dumps({"from": "system", "content":"Command failed multiple times. Aborting."})
            await send_message(request)
            return None
        await send_message(retry_prompt)
    
    if stdout:
        output = stdout.decode('utf-8', errors='ignore').strip()
        if output:
            print(f"Command output: {output}")
            request = json.dumps({"from": "system", "content": f"Command succeeded with output: {output}."})
            await send_message(request)
    return stdout.strip()