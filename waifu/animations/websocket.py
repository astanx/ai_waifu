import websockets
import json
import waifu.ollama as ai
from .broadcast import connect_client, disconnect_client ,send_message_to_all


server = None

async def handler(websocket):
    print("Client connected")
    
    origin = websocket.request.headers.get("Origin") if websocket.request else None
    print(f"Connection from origin: {origin}")
    
    connect_client(websocket)
    try:
        async for message in websocket:
            try:
                # Parse incoming message
                data = json.loads(message)
                message_type = data.get("type")
                print(f"\n Received message: {data}")
                if message_type == "message":
                    request = json.dumps({"from": "user", "content" : data.get("content", "")})
                    content, comment = await ai.send_message(request) 
                    
                    if content:
                        await send_message_to_all(content, comment)
                else:
                    print(f"Unknown message type received: {message_type}")
            except json.JSONDecodeError:
                print(f"Invalid JSON received: {message}")
            except Exception as e:
                print(f"Error processing message: {e}")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        disconnect_client(websocket)


async def start_websocket_server():
    global server
    try:
        server = await websockets.serve(handler, 'localhost', 8765)
        print("WebSocket server running on ws://localhost:8765")
        await server.wait_closed()
    except Exception as e:
        print(f"Failed to start WebSocket server: {e}")


async def stop_websocket_server():
    global server
    if server is not None:
        print("Stopping WebSocket server...")
        server.close()
        await server.wait_closed()
        server = None
