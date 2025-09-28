import os
import subprocess
import asyncio
import webbrowser
        
async def start_frontend():
    print("Choose frontend type:")
    print("1 - in browser")
    print("2 - desktop app (Electron)")
    
    choice = input("Enter 1 or 2 (base 1): ").strip()
    
    if choice not in ("1", "2"):
        print("Invalid choice. Defaulting to browser frontend.")
        choice = "1"
        
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
    
    if choice == "1":
        # Start the frontend server
        try:
            process = subprocess.Popen(
                ["npm", "run","dev"],
                cwd=frontend_dir,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            url = "http://localhost:5173"
            print(f"Frontend server started on {url} (PID: {process.pid})")
            
            await asyncio.sleep(2)  # Wait a moment for the server to start
            # Open in default browser
            webbrowser.open(url)
            
            return process
        except Exception as e:
            print(f"Failed to start frontend server: {e}")
    if choice == "2":
        # Start electron app
        try:
            process = subprocess.Popen(
                ["npm", "start"],
                cwd=frontend_dir,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("Electron app started.")
            return process
        except Exception as e:
            print(f"Failed to start electron app: {e}")
    return None
    

async def stop_frontend(process):
    if process:
        try:
            process.terminate() 
            await asyncio.sleep(1) 
            if process.poll() is None: 
                process.kill()
            print("Frontend server stopped.")
        except Exception as e:
            print(f"Error stopping frontend server: {e}")
