import asyncio
import websockets
import json

# Keep track of connected clients
connected_clients = set()

async def send_emotions_to_all(emotion: str, value: float = 1.0):
    if not connected_clients:
        print("No clients connected")
        return
    
    emotion_cmd = {
            "type": "emotion",
            "emotion": emotion,
            "value": value
        }
    data = json.dumps(emotion_cmd)
    await asyncio.gather(*(ws.send(data) for ws in connected_clients))
    print(f"Emotion sent: {emotion_cmd}")
    
async def send_message_to_all(message: str, comment: str = None):
    if not connected_clients:
        print("No clients connected")
        return

    message_cmd = {
            "type": "message",
            "content": message,
            "comment": comment
        }
    data = json.dumps(message_cmd)
    await asyncio.gather(*(ws.send(data) for ws in connected_clients))
    print(f"Message sent: {message_cmd}")
    
async def send_talk_to_all(action: str):
    if not connected_clients:
        print("No clients connected")
        return
    
    talk_cmd = {
            "type": "talk",
            "action": action,
        }
    data = json.dumps(talk_cmd)
    await asyncio.gather(*(ws.send(data) for ws in connected_clients))
    print(f"Talk sent: {talk_cmd}")
    
async def send_bone_movement_to_all(bone_name: str, rotation: dict):
    if not connected_clients:
        print("No clients connected")
        return
    
    bone_cmd = {
        "type": "bone",
        "boneName": bone_name,
        "rotation": rotation
    }
    data = json.dumps(bone_cmd)
    await asyncio.gather(*(ws.send(data) for ws in connected_clients))
    print(f"Bone movement sent: {bone_cmd}")
    
async def send_animation_to_all(action: str, url: str = ""):
    if not connected_clients:
        print("No clients connected")
        return
    
    animation_cmd = {
        "type": "animation",
        "action": action,
        "url": url
    }
    data = json.dumps(animation_cmd)
    await asyncio.gather(*(ws.send(data) for ws in connected_clients))
    print(f"Animation command sent: {animation_cmd}")
    
def connect_client(websocket):
    connected_clients.add(websocket)
    print(f"Client connected. Total clients: {len(connected_clients)}")
    
def disconnect_client(websocket):
    connected_clients.remove(websocket)
    print(f"Client disconnected. Total clients: {len(connected_clients)}")
        
