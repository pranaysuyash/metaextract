/**
 * Browser Fingerprint Generator for Client-Side
 *
 * Generates comprehensive browser fingerprints for abuse detection
 * - Multiple sessions from same device detection
 * - Cookie clearing attempt identification
 * - Device fingerprinting evasion detection
 * - Advanced abuse pattern recognition
 */

export interface BrowserFingerprintData {
  // Basic browser info
  userAgent: string;
  platform: string;
  language: string;
  timezone: string;
  cookieEnabled: boolean;
  doNotTrack: string | null;

  // Screen info
  screen: string;
  availScreen: string;
  colorDepth: number;
  pixelRatio: number;

  // Canvas fingerprint
  canvas: string;

  // WebGL fingerprint
  webgl: string;
  webglVendor: string;
  webglRenderer: string;

  // Audio fingerprint
  audio: string;

  // Font detection
  fonts: string;

  // Plugin detection
  plugins: string;

  // Hardware info
  deviceMemory: number;
  hardwareConcurrency: number;
  maxTouchPoints: number;
  touchSupport: boolean;
}

export async function generateBrowserFingerprint(): Promise<BrowserFingerprintData> {
  const fingerprint: BrowserFingerprintData = {
    // Basic browser info
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    cookieEnabled: navigator.cookieEnabled,
    doNotTrack: navigator.doNotTrack,

    // Screen info
    screen: `${screen.width}x${screen.height}`,
    availScreen: `${screen.availWidth}x${screen.availHeight}`,
    colorDepth: screen.colorDepth,
    pixelRatio: window.devicePixelRatio,

    // Canvas fingerprint (basic implementation)
    canvas: generateCanvasFingerprint(),

    // WebGL fingerprint
    webgl: generateWebGLFingerprint(),
    webglVendor: getWebGLVendor(),
    webglRenderer: getWebGLRenderer(),

    // Audio fingerprint
    audio: await generateAudioFingerprint(),

    // Font detection
    fonts: detectFonts(),

    // Plugin detection
    plugins: detectPlugins(),

    // Hardware info
    deviceMemory: (navigator as any).deviceMemory || 0,
    hardwareConcurrency: navigator.hardwareConcurrency || 0,
    maxTouchPoints: navigator.maxTouchPoints || 0,
    touchSupport: 'ontouchstart' in window,
  };

  return fingerprint;
}

function generateCanvasFingerprint(): string {
  try {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return 'unknown';

    canvas.width = 280;
    canvas.height = 60;

    ctx.fillStyle = '#f60';
    ctx.fillRect(100, 1, 62, 20);

    ctx.fillStyle = '#069';
    ctx.font = '14px Arial';
    ctx.fillText('MetaExtract Fingerprint 🚀', 2, 15);

    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
    ctx.font = '18px Times New Roman';
    ctx.fillText('Security Test', 4, 45);

    return canvas.toDataURL().substring(0, 100); // Truncate for storage
  } catch (e) {
    return 'error';
  }
}

function generateWebGLFingerprint(): string {
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl') as WebGLRenderingContext | null;
    if (!gl) return 'unavailable';

    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (!debugInfo) return 'available';

    const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
    const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);

    return `${vendor} | ${renderer}`;
  } catch (e) {
    return 'error';
  }
}

function getWebGLVendor(): string {
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl') as WebGLRenderingContext | null;
    if (!gl) return 'unavailable';

    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    return debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : 'unknown';
  } catch (e) {
    return 'error';
  }
}

function getWebGLRenderer(): string {
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl') as WebGLRenderingContext | null;
    if (!gl) return 'unavailable';

    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    return debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'unknown';
  } catch (e) {
    return 'error';
  }
}

async function generateAudioFingerprint(): Promise<string> {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const analyser = audioContext.createAnalyser();
    const gain = audioContext.createGain();
    const processor = audioContext.createScriptProcessor(4096, 1, 1);

    gain.gain.value = 0; // Mute
    oscillator.type = 'triangle';
    oscillator.frequency.value = 10000;

    oscillator.connect(analyser);
    analyser.connect(processor);
    processor.connect(gain);
    gain.connect(audioContext.destination);

    oscillator.start(0);

    const fingerprint = await new Promise<string>((resolve) => {
      processor.onaudioprocess = (e) => {
        const data = e.inputBuffer.getChannelData(0);
        let sum = 0;
        for (let i = 0; i < data.length; i++) {
          sum += Math.abs(data[i]);
        }
        resolve(sum.toFixed(4));
        oscillator.stop();
        audioContext.close();
      };
    });

    return fingerprint;
  } catch (e) {
    return 'unavailable';
  }
}

function detectFonts(): string {
  const baseFonts = ['monospace', 'sans-serif', 'serif'];
  const testFonts = [
    'Arial', 'Arial Black', 'Arial Narrow', 'Calibri', 'Cambria', 'Cambria Math',
    'Comic Sans MS', 'Consolas', 'Courier', 'Courier New', 'Georgia', 'Helvetica',
    'Impact', 'Lucida Console', 'Lucida Sans Unicode', 'Microsoft Sans Serif',
    'Palatino Linotype', 'Segoe UI', 'Tahoma', 'Times', 'Times New Roman',
    'Trebuchet MS', 'Verdana', 'Monaco'
  ];

  const testString = 'mmmmmmmmmmlli';
  const testSize = '72px';
  const h = document.getElementsByTagName('body')[0];

  const span = document.createElement('span');
  span.style.fontSize = testSize;
  span.innerHTML = testString;
  span.style.position = 'absolute';
  span.style.left = '-9999px';

  const baseFontWidths: Record<string, number> = {};
  for (const baseFont of baseFonts) {
    span.style.fontFamily = baseFont;
    h.appendChild(span);
    baseFontWidths[baseFont] = span.offsetWidth;
    h.removeChild(span);
  }

  const detectedFonts: string[] = [];
  for (const font of testFonts) {
    let detected = false;
    for (const baseFont of baseFonts) {
      span.style.fontFamily = `'${font}', ${baseFont}`;
      h.appendChild(span);
      const width = span.offsetWidth;
      h.removeChild(span);

      if (width !== baseFontWidths[baseFont]) {
        detected = true;
        break;
      }
    }
    if (detected) {
      detectedFonts.push(font);
    }
  }

  return detectedFonts.slice(0, 10).join(', '); // Limit to first 10
}

function detectPlugins(): string {
  const plugins: string[] = [];

  if (navigator.plugins) {
    for (let i = 0; i < navigator.plugins.length; i++) {
      const plugin = navigator.plugins[i];
      if (plugin && plugin.name) {
        plugins.push(plugin.name);
      }
    }
  }

  return plugins.length > 0 ? plugins.slice(0, 5).join(', ') : 'none';
}

export function generateFingerprintHash(fingerprint: BrowserFingerprintData): string {
  // Simple hash generation (client-side)
  const data = JSON.stringify(fingerprint, Object.keys(fingerprint).sort());
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    const char = data.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return Math.abs(hash).toString(16);
}

export function getSessionId(): string {
  let sessionId = sessionStorage.getItem('metaextract_session_id');
  if (!sessionId) {
    sessionId = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('metaextract_session_id', sessionId);
  }
  return sessionId;
}