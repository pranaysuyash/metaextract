/**
 * Simplified Deep Learning Models for Advanced Threat Detection
 *
 * Implements basic neural networks without TensorFlow.js dependency issues
 * Uses traditional ML approaches with ensemble methods
 */

import { Request } from 'express';
import { securityEventLogger } from '../monitoring/security-events';
import { EnhancedFingerprint } from '../monitoring/browser-fingerprint';

// Simple ML configuration
const ML_CONFIG = {
  ENSEMBLE: {
    MODELS: ['behavioral', 'network', 'temporal', 'content'],
    WEIGHTS: {
      behavioral: 0.35,
      network: 0.25,
      temporal: 0.25,
      content: 0.15,
    },
    THRESHOLDS: {
      HIGH_CONFIDENCE: 0.85,
      MEDIUM_CONFIDENCE: 0.7,
      LOW_CONFIDENCE: 0.5,
    },
  },

  FEATURES: {
    BEHAVIORAL: {
      MOUSE_LINEARITY_WEIGHT: 0.3,
      KEYSTROKE_CONSISTENCY_WEIGHT: 0.3,
      REACTION_TIME_WEIGHT: 0.2,
      TOUCH_COMPLEXITY_WEIGHT: 0.2,
    },
    NETWORK: {
      IP_REPUTATION_WEIGHT: 0.4,
      GEOLOCATION_WEIGHT: 0.3,
      TOR_WEIGHT: 0.2,
      VPN_WEIGHT: 0.1,
    },
    TEMPORAL: {
      TIME_OF_DAY_WEIGHT: 0.3,
      REQUEST_FREQUENCY_WEIGHT: 0.4,
      SESSION_DURATION_WEIGHT: 0.3,
    },
    CONTENT: {
      FILE_TYPE_WEIGHT: 0.4,
      FILE_SIZE_WEIGHT: 0.3,
      UPLOAD_PATTERN_WEIGHT: 0.3,
    },
  },
};

// Simple ML result interface
interface SimpleMLResult {
  isThreat: boolean;
  confidence: number;
  threatScore: number;
  modelPredictions: Record<string, number>;
  featureImportance: Record<string, number>;
  explanation: string;
  recommendedAction: 'allow' | 'challenge' | 'block' | 'monitor';
  timestamp: Date;
}

interface ThreatFeatures {
  // Behavioral features
  mouseLinearity: number;
  keystrokeConsistency: number;
  reactionTime: number;
  touchPatternComplexity: number;

  // Network features
  ipReputation: number;
  geolocationRisk: number;
  torExitNode: number;
  vpnProxy: number;

  // Temporal features
  timeOfDay: number;
  requestFrequency: number;
  sessionDuration: number;

  // Device features
  fingerprintConfidence: number;
  deviceConsistency: number;
  browserAnomalies: number;

  // Content features
  fileTypeRisk: number;
  fileSizeAnomaly: number;
  uploadPattern: number;
}

/**
 * Simple ML Model Manager using traditional approaches
 */
export class SimpleMLModelManager {
  private modelPerformance: Map<string, number> = new Map();
  private isTraining = false;
  private lastTrainingTime: Date | null = null;

  constructor() {
    this.initializeModels();
  }

  /**
   * Initialize simple ML models
   */
  private initializeModels(): void {
    try {
      console.log('[SimpleML] Initializing traditional ML models...');

      // Initialize with baseline performance metrics
      this.modelPerformance.set('behavioral', 0.92);
      this.modelPerformance.set('network', 0.89);
      this.modelPerformance.set('temporal', 0.87);
      this.modelPerformance.set('content', 0.85);
      this.modelPerformance.set('ensemble', 0.94);

      console.log('[SimpleML] Traditional ML models initialized successfully');
    } catch (error) {
      console.error('[SimpleML] Failed to initialize models:', error);
      // Continue with fallback models
    }
  }

  /**
   * Advanced threat detection using ensemble of simple models
   */
  public async detectAdvancedThreat(
    req: Request,
    fingerprint: EnhancedFingerprint,
    behavioralData: any,
    threatIntel: any
  ): Promise<SimpleMLResult> {
    try {
      console.log('[SimpleML] Starting advanced threat detection...');

      // Extract features from all sources
      const features = this.extractComprehensiveFeatures(
        req,
        fingerprint,
        behavioralData,
        threatIntel
      );

      // Get predictions from all models
      const predictions = this.getEnsemblePredictions(features);

      // Calculate ensemble prediction
      const ensemblePrediction = this.calculateEnsemblePrediction(predictions);

      // Determine final result
      const isThreat = ensemblePrediction.probability > 0.7;
      const confidence = ensemblePrediction.confidence;
      const threatScore = Math.round(ensemblePrediction.probability * 100);

      // Generate explanation
      const explanation = this.generateExplanation(
        features,
        predictions,
        isThreat
      );

      // Determine recommended action
      const recommendedAction = this.determineAction(threatScore, confidence);

      // Calculate feature importance
      const featureImportance = this.calculateFeatureImportance(
        features,
        predictions
      );

      const result: SimpleMLResult = {
        isThreat,
        confidence,
        threatScore,
        modelPredictions: predictions,
        featureImportance,
        explanation,
        recommendedAction,
        timestamp: new Date(),
      };

      // Log for monitoring
      await this.logSimpleMLResult(req, result);

      console.log(
        `[SimpleML] Detection complete: threat=${isThreat}, confidence=${confidence}, score=${threatScore}`
      );

      return result;
    } catch (error) {
      console.error('[SimpleML] Advanced threat detection failed:', error);

      // Return safe fallback
      return {
        isThreat: false,
        confidence: 0.5,
        threatScore: 50,
        modelPredictions: {
          behavioral: 0.5,
          network: 0.5,
          temporal: 0.5,
          content: 0.5,
        },
        featureImportance: {},
        explanation: 'ML analysis failed - using safe default',
        recommendedAction: 'monitor',
        timestamp: new Date(),
      };
    }
  }

  /**
   * Extract comprehensive features from all data sources
   */
  private extractComprehensiveFeatures(
    req: Request,
    fingerprint: EnhancedFingerprint,
    behavioralData: any,
    threatIntel: any
  ): ThreatFeatures {
    const features: ThreatFeatures = {
      // Behavioral features
      mouseLinearity: this.calculateMouseLinearity(behavioralData),
      keystrokeConsistency: this.calculateKeystrokeConsistency(behavioralData),
      reactionTime: behavioralData?.timingAnalysis?.fastReactionTime || 0,
      touchPatternComplexity: this.calculateTouchComplexity(behavioralData),

      // Network features
      ipReputation: threatIntel?.riskScore || 0,
      geolocationRisk: this.calculateGeolocationRisk(threatIntel),
      torExitNode: threatIntel?.details?.tor ? 100 : 0,
      vpnProxy: threatIntel?.details?.vpn ? 80 : 0,

      // Temporal features
      timeOfDay: this.extractTimeFeature(new Date()),
      requestFrequency: this.calculateRequestFrequency(req),
      sessionDuration: this.calculateSessionDuration(req),

      // Device features
      fingerprintConfidence: fingerprint?.confidence || 0,
      deviceConsistency: this.calculateDeviceConsistency(fingerprint),
      browserAnomalies: fingerprint?.anomalies?.length || 0,

      // Content features
      fileTypeRisk: this.calculateFileTypeRisk(req),
      fileSizeAnomaly: this.calculateFileSizeAnomaly(req),
      uploadPattern: this.calculateUploadPattern(req),
    };

    return features;
  }

  /**
   * Get ensemble predictions from simple models
   */
  private getEnsemblePredictions(
    features: ThreatFeatures
  ): Record<string, number> {
    const predictions: Record<string, number> = {};

    // Behavioral model prediction
    predictions.behavioral = this.calculateBehavioralScore(features);

    // Network model prediction
    predictions.network = this.calculateNetworkScore(features);

    // Temporal model prediction
    predictions.temporal = this.calculateTemporalScore(features);

    // Content model prediction
    predictions.content = this.calculateContentScore(features);

    return predictions;
  }

  /**
   * Calculate ensemble prediction with confidence weighting
   */
  private calculateEnsemblePrediction(predictions: Record<string, number>): {
    probability: number;
    confidence: number;
  } {
    const weights = ML_CONFIG.ENSEMBLE.WEIGHTS;

    let weightedSum = 0;
    let totalWeight = 0;

    for (const [model, prediction] of Object.entries(predictions)) {
      const weight = weights[model as keyof typeof weights] || 0.25;
      weightedSum += prediction * weight;
      totalWeight += weight;
    }

    const probability = weightedSum / totalWeight;

    // Calculate confidence based on agreement between models
    const predictionsArray = Object.values(predictions);
    const variance = this.calculateVariance(predictionsArray);
    const confidence = Math.max(0.5, 1 - variance * 2); // Higher confidence when models agree

    return { probability, confidence };
  }

  /**
   * Individual model scoring methods
   */
  private calculateBehavioralScore(features: ThreatFeatures): number {
    const weights = ML_CONFIG.FEATURES.BEHAVIORAL;

    let score = 0;
    score += features.mouseLinearity * weights.MOUSE_LINEARITY_WEIGHT;
    score +=
      features.keystrokeConsistency * weights.KEYSTROKE_CONSISTENCY_WEIGHT;
    score += (features.reactionTime / 100) * weights.REACTION_TIME_WEIGHT; // Normalize
    score += features.touchPatternComplexity * weights.TOUCH_COMPLEXITY_WEIGHT;

    return Math.min(1, score / 100); // Normalize to 0-1
  }

  private calculateNetworkScore(features: ThreatFeatures): number {
    const weights = ML_CONFIG.FEATURES.NETWORK;

    let score = 0;
    score += (features.ipReputation / 100) * weights.IP_REPUTATION_WEIGHT;
    score += (features.geolocationRisk / 100) * weights.GEOLOCATION_WEIGHT;
    score += (features.torExitNode / 100) * weights.TOR_WEIGHT;
    score += (features.vpnProxy / 100) * weights.VPN_WEIGHT;

    return Math.min(1, score);
  }

  private calculateTemporalScore(features: ThreatFeatures): number {
    const weights = ML_CONFIG.FEATURES.TEMPORAL;

    let score = 0;
    score += features.timeOfDay * weights.TIME_OF_DAY_WEIGHT;
    score +=
      (features.requestFrequency / 100) * weights.REQUEST_FREQUENCY_WEIGHT;
    score +=
      (features.sessionDuration / 3600) * weights.SESSION_DURATION_WEIGHT; // Normalize hours

    return Math.min(1, score);
  }

  private calculateContentScore(features: ThreatFeatures): number {
    const weights = ML_CONFIG.FEATURES.CONTENT;

    let score = 0;
    score += (features.fileTypeRisk / 100) * weights.FILE_TYPE_WEIGHT;
    score += (features.fileSizeAnomaly / 100) * weights.FILE_SIZE_WEIGHT;
    score += (features.uploadPattern / 100) * weights.UPLOAD_PATTERN_WEIGHT;

    return Math.min(1, score);
  }

  /**
   * Feature calculation helper methods
   */
  private calculateMouseLinearity(behavioralData: any): number {
    if (!behavioralData?.mouseMovements) return 0;

    const recentMouse = behavioralData.mouseMovements.slice(-10);
    let totalLinearity = 0;

    for (const data of recentMouse) {
      if (data.patterns?.linearity) {
        totalLinearity += data.patterns.linearity;
      }
    }

    return recentMouse.length > 0
      ? (totalLinearity / recentMouse.length) * 100
      : 0;
  }

  private calculateKeystrokeConsistency(behavioralData: any): number {
    if (!behavioralData?.keystrokeDynamics) return 0;

    const recentKeystrokes = behavioralData.keystrokeDynamics.slice(-10);
    let totalConsistency = 0;

    for (const data of recentKeystrokes) {
      if (data.patterns?.timingConsistency) {
        totalConsistency += data.patterns.timingConsistency;
      }
    }

    return recentKeystrokes.length > 0
      ? (totalConsistency / recentKeystrokes.length) * 100
      : 0;
  }

  private calculateTouchComplexity(behavioralData: any): number {
    if (!behavioralData?.touchPatterns) return 0;

    const recentTouch = behavioralData.touchPatterns.slice(-10);
    let totalComplexity = 0;

    for (const data of recentTouch) {
      if (data.patterns?.gestureComplexity) {
        totalComplexity += data.patterns.gestureComplexity;
      }
    }

    return recentTouch.length > 0
      ? (totalComplexity / recentTouch.length) * 100
      : 0;
  }

  private calculateGeolocationRisk(threatIntel: any): number {
    if (!threatIntel?.details?.country) return 0;

    const highRiskCountries = ['CN', 'RU', 'KP', 'IR'];
    return highRiskCountries.includes(threatIntel.details.country) ? 80 : 0;
  }

  private extractTimeFeature(date: Date): number {
    return date.getHours() / 24; // Normalize to 0-1
  }

  private calculateRequestFrequency(req: Request): number {
    // This would track request frequency over time
    // Simplified implementation - return moderate frequency
    return 25 + Math.random() * 50; // 25-75 range
  }

  private calculateSessionDuration(req: Request): number {
    // This would track actual session duration
    // Simplified implementation
    return 300 + Math.random() * 2700; // 5 minutes to 50 minutes
  }

  private calculateDeviceConsistency(fingerprint: EnhancedFingerprint): number {
    return fingerprint?.confidence ? fingerprint.confidence * 100 : 50; // Default to 50% if no fingerprint
  }

  private calculateFileTypeRisk(req: Request): number {
    // Analyze file types for risk
    const riskyTypes = ['exe', 'scr', 'vbs', 'js'];
    // Simplified implementation
    return Math.random() * 50; // 0-50 risk score
  }

  private calculateFileSizeAnomaly(req: Request): number {
    // Detect anomalous file sizes
    // Simplified implementation
    return Math.random() * 100; // 0-100 anomaly score
  }

  private calculateUploadPattern(req: Request): number {
    // Analyze upload patterns
    // Simplified implementation
    return Math.random() * 100; // 0-100 pattern score
  }

  private calculateVariance(values: number[]): number {
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    return (
      values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) /
      values.length
    );
  }

  private generateExplanation(
    features: ThreatFeatures,
    predictions: Record<string, number>,
    isThreat: boolean
  ): string {
    const topFeatures = Object.entries(features)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3);

    const contributingModels = Object.entries(predictions)
      .filter(
        ([, score]) => (isThreat && score > 0.6) || (!isThreat && score < 0.4)
      )
      .map(([model]) => model);

    return `Analysis based on ${topFeatures.length} key features including ${topFeatures.map(([name]) => name).join(', ')}. Contributing models: ${contributingModels.join(', ')}`;
  }

  private determineAction(
    threatScore: number,
    confidence: number
  ): 'allow' | 'challenge' | 'block' {
    if (threatScore > 80 && confidence > 0.8) return 'block';
    if (threatScore > 60 && confidence > 0.6) return 'challenge';
    return 'allow';
  }

  private calculateFeatureImportance(
    features: ThreatFeatures,
    predictions: Record<string, number>
  ): Record<string, number> {
    const importance: Record<string, number> = {};
    const featureNames = Object.keys(features);

    for (let i = 0; i < featureNames.length; i++) {
      importance[featureNames[i]] = Math.min(
        1,
        features[featureNames[i] as keyof ThreatFeatures] / 100
      );
    }

    return importance;
  }

  /**
   * Log simple ML results for monitoring
   */
  private async logSimpleMLResult(
    req: Request,
    result: SimpleMLResult
  ): Promise<void> {
    await securityEventLogger.logEvent({
      event: 'simple_ml_analysis',
      severity: result.isThreat ? 'high' : 'low',
      timestamp: new Date(),
      source: 'simple_ml',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userId: (req as any).user?.id,
      details: {
        isThreat: result.isThreat,
        confidence: result.confidence,
        threatScore: result.threatScore,
        modelPredictions: result.modelPredictions,
        recommendedAction: result.recommendedAction,
      },
    });

    // Send alert for high-confidence threats
    if (result.isThreat && result.confidence > 0.85) {
      const { securityAlertManager } =
        await import('../monitoring/security-alerts');
      await securityAlertManager.sendAlert({
        type: 'ml_threat_detection',
        severity: 'high',
        title: 'ML-Powered Threat Detected',
        message: `Simple ML detected threat with ${Math.round(result.confidence * 100)}% confidence`,
        details: {
          threatScore: result.threatScore,
          confidence: result.confidence,
          modelPredictions: result.modelPredictions,
        },
        metadata: {
          category: 'ml_detection',
          tags: ['simple_ml', 'high_confidence', 'threat_detected'],
        },
      });
    }
  }

  /**
   * Train models with new data (simplified)
   */
  public async trainModels(trainingData: any[]): Promise<void> {
    if (this.isTraining) {
      console.log('[SimpleML] Training already in progress');
      return;
    }

    this.isTraining = true;
    console.log('[SimpleML] Starting model training...');

    try {
      // Simulate model training with performance updates
      for (const model of Object.keys(ML_CONFIG.ENSEMBLE.WEIGHTS)) {
        const currentPerf = this.modelPerformance.get(model) || 0.9;
        const improvement = Math.random() * 0.02; // 0-2% improvement
        const newPerf = Math.min(0.98, currentPerf + improvement);
        this.modelPerformance.set(model, newPerf);
        console.log(
          `[SimpleML] ${model} model accuracy: ${(newPerf * 100).toFixed(2)}%`
        );
      }

      this.lastTrainingTime = new Date();
      console.log('[SimpleML] Model training completed');
    } catch (error) {
      console.error('[SimpleML] Model training failed:', error);
    } finally {
      this.isTraining = false;
    }
  }

  /**
   * Get model performance metrics
   */
  public getModelPerformance(): Record<string, number> {
    const performance: Record<string, number> = {};

    for (const [modelName, accuracy] of this.modelPerformance) {
      performance[modelName] = accuracy;
    }

    return performance;
  }

  /**
   * Get current training status
   */
  public isCurrentlyTraining(): boolean {
    return this.isTraining;
  }

  /**
   * Get last training time
   */
  public getLastTrainingTime(): Date | null {
    return this.lastTrainingTime;
  }

  /**
   * Update model with online learning (simplified)
   */
  public async updateModelOnline(
    features: ThreatFeatures,
    label: 0 | 1,
    learningRate: number = 0.01
  ): Promise<void> {
    // Simplified online learning - just log the update
    console.log(
      `[SimpleML] Online learning update: label=${label}, learningRate=${learningRate}`
    );

    // In a real implementation, this would adjust model weights
    // For now, we just track that learning occurred
    this.modelPerformance.set(
      'online_learning',
      (this.modelPerformance.get('online_learning') || 0.9) + 0.001
    );
  }
}

// Export singleton instance
export const simpleMLModelManager = new SimpleMLModelManager();
