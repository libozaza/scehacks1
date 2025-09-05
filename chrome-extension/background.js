// Background script for What Did I Just Do? Chrome Extension

const API_BASE = "http://localhost:8000";
let isTracking = false;
let connectionRetries = 0;
const MAX_RETRIES = 5;
const RETRY_DELAY = 5000; // 5 seconds

// Initialize extension
chrome.runtime.onInstalled.addListener(async () => {
  console.log("What Did I Just Do? extension installed");

  // Load tracking state from storage
  const result = await chrome.storage.local.get(["isTracking"]);
  isTracking = result.isTracking !== false; // Default to true if not set

  // Test backend connection
  await testBackendConnection();

  // Set up periodic connection check every 30 seconds
  setInterval(async () => {
    if (isTracking) {
      await testBackendConnection();
    }
  }, 30000);
});

// Track tab creation
chrome.tabs.onCreated.addListener((tab) => {
  if (isTracking && tab.url) {
    const description = tab.url.startsWith("chrome://")
      ? "Opened new Chrome page"
      : tab.url.startsWith("chrome-extension://")
      ? "Opened extension page"
      : `Opened new tab: ${tab.title || "Untitled"}`;

    sendBrowserEvent("browser_tab_created", {
      url: tab.url,
      title: tab.title || "New Tab",
      tabId: tab.id,
      description: description,
    });
  }
});

// Track tab updates (navigation, title changes)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (isTracking && changeInfo.status === "complete" && tab.url) {
    let description = "Navigated to page";

    // Make descriptions more specific based on URL type
    if (tab.url.startsWith("chrome://")) {
      description = "Opened Chrome settings page";
    } else if (tab.url.startsWith("chrome-extension://")) {
      description = "Opened extension page";
    } else if (tab.url.startsWith("file://")) {
      description = "Opened local file";
    } else if (tab.url.includes("localhost") || tab.url.includes("127.0.0.1")) {
      description = `Navigated to local development: ${
        tab.title || "Local Site"
      }`;
    } else {
      // Extract domain name for better description
      try {
        const domain = new URL(tab.url).hostname;
        description = `Navigated to ${domain}`;
        if (tab.title && tab.title !== domain) {
          description += ` - ${tab.title}`;
        }
      } catch (e) {
        description = `Navigated to: ${tab.title || "Unknown page"}`;
      }
    }

    sendBrowserEvent("browser_navigation", {
      url: tab.url,
      title: tab.title || "Untitled",
      tabId: tabId,
      changeInfo: changeInfo,
      description: description,
    });
  }
});

// Track tab removal
chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
  if (isTracking) {
    sendBrowserEvent("browser_tab_closed", {
      tabId: tabId,
      windowId: removeInfo.windowId,
      description: "Closed browser tab",
    });
  }
});

// Window focus/blur events are filtered out to prevent spam
// Commenting out to completely disable these noisy events
/*
let lastWindowFocusTime = 0;
chrome.windows.onFocusChanged.addListener((windowId) => {
  if (isTracking) {
    const now = Date.now();
    // Only send window events if 5 seconds have passed since last one
    if (now - lastWindowFocusTime > 5000) {
      lastWindowFocusTime = now;
      if (windowId === chrome.windows.WINDOW_ID_NONE) {
        sendBrowserEvent("browser_window_blur", {
          windowId: windowId,
        });
      } else {
        sendBrowserEvent("browser_window_focus", {
          windowId: windowId,
        });
      }
    }
  }
});
*/

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "browser_activity") {
    if (isTracking) {
      sendBrowserEvent(request.eventType, {
        url: sender.tab?.url,
        title: sender.tab?.title,
        ...request.data,
      });
    }
  }

  if (request.type === "toggle_tracking") {
    isTracking = request.enabled;
    // Save state to storage
    chrome.storage.local.set({ isTracking: isTracking });
    sendResponse({ success: true, tracking: isTracking });
  }

  if (request.type === "get_tracking_status") {
    sendResponse({ tracking: isTracking });
  }
});

// Test backend connection
async function testBackendConnection() {
  try {
    const response = await fetch(`${API_BASE}/`, {
      method: "GET",
      timeout: 5000,
    });

    if (response.ok) {
      console.log("Backend connection successful");
      connectionRetries = 0;
      return true;
    } else {
      throw new Error(`Backend responded with status: ${response.status}`);
    }
  } catch (error) {
    console.error("Backend connection failed:", error);
    connectionRetries++;

    if (connectionRetries < MAX_RETRIES) {
      console.log(
        `Retrying connection in ${
          RETRY_DELAY / 1000
        } seconds... (${connectionRetries}/${MAX_RETRIES})`
      );
      setTimeout(testBackendConnection, RETRY_DELAY);
    } else {
      console.error("Max retries reached. Backend appears to be down.");
      isTracking = false;
      chrome.storage.local.set({ isTracking: false });
    }
    return false;
  }
}

// Send browser event to backend with retry logic
async function sendBrowserEvent(eventType, data) {
  if (!isTracking) return;

  try {
    const response = await fetch(`${API_BASE}/browser-event`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type: eventType,
        url: data.url,
        title: data.title,
        details: data,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    // Reset retry counter on successful send
    connectionRetries = 0;
  } catch (error) {
    console.error("Error sending browser event:", error);

    // If this is a connection error, try to reconnect
    if (error.name === "TypeError" || error.message.includes("fetch")) {
      connectionRetries++;

      if (connectionRetries < MAX_RETRIES) {
        console.log(
          `Retrying connection in ${
            RETRY_DELAY / 1000
          } seconds... (${connectionRetries}/${MAX_RETRIES})`
        );
        setTimeout(() => testBackendConnection(), RETRY_DELAY);
      } else {
        console.error("Max retries reached. Disabling tracking.");
        isTracking = false;
        chrome.storage.local.set({ isTracking: false });
      }
    }
  }
}
