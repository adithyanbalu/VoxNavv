# Interfaces for Context Before Consequence

## Action Object Structure (from demo webapp to extension/backend)

```javascript
{
  action: string, // One of: SEND_DOCUMENT, DELETE_FILE, CANCEL_APPT, TRANSFER
  target: {
    id: string,   // Unique identifier for the action instance (e.g., demo-<timestamp>)
    timestamp: string // ISO timestamp of when the action was triggered
  }
}
```

## Custom Event Details

- Event name: `voxnav-action`
- Dispatched on: `window` object
- Detail: The action object as defined above

## Messaging between Content Script and Background

- From content script to background: `chrome.runtime.sendMessage(action, callback)`
- Background expects to receive the action object and can send a response.

## Future Extensions (Stage 2+)

- The background script will eventually forward the action to a backend via WebSocket.
- The backend will process the action and return an explanation and privacy log.
- The background script will then forward that response to the content script to display the UI.