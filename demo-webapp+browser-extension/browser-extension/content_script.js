// Content script that runs in the demo webapp
// Intercepts voxnav-action events and sends them to background

console.log('[Content Script] LOADED - Event listener test');

// Visual confirmation that content script is running
document.body.style.border = '3px solid red';
document.body.style.padding = '5px';
console.log('[Content Script] Applied red border and padding');

// Listen for the custom event from the demo webapp
window.addEventListener('voxnav-action', (event) => {
  const action = event.detail;
  console.log('[Content Script] Intercepted action:', action);

  // Send action to background
  console.log('[Content Script] Sending action to background:', action);
  browser.runtime.sendMessage(
    {
      type: 'actionRequest',
      action: action
    },
    (response) => {
      console.log('[Content Script] Received response from background:', response);
    }
  );
});

// Test messaging to background to verify basic communication
setTimeout(() => {
  try {
    console.log('[Content Script] Sending test message to background...');
    browser.runtime.sendMessage({test: 'event-listener-test'}, (response) => {
      console.log('[Content Script] Received test response:', response);
    });
  } catch (e) {
    console.error('[Content Script] Failed to send test message:', e);
  }
}, 2000);