/**
 * Client-side Advanced Protection Integration
 * 
 * Integrates browser fingerprinting with server-side protection
 * Handles challenges and provides seamless user experience
 */

(function(window) {
  'use strict';

  // Configuration
  const CONFIG = {
    FINGERPRINT_REFRESH_INTERVAL: 5 * 60 * 1000, // 5 minutes
    CHALLENGE_TIMEOUT: 30000, // 30 seconds
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000,
    
    ENDPOINTS: {
      FINGERPRINT: '/api/protection/fingerprint',
      CHALLENGE: '/api/protection/challenge',
      VERIFY: '/api/protection/verify'
    }
  };

  // Protection state
  let protectionState = {
    isEnabled: true,
    sessionId: null,
    fingerprint: null,
    lastFingerprintUpdate: null,
    challengeAttempts: 0,
    isProcessing: false
  };

  // Challenge handlers
  const challengeHandlers = {
    captcha: handleCaptchaChallenge,
    delay: handleDelayChallenge,
    rate_limit: handleRateLimitChallenge,
    mfa: handleMfaChallenge
  };

  /**
   * Initialize advanced protection
   */
  async function initializeProtection() {
    try {
      console.log('[AdvancedProtection] Initializing...');
      
      // Generate initial fingerprint
      await refreshFingerprint();
      
      // Set up periodic fingerprint refresh
      setInterval(refreshFingerprint, CONFIG.FINGERPRINT_REFRESH_INTERVAL);
      
      // Set up upload interceptors
      setupUploadInterceptors();
      
      // Set up challenge handlers
      setupChallengeHandlers();
      
      console.log('[AdvancedProtection] Initialization complete');
      
    } catch (error) {
      console.error('[AdvancedProtection] Initialization failed:', error);
      
      // Continue without protection on error
      protectionState.isEnabled = false;
    }
  }

  /**
   * Generate and refresh browser fingerprint
   */
  async function refreshFingerprint() {
    if (!protectionState.isEnabled) return;
    
    try {
      console.log('[AdvancedProtection] Refreshing fingerprint...');
      
      // Generate fingerprint using BrowserFingerprint library
      if (window.BrowserFingerprint) {
        protectionState.fingerprint = await window.BrowserFingerprint.generate();
        protectionState.lastFingerprintUpdate = Date.now();
        
        console.log('[AdvancedProtection] Fingerprint generated:', {
          hash: protectionState.fingerprint.hash,
          timestamp: new Date(protectionState.fingerprint.timestamp).toISOString()
        });
        
        // Send fingerprint to server
        await sendFingerprintToServer();
      } else {
        console.warn('[AdvancedProtection] BrowserFingerprint library not available');
      }
      
    } catch (error) {
      console.error('[AdvancedProtection] Fingerprint refresh failed:', error);
    }
  }

  /**
   * Send fingerprint to server
   */
  async function sendFingerprintToServer() {
    if (!protectionState.fingerprint) return;
    
    try {
      const response = await fetch(CONFIG.ENDPOINTS.FINGERPRINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fingerprint: protectionState.fingerprint,
          sessionId: protectionState.sessionId
        })
      });
      
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update session ID if provided
      if (data.sessionId) {
        protectionState.sessionId = data.sessionId;
      }
      
      console.log('[AdvancedProtection] Fingerprint sent to server successfully');
      
    } catch (error) {
      console.error('[AdvancedProtection] Failed to send fingerprint to server:', error);
    }
  }

  /**
   * Set up upload interceptors
   */
  function setupUploadInterceptors() {
    // Intercept XMLHttpRequest
    const originalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = function() {
      const xhr = new originalXHR();
      const originalOpen = xhr.open;
      const originalSend = xhr.send;
      
      xhr.open = function(method, url, ...args) {
        this._url = url;
        this._method = method;
        return originalOpen.apply(this, [method, url, ...args]);
      };
      
      xhr.send = function(data) {
        // Add fingerprint data to upload requests
        if (isUploadRequest(this._method, this._url) && protectionState.fingerprint) {
          if (data instanceof FormData) {
            data.append('fingerprintData', JSON.stringify(protectionState.fingerprint));
          } else if (typeof data === 'string') {
            try {
              const jsonData = JSON.parse(data);
              jsonData.fingerprintData = protectionState.fingerprint;
              data = JSON.stringify(jsonData);
            } catch (e) {
              // If not JSON, append as query parameter or header
              this.setRequestHeader('X-Fingerprint-Data', JSON.stringify(protectionState.fingerprint));
            }
          }
        }
        
        return originalSend.call(this, data);
      };
      
      return xhr;
    };
    
    // Intercept fetch API
    const originalFetch = window.fetch;
    window.fetch = async function(url, options = {}) {
      if (isUploadRequest(options.method, url) && protectionState.fingerprint) {
        // Clone options to avoid modifying original
        options = { ...options };
        
        if (options.body instanceof FormData) {
          options.body.append('fingerprintData', JSON.stringify(protectionState.fingerprint));
        } else if (typeof options.body === 'string') {
          try {
            const jsonData = JSON.parse(options.body);
            jsonData.fingerprintData = protectionState.fingerprint;
            options.body = JSON.stringify(jsonData);
          } catch (e) {
            // If not JSON, add as header
            options.headers = {
              ...options.headers,
              'X-Fingerprint-Data': JSON.stringify(protectionState.fingerprint)
            };
          }
        }
      }
      
      try {
        const response = await originalFetch(url, options);
        
        // Handle challenge responses
        if (response.status === 403) {
          const data = await response.json();
          if (data.challenge) {
            return handleChallengeResponse(data.challenge, url, options);
          }
        }
        
        return response;
        
      } catch (error) {
        console.error('[AdvancedProtection] Fetch error:', error);
        throw error;
      }
    };
  }

  /**
   * Check if request is an upload request
   */
  function isUploadRequest(method, url) {
    if (!method || !url) return false;
    
    const uploadMethods = ['POST', 'PUT', 'PATCH'];
    const uploadPatterns = [
      '/upload',
      '/file',
      '/document',
      '/image',
      '/media'
    ];
    
    return uploadMethods.includes(method.toUpperCase()) && 
           uploadPatterns.some(pattern => url.toLowerCase().includes(pattern));
  }

  /**
   * Handle challenge response from server
   */
  async function handleChallengeResponse(challenge, originalUrl, originalOptions) {
    console.log('[AdvancedProtection] Handling challenge:', challenge.type);
    
    try {
      protectionState.isProcessing = true;
      protectionState.challengeAttempts++;
      
      const handler = challengeHandlers[challenge.type];
      if (!handler) {
        throw new Error(`Unknown challenge type: ${challenge.type}`);
      }
      
      // Execute challenge handler
      const challengeResponse = await handler(challenge.data);
      
      // Send challenge response to server
      const verifyResponse = await fetch(CONFIG.ENDPOINTS.VERIFY, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          challengeResponse: {
            type: challenge.type,
            ...challengeResponse
          },
          sessionId: challenge.sessionId || protectionState.sessionId
        })
      });
      
      if (verifyResponse.ok) {
        console.log('[AdvancedProtection] Challenge passed, retrying original request');
        
        // Reset challenge attempts on success
        protectionState.challengeAttempts = 0;
        protectionState.isProcessing = false;
        
        // Retry original request
        return window.fetch(originalUrl, originalOptions);
        
      } else {
        throw new Error('Challenge verification failed');
      }
      
    } catch (error) {
      console.error('[AdvancedProtection] Challenge handling failed:', error);
      
      protectionState.isProcessing = false;
      
      // Retry with exponential backoff
      if (protectionState.challengeAttempts < CONFIG.MAX_RETRIES) {
        const delay = CONFIG.RETRY_DELAY * Math.pow(2, protectionState.challengeAttempts - 1);
        console.log(`[AdvancedProtection] Retrying challenge in ${delay}ms...`);
        
        await new Promise(resolve => setTimeout(resolve, delay));
        return handleChallengeResponse(challenge, originalUrl, originalOptions);
      }
      
      // Max retries reached, show error to user
      showChallengeError(challenge.type, error);
      throw error;
    }
  }

  /**
   * Handle CAPTCHA challenge
   */
  async function handleCaptchaChallenge(data) {
    console.log('[AdvancedProtection] Handling CAPTCHA challenge');
    
    return new Promise((resolve, reject) => {
      // Create CAPTCHA container
      const container = document.createElement('div');
      container.id = 'advanced-protection-captcha';
      container.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
      `;
      
      const content = document.createElement('div');
      content.style.cssText = `
        background: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        max-width: 400px;
      `;
      
      content.innerHTML = `
        <h3>Security Verification Required</h3>
        <p>Please complete the CAPTCHA to continue.</p>
        <div id="captcha-container"></div>
        <button id="captcha-submit" style="margin-top: 10px; padding: 10px 20px;">Submit</button>
      `;
      
      container.appendChild(content);
      document.body.appendChild(container);
      
      // Handle CAPTCHA completion
      const submitButton = content.querySelector('#captcha-submit');
      submitButton.addEventListener('click', () => {
        const token = 'mock_captcha_token_' + Math.random().toString(36).substr(2, 9);
        
        // Clean up
        document.body.removeChild(container);
        
        resolve({
          token: token,
          completed: true
        });
      });
      
      // Timeout handling
      setTimeout(() => {
        if (document.body.contains(container)) {
          document.body.removeChild(container);
          reject(new Error('CAPTCHA timeout'));
        }
      }, CONFIG.CHALLENGE_TIMEOUT);
    });
  }

  /**
   * Handle delay challenge
   */
  async function handleDelayChallenge(data) {
    console.log('[AdvancedProtection] Handling delay challenge');
    
    return new Promise((resolve) => {
      // Create delay notification
      const notification = document.createElement('div');
      notification.id = 'advanced-protection-delay';
      notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #f0f0f0;
        border: 1px solid #ccc;
        padding: 15px;
        border-radius: 5px;
        z-index: 10000;
        max-width: 300px;
      `;
      
      const delaySeconds = data.delaySeconds || 5;
      let remaining = delaySeconds;
      
      const updateNotification = () => {
        notification.innerHTML = `
          <strong>Security Check</strong><br>
          Please wait ${remaining} seconds...<br>
          <small>This helps protect against automated uploads.</small>
        `;
      };
      
      updateNotification();
      document.body.appendChild(notification);
      
      // Countdown
      const interval = setInterval(() => {
        remaining--;
        updateNotification();
        
        if (remaining <= 0) {
          clearInterval(interval);
          document.body.removeChild(notification);
          resolve({
            completed: true,
            waitedSeconds: delaySeconds
          });
        }
      }, 1000);
    });
  }

  /**
   * Handle rate limit challenge
   */
  async function handleRateLimitChallenge(data) {
    console.log('[AdvancedProtection] Handling rate limit challenge');
    
    return new Promise((resolve) => {
      const maxRequests = data.maxRequests || 5;
      const windowMinutes = data.windowMinutes || 1;
      
      // Show rate limit notification
      const notification = document.createElement('div');
      notification.id = 'advanced-protection-rate-limit';
      notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        z-index: 10000;
        max-width: 300px;
      `;
      
      notification.innerHTML = `
        <strong>Rate Limit Notice</strong><br>
        To prevent abuse, please limit uploads to ${maxRequests} requests per ${windowMinutes} minute${windowMinutes > 1 ? 's' : ''}.<br>
        <small>Click to acknowledge and continue.</small>
      `;
      
      document.body.appendChild(notification);
      
      // Auto-dismiss after acknowledgment
      notification.addEventListener('click', () => {
        document.body.removeChild(notification);
        resolve({
          acknowledged: true,
          maxRequests: maxRequests,
          windowMinutes: windowMinutes
        });
      });
      
      // Auto-dismiss after timeout
      setTimeout(() => {
        if (document.body.contains(notification)) {
          document.body.removeChild(notification);
          resolve({
            acknowledged: true,
            maxRequests: maxRequests,
            windowMinutes: windowMinutes
          });
        }
      }, CONFIG.CHALLENGE_TIMEOUT);
    });
  }

  /**
   * Handle MFA challenge (placeholder)
   */
  async function handleMfaChallenge(data) {
    console.log('[AdvancedProtection] Handling MFA challenge');
    
    // This would implement MFA verification
    // For now, simulate successful MFA
    return {
      completed: true,
      method: 'simulated'
    };
  }

  /**
   * Set up challenge handlers
   */
  function setupChallengeHandlers() {
    // Preload challenge resources if needed
    // This could include CAPTCHA libraries, etc.
  }

  /**
   * Show challenge error to user
   */
  function showChallengeError(challengeType, error) {
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #f8d7da;
      border: 1px solid #f5c6cb;
      color: #721c24;
      padding: 15px;
      border-radius: 5px;
      z-index: 10000;
      max-width: 300px;
    `;
    
    notification.innerHTML = `
      <strong>Security Verification Failed</strong><br>
      Unable to complete ${challengeType} verification.<br>
      <small>Error: ${error.message}</small>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 5000);
  }

  /**
   * Get current protection state
   */
  function getProtectionState() {
    return { ...protectionState };
  }

  /**
   * Enable/disable protection
   */
  function setProtectionEnabled(enabled) {
    protectionState.isEnabled = enabled;
    console.log(`[AdvancedProtection] Protection ${enabled ? 'enabled' : 'disabled'}`);
  }

  /**
   * Manually refresh fingerprint
   */
  function manualRefresh() {
    return refreshFingerprint();
  }

  // Expose public API
  window.AdvancedProtection = {
    initialize: initializeProtection,
    getState: getProtectionState,
    setEnabled: setProtectionEnabled,
    refreshFingerprint: manualRefresh,
    CONFIG: CONFIG
  };

  // Auto-initialize if DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeProtection);
  } else {
    initializeProtection();
  }

})(window);