// Background script for the extension
// Handles actionRequest messages from content script and sends mock responses

const browserApi = typeof browser !== 'undefined' ? browser : chrome;

console.log('[Background] SCRIPT STARTING');

// Handle incoming messages from content scripts
browserApi.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[Background] Received message:', message);
  console.log('[Background] Sender:', sender);

  // Handle actionRequest messages from content script
  if (message.type === 'actionRequest') {
    console.log('[Background] Processing actionRequest:', message.action);

    const actionType = message.action.action;
    const explanations = {
      "SEND_DOCUMENT": "John requested the final report on August 28",
      "DELETE_FILE": "This file was created by John Smith for the project presentation",
      "CANCEL_APPT": "The appointment was arranged by your assistant on September 1",
      "TRANSFER": "You approved a similar transaction of $500 to this recipient yesterday"
    };

    // Mock privacy log (hardcoded for demo)
    const privacyLog = {
      "used": {
        "messages": 1,
        "contacts": 1
      },
      "notUsed": {
        "messages": 46,
        "files": 15,
        "calendar": 10,
        "contacts": 0
      }
    };

    const responseData = {
      status: "success",
      action: actionType,
      timestamp: message.action.target.timestamp,
      explanation: explanations[actionType] || "Context unavailable for this action",
      privacyLog: privacyLog,
      message: "Action processed successfully (mock response)"
    };

    console.log('[Background] Sending response:', responseData);
    sendResponse(responseData);
    return true; // Indicate we'll respond asynchronously
  }

  // For any other message, return false (no response)
  console.log('[Background] Unhandled message type:', message.type);
  return false;
});

console.log('[Background] SCRIPT SETUP COMPLETE');