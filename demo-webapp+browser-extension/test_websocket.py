import asyncio
import websockets

async def test():
    try:
        async with websockets.connect('ws://localhost:8000/ws/action') as websocket:
            await websocket.send('{"action": "TEST"}')
            response = await websocket.recv()
            print("Received:", response)
    except Exception as e:
        print("Error:", e)

asyncio.run(test())