/**
 * Enhanced Protection API Routes
 * 
 * API endpoints for advanced threat intelligence and behavioral analysis
 */

import { Router, Request, Response } from 'express';
import { enhancedProtectionMiddleware, verifyEnhancedChallengeResponse, getEnhancedProtectionStats } from '../middleware/enhanced-protection';
import { threatIntelligenceService } from '../monitoring/production-validation';
import { securityEventLogger } from '../monitoring/security-events';
import { securityAlertManager } from '../monitoring/security-alerts';
import { ENHANCED_PROTECTION_CONFIG } from '../middleware/enhanced-protection';

const router = Router();

/**
 * POST /api/enhanced-protection/check
 * Enhanced protection check endpoint
 */
router.post('/check', enhancedProtectionMiddleware, async (req: Request, res: Response) => {
  try {
    const protectionResult = (req as any).enhancedProtectionResult;
    
    if (!protectionResult) {
      return res.status(500).json({
        error: 'Protection analysis failed',
        message: 'Unable to perform enhanced protection analysis'
      });
    }

    res.json({
      success: true,
      protection: {
        action: protectionResult.action,
        confidence: protectionResult.confidence,
        riskScore: protectionResult.riskScore,
        riskLevel: protectionResult.riskLevel,
        reasons: protectionResult.reasons,
        recommendations: protectionResult.recommendations,
        incidentId: protectionResult.incidentId,
        requiresVerification: protectionResult.requiresVerification
      },
      analysis: {
        threatIntelligence: protectionResult.threatIntelligence,
        behavioralAnalysis: protectionResult.behavioralAnalysis,
        mlAnalysis: protectionResult.mlAnalysis,
        deviceAnalysis: protectionResult.deviceAnalysis
      },
      timestamp: new Date()
    });

  } catch (error) {
    console.error('[EnhancedProtectionCheck] Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to perform enhanced protection check'
    });
  }
});

/**
 * POST /api/enhanced-protection/verify-challenge
 * Verify enhanced challenge response
 */
router.post('/verify-challenge', verifyEnhancedChallengeResponse, (req: Request, res: Response) => {
  // Challenge passed, continue with original request
  res.json({
    success: true,
    message: 'Challenge verification successful',
    incidentId: (req as any).incidentId
  });
});

/**
 * POST /api/enhanced-protection/behavioral-data
 * Receive behavioral analysis data from client
 */
router.post('/behavioral-data', async (req: Request, res: Response) => {
  try {
    const { behavioralData } = req.body;
    const userId = (req as any).user?.id;
    
    if (!behavioralData) {
      return res.status(400).json({
        error: 'Behavioral data is required'
      });
    }

    // Validate behavioral data structure
    const validationResult = validateBehavioralData(behavioralData);
    if (!validationResult.isValid) {
      return res.status(400).json({
        error: 'Invalid behavioral data',
        details: validationResult.errors
      });
    }

    // Log behavioral analysis data
    await securityEventLogger.logEvent({
      event: 'behavioral_analysis_received',
      severity: behavioralData.isHuman ? 'low' : 'high',
      timestamp: new Date(),
      source: 'behavioral_analysis',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userId,
      details: {
        behavioralScore: behavioralData.behavioralScore,
        isHuman: behavioralData.isHuman,
        confidence: behavioralData.confidence,
        dataPoints: behavioralData.dataPoints,
        collectionTime: behavioralData.collectionTime
      }
    });

    // Process for ML model training if high confidence
    if (behavioralData.confidence > 0.8) {
      // This would feed into ML model for continuous improvement
      console.log(`[BehavioralData] High confidence behavioral data received: human=${behavioralData.isHuman}, score=${behavioralData.behavioralScore}`);
    }

    // Alert for non-human behavior
    if (!behavioralData.isHuman && behavioralData.confidence > 0.7) {
      await securityAlertManager.sendAlert({
        type: 'behavioral_anomaly',
        severity: 'medium',
        title: 'Non-Human Behavioral Patterns Detected',
        message: `Behavioral analysis indicates automated behavior with ${Math.round(behavioralData.confidence * 100)}% confidence`,
        details: {
          behavioralScore: behavioralData.behavioralScore,
          confidence: behavioralData.confidence,
          dataPoints: behavioralData.dataPoints,
          ipAddress: req.ip || req.connection.remoteAddress
        },
        metadata: {
          category: 'behavioral_analysis',
          tags: ['non_human', 'automated_behavior', 'high_confidence']
        }
      });
    }

    res.json({
      success: true,
      message: 'Behavioral data received successfully',
      analysis: {
        behavioralScore: behavioralData.behavioralScore,
        isHuman: behavioralData.isHuman,
        confidence: behavioralData.confidence
      }
    });

  } catch (error) {
    console.error('[BehavioralDataEndpoint] Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to process behavioral data'
    });
  }
});

/**
 * GET /api/enhanced-protection/threat-intel/:ip
 * Get threat intelligence for specific IP
 */
router.get('/threat-intel/:ip', async (req: Request, res: Response) => {
  try {
    const { ip } = req.params;
    const userId = (req as any).user?.id;
    
    if (!isValidIP(ip)) {
      return res.status(400).json({
        error: 'Invalid IP address format'
      });
    }

    // Create mock request for threat intelligence check
    const mockReq = {
      ip: ip,
      connection: { remoteAddress: ip },
      headers: req.headers,
      body: {},
      path: req.path,
      method: req.method
    } as any;

    const threatIntel = await threatIntelligenceService.checkThreatIntelligence(mockReq);

    // Log the lookup
    await securityEventLogger.logEvent({
      event: 'threat_intelligence_lookup',
      severity: threatIntel.threatLevel,
      timestamp: new Date(),
      source: 'threat_intelligence_endpoint',
      ipAddress: ip,
      userId,
      details: {
        riskScore: threatIntel.riskScore,
        threatLevel: threatIntel.threatLevel,
        sources: threatIntel.sources,
        recommendations: threatIntel.recommendations
      }
    });

    res.json({
      success: true,
      threatIntelligence: threatIntel,
      timestamp: new Date()
    });

  } catch (error) {
    console.error('[ThreatIntelEndpoint] Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to retrieve threat intelligence'
    });
  }
});

/**
 * POST /api/enhanced-protection/report-threat
 * Report malicious IP to threat intelligence services
 */
router.post('/report-threat', async (req: Request, res: Response) => {
  try {
    const { ipAddress, categories, comment } = req.body;
    const userId = (req as any).user?.id;
    
    if (!ipAddress || !categories || !Array.isArray(categories)) {
      return res.status(400).json({
        error: 'IP address and categories are required'
      });
    }

    if (!isValidIP(ipAddress)) {
      return res.status(400).json({
        error: 'Invalid IP address format'
      });
    }

    // Report to threat intelligence services
    await threatIntelligenceService.reportMaliciousIP(ipAddress, categories, comment);

    // Log the report
    await securityEventLogger.logEvent({
      event: 'threat_report_submitted',
      severity: 'medium',
      timestamp: new Date(),
      source: 'threat_report_endpoint',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userId,
      details: {
        reportedIP: ipAddress,
        categories: categories,
        comment: comment
      }
    });

    res.json({
      success: true,
      message: 'Threat report submitted successfully',
      reportedIP: ipAddress,
      categories: categories,
      timestamp: new Date()
    });

  } catch (error) {
    console.error('[ThreatReportEndpoint] Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to submit threat report'
    });
  }
});

/**
 * GET /api/enhanced-protection/stats
 * Get enhanced protection statistics
 */
router.get('/stats', async (req: Request, res: Response) => {
  try {
    const stats = await getEnhancedProtectionStats();
    
    res.json({
      success: true,
      stats: stats,
      timestamp: new Date()
    });

  } catch (error) {
    console.error('[EnhancedProtectionStatsEndpoint] Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to retrieve enhanced protection statistics'
    });
  }
});

/**
 * GET /api/enhanced-protection/config
 * Get enhanced protection configuration
 */
router.get('/config', (req: Request, res: Response) => {
  // Return safe configuration (without API keys)
  const safeConfig = {
    features: {
      threatIntelligence: ENHANCED_PROTECTION_CONFIG.THREAT_INTELLIGENCE,
      behavioralAnalysis: ENHANCED_PROTECTION_CONFIG.BEHAVIORAL_ANALYSIS,
      advancedML: ENHANCED_PROTECTION_CONFIG.ADVANCED_ML,
      realTimeUpdates: ENHANCED_PROTECTION_CONFIG.REAL_TIME_UPDATES
    },
    thresholds: {
      critical: ENHANCED_PROTECTION_CONFIG.CRITICAL_RISK_THRESHOLD,
      high: ENHANCED_PROTECTION_CONFIG.HIGH_RISK_THRESHOLD,
      medium: ENHANCED_PROTECTION_CONFIG.MEDIUM_RISK_THRESHOLD,
      low: ENHANCED_PROTECTION_CONFIG.LOW_RISK_THRESHOLD
    },
    weights: ENHANCED_PROTECTION_CONFIG.WEIGHTS,
    challenges: {
      types: Object.values(ENHANCED_PROTECTION_CONFIG.CHALLENGES),
      actions: Object.values(ENHANCED_PROTECTION_CONFIG.ACTIONS)
    },
    timestamp: new Date()
  };

  res.json({
    success: true,
    config: safeConfig
  });
});

/**
 * POST /api/enhanced-protection/feedback
 * Submit feedback on protection decisions
 */
router.post('/feedback', async (req: Request, res: Response) => {
  try {
    const { 
      incidentId, 
      decision, 
      wasCorrect, 
      feedback, 
      context,
      expectedAction,
      actualAction
    } = req.body;
    
    const userId = (req as any).user?.id;

    if (!incidentId || decision === undefined || wasCorrect === undefined) {
      return res.status(400).json({
        error: 'Incident ID, decision, and wasCorrect are required'
      });
    }

    // Log the feedback
    await securityEventLogger.logEvent({
      event: 'enhanced_protection_feedback',
      severity: wasCorrect ? 'low' : 'medium',
      timestamp: new Date(),
      source: 'enhanced_protection_feedback',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userId,
      details: {
        incidentId,
        decision,
        wasCorrect,
        feedback: feedback || '',
        context: context || {},
        expectedAction,
        actualAction
      }
    });

    // Process feedback for ML model improvement
    if (!wasCorrect) {
      // This would be used to retrain or adjust the ML models
      console.log(`[EnhancedProtectionFeedback] Incorrect decision reported for incident ${incidentId}`);
    }

    res.json({
      success: true,
      message: 'Feedback submitted successfully',
      incidentId,
      timestamp: new Date()
    });

  } catch (error) {
    console.error('[EnhancedProtectionFeedbackEndpoint] Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to submit feedback'
    });
  }
});

/**
 * WebSocket endpoint for real-time behavioral analysis
 */
router.ws('/behavioral-stream', (ws, req) => {
  console.log('[EnhancedProtection] Behavioral analysis WebSocket connection established');
  
  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message.toString());
      
      if (data.type === 'behavioral_data') {
        // Process real-time behavioral data
        const { behavioralData } = data;
        
        if (behavioralData && behavioralData.confidence > 0.7) {
          // Real-time analysis and response
          const analysis = {
            type: 'behavioral_analysis',
            behavioralScore: behavioralData.behavioralScore,
            isHuman: behavioralData.isHuman,
            confidence: behavioralData.confidence,
            timestamp: Date.now()
          };
          
          ws.send(JSON.stringify(analysis));
          
          // Alert for immediate threats
          if (!behavioralData.isHuman && behavioralData.confidence > 0.8) {
            ws.send(JSON.stringify({
              type: 'immediate_threat',
              message: 'Non-human behavior detected with high confidence',
              action: 'immediate_verification_required'
            }));
          }
        }
      }
    } catch (error) {
      console.error('[BehavioralStream] Error processing message:', error);
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Failed to process behavioral data'
      }));
    }
  });
  
  ws.on('close', () => {
    console.log('[EnhancedProtection] Behavioral analysis WebSocket connection closed');
  });
});

/**
 * Helper functions
 */
function validateBehavioralData(data: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  if (typeof data.behavioralScore !== 'number' || data.behavioralScore < 0 || data.behavioralScore > 100) {
    errors.push('Behavioral score must be a number between 0 and 100');
  }
  
  if (typeof data.isHuman !== 'boolean') {
    errors.push('isHuman must be a boolean');
  }
  
  if (typeof data.confidence !== 'number' || data.confidence < 0 || data.confidence > 1) {
    errors.push('Confidence must be a number between 0 and 1');
  }
  
  if (data.dataPoints && typeof data.dataPoints !== 'object') {
    errors.push('Data points must be an object');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

function isValidIP(ip: string): boolean {
  const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  const ipv6Regex = /^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.)$/;
  
  return ipv4Regex.test(ip) || ipv6Regex.test(ip);
}

export default router;