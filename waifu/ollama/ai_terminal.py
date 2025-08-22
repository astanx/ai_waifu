import subprocess
import asyncio
from .ollama import chat
from .ai_waifu import comment_action
from waifu.stt import *
from prompts.confirm import system_prompt as confirm_system_prompt
from prompts.terminal import system_prompt as terminal_system_prompt

terminal_messages = terminal_system_prompt.copy()

confirm_messages = confirm_system_prompt.copy()

async def send_message(text):
    try:
        content = chat(terminal_messages, text)
        await handle_command(content)
        return content
    except Exception as e:
        print(f"Error with Ollama: {e}")
        raise


async def handle_command(content):
    if (content.startswith("rm") or content.startswith("sudo") 
        or content.startswith("chmod") or content.startswith("chown")
             or content.startswith("rmdir")):
        await comment_action(content)
        
        print("Warning: Command contains potentially dangerous operations.")
        placeholder = f"\n{content}\nSay yes/no (press Enter to use voice) or type it to execute this command: "

        confirm_text = user_input(placeholder)
        confirm_content = chat(confirm_messages, confirm_text).strip()
        if confirm_content not in ["1", "0"]:
            print(f"Unexpected response: {confirm_content}. Expected '1' or '0'.")
            raise ValueError("Response must be '1' or '0'")
            
        if confirm_content == "1":
            output = await asyncio.to_thread(run_command, content)

            if output:
                asyncio.create_task(comment_action(output))
        else:
            print("Command is not safe to execute. Skipping.")
            return None
    elif content.startswith("#undefined"):
        print("Command not recognized or undefined.")
           
    elif content.startswith("curl"):
        # Handle curl commands for external information
        print("Using curl for external information, please ensure you have internet access.")
        try:
            await asyncio.gather(
                comment_action(content),
                asyncio.to_thread(run_command, content)
            )
        except Exception as e:
            print(f"Error executing curl command: {e}")
            print("Check your internet connection or the command syntax.")
    else:
        # Handle other commands
        await asyncio.gather(
                comment_action(content),
                asyncio.to_thread(run_command, content)
        )

def run_command(content):
    print(f"Executing command: {content}")

    proc = subprocess.Popen(
                content,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )   
    stdout, stderr = proc.communicate()

    if proc.returncode != 0:
        print(f"Error executing command: {stderr.strip()}")
        return None
    proc.kill()
    print(f"Command output: {stdout.strip()}")
    return stdout.strip()