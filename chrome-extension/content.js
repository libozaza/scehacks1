// Content script for What Did I Just Do? Chrome Extension

let isTracking = false;
let lastClickTime = 0;
let lastTypingTime = 0;
let typingTimeout = null;

// Initialize content script
init();

function init() {
  // Check if tracking is enabled
  chrome.runtime.sendMessage({ type: 'get_tracking_status' }, (response) => {
    if (response && response.tracking) {
      startTracking();
    }
  });
  
  // Listen for tracking toggle messages
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'toggle_tracking') {
      if (request.enabled) {
        startTracking();
      } else {
        stopTracking();
      }
    }
  });
}

function startTracking() {
  if (isTracking) return;
  
  isTracking = true;
  
  // Track clicks on links and buttons
  document.addEventListener('click', handleClick, true);
  
  // Track form inputs and typing
  document.addEventListener('input', handleInput, true);
  document.addEventListener('keydown', handleKeydown, true);
  
  // Track focus/blur events
  document.addEventListener('focusin', handleFocusIn, true);
  document.addEventListener('focusout', handleFocusOut, true);
  
  // Track scroll events (throttled)
  document.addEventListener('scroll', throttle(handleScroll, 2000), true);
  
  console.log('What Did I Just Do? tracking started');
}

function stopTracking() {
  if (!isTracking) return;
  
  isTracking = false;
  
  document.removeEventListener('click', handleClick, true);
  document.removeEventListener('input', handleInput, true);
  document.removeEventListener('keydown', handleKeydown, true);
  document.removeEventListener('focusin', handleFocusIn, true);
  document.removeEventListener('focusout', handleFocusOut, true);
  document.removeEventListener('scroll', handleScroll, true);
  
  console.log('What Did I Just Do? tracking stopped');
}

function handleClick(event) {
  if (!isTracking) return;
  
  const now = Date.now();
  if (now - lastClickTime < 1000) return; // Throttle clicks
  
  lastClickTime = now;
  
  const target = event.target;
  const tagName = target.tagName.toLowerCase();
  
  // Only track meaningful clicks
  if (tagName === 'a' || tagName === 'button' || target.closest('a') || target.closest('button')) {
    const link = target.closest('a') || target;
    const href = link.href || link.getAttribute('href');
    const text = target.textContent?.trim() || target.alt || target.title || 'Unknown';
    
    sendActivity('browser_click', {
      element: tagName,
      href: href,
      text: text.substring(0, 100), // Limit text length
      x: event.clientX,
      y: event.clientY
    });
  }
}

function handleInput(event) {
  if (!isTracking) return;
  
  const target = event.target;
  const tagName = target.tagName.toLowerCase();
  
  // Only track form inputs, not sensitive fields
  if (tagName === 'input' || tagName === 'textarea') {
    const type = target.type || 'text';
    const name = target.name || target.id || 'unnamed';
    
    // Skip sensitive input types
    if (['password', 'email', 'tel', 'number'].includes(type)) {
      return;
    }
    
    // Throttle typing events
    const now = Date.now();
    if (now - lastTypingTime < 2000) {
      clearTimeout(typingTimeout);
      typingTimeout = setTimeout(() => {
        sendActivity('browser_typing', {
          element: tagName,
          type: type,
          name: name,
          length: target.value?.length || 0
        });
      }, 1000);
    } else {
      lastTypingTime = now;
      sendActivity('browser_typing', {
        element: tagName,
        type: type,
        name: name,
        length: target.value?.length || 0
      });
    }
  }
}

function handleKeydown(event) {
  if (!isTracking) return;
  
  // Track special key combinations
  if (event.ctrlKey || event.metaKey) {
    const key = event.key.toLowerCase();
    if (['c', 'v', 'x', 'z', 's', 'f', 'r'].includes(key)) {
      sendActivity('browser_shortcut', {
        key: key,
        ctrlKey: event.ctrlKey,
        metaKey: event.metaKey,
        shiftKey: event.shiftKey
      });
    }
  }
}

function handleFocusIn(event) {
  if (!isTracking) return;
  
  const target = event.target;
  const tagName = target.tagName.toLowerCase();
  
  if (['input', 'textarea', 'select'].includes(tagName)) {
    sendActivity('browser_focus', {
      element: tagName,
      type: target.type || 'text',
      name: target.name || target.id || 'unnamed'
    });
  }
}

function handleFocusOut(event) {
  if (!isTracking) return;
  
  const target = event.target;
  const tagName = target.tagName.toLowerCase();
  
  if (['input', 'textarea', 'select'].includes(tagName)) {
    sendActivity('browser_blur', {
      element: tagName,
      type: target.type || 'text',
      name: target.name || target.id || 'unnamed'
    });
  }
}

function handleScroll(event) {
  if (!isTracking) return;
  
  sendActivity('browser_scroll', {
    scrollX: window.scrollX,
    scrollY: window.scrollY,
    scrollHeight: document.documentElement.scrollHeight,
    clientHeight: document.documentElement.clientHeight
  });
}

function sendActivity(eventType, data) {
  chrome.runtime.sendMessage({
    type: 'browser_activity',
    eventType: eventType,
    data: data
  });
}

// Utility function to throttle events
function throttle(func, limit) {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}
