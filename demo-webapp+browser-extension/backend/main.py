"""
FastAPI backend for Context Before Consequence
Handles WebSocket connections for action processing
"""
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Context Before Consequence API")

# In-memory storage for synthetic data (will be loaded from JSON files)
synthetic_data = {
    "messages": [],
    "calendar": [],
    "files": [],
    "contacts": []
}

# Load synthetic data on startup
def load_synthetic_data():
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    try:
        for data_type in synthetic_data.keys():
            file_path = os.path.join(data_dir, f"{data_type}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    synthetic_data[data_type] = json.load(f)
                logger.info(f"Loaded {len(synthetic_data[data_type])} {data_type}")
            else:
                logger.warning(f"Synthetic data file not found: {file_path}")
    except Exception as e:
        logger.error(f"Error loading synthetic data: {e}")

@app.on_event("startup")
async def startup_event():
    load_synthetic_data()
    logger.info("Backend started successfully")

@app.get("/")
async def root():
    return {"message": "Context Before Consequence API is running"}

@app.websocket("/ws/action")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    try:
        while True:
            # Receive action from client
            data = await websocket.receive_text()
            action_data = json.loads(data)
            logger.info(f"Received action: {action_data}")

            # Validate action structure (basic validation)
            if not isinstance(action_data, dict) or "action" not in action_data or "target" not in action_data:
                await websocket.send_text(json.dumps({
                    "error": "Invalid action structure"
                }))
                continue

            # For now, we return a mock response based on the action type
            # In a real implementation, this would go through the risk engine, context retrieval, etc.
            action_type = action_data.get("action")
            timestamp = action_data.get("target", {}).get("timestamp")

            # Mock explanation and privacy log
            explanations = {
                "SEND_DOCUMENT": "John requested the final report on August 28",
                "DELETE_FILE": "This file was created by John Smith for the project presentation",
                "CANCEL_APPT": "The appointment was arranged by your assistant on September 1",
                "TRANSFER": "You approved a similar transaction of $500 to this recipient yesterday"
            }

            # Mock privacy log (hardcoded for demo)
            privacy_log = {
                "used": {
                    "messages": 1,
                    "contacts": 1
                },
                "notUsed": {
                    "messages": 46,
                    "files": 15,
                    "calendar": 10,
                    "contacts": 0  # Assuming we used 1 contact in the used section
                }
            }

            # Adjust notUsed counts based on what we "used" (for demo consistency)
            if action_type in explanations:
                # We'll just use the same mock for all actions for simplicity
                pass

            response = {
                "status": "success",
                "action": action_type,
                "timestamp": timestamp,
                "explanation": explanations.get(action_type, "Context unavailable for this action"),
                "privacyLog": privacy_log,
                "message": "Action processed successfully"
            }

            await websocket.send_text(json.dumps(response))
            logger.info(f"Sent response: {response}")

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)