# WebSocket Implementation Guide for Images MVP

## 🎯 Objective

Implement real-time progress tracking for the Images MVP upload process using WebSocket connections.

## 🚨 Current Problem

The client tries to connect to a WebSocket endpoint that doesn't exist:
```typescript
const ws = new WebSocket(`ws://${window.location.host}/api/images_mvp/progress/${sessionId}`);
// This returns 404 - endpoint doesn't exist
```

## ✅ Implementation Plan

### **Step 1: Add WebSocket Backend Endpoint**

Add to `/server/routes/images-mvp-enhanced.ts`:

```typescript
import { WebSocket } from 'ws';

// Add WebSocket route
app.ws('/api/images_mvp/progress/:sessionId', (ws, req) => {
  const sessionId = req.params.sessionId;
  const clientId = req.headers['x-client-id'] || 'anonymous';
  
  console.log(`[WebSocket] Client connected: ${clientId}, session: ${sessionId}`);
  
  // Send initial connection confirmation
  ws.send(JSON.stringify({
    type: 'connected',
    sessionId,
    timestamp: new Date().toISOString()
  }));
  
  // Handle client messages
  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data.toString());
      console.log(`[WebSocket] Received:`, message);
      
      // Handle different message types
      if (message.type === 'ping') {
        ws.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }));
      }
    } catch (error) {
      console.error('[WebSocket] Message parse error:', error);
    }
  });
  
  // Handle client disconnection
  ws.on('close', (code, reason) => {
    console.log(`[WebSocket] Client disconnected: ${clientId}, code: ${code}, reason: ${reason}`);
  });
  
  ws.on('error', (error) => {
    console.error('[WebSocket] Error:', error);
  });
  
  // Keep connection alive
  const pingInterval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping', timestamp: new Date().toISOString() }));
    }
  }, 30000); // Ping every 30 seconds
  
  ws.on('close', () => {
    clearInterval(pingInterval);
  });
});
```

### **Step 2: Add Progress Tracking to Extraction Pipeline**

Modify the extraction function to send progress updates:

```typescript
// In your extraction function
async function extractWithProgress(
  file: File,
  sessionId: string,
  ws: WebSocket,
  onProgress: (progress: number, status: string) => void
) {
  try {
    // Send initial progress
    onProgress(10, 'Starting extraction...');
    
    // Step 1: File validation
    onProgress(20, 'Validating file...');
    await validateFile(file);
    
    // Step 2: Upload
    onProgress(30, 'Uploading file...');
    await uploadFile(file);
    
    // Step 3: Processing
    onProgress(50, 'Processing metadata...');
    const metadata = await extractMetadata(file);
    
    // Step 4: Analysis
    onProgress(70, 'Analyzing results...');
    const analysis = await analyzeResults(metadata);
    
    // Step 5: Final processing
    onProgress(90, 'Finalizing results...');
    const finalResults = await finalizeResults(analysis);
    
    // Step 6: Complete
    onProgress(100, 'Extraction complete!');
    
    return finalResults;
  } catch (error) {
    onProgress(0, 'Extraction failed');
    throw error;
  }
}
```

### **Step 3: Client-Side WebSocket Implementation**

Update `client/src/components/images-mvp/progress-tracker.tsx`:

```typescript
import { useEffect, useState } from 'react';

export function ProgressTracker({ sessionId }: { sessionId: string }) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Connecting...');
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!sessionId) return;

    const ws = new WebSocket(`ws://${window.location.host}/api/images_mvp/progress/${sessionId}`);

    ws.onopen = () => {
      console.log('[WebSocket] Connected');
      setIsConnected(true);
      setStatus('Connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('[WebSocket] Received:', data);

        if (data.type === 'progress') {
          setProgress(data.progress || 0);
          setStatus(data.status || 'Processing...');
        } else if (data.type === 'connected') {
          setStatus('Connected to server');
        } else if (data.type === 'ping') {
          // Keep connection alive
          console.log('[WebSocket] Ping received');
        }
      } catch (error) {
        console.error('[WebSocket] Message parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[WebSocket] Error:', error);
      setIsConnected(false);
      setStatus('Connection error');
    };

    ws.onclose = (event) => {
      console.log('[WebSocket] Disconnected:', event.code, event.reason);
      setIsConnected(false);
      setStatus('Disconnected');
    };

    return () => {
      console.log('[WebSocket] Cleaning up connection');
      ws.close();
    };
  }, [sessionId]);

  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-slate-400">Processing Progress</span>
        <span className="text-xs text-slate-500">{status}</span>
      </div>
      
      <div className="w-full bg-white/10 rounded-full h-2 mb-2">
        <div 
          className="bg-primary h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
      
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{progress}%</span>
        {!isConnected && (
          <span className="text-xs text-yellow-500">Reconnecting...</span>
        )}
      </div>
    </div>
  );
}
```

### **Step 4: Integration with Upload Process**

Update the upload handler to use progress tracking:

```typescript
// In your upload handler
app.post('/api/images_mvp/extract', upload.single('file'), async (req, res) => {
  const sessionId = req.body.session_id || generateSessionId();
  const file = req.file;
  
  try {
    // Send initial progress
    res.status(202).json({
      sessionId,
      status: 'processing',
      message: 'File upload started'
    });
    
    // Process with progress tracking
    const result = await extractWithProgress(
      file,
      sessionId,
      (progress, status) => {
        // This will be called to update progress
        console.log(`[Progress] ${progress}% - ${status}`);
      }
    );
    
    res.json({
      success: true,
      data: result,
      sessionId
    });
    
  } catch (error) {
    console.error('[Upload] Error:', error);
    res.status(500).json({
      error: 'Upload failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});
```

## 🧪 **Testing the Implementation**

### **Step 1: Test WebSocket Connection**
```bash
# Test WebSocket connection
wscat -c ws://localhost:3000/api/images_mvp/progress/test-session
```

### **Step 2: Test with Real Upload**
```typescript
// Test the complete flow
const formData = new FormData();
formData.append('file', file);
formData.append('session_id', 'test-session-123');

const response = await fetch('/api/images_mvp/extract', {
  method: 'POST',
  body: formData,
});

// WebSocket will connect automatically and show progress
```

## 🔍 **Debugging Guide**

### **Common Issues**:
1. **WebSocket connection fails** → Check server logs, verify endpoint exists
2. **Progress not updating** → Check extraction pipeline integration
3. **Mobile WebSocket issues** → Test on actual devices
4. **Memory leaks** → Ensure proper cleanup in useEffect

### **Debug Commands**:
```bash
# Check if WebSocket endpoint exists
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  -H "Sec-WebSocket-Version: 13" \
  http://localhost:3000/api/images_mvp/progress/test

# Monitor WebSocket connections
npm run dev:server | grep -i websocket
```

## 📈 **Performance Considerations**

- **Connection Pooling**: Limit concurrent WebSocket connections
- **Memory Management**: Clean up connections properly
- **Error Recovery**: Implement reconnection logic
- **Progress Granularity**: Update every 10-20% for smooth UX

## 🎯 **Success Criteria**

✅ **WebSocket connects successfully** - No connection errors  
✅ **Progress updates smoothly** - Real-time feedback during upload  
✅ **Mobile compatibility** - Works on all device sizes  
✅ **Error recovery** - Handles disconnections gracefully  
✅ **Performance** - No memory leaks or excessive resource usage

---

**Next Step**: Implement this WebSocket solution and then proceed with mobile responsiveness fixes.