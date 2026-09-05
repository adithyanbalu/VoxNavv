// Map button IDs to action types
const actionMap = {
  'send-doc': 'SEND_DOCUMENT',
  'delete-file': 'DELETE_FILE',
  'cancel-appt': 'CANCEL_APPT',
  'transfer-money': 'TRANSFER'
};

// Function to create and dispatch a custom event with action data
function handleButtonClick(event) {
  const buttonId = event.target.id;
  const actionType = actionMap[buttonId];

  if (!actionType) {
    console.error('Unknown button ID:', buttonId);
    return;
  }

  // Build the structured action object
  const action = {
    action: actionType,
    target: {
      id: 'demo-' + Date.now(),
      timestamp: new Date().toISOString()
    }
  };

  // Log for debugging (can be removed or kept)
  console.log('[Demo Webapp] Action:', action);

  // Dispatch custom event for the extension to intercept
  window.dispatchEvent(new CustomEvent('voxnav-action', { detail: action }));
}

// Attach click listeners to all buttons
document.addEventListener('DOMContentLoaded', () => {
  Object.keys(actionMap).forEach(id => {
    const btn = document.getElementById(id);
    if (btn) {
      btn.addEventListener('click', handleButtonClick);
    } else {
      console.warn('Button not found:', id);
    }
  });
});