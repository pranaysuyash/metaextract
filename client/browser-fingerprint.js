/**
 * Client-side Browser Fingerprinting Library
 * 
 * Generates comprehensive browser fingerprints for abuse detection
 * Compatible with all major browsers (Chrome, Firefox, Safari, Edge)
 * 
 * Usage:
 * const fingerprint = await generateBrowserFingerprint();
 * console.log(fingerprint);
 */

(function(window) {
  'use strict';

  // Configuration
  const CONFIG = {
    CANVAS_STRENGTH: 10,
    WEBGL_STRENGTH: 10,
    AUDIO_STRENGTH: 10,
    FONT_LIST: [
      'Arial', 'Arial Black', 'Arial Narrow', 'Calibri', 'Cambria', 'Cambria Math',
      'Comic Sans MS', 'Consolas', 'Courier', 'Courier New', 'Georgia', 'Helvetica',
      'Impact', 'Lucida Console', 'Lucida Sans Unicode', 'Microsoft Sans Serif',
      'MS Gothic', 'MS PGothic', 'MS Sans Serif', 'MS Serif', 'Palatino Linotype',
      'Segoe Print', 'Segoe Script', 'Segoe UI', 'Segoe UI Light', 'Segoe UI Semibold',
      'Segoe UI Symbol', 'Tahoma', 'Times', 'Times New Roman', 'Trebuchet MS',
      'Verdana', 'Wingdings', 'Wingdings 2', 'Wingdings 3'
    ],
    PLUGIN_LIST: [
      'Chrome PDF Plugin', 'Chrome PDF Viewer', 'Native Client', 'Shockwave Flash',
      'QuickTime Plug-in', 'Java Applet Plug-in', 'Windows Media Player Plug-in'
    ]
  };

  /**
   * Generate comprehensive browser fingerprint
   */
  async function generateBrowserFingerprint() {
    const fingerprint = {
      timestamp: Date.now(),
      
      // Basic browser info
      userAgent: navigator.userAgent,
      language: navigator.language,
      languages: navigator.languages || [navigator.language],
      platform: navigator.platform,
      cookieEnabled: navigator.cookieEnabled,
      doNotTrack: navigator.doNotTrack,
      
      // Screen and display info
      screen: {
        width: screen.width,
        height: screen.height,
        availWidth: screen.availWidth,
        availHeight: screen.availHeight,
        colorDepth: screen.colorDepth,
        pixelDepth: screen.pixelDepth,
        orientation: screen.orientation?.type || 'unknown'
      },
      
      // Window info
      window: {
        innerWidth: window.innerWidth,
        innerHeight: window.innerHeight,
        outerWidth: window.outerWidth,
        outerHeight: window.outerHeight,
        devicePixelRatio: window.devicePixelRatio || 1
      },
      
      // Hardware info
      hardware: {
        deviceMemory: navigator.deviceMemory || 0,
        hardwareConcurrency: navigator.hardwareConcurrency || 0,
        maxTouchPoints: navigator.maxTouchPoints || 0
      },
      
      // Touch support
      touch: {
        maxTouchPoints: navigator.maxTouchPoints || 0,
        touchEvent: 'ontouchstart' in window,
        touchStart: 'ontouchstart' in window,
        touchEnd: 'ontouchend' in window,
        touchMove: 'ontouchmove' in window
      },
      
      // Canvas fingerprint
      canvas: await getCanvasFingerprint(),
      
      // WebGL fingerprint
      webgl: await getWebGLFingerprint(),
      
      // Audio fingerprint
      audio: await getAudioFingerprint(),
      
      // Font detection
      fonts: await getInstalledFonts(),
      
      // Plugin detection
      plugins: getPlugins(),
      
      // Timezone info
      timezone: {
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        offset: new Date().getTimezoneOffset(),
        dst: isDST()
      },
      
      // Media capabilities
      mediaCapabilities: getMediaCapabilities(),
      
      // Network info
      network: {
        connection: navigator.connection ? {
          effectiveType: navigator.connection.effectiveType,
          downlink: navigator.connection.downlink,
          rtt: navigator.connection.rtt
        } : null
      }
    };

    // Generate hash
    fingerprint.hash = await generateHash(fingerprint);
    
    return fingerprint;
  }

  /**
   * Generate canvas fingerprint
   */
  async function getCanvasFingerprint() {
    try {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      canvas.width = 200;
      canvas.height = 50;
      
      // Draw text with different fonts and styles
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillStyle = '#f60';
      ctx.fillRect(125, 1, 62, 20);
      
      ctx.fillStyle = '#069';
      ctx.font = '16px Arial';
      ctx.fillText('Browser Fingerprint', 2, 15);
      
      ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
      ctx.font = '18px Arial';
      ctx.fillText('Canvas Test', 4, 45);
      
      // Add some randomness
      for (let i = 0; i < CONFIG.CANVAS_STRENGTH; i++) {
        ctx.fillStyle = `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 0.5)`;
        ctx.fillRect(Math.random() * canvas.width, Math.random() * canvas.height, 2, 2);
      }
      
      // Get image data and create hash
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;
      
      // Create hash from image data
      const hash = await hashData(data);
      
      // Clean up
      canvas.remove();
      
      return {
        hash: hash,
        width: canvas.width,
        height: canvas.height,
        textMetrics: ctx.measureText('Browser Fingerprint').width
      };
    } catch (error) {
      console.warn('Canvas fingerprint failed:', error);
      return { hash: 'error', width: 0, height: 0, textMetrics: 0 };
    }
  }

  /**
   * Generate WebGL fingerprint
   */
  async function getWebGLFingerprint() {
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      
      if (!gl) {
        return { vendor: 'unknown', renderer: 'unknown', version: 'unknown', extensions: [] };
      }
      
      const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
      const vendor = debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : 'unknown';
      const renderer = debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'unknown';
      const version = gl.getParameter(gl.VERSION);
      
      // Get extensions
      const extensions = gl.getSupportedExtensions() || [];
      
      // Create hash from WebGL info
      const webglHash = await hashData({ vendor, renderer, version, extensions });
      
      // Add some WebGL rendering to make it more unique
      gl.clearColor(Math.random(), Math.random(), Math.random(), 1);
      gl.clear(gl.COLOR_BUFFER_BIT);
      
      // Get pixel data for additional uniqueness
      const pixels = new Uint8Array(4);
      gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
      
      const pixelHash = await hashData(pixels);
      
      // Clean up
      canvas.remove();
      
      return {
        vendor,
        renderer,
        version,
        extensions: extensions.slice(0, 10), // Limit to avoid too much data
        webglHash,
        pixelHash
      };
    } catch (error) {
      console.warn('WebGL fingerprint failed:', error);
      return { vendor: 'error', renderer: 'error', version: 'error', extensions: [] };
    }
  }

  /**
   * Generate audio fingerprint
   */
  async function getAudioFingerprint() {
    try {
      if (!window.AudioContext && !window.webkitAudioContext) {
        return { oscillator: 'unsupported', dynamics: 'unsupported', frequency: 0 };
      }
      
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      
      // Create oscillator
      const oscillator = audioContext.createOscillator();
      oscillator.type = 'triangle';
      oscillator.frequency.setValueAtTime(10000, audioContext.currentTime);
      
      // Create compressor
      const compressor = audioContext.createDynamicsCompressor();
      compressor.threshold.setValueAtTime(-50, audioContext.currentTime);
      compressor.knee.setValueAtTime(40, audioContext.currentTime);
      compressor.ratio.setValueAtTime(12, audioContext.currentTime);
      compressor.attack.setValueAtTime(0, audioContext.currentTime);
      compressor.release.setValueAtTime(0.25, audioContext.currentTime);
      
      // Connect and process
      oscillator.connect(compressor);
      compressor.connect(audioContext.destination);
      
      oscillator.start();
      
      // Get frequency response
      const frequencyData = new Float32Array(32);
      compressor.frequencyResponse(new Float32Array([1000, 2000, 3000]), frequencyData, new Float32Array(32));
      
      // Create hash from audio data
      const oscillatorHash = await hashData(oscillator);
      const dynamicsHash = await hashData(compressor);
      const frequencyHash = await hashData(frequencyData);
      
      oscillator.stop();
      audioContext.close();
      
      return {
        oscillator: oscillatorHash,
        dynamics: dynamicsHash,
        frequency: frequencyHash,
        sampleRate: audioContext.sampleRate
      };
    } catch (error) {
      console.warn('Audio fingerprint failed:', error);
      return { oscillator: 'error', dynamics: 'error', frequency: 'error', sampleRate: 0 };
    }
  }

  /**
   * Detect installed fonts
   */
  async function getInstalledFonts() {
    try {
      const availableFonts = [];
      const testString = 'Browser Fingerprint Test';
      const testSize = '72px';
      const baseFonts = ['monospace', 'serif', 'sans-serif'];
      
      // Create test element
      const testElement = document.createElement('span');
      testElement.style.position = 'absolute';
      testElement.style.left = '-9999px';
      testElement.style.fontSize = testSize;
      testElement.style.lineHeight = 'normal';
      document.body.appendChild(testElement);
      
      // Test each font
      for (const font of CONFIG.FONT_LIST) {
        let isAvailable = false;
        
        for (const baseFont of baseFonts) {
          testElement.style.fontFamily = `'${font}', ${baseFont}`;
          const testWidth = testElement.offsetWidth;
          const testHeight = testElement.offsetHeight;
          
          testElement.style.fontFamily = baseFont;
          const baseWidth = testElement.offsetWidth;
          const baseHeight = testElement.offsetHeight;
          
          if (testWidth !== baseWidth || testHeight !== baseHeight) {
            isAvailable = true;
            break;
          }
        }
        
        if (isAvailable) {
          availableFonts.push(font);
        }
      }
      
      // Clean up
      document.body.removeChild(testElement);
      
      // Create hash from font list
      const fontHash = await hashData(availableFonts);
      
      return {
        count: availableFonts.length,
        fonts: availableFonts,
        hash: fontHash
      };
    } catch (error) {
      console.warn('Font detection failed:', error);
      return { count: 0, fonts: [], hash: 'error' };
    }
  }

  /**
   * Get browser plugins
   */
  function getPlugins() {
    try {
      const plugins = [];
      
      if (navigator.plugins) {
        for (let i = 0; i < navigator.plugins.length; i++) {
          const plugin = navigator.plugins[i];
          plugins.push({
            name: plugin.name,
            filename: plugin.filename,
            description: plugin.description,
            version: plugin.version || 'unknown'
          });
        }
      }
      
      return {
        count: plugins.length,
        plugins: plugins
      };
    } catch (error) {
      console.warn('Plugin detection failed:', error);
      return { count: 0, plugins: [] };
    }
  }

  /**
   * Get media capabilities
   */
  function getMediaCapabilities() {
    try {
      const capabilities = {
        video: {
          h264: MediaSource.isTypeSupported('video/mp4; codecs="avc1.42E01E"'),
          webm: MediaSource.isTypeSupported('video/webm; codecs="vp8, vorbis"'),
          ogg: MediaSource.isTypeSupported('video/ogg; codecs="theora"')
        },
        audio: {
          mp3: new Audio().canPlayType('audio/mpeg') !== '',
          ogg: new Audio().canPlayType('audio/ogg') !== '',
          wav: new Audio().canPlayType('audio/wav') !== '',
          m4a: new Audio().canPlayType('audio/x-m4a') !== ''
        }
      };
      
      return capabilities;
    } catch (error) {
      console.warn('Media capabilities detection failed:', error);
      return { video: {}, audio: {} };
    }
  }

  /**
   * Check if daylight saving time is active
   */
  function isDST() {
    const date = new Date();
    const january = new Date(date.getFullYear(), 0, 1);
    const july = new Date(date.getFullYear(), 6, 1);
    
    return Math.max(january.getTimezoneOffset(), july.getTimezoneOffset()) !== date.getTimezoneOffset();
  }

  /**
   * Generate hash from data
   */
  async function hashData(data) {
    try {
      const textEncoder = new TextEncoder();
      const dataString = JSON.stringify(data);
      const dataBuffer = textEncoder.encode(dataString);
      
      const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      
      return hashHex;
    } catch (error) {
      console.warn('Hash generation failed:', error);
      return 'hash_error';
    }
  }

  /**
   * Generate overall hash from fingerprint
   */
  async function generateHash(fingerprint) {
    try {
      // Create a stable representation by sorting keys
      const sortedFingerprint = {};
      Object.keys(fingerprint).sort().forEach(key => {
        sortedFingerprint[key] = fingerprint[key];
      });
      
      return await hashData(sortedFingerprint);
    } catch (error) {
      console.warn('Overall hash generation failed:', error);
      return 'overall_hash_error';
    }
  }

  // Utility functions
  const utils = {
    // Check if fingerprint is valid
    isValidFingerprint: function(fingerprint) {
      return fingerprint && fingerprint.hash && fingerprint.timestamp;
    },
    
    // Compare two fingerprints
    compareFingerprints: async function(fp1, fp2) {
      if (!fp1 || !fp2) return 0;
      
      let similarity = 0;
      let total = 0;
      
      // Compare basic properties
      const basicProps = ['userAgent', 'language', 'platform', 'cookieEnabled'];
      basicProps.forEach(prop => {
        total++;
        if (fp1[prop] === fp2[prop]) similarity++;
      });
      
      // Compare hashes
      if (fp1.hash === fp2.hash) similarity += 5;
      
      // Compare canvas hashes
      if (fp1.canvas?.hash === fp2.canvas?.hash) similarity += 3;
      
      // Compare WebGL hashes
      if (fp1.webgl?.webglHash === fp2.webgl?.webglHash) similarity += 3;
      
      // Compare audio hashes
      if (fp1.audio?.oscillator === fp2.audio?.oscillator) similarity += 2;
      
      return similarity / (total + 13); // Normalized to 0-1
    },
    
    // Detect anomalies
    detectAnomalies: function(fingerprint) {
      const anomalies = [];
      
      // Check for headless browser
      if (fingerprint.userAgent.includes('HeadlessChrome')) {
        anomalies.push('Headless browser detected');
      }
      
      // Check for minimal fingerprint
      if (!fingerprint.canvas || fingerprint.canvas.hash === 'error') {
        anomalies.push('Canvas fingerprint failed');
      }
      
      // Check for plugin inconsistencies
      if (fingerprint.plugins.count === 0 && fingerprint.userAgent.includes('Chrome')) {
        anomalies.push('Chrome with no plugins detected');
      }
      
      // Check for mobile inconsistencies
      if (fingerprint.userAgent.includes('Mobile') && fingerprint.touch.maxTouchPoints === 0) {
        anomalies.push('Mobile UA but no touch support');
      }
      
      return anomalies;
    }
  };

  // Expose the library
  window.BrowserFingerprint = {
    generate: generateBrowserFingerprint,
    utils: utils,
    CONFIG: CONFIG
  };

})(window);