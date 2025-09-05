// Background script for What Did I Just Do? Chrome Extension

const API_BASE = 'http://localhost:8000';
let isTracking = false;

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('What Did I Just Do? extension installed');
  isTracking = true;
});

// Track tab creation
chrome.tabs.onCreated.addListener((tab) => {
  if (isTracking && tab.url) {
    sendBrowserEvent('browser_tab_created', {
      url: tab.url,
      title: tab.title || 'New Tab',
      tabId: tab.id
    });
  }
});

// Track tab updates (navigation, title changes)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (isTracking && changeInfo.status === 'complete' && tab.url) {
    sendBrowserEvent('browser_navigation', {
      url: tab.url,
      title: tab.title || 'Untitled',
      tabId: tabId,
      changeInfo: changeInfo
    });
  }
});

// Track tab removal
chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
  if (isTracking) {
    sendBrowserEvent('browser_tab_closed', {
      tabId: tabId,
      windowId: removeInfo.windowId
    });
  }
});

// Track window focus/blur
chrome.windows.onFocusChanged.addListener((windowId) => {
  if (isTracking) {
    if (windowId === chrome.windows.WINDOW_ID_NONE) {
      sendBrowserEvent('browser_window_blur', {
        windowId: windowId
      });
    } else {
      sendBrowserEvent('browser_window_focus', {
        windowId: windowId
      });
    }
  }
});

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'browser_activity') {
    if (isTracking) {
      sendBrowserEvent(request.eventType, {
        url: sender.tab?.url,
        title: sender.tab?.title,
        ...request.data
      });
    }
  }
  
  if (request.type === 'toggle_tracking') {
    isTracking = request.enabled;
    sendResponse({ success: true, tracking: isTracking });
  }
  
  if (request.type === 'get_tracking_status') {
    sendResponse({ tracking: isTracking });
  }
});

// Send browser event to backend
async function sendBrowserEvent(eventType, data) {
  try {
    const response = await fetch(`${API_BASE}/browser-event`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        type: eventType,
        url: data.url,
        title: data.title,
        details: data
      })
    });
    
    if (!response.ok) {
      console.error('Failed to send browser event:', response.statusText);
    }
  } catch (error) {
    console.error('Error sending browser event:', error);
  }
}
