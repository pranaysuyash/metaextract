/**
 * Advanced Protection API Routes
 * 
 * Provides endpoints for browser fingerprinting and ML anomaly detection
 */

import { Router, Request, Response } from 'express';
import { generateFingerprint, analyzeFingerprint, trackFingerprint } from '../monitoring/browser-fingerprint';
import { mlAnomalyDetector } from '../monitoring/ml-anomaly-detection';
import { securityEventLogger } from '../monitoring/security-events';
import { securityAlertManager } from '../monitoring/security-alerts';
import { getProtectionStats, getRiskLevel } from '../middleware/advanced-protection';

const router = Router();

/**
 * POST /api/protection/fingerprint
 * Submit browser fingerprint data
 */
router.post('/fingerprint', async (req: Request, res: Response) => {
  try {
    const { fingerprint, sessionId } = req.body;
    const userId = (req as any).user?.id;
    
    if (!fingerprint) {
      return res.status(400).json({
        error: 'Fingerprint data is required'
      });
    }

    // Validate fingerprint data
    const validationResult = validateFingerprintData(fingerprint);
    if (!validationResult.isValid) {
      await securityEventLogger.logEvent({
        event: 'invalid_fingerprint',
        severity: 'low',
        timestamp: new Date(),
        source: 'fingerprint_endpoint',
        ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
        userId,
        details: {
          validationErrors: validationResult.errors,
          receivedFingerprint: fingerprint
        }
      });

      return res.status(400).json({
        error: 'Invalid fingerprint data',
        details: validationResult.errors
      });
    }

    // Analyze fingerprint for anomalies
    const analysis = await analyzeFingerprint(fingerprint);
    
    // Track fingerprint across sessions
    const tracking = await trackFingerprint(fingerprint, userId);

    // Log the fingerprint submission
    await securityEventLogger.logEvent({
      event: 'fingerprint_submitted',
      severity: analysis.riskScore > 50 ? 'medium' : 'low',
      timestamp: new Date(),
      source: 'fingerprint_endpoint',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userId,
      details: {
        fingerprintId: fingerprint.fingerprintHash,
        deviceId: fingerprint.deviceId,
        sessionId: sessionId || fingerprint.sessionId,
        riskScore: analysis.riskScore,
        confidence: analysis.confidence,
        anomalies: analysis.anomalies,
        isUnique: analysis.isUnique,
        similarDevices: analysis.similarFingerprints.length,
        tracking: {
          isNewDevice: tracking.isNewDevice,
          previousSessions: tracking.previousSessions,
          riskLevel: tracking.riskLevel
        }
      }
    });

    // Send alert for high-risk fingerprints
    if (analysis.riskScore >= 80) {
      await securityAlertManager.sendAlert({
        type: 'security',
        severity: 'high',
        title: 'High-Risk Browser Fingerprint Detected',
        message: `Suspicious browser fingerprint with risk score ${analysis.riskScore}/100`,
        details: {
          fingerprintId: fingerprint.fingerprintHash,
          deviceId: fingerprint.deviceId,
          ipAddress: req.ip || req.connection.remoteAddress,
          userAgent: fingerprint.userAgent,
          anomalies: analysis.anomalies,
          similarDevices: analysis.similarFingerprints.length
        },
        metadata: {
          category: 'fingerprint_analysis',
          tags: ['high_risk', 'fingerprint', 'suspicious']
        }
      });
    }

    res.json({
      success: true,
      fingerprintId: fingerprint.fingerprintHash,
      deviceId: fingerprint.deviceId,
      sessionId: sessionId || fingerprint.sessionId,
      analysis: {
        riskScore: analysis.riskScore,
        riskLevel: getRiskLevel(analysis.riskScore),
        confidence: analysis.confidence,
        isUnique: analysis.isUnique,
        anomalies: analysis.anomalies,
        recommendations: analysis.recommendations
      },
      tracking: {
        isNewDevice: tracking.isNewDevice,
        previousSessions: tracking.previousSessions,
        riskLevel: tracking.riskLevel,
        action: tracking.action
      }
    });

  } catch (error: unknown) {
    console.error('[FingerprintEndpoint] Error:', error);
    const errorDetails: { message?: string; stack?: string; raw?: string } = {};
    if (error instanceof Error) {
      errorDetails.message = error.message;
      errorDetails.stack = error.stack;
    } else {
      errorDetails.raw = typeof error === 'string' ? error : JSON.stringify(error);
    }

    await securityEventLogger.logEvent({
      event: 'fingerprint_error',
      severity: 'medium',
      timestamp: new Date(),
      source: 'fingerprint_endpoint',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userId: (req as any).user?.id,
      details: errorDetails
    });

    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to process fingerprint data'
    });
  }
});

/**
 * GET /api/protection/fingerprint/:id
 * Get fingerprint analysis by ID
 */
router.get('/fingerprint/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const userId = (req as any).user?.id;
    
    // Validate fingerprint ID format
    if (!isValidFingerprintId(id)) {
      return res.status(400).json({
        error: 'Invalid fingerprint ID format'
      });
    }

    // Get fingerprint data from storage
    const fingerprintData = await getFingerprintById(id);
    
    if (!fingerprintData) {
      return res.status(404).json({
        error: 'Fingerprint not found'
      });
    }

    // Check authorization
    if (fingerprintData.userId && fingerprintData.userId !== userId) {
      return res.status(403).json({
        error: 'Access denied'
      });
    }

    // Re-analyze fingerprint with current data
    const analysis = await analyzeFingerprint(fingerprintData.fingerprintData);

    res.json({
      fingerprintId: id,
      deviceId: fingerprintData.deviceId,
      userId: fingerprintData.userId,
      timestamp: fingerprintData.timestamp,
      analysis: {
        riskScore: analysis.riskScore,
        riskLevel: getRiskLevel(analysis.riskScore),
        confidence: analysis.confidence,
        isUnique: analysis.isUnique,
        anomalies: analysis.anomalies,
        recommendations: analysis.recommendations,
        similarFingerprints: analysis.similarFingerprints
      },
      metadata: {
        ipAddress: fingerprintData.ipAddress,
        userAgent: fingerprintData.fingerprintData.userAgent,
        confidence: fingerprintData.confidence,
        anomalies: fingerprintData.anomalies
      }
    });

  } catch (error) {
    console.error('[FingerprintGetEndpoint] Error:', error);
    res.status(500).json({
      error: 'Internal server error'
    });
  }
});

/**
 * POST /api/protection/anomaly-detection
 * Run ML anomaly detection on current request
 */
router.post('/anomaly-detection', async (req: Request, res: Response) => {
  try {
    const { fingerprintData, context } = req.body;
    const userId = (req as any).user?.id;

    // Parse fingerprint if provided
    let fingerprint;
    if (fingerprintData) {
      fingerprint = {
        ...fingerprintData,
        fingerprintHash: fingerprintData.hash,
        deviceId: fingerprintData.deviceId || 'unknown',
        sessionId: fingerprintData.sessionId || 'unknown',
        ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
        timestamp: new Date(),
        confidence: 0.8,
        anomalies: []
      };
    }

    // Run ML anomaly detection
    const anomalyResult = await mlAnomalyDetector.detectUploadAnomaly(req, fingerprint);

    // Log the detection
    await securityEventLogger.logEvent({
      event: 'anomaly_detection',
      severity: anomalyResult.riskLevel,
      timestamp: new Date(),
      source: 'anomaly_endpoint',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userId,
      details: {
        isAnomalous: anomalyResult.isAnomalous,
        confidence: anomalyResult.confidence,
        riskScore: anomalyResult.riskScore,
        riskLevel: anomalyResult.riskLevel,
        contributingFactors: anomalyResult.contributingFactors,
        modelVersion: anomalyResult.modelVersion,
        context: context || {}
      }
    });

    // Send alert for high-risk detections
    if (anomalyResult.riskLevel === 'high' || anomalyResult.riskLevel === 'critical') {
      await securityAlertManager.sendAlert({
        type: 'security',
        severity: 'high',
        title: 'ML Anomaly Detection Alert',
        message: `High-risk behavior detected with confidence ${Math.round(anomalyResult.confidence * 100)}%`,
        details: {
          riskScore: anomalyResult.riskScore,
          riskLevel: anomalyResult.riskLevel,
          contributingFactors: anomalyResult.contributingFactors,
          ipAddress: req.ip || req.connection.remoteAddress,
          userAgent: req.headers['user-agent'],
          modelVersion: anomalyResult.modelVersion
        },
        metadata: {
          category: 'anomaly_detection',
          tags: ['ml_detection', 'high_risk', 'suspicious_behavior']
        }
      });
    }

    res.json({
      success: true,
      detection: {
        isAnomalous: anomalyResult.isAnomalous,
        confidence: anomalyResult.confidence,
        riskScore: anomalyResult.riskScore,
        riskLevel: anomalyResult.riskLevel,
        contributingFactors: anomalyResult.contributingFactors,
        recommendations: anomalyResult.recommendations,
        modelVersion: anomalyResult.modelVersion,
        timestamp: anomalyResult.timestamp
      }
    });

  } catch (error) {
    console.error('[AnomalyDetectionEndpoint] Error:', error);
    
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to run anomaly detection'
    });
  }
});

/**
 * GET /api/protection/stats
 * Get protection system statistics
 */
router.get('/stats', async (req: Request, res: Response) => {
  try {
    const stats = await getProtectionStats();
    const modelStats = mlAnomalyDetector.getModelStats();

    res.json({
      success: true,
      stats: {
        ...stats,
        mlModel: modelStats
      },
      timestamp: new Date()
    });

  } catch (error) {
    console.error('[ProtectionStatsEndpoint] Error:', error);
    res.status(500).json({
      error: 'Internal server error'
    });
  }
});

/**
 * GET /api/protection/model-info
 * Get ML model information
 */
router.get('/model-info', async (req: Request, res: Response) => {
  try {
    const modelStats = mlAnomalyDetector.getModelStats();
    const modelVersion = mlAnomalyDetector.getModelVersion();
    const isTrained = mlAnomalyDetector.isModelTrained();

    res.json({
      success: true,
      model: {
        version: modelVersion,
        isTrained,
        stats: modelStats,
        config: {
          minSamples: 50,
          trainingWindowHours: 24,
          retrainingIntervalHours: 6,
          anomalyThreshold: 0.8,
          featureWeights: {
            uploadFrequency: 0.25,
            fileSize: 0.20,
            ipStability: 0.15,
            deviceConsistency: 0.15,
            timePattern: 0.10,
            geolocation: 0.10,
            fingerprint: 0.05
          }
        }
      },
      timestamp: new Date()
    });

  } catch (error) {
    console.error('[ModelInfoEndpoint] Error:', error);
    res.status(500).json({
      error: 'Internal server error'
    });
  }
});

/**
 * POST /api/protection/feedback
 * Submit feedback on protection decisions
 */
router.post('/feedback', async (req: Request, res: Response) => {
  try {
    const { fingerprintId, decision, wasCorrect, feedback, context } = req.body;
    const userId = (req as any).user?.id;

    if (!fingerprintId || !decision) {
      return res.status(400).json({
        error: 'Fingerprint ID and decision are required'
      });
    }

    // Log the feedback
    await securityEventLogger.logEvent({
      event: 'protection_feedback',
      severity: 'low',
      timestamp: new Date(),
      source: 'feedback_endpoint',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userId,
      details: {
        fingerprintId,
        decision,
        wasCorrect,
        feedback: feedback || '',
        context: context || {}
      }
    });

    // Process feedback for model improvement
    if (wasCorrect !== undefined) {
      // This would update the ML model with feedback
      console.log(`[ProtectionFeedback] Processing feedback: decision=${decision}, wasCorrect=${wasCorrect}`);
    }

    res.json({
      success: true,
      message: 'Feedback submitted successfully'
    });

  } catch (error) {
    console.error('[ProtectionFeedbackEndpoint] Error:', error);
    res.status(500).json({
      error: 'Internal server error'
    });
  }
});

/**
 * Helper functions
 */

function validateFingerprintData(fingerprint: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!fingerprint.hash) {
    errors.push('Missing fingerprint hash');
  }

  if (!fingerprint.timestamp) {
    errors.push('Missing timestamp');
  }

  if (!fingerprint.userAgent) {
    errors.push('Missing user agent');
  }

  if (fingerprint.canvas && typeof fingerprint.canvas !== 'object') {
    errors.push('Invalid canvas fingerprint format');
  }

  if (fingerprint.webgl && typeof fingerprint.webgl !== 'object') {
    errors.push('Invalid WebGL fingerprint format');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

function isValidFingerprintId(id: string): boolean {
  // Validate SHA256 hash format (64 hex characters)
  return /^[a-fA-F0-9]{64}$/.test(id);
}

async function getFingerprintById(id: string): Promise<any> {
  try {
    // This would query the database
    // For now, return mock data
    return {
      id,
      deviceId: 'mock_device_123',
      userId: null,
      fingerprintData: {
        fingerprintHash: id,
        deviceId: 'mock_device_123',
        sessionId: 'mock_session_456',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        timestamp: new Date()
      },
      ipAddress: '192.168.1.1',
      timestamp: new Date(),
      confidence: 0.85,
      anomalies: []
    };
  } catch (error) {
    console.error('[GetFingerprintById] Error:', error);
    return null;
  }
}

export default router;