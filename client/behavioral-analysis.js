/**
 * Advanced Behavioral Analysis Library
 * 
 * Client-side behavioral fingerprinting for sophisticated threat detection
 * Captures mouse movements, keystroke dynamics, touch patterns, and timing analysis
 */

(function(window) {
  'use strict';

  // Configuration
  const CONFIG = {
    // Data collection intervals
    MOUSE_SAMPLE_INTERVAL: 50, // ms
    KEYSTROKE_SAMPLE_INTERVAL: 10, // ms
    TOUCH_SAMPLE_INTERVAL: 25, // ms
    
    // Analysis thresholds
    MIN_MOUSE_MOVEMENTS: 50,
    MIN_KEYSTROKES: 10,
    MIN_TOUCH_EVENTS: 20,
    
    // Behavioral patterns
    BOT_DETECTION: {
      MOUSE_LINEARITY_THRESHOLD: 0.95, // Perfectly straight lines
      MOUSE_SPEED_THRESHOLD: 5000, // Pixels per second (too fast)
      MOUSE_CONSISTENCY_THRESHOLD: 0.98, // Too consistent movements
      KEYSTROKE_TIMING_THRESHOLD: 0.95, // Too consistent timing
      TOUCH_PATTERN_THRESHOLD: 0.99, // Too perfect touch patterns
      REACTION_TIME_THRESHOLD: 100 // Too fast reaction (<100ms)
    },
    
    // Privacy settings
    MAX_DATA_POINTS: 1000,
    DATA_RETENTION_MS: 5 * 60 * 1000, // 5 minutes
    ANONYMIZE_DATA: true
  };

  // Behavioral data collectors
  let behavioralData = {
    mouseMovements: [],
    keystrokeDynamics: [],
    touchPatterns: [],
    timingAnalysis: {},
    deviceInteraction: {},
    behavioralScore: 0,
    isHuman: true,
    confidence: 0.8
  };

  let isCollecting = false;
  let collectionStartTime = null;
  let lastInteractionTime = null;

  /**
   * Initialize behavioral analysis
   */
  function initializeBehavioralAnalysis() {
    if (isCollecting) return;
    
    console.log('[BehavioralAnalysis] Initializing...');
    
    collectionStartTime = Date.now();
    lastInteractionTime = Date.now();
    isCollecting = true;
    
    // Set up event listeners
    setupMouseTracking();
    setupKeystrokeTracking();
    setupTouchTracking();
    setupTimingAnalysis();
    setupDeviceInteractionTracking();
    
    // Start periodic analysis
    startBehavioralAnalysis();
    
    console.log('[BehavioralAnalysis] Initialization complete');
  }

  /**
   * Mouse movement tracking with advanced metrics
   */
  function setupMouseTracking() {
    let lastMouseEvent = null;
    let mouseMovementBuffer = [];
    
    document.addEventListener('mousemove', function(event) {
      if (!isCollecting) return;
      
      const timestamp = Date.now();
      const position = { x: event.clientX, y: event.clientY };
      
      // Calculate movement metrics
      let velocity = 0;
      let acceleration = 0;
      let angle = 0;
      let distance = 0;
      
      if (lastMouseEvent) {
        const timeDiff = timestamp - lastMouseEvent.timestamp;
        const distancePixels = Math.sqrt(
          Math.pow(position.x - lastMouseEvent.position.x, 2) + 
          Math.pow(position.y - lastMouseEvent.position.y, 2)
        );
        
        velocity = timeDiff > 0 ? distancePixels / timeDiff : 0;
        distance = distancePixels;
        
        // Calculate movement angle
        angle = Math.atan2(
          position.y - lastMouseEvent.position.y,
          position.x - lastMouseEvent.position.x
        );
        
        // Calculate acceleration
        if (lastMouseEvent.velocity > 0) {
          acceleration = (velocity - lastMouseEvent.velocity) / timeDiff;
        }
      }
      
      const mouseEvent = {
        timestamp,
        position,
        velocity,
        acceleration,
        angle,
        distance,
        target: event.target?.tagName || 'unknown',
        path: getElementPath(event.target)
      };
      
      mouseMovementBuffer.push(mouseEvent);
      lastMouseEvent = mouseEvent;
      
      // Process buffer periodically
      if (mouseMovementBuffer.length >= 10) {
        processMouseMovements(mouseMovementBuffer);
        mouseMovementBuffer = [];
      }
      
      // Maintain data limits
      if (behavioralData.mouseMovements.length >= CONFIG.MAX_DATA_POINTS) {
        behavioralData.mouseMovements = behavioralData.mouseMovements.slice(-CONFIG.MAX_DATA_POINTS / 2);
      }
    });
  }

  /**
   * Process mouse movement patterns for bot detection
   */
  function processMouseMovements(movements) {
    if (movements.length < 3) return;
    
    // Calculate movement patterns
    const patterns = analyzeMousePatterns(movements);
    
    // Detect bot-like behavior
    const botIndicators = detectBotMouseBehavior(patterns);
    
    behavioralData.mouseMovements.push({
      timestamp: Date.now(),
      movements: movements,
      patterns: patterns,
      botIndicators: botIndicators,
      isSuspicious: botIndicators.length > 0
    });
    
    // Update behavioral score
    updateBehavioralScore('mouse', botIndicators.length > 0 ? -10 : 2);
  }

  /**
   * Analyze mouse movement patterns
   */
  function analyzeMousePatterns(movements) {
    const patterns = {
      linearity: 0,
      speed: 0,
      consistency: 0,
      curvature: 0,
      acceleration: 0,
      deceleration: 0,
      stops: 0,
      directionChanges: 0
    };
    
    if (movements.length < 3) return patterns;
    
    let totalVelocity = 0;
    let maxVelocity = 0;
    let velocityVariations = 0;
    let directionChanges = 0;
    let stops = 0;
    let linearSegments = 0;
    
    for (let i = 1; i < movements.length; i++) {
      const current = movements[i];
      const previous = movements[i - 1];
      
      // Velocity analysis
      totalVelocity += current.velocity;
      maxVelocity = Math.max(maxVelocity, current.velocity);
      
      // Consistency analysis
      if (i > 1) {
        const velocityDiff = Math.abs(current.velocity - previous.velocity);
        velocityVariations += velocityDiff;
        
        // Direction change detection
        const angleDiff = Math.abs(current.angle - previous.angle);
        if (angleDiff > Math.PI / 4) { // 45 degrees
          directionChanges++;
        }
      }
      
      // Stop detection
      if (current.velocity < 10) { // Less than 10 pixels/second
        stops++;
      }
      
      // Linearity detection
      if (i > 1) {
        const angleConsistency = Math.abs(current.angle - movements[i - 2].angle);
        if (angleConsistency < 0.1) {
          linearSegments++;
        }
      }
    }
    
    patterns.speed = totalVelocity / movements.length;
    patterns.consistency = 1 - (velocityVariations / (movements.length * maxVelocity));
    patterns.directionChanges = directionChanges;
    patterns.stops = stops;
    patterns.linearity = linearSegments / (movements.length - 2);
    
    // Calculate acceleration patterns
    const accelerations = movements.filter(m => m.acceleration > 0).length;
    const decelerations = movements.filter(m => m.acceleration < 0).length;
    patterns.acceleration = accelerations / movements.length;
    patterns.deceleration = decelerations / movements.length;
    
    return patterns;
  }

  /**
   * Detect bot-like mouse behavior
   */
  function detectBotMouseBehavior(patterns) {
    const indicators = [];
    
    // Check for overly linear movements (robots move in straight lines)
    if (patterns.linearity > CONFIG.BOT_DETECTION.MOUSE_LINEARITY_THRESHOLD) {
      indicators.push('Excessively linear mouse movements');
    }
    
    // Check for impossible speeds
    if (patterns.speed > CONFIG.BOT_DETECTION.MOUSE_SPEED_THRESHOLD) {
      indicators.push('Mouse movements too fast for human');
    }
    
    // Check for overly consistent movements
    if (patterns.consistency > CONFIG.BOT_DETECTION.MOUSE_CONSISTENCY_THRESHOLD) {
      indicators.push('Mouse movement consistency too perfect');
    }
    
    // Check for lack of natural stops
    if (patterns.stops < 2 && patterns.speed > 100) {
      indicators.push('No natural mouse stops detected');
    }
    
    // Check for lack of direction changes
    if (patterns.directionChanges < 1 && patterns.speed > 50) {
      indicators.push('No natural direction changes');
    }
    
    return indicators;
  }

  /**
   * Keystroke dynamics tracking
   */
  function setupKeystrokeTracking() {
    let keystrokeBuffer = [];
    let lastKeyEvent = null;
    
    document.addEventListener('keydown', function(event) {
      if (!isCollecting) return;
      
      const timestamp = Date.now();
      const keyEvent = {
        timestamp,
        key: event.key,
        code: event.code,
        location: event.location,
        repeat: event.repeat,
        isTrusted: event.isTrusted,
        target: event.target?.tagName || 'unknown'
      };
      
      // Calculate timing metrics
      if (lastKeyEvent) {
        const timeDiff = timestamp - lastKeyEvent.timestamp;
        keyEvent.flightTime = timeDiff; // Time between key releases
        keyEvent.dwellTime = timeDiff; // Time key was held down (simplified)
      }
      
      keystrokeBuffer.push(keyEvent);
      lastKeyEvent = keyEvent;
      
      // Process buffer periodically
      if (keystrokeBuffer.length >= CONFIG.MIN_KEYSTROKES) {
        processKeystrokes(keystrokeBuffer);
        keystrokeBuffer = [];
      }
      
      // Maintain data limits
      if (behavioralData.keystrokeDynamics.length >= CONFIG.MAX_DATA_POINTS) {
        behavioralData.keystrokeDynamics = behavioralData.keystrokeDynamics.slice(-CONFIG.MAX_DATA_POINTS / 2);
      }
    });
  }

  /**
   * Process keystroke dynamics
   */
  function processKeystrokes(keystrokes) {
    const patterns = analyzeKeystrokePatterns(keystrokes);
    const botIndicators = detectBotKeystrokeBehavior(patterns);
    
    behavioralData.keystrokeDynamics.push({
      timestamp: Date.now(),
      keystrokes: keystrokes,
      patterns: patterns,
      botIndicators: botIndicators,
      isSuspicious: botIndicators.length > 0
    });
    
    // Update behavioral score
    updateBehavioralScore('keystroke', botIndicators.length > 0 ? -15 : 3);
  }

  /**
   * Analyze keystroke patterns
   */
  function analyzeKeystrokePatterns(keystrokes) {
    const patterns = {
      averageDwellTime: 0,
      averageFlightTime: 0,
      timingConsistency: 0,
      keyRepeatRate: 0,
      typingSpeed: 0,
      rhythmVariation: 0,
      pausePatterns: []
    };
    
    if (keystrokes.length < 2) return patterns;
    
    let totalDwellTime = 0;
    let totalFlightTime = 0;
    let timingVariations = 0;
    let keyRepeats = 0;
    let characterCount = 0;
    const flightTimes = [];
    
    for (let i = 1; i < keystrokes.length; i++) {
      const current = keystrokes[i];
      const previous = keystrokes[i - 1];
      
      if (current.dwellTime) {
        totalDwellTime += current.dwellTime;
      }
      
      if (current.flightTime) {
        totalFlightTime += current.flightTime;
        flightTimes.push(current.flightTime);
      }
      
      // Count key repeats
      if (current.key === previous.key && current.repeat) {
        keyRepeats++;
      }
      
      // Count meaningful characters (exclude special keys)
      if (current.key.length === 1 && !current.key.match(/[\x00-\x1F]/)) {
        characterCount++;
      }
    }
    
    patterns.averageDwellTime = totalDwellTime / (keystrokes.length - 1);
    patterns.averageFlightTime = totalFlightTime / (keystrokes.length - 1);
    patterns.keyRepeatRate = keyRepeats / keystrokes.length;
    patterns.typingSpeed = characterCount > 0 ? (characterCount / (keystrokes.length * 0.1)) : 0; // chars per second
    
    // Calculate timing consistency
    if (flightTimes.length > 1) {
      const avgFlight = patterns.averageFlightTime;
      const variance = flightTimes.reduce((sum, time) => sum + Math.pow(time - avgFlight, 2), 0) / flightTimes.length;
      patterns.timingConsistency = 1 - (Math.sqrt(variance) / avgFlight);
    }
    
    // Detect pause patterns
    const longPauses = flightTimes.filter(time => time > 500); // >500ms pauses
    patterns.pausePatterns = {
      pauseCount: longPauses.length,
      averagePauseDuration: longPauses.length > 0 ? longPauses.reduce((a, b) => a + b, 0) / longPauses.length : 0
    };
    
    return patterns;
  }

  /**
   * Detect bot-like keystroke behavior
   */
  function detectBotKeystrokeBehavior(patterns) {
    const indicators = [];
    
    // Check for overly consistent timing
    if (patterns.timingConsistency > CONFIG.BOT_DETECTION.KEYSTROKE_TIMING_THRESHOLD) {
      indicators.push('Keystroke timing too consistent for human');
    }
    
    // Check for impossible typing speed
    if (patterns.typingSpeed > 20) { // >20 chars per second
      indicators.push('Typing speed impossible for human');
    }
    
    // Check for lack of natural pauses
    if (patterns.pausePatterns.pauseCount === 0 && patterns.typingSpeed > 10) {
      indicators.push('No natural typing pauses detected');
    }
    
    // Check for excessive key repeats
    if (patterns.keyRepeatRate > 0.1) { // >10% key repeats
      indicators.push('Excessive key repeat patterns');
    }
    
    return indicators;
  }

  /**
   * Touch pattern tracking for mobile devices
   */
  function setupTouchTracking() {
    let touchBuffer = [];
    let lastTouchEvent = null;
    
    document.addEventListener('touchstart', function(event) {
      if (!isCollecting) return;
      handleTouchEvent('start', event);
    });
    
    document.addEventListener('touchmove', function(event) {
      if (!isCollecting) return;
      handleTouchEvent('move', event);
    });
    
    document.addEventListener('touchend', function(event) {
      if (!isCollecting) return;
      handleTouchEvent('end', event);
    });
    
    function handleTouchEvent(type, event) {
      const timestamp = Date.now();
      const touches = Array.from(event.touches || event.changedTouches).map(touch => ({
        identifier: touch.identifier,
        x: touch.clientX,
        y: touch.clientY,
        radiusX: touch.radiusX,
        radiusY: touch.radiusY,
        rotationAngle: touch.rotationAngle,
        force: touch.force
      }));
      
      const touchEvent = {
        timestamp,
        type,
        touches: touches,
        target: event.target?.tagName || 'unknown',
        preventDefault: event.defaultPrevented
      };
      
      // Calculate touch metrics
      if (lastTouchEvent && touches.length > 0) {
        const timeDiff = timestamp - lastTouchEvent.timestamp;
        const movement = calculateTouchMovement(lastTouchEvent.touches, touches);
        touchEvent.movement = movement;
        touchEvent.duration = timeDiff;
      }
      
      touchBuffer.push(touchEvent);
      lastTouchEvent = touchEvent;
      
      // Process buffer periodically
      if (touchBuffer.length >= CONFIG.MIN_TOUCH_EVENTS) {
        processTouchPatterns(touchBuffer);
        touchBuffer = [];
      }
      
      // Maintain data limits
      if (behavioralData.touchPatterns.length >= CONFIG.MAX_DATA_POINTS) {
        behavioralData.touchPatterns = behavioralData.touchPatterns.slice(-CONFIG.MAX_DATA_POINTS / 2);
      }
    }
  }

  /**
   * Process touch patterns
   */
  function processTouchPatterns(touches) {
    const patterns = analyzeTouchPatterns(touches);
    const botIndicators = detectBotTouchBehavior(patterns);
    
    behavioralData.touchPatterns.push({
      timestamp: Date.now(),
      touches: touches,
      patterns: patterns,
      botIndicators: botIndicators,
      isSuspicious: botIndicators.length > 0
    });
    
    // Update behavioral score
    updateBehavioralScore('touch', botIndicators.length > 0 ? -12 : 4);
  }

  /**
   * Analyze touch patterns
   */
  function analyzeTouchPatterns(touches) {
    const patterns = {
      averageTouchDuration: 0,
      touchPressureVariance: 0,
      touchSizeVariance: 0,
      gestureComplexity: 0,
      multiTouchCoordination: 0,
      swipeVelocity: 0,
      pinchZoomPatterns: []
    };
    
    if (touches.length < 2) return patterns;
    
    let totalDuration = 0;
    let totalPressure = 0;
    let pressureVariations = 0;
    let totalSize = 0;
    let sizeVariations = 0;
    let swipeVelocities = [];
    
    for (let i = 0; i < touches.length; i++) {
      const touch = touches[i];
      
      if (touch.duration) {
        totalDuration += touch.duration;
      }
      
      // Pressure analysis
      if (touch.touches[0] && touch.touches[0].force !== undefined) {
        const pressure = touch.touches[0].force;
        totalPressure += pressure;
        
        if (i > 0) {
          const prevPressure = touches[i - 1].touches[0]?.force || 0;
          pressureVariations += Math.abs(pressure - prevPressure);
        }
      }
      
      // Size analysis
      if (touch.touches[0] && touch.touches[0].radiusX !== undefined) {
        const size = touch.touches[0].radiusX * touch.touches[0].radiusY;
        totalSize += size;
        
        if (i > 0) {
          const prevSize = (touches[i - 1].touches[0]?.radiusX || 0) * (touches[i - 1].touches[0]?.radiusY || 0);
          sizeVariations += Math.abs(size - prevSize);
        }
      }
      
      // Swipe velocity
      if (touch.movement && touch.duration) {
        const velocity = touch.movement.distance / touch.duration;
        swipeVelocities.push(velocity);
      }
    }
    
    patterns.averageTouchDuration = totalDuration / touches.length;
    patterns.touchPressureVariance = pressureVariations / touches.length;
    patterns.touchSizeVariance = sizeVariations / touches.length;
    
    if (swipeVelocities.length > 0) {
      patterns.swipeVelocity = swipeVelocities.reduce((a, b) => a + b, 0) / swipeVelocities.length;
    }
    
    // Multi-touch coordination analysis
    const multiTouchEvents = touches.filter(t => t.touches.length > 1);
    if (multiTouchEvents.length > 0) {
      patterns.multiTouchCoordination = analyzeMultiTouchCoordination(multiTouchEvents);
    }
    
    return patterns;
  }

  /**
   * Detect bot-like touch behavior
   */
  function detectBotTouchBehavior(patterns) {
    const indicators = [];
    
    // Check for perfectly consistent touch patterns
    if (patterns.touchPressureVariance < 0.01 && patterns.averageTouchDuration > 0) {
      indicators.push('Touch pressure too consistent');
    }
    
    // Check for impossible swipe velocities
    if (patterns.swipeVelocity > 2000) { // 2000 pixels/second
      indicators.push('Swipe velocity impossible for human');
    }
    
    // Check for lack of natural touch size variation
    if (patterns.touchSizeVariance < 0.01 && patterns.averageTouchDuration > 100) {
      indicators.push('Touch size too consistent');
    }
    
    // Check for perfect multi-touch coordination
    if (patterns.multiTouchCoordination > CONFIG.BOT_DETECTION.TOUCH_PATTERN_THRESHOLD) {
      indicators.push('Multi-touch coordination too perfect');
    }
    
    return indicators;
  }

  /**
   * Analyze multi-touch coordination
   */
  function analyzeMultiTouchCoordination(multiTouchEvents) {
    let coordinationScore = 0;
    let totalEvents = multiTouchEvents.length;
    
    for (const event of multiTouchEvents) {
      if (event.touches.length >= 2) {
        // Calculate distance between touch points
        const touch1 = event.touches[0];
        const touch2 = event.touches[1];
        
        const distance = Math.sqrt(
          Math.pow(touch2.x - touch1.x, 2) + Math.pow(touch2.y - touch1.y, 2)
        );
        
        // Perfect coordination would maintain exact distances
        // Humans have slight variations
        if (distance > 0) {
          coordinationScore += 1 / distance; // Inverse relationship
        }
      }
    }
    
    return totalEvents > 0 ? coordinationScore / totalEvents : 0;
  }

  /**
   * Calculate touch movement between events
   */
  function calculateTouchMovement(previousTouches, currentTouches) {
    if (previousTouches.length === 0 || currentTouches.length === 0) {
      return { distance: 0, direction: 0 };
    }
    
    // Use first touch point for movement calculation
    const prev = previousTouches[0];
    const curr = currentTouches[0];
    
    const distance = Math.sqrt(
      Math.pow(curr.x - prev.x, 2) + Math.pow(curr.y - prev.y, 2)
    );
    
    const direction = Math.atan2(curr.y - prev.y, curr.x - prev.x);
    
    return { distance, direction };
  }

  /**
   * Timing analysis for reaction times and patterns
   */
  function setupTimingAnalysis() {
    let pageLoadTime = Date.now();
    let firstInteractionTime = null;
    let interactionGaps = [];
    let lastInteractionTime = null;
    
    // Track first interaction
    document.addEventListener('click', function() {
      if (!firstInteractionTime) {
        firstInteractionTime = Date.now();
        const reactionTime = firstInteractionTime - pageLoadTime;
        
        // Suspicious if reaction time is too fast (<100ms)
        if (reactionTime < CONFIG.BOT_DETECTION.REACTION_TIME_THRESHOLD) {
          behavioralData.timingAnalysis.fastReactionTime = reactionTime;
          updateBehavioralScore('timing', -20);
        }
      }
    }, { once: true });
    
    // Track interaction gaps
    document.addEventListener('click', function() {
      if (!isCollecting) return;
      
      const now = Date.now();
      if (lastInteractionTime) {
        const gap = now - lastInteractionTime;
        interactionGaps.push(gap);
        
        // Keep only recent gaps
        if (interactionGaps.length > 50) {
          interactionGaps = interactionGaps.slice(-30);
        }
        
        // Analyze interaction patterns
        if (interactionGaps.length >= 10) {
          analyzeInteractionPatterns(interactionGaps);
        }
      }
      lastInteractionTime = now;
    });
  }

  /**
   * Analyze interaction timing patterns
   */
  function analyzeInteractionPatterns(gaps) {
    const patterns = {
      averageGap: gaps.reduce((a, b) => a + b, 0) / gaps.length,
      gapVariance: 0,
      rhythmicPattern: 0,
      tooRegular: false
    };
    
    // Calculate variance
    const avgGap = patterns.averageGap;
    const variance = gaps.reduce((sum, gap) => sum + Math.pow(gap - avgGap, 2), 0) / gaps.length;
    patterns.gapVariance = variance;
    
    // Detect rhythmic patterns (too regular)
    const coefficientOfVariation = Math.sqrt(variance) / avgGap;
    if (coefficientOfVariation < 0.1) { // Less than 10% variation
      patterns.tooRegular = true;
      updateBehavioralScore('timing', -15);
    }
    
    behavioralData.timingAnalysis.interactionPatterns = patterns;
  }

  /**
   * Device interaction tracking
   */
  function setupDeviceInteractionTracking() {
    // Track device orientation changes
    window.addEventListener('orientationchange', function() {
      if (!isCollecting) return;
      
      behavioralData.deviceInteraction.orientationChanges = 
        (behavioralData.deviceInteraction.orientationChanges || 0) + 1;
      
      updateBehavioralScore('device', 1);
    });
    
    // Track device motion (mobile devices)
    if (window.DeviceMotionEvent) {
      let motionEvents = [];
      
      window.addEventListener('devicemotion', function(event) {
        if (!isCollecting) return;
        
        const motionData = {
          timestamp: Date.now(),
          acceleration: event.acceleration,
          accelerationIncludingGravity: event.accelerationIncludingGravity,
          rotationRate: event.rotationRate,
          interval: event.interval
        };
        
        motionEvents.push(motionData);
        
        // Process motion patterns
        if (motionEvents.length >= 20) {
          analyzeMotionPatterns(motionEvents);
          motionEvents = [];
        }
      });
    }
    
    // Track visibility changes (tab switching)
    document.addEventListener('visibilitychange', function() {
      if (!isCollecting) return;
      
      behavioralData.deviceInteraction.visibilityChanges = 
        (behavioralData.deviceInteraction.visibilityChanges || 0) + 1;
      
      // Suspicious if too many rapid visibility changes
      if (behavioralData.deviceInteraction.visibilityChanges > 10) {
        updateBehavioralScore('device', -5);
      }
    });
  }

  /**
   * Analyze device motion patterns
   */
  function analyzeMotionPatterns(motionEvents) {
    const patterns = {
      averageAcceleration: 0,
      motionVariance: 0,
      deviceStability: 0,
      naturalMotion: true
    };
    
    let totalAcceleration = 0;
    let accelerations = [];
    
    for (const event of motionEvents) {
      if (event.acceleration) {
        const magnitude = Math.sqrt(
          Math.pow(event.acceleration.x || 0, 2) +
          Math.pow(event.acceleration.y || 0, 2) +
          Math.pow(event.acceleration.z || 0, 2)
        );
        totalAcceleration += magnitude;
        accelerations.push(magnitude);
      }
    }
    
    if (accelerations.length > 0) {
      patterns.averageAcceleration = totalAcceleration / accelerations.length;
      
      // Calculate variance
      const avg = patterns.averageAcceleration;
      const variance = accelerations.reduce((sum, acc) => sum + Math.pow(acc - avg, 2), 0) / accelerations.length;
      patterns.motionVariance = variance;
      
      // Detect if device is too stable (possibly on a stand/desk)
      if (variance < 0.1 && avg < 0.5) {
        patterns.naturalMotion = false;
        updateBehavioralScore('device', -8);
      }
    }
    
    behavioralData.deviceInteraction.motionPatterns = patterns;
  }

  /**
   * Start behavioral analysis
   */
  function startBehavioralAnalysis() {
    setInterval(function() {
      if (!isCollecting) return;
      
      // Comprehensive behavioral analysis
      const analysis = performComprehensiveAnalysis();
      
      // Update overall behavioral assessment
      behavioralData.behavioralScore = analysis.overallScore;
      behavioralData.isHuman = analysis.isHuman;
      behavioralData.confidence = analysis.confidence;
      
      // Send to server periodically
      if (Math.random() < 0.1) { // 10% chance to send (reduce network load)
        sendBehavioralData();
      }
      
      // Clean up old data
      cleanupOldData();
      
    }, 30000); // Analyze every 30 seconds
  }

  /**
   * Perform comprehensive behavioral analysis
   */
  function performComprehensiveAnalysis() {
    let overallScore = 100; // Start with perfect human score
    let confidence = 0.8;
    let isHuman = true;
    
    // Analyze mouse behavior
    const mouseAnalysis = analyzeMouseBehavior();
    overallScore += mouseAnalysis.scoreAdjustment;
    confidence *= mouseAnalysis.confidenceMultiplier;
    
    // Analyze keystroke behavior
    const keystrokeAnalysis = analyzeKeystrokeBehavior();
    overallScore += keystrokeAnalysis.scoreAdjustment;
    confidence *= keystrokeAnalysis.confidenceMultiplier;
    
    // Analyze touch behavior
    const touchAnalysis = analyzeTouchBehavior();
    overallScore += touchAnalysis.scoreAdjustment;
    confidence *= touchAnalysis.confidenceMultiplier;
    
    // Analyze timing behavior
    const timingAnalysis = analyzeTimingBehavior();
    overallScore += timingAnalysis.scoreAdjustment;
    confidence *= timingAnalysis.confidenceMultiplier;
    
    // Final assessment
    overallScore = Math.max(0, Math.min(100, overallScore));
    confidence = Math.max(0.1, Math.min(1.0, confidence));
    isHuman = overallScore > 50; // Threshold for human vs bot
    
    return {
      overallScore,
      isHuman,
      confidence,
      breakdown: {
        mouse: mouseAnalysis,
        keystroke: keystrokeAnalysis,
        touch: touchAnalysis,
        timing: timingAnalysis
      }
    };
  }

  /**
   * Analyze mouse behavior comprehensively
   */
  function analyzeMouseBehavior() {
    const recentMouseData = behavioralData.mouseMovements.slice(-10);
    let scoreAdjustment = 0;
    let confidenceMultiplier = 1.0;
    
    if (recentMouseData.length === 0) {
      return { scoreAdjustment: -10, confidenceMultiplier: 0.9, reason: 'No mouse data' };
    }
    
    const suspiciousEvents = recentMouseData.filter(data => data.isSuspicious).length;
    
    if (suspiciousEvents > recentMouseData.length * 0.5) {
      scoreAdjustment = -30;
      confidenceMultiplier = 0.7;
    } else if (suspiciousEvents > 0) {
      scoreAdjustment = -15;
      confidenceMultiplier = 0.85;
    } else {
      scoreAdjustment = 5;
      confidenceMultiplier = 1.1;
    }
    
    return { scoreAdjustment, confidenceMultiplier, suspiciousEvents };
  }

  /**
   * Analyze keystroke behavior
   */
  function analyzeKeystrokeBehavior() {
    const recentKeystrokeData = behavioralData.keystrokeDynamics.slice(-10);
    let scoreAdjustment = 0;
    let confidenceMultiplier = 1.0;
    
    if (recentKeystrokeData.length === 0) {
      return { scoreAdjustment: -5, confidenceMultiplier: 0.95, reason: 'No keystroke data' };
    }
    
    const suspiciousEvents = recentKeystrokeData.filter(data => data.isSuspicious).length;
    
    if (suspiciousEvents > recentKeystrokeData.length * 0.6) {
      scoreAdjustment = -25;
      confidenceMultiplier = 0.75;
    } else if (suspiciousEvents > 0) {
      scoreAdjustment = -12;
      confidenceMultiplier = 0.88;
    } else {
      scoreAdjustment = 3;
      confidenceMultiplier = 1.05;
    }
    
    return { scoreAdjustment, confidenceMultiplier, suspiciousEvents };
  }

  /**
   * Analyze touch behavior
   */
  function analyzeTouchBehavior() {
    const recentTouchData = behavioralData.touchPatterns.slice(-10);
    let scoreAdjustment = 0;
    let confidenceMultiplier = 1.0;
    
    if (recentTouchData.length === 0) {
      return { scoreAdjustment: 0, confidenceMultiplier: 1.0, reason: 'No touch data' };
    }
    
    const suspiciousEvents = recentTouchData.filter(data => data.isSuspicious).length;
    
    if (suspiciousEvents > recentTouchData.length * 0.7) {
      scoreAdjustment = -20;
      confidenceMultiplier = 0.8;
    } else if (suspiciousEvents > 0) {
      scoreAdjustment = -10;
      confidenceMultiplier = 0.9;
    } else {
      scoreAdjustment = 4;
      confidenceMultiplier = 1.08;
    }
    
    return { scoreAdjustment, confidenceMultiplier, suspiciousEvents };
  }

  /**
   * Analyze timing behavior
   */
  function analyzeTimingBehavior() {
    let scoreAdjustment = 0;
    let confidenceMultiplier = 1.0;
    
    if (behavioralData.timingAnalysis.fastReactionTime) {
      scoreAdjustment = -20;
      confidenceMultiplier = 0.85;
    }
    
    const interactionPatterns = behavioralData.timingAnalysis.interactionPatterns;
    if (interactionPatterns && interactionPatterns.tooRegular) {
      scoreAdjustment -= 15;
      confidenceMultiplier *= 0.9;
    }
    
    return { scoreAdjustment, confidenceMultiplier };
  }

  /**
   * Update behavioral score
   */
  function updateBehavioralScore(type, adjustment) {
    behavioralData.behavioralScore += adjustment;
    behavioralData.behavioralScore = Math.max(0, Math.min(100, behavioralData.behavioralScore));
    
    console.log(`[BehavioralAnalysis] ${type} score updated: ${adjustment > 0 ? '+' : ''}${adjustment}, new score: ${behavioralData.behavioralScore}`);
  }

  /**
   * Send behavioral data to server
   */
  function sendBehavioralData() {
    if (!window.AdvancedProtection || !window.AdvancedProtection.isEnabled()) return;
    
    const data = {
      timestamp: Date.now(),
      behavioralScore: behavioralData.behavioralScore,
      isHuman: behavioralData.isHuman,
      confidence: behavioralData.confidence,
      mouseMovements: behavioralData.mouseMovements.slice(-5), // Last 5 only
      keystrokeDynamics: behavioralData.keystrokeDynamics.slice(-5),
      touchPatterns: behavioralData.touchPatterns.slice(-5),
      timingAnalysis: behavioralData.timingAnalysis,
      deviceInteraction: behavioralData.deviceInteraction
    };
    
    // Send via existing protection system
    fetch('/api/protection/behavioral-data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Fingerprint-Session': window.AdvancedProtection.getSessionId() || ''
      },
      body: JSON.stringify(data)
    }).catch(error => {
      console.warn('[BehavioralAnalysis] Failed to send data:', error);
    });
  }

  /**
   * Clean up old data
   */
  function cleanupOldData() {
    const cutoffTime = Date.now() - CONFIG.DATA_RETENTION_MS;
    
    behavioralData.mouseMovements = behavioralData.mouseMovements.filter(
      data => data.timestamp > cutoffTime
    );
    
    behavioralData.keystrokeDynamics = behavioralData.keystrokeDynamics.filter(
      data => data.timestamp > cutoffTime
    );
    
    behavioralData.touchPatterns = behavioralData.touchPatterns.filter(
      data => data.timestamp > cutoffTime
    );
  }

  /**
   * Utility function to get element path
   */
  function getElementPath(element) {
    if (!element) return 'unknown';
    
    const path = [];
    let current = element;
    
    while (current && current !== document.body) {
      let selector = current.tagName?.toLowerCase() || '';
      if (current.id) {
        selector += `#${current.id}`;
      } else if (current.className) {
        selector += `.${current.className.split(' ')[0]}`;
      }
      path.unshift(selector);
      current = current.parentElement;
    }
    
    return path.join(' > ');
  }

  /**
   * Get current behavioral analysis
   */
  function getBehavioralAnalysis() {
    return {
      behavioralScore: behavioralData.behavioralScore,
      isHuman: behavioralData.isHuman,
      confidence: behavioralData.confidence,
      dataPoints: {
        mouseMovements: behavioralData.mouseMovements.length,
        keystrokeDynamics: behavioralData.keystrokeDynamics.length,
        touchPatterns: behavioralData.touchPatterns.length
      },
      collectionTime: collectionStartTime ? Date.now() - collectionStartTime : 0
    };
  }

  /**
   * Stop behavioral analysis
   */
  function stopBehavioralAnalysis() {
    isCollecting = false;
    console.log('[BehavioralAnalysis] Stopped collection');
  }

  // Auto-initialize
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeBehavioralAnalysis);
  } else {
    initializeBehavioralAnalysis();
  }

  // Expose public API
  window.BehavioralAnalysis = {
    initialize: initializeBehavioralAnalysis,
    stop: stopBehavioralAnalysis,
    getAnalysis: getBehavioralAnalysis,
    isCollecting: () => isCollecting,
    CONFIG: CONFIG
  };

})(window);