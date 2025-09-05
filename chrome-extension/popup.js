// Popup script for What Did I Just Do? Chrome Extension

let isTracking = false;

// Initialize popup
document.addEventListener('DOMContentLoaded', () => {
  checkTrackingStatus();
  setupEventListeners();
});

function setupEventListeners() {
  const toggleBtn = document.getElementById('toggle-btn');
  toggleBtn.addEventListener('click', toggleTracking);
}

function checkTrackingStatus() {
  chrome.runtime.sendMessage({ type: 'get_tracking_status' }, (response) => {
    if (response) {
      isTracking = response.tracking;
      updateUI();
    }
  });
}

function toggleTracking() {
  const newState = !isTracking;
  
  chrome.runtime.sendMessage({ 
    type: 'toggle_tracking', 
    enabled: newState 
  }, (response) => {
    if (response && response.success) {
      isTracking = newState;
      updateUI();
    }
  });
}

function updateUI() {
  const statusEl = document.getElementById('status');
  const statusText = document.getElementById('status-text');
  const toggleBtn = document.getElementById('toggle-btn');
  const statusDot = statusEl.querySelector('.status-dot');
  
  if (isTracking) {
    statusEl.className = 'status active';
    statusText.textContent = 'Tracking Active';
    toggleBtn.textContent = 'Stop Tracking';
    toggleBtn.className = 'button secondary';
    statusDot.className = 'status-dot active';
  } else {
    statusEl.className = 'status inactive';
    statusText.textContent = 'Tracking Inactive';
    toggleBtn.textContent = 'Start Tracking';
    toggleBtn.className = 'button primary';
    statusDot.className = 'status-dot inactive';
  }
}
