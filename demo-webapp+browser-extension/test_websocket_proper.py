import asyncio
import websockets
import json

async def test():
    try:
        async with websockets.connect('ws://localhost:8000/ws/action') as websocket:
            action = {
                "action": "SEND_DOCUMENT",
                "target": {
                    "id": "demo-test",
                    "timestamp": "2026-09-05T02:40:00Z"
                }
            }
            await websocket.send(json.dumps(action))
            response = await websocket.recv()
            print("Received:", response)
    except Exception as e:
        print("Error:", e)

asyncio.run(test())