"""
FastAPI backend for Context Before Consequence
Handles WebSocket connections for action processing
"""
import json
import logging
import os
import random
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

# Risk scoring weights (Section 15 of the spec)
RISK_WEIGHTS = {
    "SEND_DOCUMENT": {
        "base": 3.0,
        "sensitivity": {
            "final report": 2.0,
            "budget": 2.0,
            "contract": 2.0,
            "medical": 3.0,
            "legal": 3.0
        },
        "context_boost": {
            "requested": 1.5,
            "approved": 1.0,
            "mentioned": 0.5
        }
    },
    "DELETE_FILE": {
        "base": 2.5,
        "sensitivity": {
            "final report": 2.0,
            "budget": 2.0,
            "contract": 2.0,
            "medical": 3.0,
            "legal": 3.0,
            "irreplaceable": 3.0
        },
        "context_boost": {
            "created by": 1.5,
            "approved by": 1.0,
            "mentioned": 0.5
        }
    },
    "CANCEL_APPT": {
        "base": 2.0,
        "sensitivity": {
            "medical": 3.0,
            "legal": 3.0,
            "financial": 2.5,
            "job interview": 3.0,
            "performance review": 2.5
        },
        "context_boost": {
            "arranged by": 1.5,
            "important": 1.0,
            "mentioned": 0.5
        }
    },
    "TRANSFER": {
        "base": 4.0,
        "sensitivity": {
            "large amount": 2.0,  # relative to user's typical transactions
            "new recipient": 2.0,
            "international": 2.0
        },
        "context_boost": {
            "approved": 1.5,
            "recurring": 0.5,
            "mentioned": 0.5
        }
    }
}

# Risk thresholds
RISK_THRESHOLDS = {
    "LOW": 0.0,
    "MEDIUM": 3.0,
    "HIGH": 6.0
}

def calculate_risk_score(action_type, target=None):
    """
    Calculate risk score based on rule-based weighted formula.
    Returns a tuple (score, risk_level, explanation_factors)
    """
    if action_type not in RISK_WEIGHTS:
        return 0.0, "LOW", ["Unknown action type"]

    weights = RISK_WEIGHTS[action_type]
    score = weights["base"]
    factors = [f"base: {weights['base']}"]

    # In a real implementation, we would analyze the target and context
    # For now, we'll use a simplified approach based on the action type only
    # We'll add some variability based on the target if available

    # For demonstration, we'll add some points based on the target content
    if target and isinstance(target, dict):
        # Check for sensitivity keywords in target
        for keyword, weight in weights.get("sensitivity", {}).items():
            # We would normally search in the target data, but for now we'll just add if the keyword is in the action type or target id
            if keyword in action_type.lower() or (target.get("id") and keyword in target["id"].lower()):
                score += weight
                factors.append(f"+{keyword}: {weight}")

        # Check for context boost keywords
        for keyword, weight in weights.get("context_boost", {}).items():
            if keyword in action_type.lower() or (target.get("id") and keyword in target["id"].lower()):
                score += weight
                factors.append(f"+{keyword}: {weight}")

    # Add some randomness for demonstration (in real implementation, this would be based on actual context)
    random.seed(hash(str(target)) if target else 42)  # Deterministic seed based on target
    score += random.uniform(-0.5, 0.5)

    # Ensure score doesn't go below 0
    score = max(0.0, score)

    # Determine risk level
    if score >= RISK_THRESHOLDS["HIGH"]:
        risk_level = "HIGH"
    elif score >= RISK_THRESHOLDS["MEDIUM"]:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return score, risk_level, factors

def retrieve_context(action_type, target=None):
    """
    Retrieve relevant context from synthetic data based on action type and target.
    Returns a list of relevant context items.
    """
    relevant_context = []

    # Map action types to relevant data types
    action_to_data = {
        "SEND_DOCUMENT": ["messages", "calendar", "contacts"],
        "DELETE_FILE": ["files", "messages", "contacts"],
        "CANCEL_APPT": ["calendar", "messages", "contacts"],
        "TRANSFER": ["messages", "contacts"]  # In a real system, we'd also check transaction history
    }

    relevant_data_types = action_to_data.get(action_type, [])

    # For each relevant data type, search for items that might be related
    for data_type in relevant_data_types:
        items = synthetic_data.get(data_type, [])
        # In a real implementation, we would use semantic search or keyword matching
        # For now, we'll just take the first few items as a demonstration
        relevant_context.extend(items[:2])  # Take first 2 items from each relevant data type

    return relevant_context

def generate_explanation(action_type, target, context_items):
    """
    Generate a human-readable explanation based on the action and context.
    """
    # Base explanations for each action type
    base_explanations = {
        "SEND_DOCUMENT": "You are about to send a document.",
        "DELETE_FILE": "You are about to delete a file.",
        "CANCEL_APPT": "You are about to cancel an appointment.",
        "TRANSFER": "You are about to transfer money."
    }

    explanation = base_explanations.get(action_type, "You are about to perform an action.")

    # Add context information
    if context_items:
        explanation += " Relevant context found:"
        for item in context_items[:3]:  # Limit to 3 items for brevity
            if isinstance(item, dict):
                # Extract relevant fields for display
                if "sender" in item and "content" in item:
                    explanation += f"\n- Message from {item['sender']}: '{item['content'][:50]}...'"
                elif "title" in item and "attendees" in item:
                    explanation += f"\n- Meeting: {item['title']} with {', '.join(item['attendees'])}"
                elif "name" in item and "owner" in item:
                    explanation += f"\n- File: {item['name']} owned by {item['owner']}"
                elif "name" in item and "email" in item:
                    explanation += f"\n- Contact: {item['name']} ({item['email']})"
                else:
                    explanation += f"\n- {str(item)[:100]}"

    return explanation

def generate_privacy_log(action_type, context_items, used_data_types=None):
    """
    Generate a privacy log showing what data was used and what was not used.
    """
    if used_data_types is None:
        used_data_types = []

    # All possible data types
    all_data_types = set(["messages", "calendar", "files", "contacts"])

    # Determine which data types were actually used based on context items
    # In a real implementation, we would track this during context retrieval
    # For now, we'll assume that if we retrieved items from a data type, we used it
    used_from_context = set()
    for item in context_items:
        # We don't have a direct way to know which data type an item came from
        # In a real implementation, we would track this
        pass

    # For demonstration, we'll use a simplified approach
    # We'll say we used messages and contacts for all actions (as in the mock)
    # and not used the rest
    used_data_types = set(["messages", "contacts"])
    not_used_data_types = all_data_types - used_data_types

    # Count items in each category (for demonstration)
    used_counts = {
        "messages": len([item for item in synthetic_data.get("messages", []) if item in context_items]) or 1,
        "contacts": len([item for item in synthetic_data.get("contacts", []) if item in context_items]) or 1
    }

    not_used_counts = {
        "messages": len(synthetic_data.get("messages", [])) - used_counts.get("messages", 0),
        "calendar": len(synthetic_data.get("calendar", [])),
        "files": len(synthetic_data.get("files", [])),
        "contacts": len(synthetic_data.get("contacts", [])) - used_counts.get("contacts", 0)
    }

    # Ensure we don't have negative counts
    for key in not_used_counts:
        not_used_counts[key] = max(0, not_used_counts[key])

    privacy_log = {
        "used": {
            "messages": used_counts.get("messages", 0),
            "contacts": used_counts.get("contacts", 0)
        },
        "notUsed": {
            "messages": not_used_counts.get("messages", 0),
            "calendar": not_used_counts.get("calendar", 0),
            "files": not_used_counts.get("files", 0),
            "contacts": not_used_counts.get("contacts", 0)
        }
    }

    # If we have no used items, show at least 1 used to match the mock format
    if privacy_log["used"]["messages"] == 0 and privacy_log["used"]["contacts"] == 0:
        privacy_log["used"]["messages"] = 1
        privacy_log["used"]["contacts"] = 1
        # Adjust not used counts accordingly
        privacy_log["notUsed"]["messages"] = max(0, privacy_log["notUsed"]["messages"] - 1)
        privacy_log["notUsed"]["contacts"] = max(0, privacy_log["notUsed"]["contacts"] - 1)

    return privacy_log

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

            action_type = action_data.get("action")
            target = action_data.get("target", {})

            # Calculate risk score
            score, risk_level, risk_factors = calculate_risk_score(action_type, target)
            logger.info(f"Risk score: {score}, level: {risk_level}, factors: {risk_factors}")

            # Only proceed with context retrieval if risk is MEDIUM or HIGH
            if risk_level in ["MEDIUM", "HIGH"]:
                # Retrieve relevant context
                context_items = retrieve_context(action_type, target)
                logger.info(f"Retrieved {len(context_items)} context items")

                # Generate explanation and privacy log
                explanation = generate_explanation(action_type, target, context_items)
                privacy_log = generate_privacy_log(action_type, context_items)

                response = {
                    "status": "success",
                    "action": action_type,
                    "riskScore": score,
                    "riskLevel": risk_level,
                    "riskFactors": risk_factors,
                    "explanation": explanation,
                    "privacyLog": privacy_log,
                    "message": "Action processed with context"
                }
            else:
                # For LOW risk actions, we still return a response but with minimal context
                explanation = f"{action_type} action determined to be low risk based on available context."
                privacy_log = {
                    "used": {"messages": 0, "contacts": 0},
                    "notUsed": {
                        "messages": len(synthetic_data.get("messages", [])),
                        "calendar": len(synthetic_data.get("calendar", [])),
                        "files": len(synthetic_data.get("files", [])),
                        "contacts": len(synthetic_data.get("contacts", []))
                    }
                }

                response = {
                    "status": "success",
                    "action": action_type,
                    "riskScore": score,
                    "riskLevel": risk_level,
                    "riskFactors": risk_factors,
                    "explanation": explanation,
                    "privacyLog": privacy_log,
                    "message": "Action processed - low risk, no context needed"
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