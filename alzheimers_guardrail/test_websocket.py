import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/audio"
    try:
        async with websockets.connect(uri) as websocket:
            # Send test message
            test_message = {
                "action": "SEND_DOCUMENT",
                "target": {
                    "recipient": "test@example.com",
                    "document_id": "DOC_123"
                }
            }
            await websocket.send(json.dumps(test_message))
            print(f"Sent: {test_message}")

            # Wait for response
            response = await websocket.recv()
            print(f"Received: {response}")

            # Parse and display the response
            try:
                parsed = json.loads(response)
                print(f"Parsed response: {json.dumps(parsed, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response is not JSON: {response}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())