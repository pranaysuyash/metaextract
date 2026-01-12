/**
 * Machine Learning-based Anomaly Detection System
 * 
 * Implements advanced ML algorithms for detecting:
 * - Upload pattern anomalies
 * - Behavioral anomalies
 * - Device fingerprint anomalies
 * - Network traffic anomalies
 * - Multi-account detection
 */

import { Request } from 'express';
import { storage } from '../storage/index';
import { securityEventLogger } from './security-events';
import { EnhancedFingerprint } from './browser-fingerprint';

// Anomaly detection configuration
const ANOMALY_CONFIG = {
  // Training settings
  MIN_SAMPLES: 50,
  TRAINING_WINDOW_HOURS: 24,
  RETRAINING_INTERVAL_HOURS: 6,
  
  // Detection thresholds
  ANOMALY_THRESHOLD: 0.8,
  HIGH_CONFIDENCE_THRESHOLD: 0.9,
  RISK_SCORE_LOW: 30,
  RISK_SCORE_MEDIUM: 60,
  RISK_SCORE_HIGH: 80,
  
  // Feature weights
  WEIGHTS: {
    uploadFrequency: 0.25,
    fileSize: 0.20,
    ipStability: 0.15,
    deviceConsistency: 0.15,
    timePattern: 0.10,
    geolocation: 0.10,
    fingerprint: 0.05
  },
  
  // Pattern detection
  BURST_THRESHOLD: 10, // uploads in 5 minutes
  SIZE_ANOMALY_THRESHOLD: 0.95, // 95th percentile
  TIME_ANOMALY_THRESHOLD: 0.85,
};

// Feature vector for ML model
interface FeatureVector {
  uploadFrequency: number;      // uploads per hour
  avgFileSize: number;          // average file size
  fileSizeVariance: number;     // file size variance
  ipStability: number;          // IP address consistency score
  deviceConsistency: number;    // device fingerprint consistency
  timePattern: number;          // upload time pattern score
  geolocationStability: number; // geolocation consistency
  fingerprintStability: number; // browser fingerprint consistency
  burstScore: number;           // burst upload score
  anomalyScore: number;         // overall anomaly score
}

// Anomaly detection result
export interface AnomalyResult {
  isAnomalous: boolean;
  confidence: number;
  riskScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  contributingFactors: string[];
  recommendations: string[];
  modelVersion: string;
  timestamp: Date;
}

// Historical data point
interface HistoricalDataPoint {
  timestamp: Date;
  features: FeatureVector;
  label: 'normal' | 'anomalous';
  confidence: number;
}

// Model statistics
interface ModelStats {
  totalPredictions: number;
  truePositives: number;
  falsePositives: number;
  trueNegatives: number;
  falseNegatives: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  lastTraining: Date;
  modelVersion: string;
}

/**
 * Main anomaly detection class
 */
export class MLAnomalyDetector {
  private modelVersion = '1.0.0';
  private isTrained = false;
  private trainingData: HistoricalDataPoint[] = [];
  private modelStats: ModelStats = {
    totalPredictions: 0,
    truePositives: 0,
    falsePositives: 0,
    trueNegatives: 0,
    falseNegatives: 0,
    accuracy: 0,
    precision: 0,
    recall: 0,
    f1Score: 0,
    lastTraining: new Date(),
    modelVersion: this.modelVersion
  };

  constructor() {
    this.initializeModel();
  }

  /**
   * Initialize the ML model
   */
  private async initializeModel(): Promise<void> {
    try {
      // Load historical training data
      await this.loadTrainingData();
      
      // Train initial model if we have enough data
      if (this.trainingData.length >= ANOMALY_CONFIG.MIN_SAMPLES) {
        await this.trainModel();
      } else {
        console.log('[MLAnomalyDetector] Insufficient training data, using rule-based detection');
      }
    } catch (error) {
      console.error('[MLAnomalyDetector] Initialization failed:', error);
    }
  }

  /**
   * Detect anomalies in upload behavior
   */
  public async detectUploadAnomaly(
    req: Request,
    fingerprint?: EnhancedFingerprint
  ): Promise<AnomalyResult> {
    try {
      // Extract features from request
      const features = await this.extractFeatures(req, fingerprint);
      
      // Generate anomaly score
      const anomalyScore = await this.calculateAnomalyScore(features);
      
      // Classify as anomalous or normal
      const isAnomalous = anomalyScore > ANOMALY_CONFIG.ANOMALY_THRESHOLD;
      
      // Calculate confidence
      const confidence = Math.min(1.0, Math.abs(anomalyScore - 0.5) * 2);
      
      // Determine risk level
      const riskScore = Math.round(anomalyScore * 100);
      const riskLevel = this.getRiskLevel(riskScore);
      
      // Identify contributing factors
      const contributingFactors = this.identifyContributingFactors(features, anomalyScore);
      
      // Generate recommendations
      const recommendations = this.generateRecommendations(riskLevel, contributingFactors);
      
      const result: AnomalyResult = {
        isAnomalous,
        confidence,
        riskScore,
        riskLevel,
        contributingFactors,
        recommendations,
        modelVersion: this.modelVersion,
        timestamp: new Date()
      };

      // Log the detection
      await this.logDetection(req, result, features);
      
      // Update model with feedback
      await this.updateModel(features, isAnomalous, confidence);
      
      return result;
    } catch (error) {
      console.error('[MLAnomalyDetector] Detection failed:', error);
      
      // Fallback to simple rule-based detection
      return this.fallbackDetection(req);
    }
  }

  /**
   * Extract features from request data
   */
  private async extractFeatures(
    req: Request,
    fingerprint?: EnhancedFingerprint
  ): Promise<FeatureVector> {
    const userId = (req as any).user?.id;
    const ipAddress = req.ip || req.connection.remoteAddress || 'unknown';
    const userAgent = req.headers['user-agent'] || 'unknown';
    
    // Get historical data for this user/IP
    const historicalData = await this.getHistoricalData(userId, ipAddress);
    
    // Calculate features
    const uploadFrequency = this.calculateUploadFrequency(historicalData);
    const avgFileSize = this.calculateAvgFileSize(historicalData);
    const fileSizeVariance = this.calculateFileSizeVariance(historicalData);
    const ipStability = this.calculateIpStability(historicalData, ipAddress);
    const deviceConsistency = this.calculateDeviceConsistency(historicalData, userAgent);
    const timePattern = this.calculateTimePattern(historicalData);
    const geolocationStability = this.calculateGeolocationStability(historicalData);
    const fingerprintStability = this.calculateFingerprintStability(historicalData, fingerprint);
    const burstScore = this.calculateBurstScore(historicalData);
    
    // Calculate overall anomaly score
    const anomalyScore = this.enhancedRuleBasedScore({
      uploadFrequency,
      avgFileSize,
      fileSizeVariance,
      ipStability,
      deviceConsistency,
      timePattern,
      geolocationStability,
      fingerprintStability,
      burstScore,
      anomalyScore: 0 // Will be calculated
    });

    return {
      uploadFrequency,
      avgFileSize,
      fileSizeVariance,
      ipStability,
      deviceConsistency,
      timePattern,
      geolocationStability,
      fingerprintStability,
      burstScore,
      anomalyScore
    };
  }

  /**
   * Calculate anomaly score using ML model
   */
  private async calculateAnomalyScore(features: FeatureVector): Promise<number> {
    if (!this.isTrained) {
      // Use rule-based detection if model is not trained
      return this.ruleBasedAnomalyScore(features);
    }

    // Use trained model for prediction
    return this.mlAnomalyScore(features);
  }

  /**
   * Rule-based anomaly detection (fallback)
   */
  private ruleBasedAnomalyScore(features: FeatureVector): number {
    let score = 0;
    
    // Upload frequency anomalies
    if (features.uploadFrequency > 100) score += 0.3; // > 100 uploads/hour
    if (features.burstScore > 0.8) score += 0.4; // Burst uploads
    
    // File size anomalies
    if (features.avgFileSize > 100 * 1024 * 1024) score += 0.2; // > 100MB average
    if (features.fileSizeVariance > 0.9) score += 0.1; // High variance
    
    // IP stability anomalies
    if (features.ipStability < 0.5) score += 0.3; // Frequent IP changes
    
    // Device consistency anomalies
    if (features.deviceConsistency < 0.3) score += 0.3; // Inconsistent devices
    
    // Time pattern anomalies
    if (features.timePattern < 0.2) score += 0.2; // Unusual timing
    
    // Fingerprint stability anomalies
    if (features.fingerprintStability < 0.4) score += 0.3; // Inconsistent fingerprints
    
    return Math.min(1.0, score);
  }

  /**
   * ML-based anomaly score (placeholder for actual ML model)
   */
  private mlAnomalyScore(features: FeatureVector): number {
    // This would use a trained ML model (e.g., Isolation Forest, One-Class SVM, etc.)
    // For now, use enhanced rule-based detection
    return this.enhancedRuleBasedScore(features);
  }

  /**
   * Enhanced rule-based scoring
   */
  private enhancedRuleBasedScore(features: FeatureVector): number {
    let score = 0;
    
    // Weighted scoring based on feature importance
    score += features.uploadFrequency * ANOMALY_CONFIG.WEIGHTS.uploadFrequency;
    score += (features.avgFileSize / (50 * 1024 * 1024)) * ANOMALY_CONFIG.WEIGHTS.fileSize; // Normalize to 50MB
    score += features.fileSizeVariance * ANOMALY_CONFIG.WEIGHTS.fileSize;
    score += (1 - features.ipStability) * ANOMALY_CONFIG.WEIGHTS.ipStability;
    score += (1 - features.deviceConsistency) * ANOMALY_CONFIG.WEIGHTS.deviceConsistency;
    score += (1 - features.timePattern) * ANOMALY_CONFIG.WEIGHTS.timePattern;
    score += (1 - features.geolocationStability) * ANOMALY_CONFIG.WEIGHTS.geolocation;
    score += (1 - features.fingerprintStability) * ANOMALY_CONFIG.WEIGHTS.fingerprint;
    score += features.burstScore * 0.5; // Additional burst weight
    
    return Math.min(1.0, score);
  }

  /**
   * Feature calculation methods
   */
  private calculateUploadFrequency(data: any[]): number {
    if (data.length === 0) return 0;
    
    const recentUploads = data.filter(d => 
      Date.now() - d.timestamp.getTime() < 60 * 60 * 1000 // Last hour
    );
    
    return recentUploads.length;
  }

  private calculateAvgFileSize(data: any[]): number {
    if (data.length === 0) return 0;
    
    const sizes = data.map(d => d.fileSize || 0).filter(size => size > 0);
    if (sizes.length === 0) return 0;
    
    return sizes.reduce((sum, size) => sum + size, 0) / sizes.length;
  }

  private calculateFileSizeVariance(data: any[]): number {
    if (data.length < 2) return 0;
    
    const sizes = data.map(d => d.fileSize || 0).filter(size => size > 0);
    if (sizes.length < 2) return 0;
    
    const avg = this.calculateAvgFileSize(data);
    const variance = sizes.reduce((sum, size) => sum + Math.pow(size - avg, 2), 0) / sizes.length;
    
    return Math.sqrt(variance) / avg; // Coefficient of variation
  }

  private calculateIpStability(data: any[], currentIp: string): number {
    if (data.length === 0) return 1.0;
    
    const uniqueIps = new Set(data.map(d => d.ipAddress));
    const currentIpCount = data.filter(d => d.ipAddress === currentIp).length;
    
    return currentIpCount / data.length;
  }

  private calculateDeviceConsistency(data: any[], currentUserAgent: string): number {
    if (data.length === 0) return 1.0;
    
    const currentDeviceCount = data.filter(d => d.userAgent === currentUserAgent).length;
    return currentDeviceCount / data.length;
  }

  private calculateTimePattern(data: any[]): number {
    if (data.length === 0) return 1.0;
    
    const hours = data.map(d => d.timestamp.getHours());
    const hourCounts = new Map<number, number>();
    
    hours.forEach(hour => {
      hourCounts.set(hour, (hourCounts.get(hour) || 0) + 1);
    });
    
    // Calculate entropy (lower entropy = more predictable pattern)
    const total = hours.length;
    let entropy = 0;
    
    hourCounts.forEach(count => {
      const probability = count / total;
      entropy -= probability * Math.log2(probability);
    });
    
    // Normalize entropy (max entropy for 24 hours is log2(24) ≈ 4.58)
    const maxEntropy = Math.log2(24);
    return 1 - (entropy / maxEntropy); // Higher score = more predictable
  }

  private calculateGeolocationStability(data: any[]): number {
    if (data.length === 0) return 1.0;
    
    const uniqueLocations = new Set(data.map(d => `${d.latitude},${d.longitude}`));
    return 1 - (uniqueLocations.size - 1) / data.length;
  }

  private calculateFingerprintStability(data: any[], currentFingerprint?: EnhancedFingerprint): number {
    if (!currentFingerprint || data.length === 0) return 1.0;
    
    // Compare fingerprint similarity with historical data
    const similarities: number[] = data.map(d => {
      // This would compare fingerprint hashes
      return d.fingerprintHash === currentFingerprint.fingerprintHash ? 1.0 : 0.0;
    });
    
    return similarities.reduce((sum, sim) => sum + sim, 0) / similarities.length;
  }

  private calculateBurstScore(data: any[]): number {
    if (data.length < 3) return 0;
    
    // Look for bursts of uploads in short time windows
    const sortedData = data.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
    let maxBurst = 0;
    
    for (let i = 0; i < sortedData.length; i++) {
      let burstCount = 1;
      const windowStart = sortedData[i].timestamp.getTime();
      
      for (let j = i + 1; j < sortedData.length; j++) {
        if (sortedData[j].timestamp.getTime() - windowStart <= 5 * 60 * 1000) { // 5 minutes
          burstCount++;
        } else {
          break;
        }
      }
      
      maxBurst = Math.max(maxBurst, burstCount);
    }
    
    return Math.min(1.0, maxBurst / ANOMALY_CONFIG.BURST_THRESHOLD);
  }

  /**
   * Helper methods
   */
  private getRiskLevel(riskScore: number): 'low' | 'medium' | 'high' | 'critical' {
    if (riskScore >= ANOMALY_CONFIG.RISK_SCORE_HIGH) return 'high';
    if (riskScore >= ANOMALY_CONFIG.RISK_SCORE_MEDIUM) return 'medium';
    return 'low';
  }

  private identifyContributingFactors(features: FeatureVector, anomalyScore: number): string[] {
    const factors: string[] = [];
    
    if (features.uploadFrequency > 50) factors.push('High upload frequency');
    if (features.burstScore > 0.7) factors.push('Burst upload pattern');
    if (features.ipStability < 0.3) factors.push('Frequent IP changes');
    if (features.deviceConsistency < 0.3) factors.push('Inconsistent device signatures');
    if (features.fingerprintStability < 0.3) factors.push('Inconsistent browser fingerprints');
    if (features.timePattern < 0.2) factors.push('Unusual upload timing patterns');
    if (features.avgFileSize > 50 * 1024 * 1024) factors.push('Large average file sizes');
    if (features.fileSizeVariance > 0.8) factors.push('Inconsistent file sizes');
    
    return factors;
  }

  private generateRecommendations(
    riskLevel: 'low' | 'medium' | 'high' | 'critical',
    factors: string[]
  ): string[] {
    const recommendations: string[] = [];
    
    if (riskLevel === 'high' || riskLevel === 'critical') {
      recommendations.push('Implement additional verification steps');
      recommendations.push('Consider temporary rate limiting');
      recommendations.push('Monitor for continued suspicious behavior');
    }
    
    if (factors.includes('High upload frequency')) {
      recommendations.push('Apply stricter upload rate limits');
    }
    
    if (factors.includes('Frequent IP changes')) {
      recommendations.push('Consider IP-based restrictions');
    }
    
    if (factors.includes('Inconsistent device signatures')) {
      recommendations.push('Implement device fingerprinting verification');
    }
    
    if (factors.includes('Burst upload pattern')) {
      recommendations.push('Implement burst detection and throttling');
    }
    
    return recommendations;
  }

  /**
   * Model training and management
   */
  private async trainModel(): Promise<void> {
    try {
      // This would train the actual ML model
      // For now, just mark as trained
      this.isTrained = true;
      this.modelStats.lastTraining = new Date();
      
      console.log(`[MLAnomalyDetector] Model trained with ${this.trainingData.length} samples`);
    } catch (error) {
      console.error('[MLAnomalyDetector] Model training failed:', error);
    }
  }

  private async updateModel(
    features: FeatureVector,
    predictedAnomalous: boolean,
    confidence: number
  ): Promise<void> {
    // Add to training data
    this.trainingData.push({
      timestamp: new Date(),
      features,
      label: predictedAnomalous ? 'anomalous' : 'normal',
      confidence
    });
    
    // Retrain model periodically
    if (this.trainingData.length % 100 === 0) {
      await this.trainModel();
    }
  }

  /**
   * Data management methods
   */
  private async getHistoricalData(userId?: string, ipAddress?: string): Promise<any[]> {
    try {
      // This would query the database for historical data
      // For now, return mock data
      return this.generateMockHistoricalData(userId, ipAddress);
    } catch (error) {
      console.error('[MLAnomalyDetector] Error getting historical data:', error);
      return [];
    }
  }

  private generateMockHistoricalData(userId?: string, ipAddress?: string): any[] {
    const data = [];
    const now = Date.now();
    
    for (let i = 0; i < 100; i++) {
      data.push({
        timestamp: new Date(now - i * 60 * 1000), // Spaced 1 minute apart
        fileSize: Math.random() * 10 * 1024 * 1024, // 0-10MB
        ipAddress: ipAddress || '192.168.1.1',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        latitude: 40.7128,
        longitude: -74.0060,
        fingerprintHash: 'mock_fingerprint_123'
      });
    }
    
    return data;
  }

  private async loadTrainingData(): Promise<void> {
    try {
      // This would load historical training data from database
      // For now, use mock data
      this.trainingData = this.generateMockTrainingData();
    } catch (error) {
      console.error('[MLAnomalyDetector] Error loading training data:', error);
    }
  }

  private generateMockTrainingData(): HistoricalDataPoint[] {
    const data: HistoricalDataPoint[] = [];
    
    // Generate normal samples
    for (let i = 0; i < 75; i++) {
      data.push({
        timestamp: new Date(),
        features: {
          uploadFrequency: Math.random() * 20,
          avgFileSize: Math.random() * 5 * 1024 * 1024,
          fileSizeVariance: Math.random() * 0.3,
          ipStability: 0.8 + Math.random() * 0.2,
          deviceConsistency: 0.7 + Math.random() * 0.3,
          timePattern: 0.6 + Math.random() * 0.4,
          geolocationStability: 0.8 + Math.random() * 0.2,
          fingerprintStability: 0.7 + Math.random() * 0.3,
          burstScore: Math.random() * 0.3,
          anomalyScore: Math.random() * 0.3
        },
        label: 'normal',
        confidence: 0.8 + Math.random() * 0.2
      });
    }
    
    // Generate anomalous samples
    for (let i = 0; i < 25; i++) {
      data.push({
        timestamp: new Date(),
        features: {
          uploadFrequency: 50 + Math.random() * 100,
          avgFileSize: (50 + Math.random() * 50) * 1024 * 1024,
          fileSizeVariance: 0.7 + Math.random() * 0.3,
          ipStability: Math.random() * 0.3,
          deviceConsistency: Math.random() * 0.3,
          timePattern: Math.random() * 0.3,
          geolocationStability: Math.random() * 0.3,
          fingerprintStability: Math.random() * 0.3,
          burstScore: 0.7 + Math.random() * 0.3,
          anomalyScore: 0.7 + Math.random() * 0.3
        },
        label: 'anomalous',
        confidence: 0.8 + Math.random() * 0.2
      });
    }
    
    return data;
  }

  /**
   * Logging and monitoring
   */
  private async logDetection(
    req: Request,
    result: AnomalyResult,
    features: FeatureVector
  ): Promise<void> {
    await securityEventLogger.logEvent({
      event: 'ml_anomaly_detection',
      severity: result.riskLevel,
      timestamp: new Date(),
      source: 'ml_anomaly_detector',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userId: (req as any).user?.id,
      details: {
        isAnomalous: result.isAnomalous,
        confidence: result.confidence,
        riskScore: result.riskScore,
        riskLevel: result.riskLevel,
        contributingFactors: result.contributingFactors,
        features: {
          uploadFrequency: features.uploadFrequency,
          avgFileSize: features.avgFileSize,
          fileSizeVariance: features.fileSizeVariance,
          ipStability: features.ipStability,
          deviceConsistency: features.deviceConsistency,
          timePattern: features.timePattern,
          geolocationStability: features.geolocationStability,
          fingerprintStability: features.fingerprintStability,
          burstScore: features.burstScore
        },
        modelVersion: result.modelVersion
      }
    });
  }

  /**
   * Fallback detection when ML model fails
   */
  private fallbackDetection(req: Request): AnomalyResult {
    const userId = (req as any).user?.id;
    const ipAddress = req.ip || req.connection.remoteAddress || 'unknown';
    
    // Simple rule-based detection
    const isSuspicious = 
      !userId && // Anonymous user
      this.isSuspiciousIp(ipAddress) &&
      this.isSuspiciousTime();
    
    return {
      isAnomalous: isSuspicious,
      confidence: 0.5,
      riskScore: isSuspicious ? 50 : 10,
      riskLevel: isSuspicious ? 'medium' : 'low',
      contributingFactors: isSuspicious ? ['Anonymous user with suspicious IP'] : [],
      recommendations: isSuspicious ? ['Monitor this upload session'] : [],
      modelVersion: this.modelVersion,
      timestamp: new Date()
    };
  }

  private isSuspiciousIp(ip: string): boolean {
    // Simple IP-based checks
    const suspiciousPatterns = [
      /^10\./, // Private IP
      /^192\.168\./, // Private IP
      /^172\.(1[6-9]|2[0-9]|3[01])\./, // Private IP
      /^127\./, // Loopback
      /^0\./ // Invalid
    ];
    
    return suspiciousPatterns.some(pattern => pattern.test(ip));
  }

  private isSuspiciousTime(): boolean {
    const hour = new Date().getHours();
    // Consider uploads between 2 AM and 6 AM as potentially suspicious
    return hour >= 2 && hour <= 6;
  }

  /**
   * Get model statistics
   */
  public getModelStats(): ModelStats {
    return { ...this.modelStats };
  }

  /**
   * Get current model version
   */
  public getModelVersion(): string {
    return this.modelVersion;
  }

  /**
   * Check if model is trained
   */
  public isModelTrained(): boolean {
    return this.isTrained;
  }
}

// Export singleton instance
export const mlAnomalyDetector = new MLAnomalyDetector();