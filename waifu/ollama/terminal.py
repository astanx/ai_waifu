import subprocess
import platform
import tempfile
import os
import time

def open_terminal_and_ask(command, timeout=30):
    # Create temporary script and exit code file
    temp_script = tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False)
    exit_code_file = tempfile.NamedTemporaryFile(mode='w', suffix='.exit', delete=False)
    
    if platform.system() == "Windows":
        temp_script.write(f"""
@echo off
echo {command}
set /p RESPONSE=Type yes/no to execute this command: 
if /i "%RESPONSE%"=="yes" (
    echo 1 > {exit_code_file.name}
    exit /b 1
) else (
    echo 0 > {exit_code_file.name}
    exit /b 0
)
""")
        temp_script.close()
        try:
            # Start a new cmd window and wait for it to finish
            process = subprocess.Popen(["start", "cmd", "/c", temp_script.name], shell=True)
            # Poll for the exit code file
            start_time = time.time()
            while time.time() - start_time < timeout:
                if os.path.exists(exit_code_file.name):
                    try:
                        with open(exit_code_file.name, 'r') as f:
                            exit_code = int(f.read().strip())
                        return exit_code
                    except:
                        pass
                time.sleep(0.1)  # Short sleep to avoid CPU overload
            return 0  # Return 0 if timeout occurs
        except Exception:
            return 0
        finally:
            try:
                os.unlink(temp_script.name)
                os.unlink(exit_code_file.name)
            except:
                pass
    else:
        # For macOS and Linux
        temp_script.write(f"""
#!/bin/bash
echo "{command}"
read -p "Type yes/no to execute this command: " response
if [ "$response" = "yes" ]; then
    echo 1 > {exit_code_file.name}
    exit 1
else
    echo 0 > {exit_code_file.name}
    exit 0
fi
""")
        temp_script.close()
        os.chmod(temp_script.name, 0o755)
        try:
            if platform.system() == "Darwin":
                # Use osascript to open a new Terminal window and run the script
                osa_command = f"""
                tell application "Terminal"
                    do script "bash {temp_script.name}; exit"
                    activate
                end tell
                """
                process = subprocess.Popen(["osascript", "-e", osa_command])
            else:
                # For Linux, use x-terminal-emulator or fallback to common terminals
                process = subprocess.Popen(["x-terminal-emulator", "-e", f"bash {temp_script.name}"] or
                                          ["gnome-terminal", "--", "bash", temp_script.name] or
                                          ["xterm", "-e", f"bash {temp_script.name}"])
            # Poll for the exit code file
            start_time = time.time()
            while time.time() - start_time < timeout:
                if os.path.exists(exit_code_file.name):
                    try:
                        with open(exit_code_file.name, 'r') as f:
                            exit_code = int(f.read().strip())
                        return exit_code
                    except:
                        pass
                time.sleep(0.1)  # Short sleep to avoid CPU overload
            return 0  # Return 0 if timeout occurs
        except Exception:
            return 0
        finally:
            try:
                os.unlink(temp_script.name)
                os.unlink(exit_code_file.name)
            except:
                pass

# Test the function
if __name__ == "__main__":
    print(open_terminal_and_ask("echo Hello, World!"))