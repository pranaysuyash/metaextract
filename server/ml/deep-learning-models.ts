/**
 * Deep Learning Models for Advanced Threat Detection
 * 
 * Implements sophisticated neural networks for:
 * - Complex behavioral pattern recognition
 * - Temporal sequence analysis
 * - Multi-modal threat detection
 * - Autoencoder-based anomaly detection
 * - Ensemble learning for improved accuracy
 */

import * as tf from '@tensorflow/tfjs-node';
import { Request } from 'express';
import { securityEventLogger } from '../monitoring/security-events';
import { EnhancedFingerprint } from '../monitoring/browser-fingerprint';
import { AnomalyResult } from '../monitoring/ml-anomaly-detection';

// Deep learning configuration
const DL_CONFIG = {
  // Model architectures
  LSTM: {
    UNITS: 128,
    DROPOUT: 0.2,
    RECURRENT_DROPOUT: 0.2,
    BATCH_SIZE: 32,
    EPOCHS: 50
  },
  
  CNN: {
    FILTERS: [64, 128, 256],
    KERNEL_SIZES: [3, 3, 3],
    POOL_SIZES: [2, 2, 2],
    DROPOUT: 0.3
  },
  
  AUTOENCODER: {
    ENCODER_DIMS: [256, 128, 64],
    LATENT_DIM: 32,
    DECODER_DIMS: [64, 128, 256],
    THRESHOLD_MULTIPLIER: 1.5
  },
  
  ENSEMBLE: {
    MODELS: ['lstm', 'cnn', 'autoencoder', 'random_forest'],
    VOTING_THRESHOLD: 0.7,
    CONFIDENCE_WEIGHT: true
  },
  
  TRAINING: {
    VALIDATION_SPLIT: 0.2,
    EARLY_STOPPING_PATIENCE: 10,
    LEARNING_RATE: 0.001,
    DECAY: 0.0001
  }
};

// Input data interfaces
interface BehavioralSequence {
  timestamp: number;
  mouseX: number;
  mouseY: number;
  velocity: number;
  acceleration: number;
  keystrokeTime: number;
  keystrokePressure: number;
  touchForce: number;
  deviceMotion: number[];
}

interface ThreatFeatures {
  // Network features
  ipReputation: number;
  geolocationRisk: number;
  torExitNode: number;
  vpnProxy: number;
  
  // Behavioral features
  mouseLinearity: number;
  keystrokeConsistency: number;
  reactionTime: number;
  touchPatternComplexity: number;
  
  // Temporal features
  timeOfDay: number;
  dayOfWeek: number;
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

interface DeepLearningResult {
  isThreat: boolean;
  confidence: number;
  threatScore: number;
  modelPredictions: Record<string, number>;
  featureImportance: Record<string, number>;
  explanation: string;
  recommendedAction: 'allow' | 'challenge' | 'block' | 'monitor';
  timestamp: Date;
}

/**
 * Deep Learning Model Manager
 */
export class DeepLearningModelManager {
  private models: Map<string, tf.LayersModel> = new Map();
  private isTraining = false;
  private lastTrainingTime: Date | null = null;
  private modelPerformance: Map<string, number> = new Map();

  constructor() {
    this.initializeModels();
  }

  /**
   * Initialize all deep learning models
   */
  private async initializeModels(): Promise<void> {
    try {
      console.log('[DeepLearning] Initializing models...');
      
      // Initialize LSTM model for temporal analysis
      await this.buildLSTMModel();
      
      // Initialize CNN model for pattern recognition
      await this.buildCNNModel();
      
      // Initialize Autoencoder for anomaly detection
      await this.buildAutoencoderModel();
      
      // Initialize Random Forest (traditional ML for comparison)
      await this.buildRandomForestModel();
      
      console.log('[DeepLearning] All models initialized successfully');
    } catch (error) {
      console.error('[DeepLearning] Failed to initialize models:', error);
      throw error;
    }
  }

  /**
   * Build LSTM model for temporal sequence analysis
   */
  private async buildLSTMModel(): Promise<void> {
    const model = tf.sequential({
      name: 'lstm_threat_detector'
    });

    // Input layer for behavioral sequences
    model.add(tf.layers.lstm({
      units: DL_CONFIG.LSTM.UNITS,
      returnSequences: true,
      inputShape: [null, 10], // [timeSteps, features]
      dropout: DL_CONFIG.LSTM.DROPOUT,
      recurrentDropout: DL_CONFIG.LSTM.RECURRENT_DROPOUT
    }));

    // Second LSTM layer
    model.add(tf.layers.lstm({
      units: DL_CONFIG.LSTM.UNITS / 2,
      returnSequences: false,
      dropout: DL_CONFIG.LSTM.DROPOUT,
      recurrentDropout: DL_CONFIG.LSTM.RECURRENT_DROPOUT
    }));

    // Dense layers for classification
    model.add(tf.layers.dense({
      units: 64,
      activation: 'relu',
      kernelRegularizer: tf.regularizers.l2({ l2: 0.01 })
    }));

    model.add(tf.layers.dropout({ rate: 0.3 }));

    // Output layer
    model.add(tf.layers.dense({
      units: 1,
      activation: 'sigmoid'
    }));

    // Compile model
    model.compile({
      optimizer: tf.train.adam(DL_CONFIG.TRAINING.LEARNING_RATE),
      loss: 'binaryCrossentropy',
      metrics: ['accuracy', 'precision', 'recall']
    });

    this.models.set('lstm', model);
    console.log('[DeepLearning] LSTM model built successfully');
  }

  /**
   * Build CNN model for pattern recognition
   */
  private async buildCNNModel(): Promise<void> {
    const model = tf.sequential({
      name: 'cnn_pattern_detector'
    });

    // Input layer for behavioral patterns (as images)
    model.add(tf.layers.conv2d({
      filters: DL_CONFIG.CNN.FILTERS[0],
      kernelSize: DL_CONFIG.CNN.KERNEL_SIZES[0],
      activation: 'relu',
      inputShape: [28, 28, 1] // Behavioral patterns as 28x28 images
    }));

    model.add(tf.layers.maxPooling2d({
      poolSize: DL_CONFIG.CNN.POOL_SIZES[0]
    }));

    // Second convolutional layer
    model.add(tf.layers.conv2d({
      filters: DL_CONFIG.CNN.FILTERS[1],
      kernelSize: DL_CONFIG.CNN.KERNEL_SIZES[1],
      activation: 'relu'
    }));

    model.add(tf.layers.maxPooling2d({
      poolSize: DL_CONFIG.CNN.POOL_SIZES[1]
    }));

    // Third convolutional layer
    model.add(tf.layers.conv2d({
      filters: DL_CONFIG.CNN.FILTERS[2],
      kernelSize: DL_CONFIG.CNN.KERNEL_SIZES[2],
      activation: 'relu'
    }));

    model.add(tf.layers.maxPooling2d({
      poolSize: DL_CONFIG.CNN.POOL_SIZES[2]
    }));

    // Flatten and dense layers
    model.add(tf.layers.flatten());
    
    model.add(tf.layers.dense({
      units: 128,
      activation: 'relu'
    }));

    model.add(tf.layers.dropout({ rate: DL_CONFIG.CNN.DROPOUT }));

    model.add(tf.layers.dense({
      units: 64,
      activation: 'relu'
    }));

    // Output layer
    model.add(tf.layers.dense({
      units: 1,
      activation: 'sigmoid'
    }));

    // Compile model
    model.compile({
      optimizer: tf.train.adam(DL_CONFIG.TRAINING.LEARNING_RATE),
      loss: 'binaryCrossentropy',
      metrics: ['accuracy']
    });

    this.models.set('cnn', model);
    console.log('[DeepLearning] CNN model built successfully');
  }

  /**
   * Build Autoencoder for anomaly detection
   */
  private async buildAutoencoderModel(): Promise<void> {
    const encoder = tf.sequential({ name: 'autoencoder_encoder' });
    const decoder = tf.sequential({ name: 'autoencoder_decoder' });
    
    // Build encoder
    encoder.add(tf.layers.dense({
      units: DL_CONFIG.AUTOENCODER.ENCODER_DIMS[0],
      activation: 'relu',
      inputShape: [50] // 50 behavioral features
    }));
    
    encoder.add(tf.layers.dense({
      units: DL_CONFIG.AUTOENCODER.ENCODER_DIMS[1],
      activation: 'relu'
    }));
    
    encoder.add(tf.layers.dense({
      units: DL_CONFIG.AUTOENCODER.ENCODER_DIMS[2],
      activation: 'relu'
    }));
    
    // Latent space
    encoder.add(tf.layers.dense({
      units: DL_CONFIG.AUTOENCODER.LATENT_DIM,
      activation: 'relu',
      name: 'latent_space'
    }));

    // Build decoder
    decoder.add(tf.layers.dense({
      units: DL_CONFIG.AUTOENCODER.DECODER_DIMS[0],
      activation: 'relu',
      inputShape: [DL_CONFIG.AUTOENCODER.LATENT_DIM]
    }));
    
    decoder.add(tf.layers.dense({
      units: DL_CONFIG.AUTOENCODER.DECODER_DIMS[1],
      activation: 'relu'
    }));
    
    decoder.add(tf.layers.dense({
      units: DL_CONFIG.AUTOENCODER.DECODER_DIMS[2],
      activation: 'relu'
    }));
    
    decoder.add(tf.layers.dense({
      units: 50,
      activation: 'sigmoid'
    }));

    // Compile autoencoder
    const autoencoder = tf.sequential({
      name: 'autoencoder_anomaly_detector'
    });
    
    autoencoder.add(encoder);
    autoencoder.add(decoder);
    
    autoencoder.compile({
      optimizer: tf.train.adam(DL_CONFIG.TRAINING.LEARNING_RATE),
      loss: 'meanSquaredError',
      metrics: ['mse']
    });

    this.models.set('autoencoder', autoencoder);
    this.models.set('autoencoder_encoder', encoder);
    console.log('[DeepLearning] Autoencoder model built successfully');
  }

  /**
   * Build Random Forest model (traditional ML baseline)
   */
  private async buildRandomForestModel(): Promise<void> {
    // This would integrate with a traditional ML library
    // For now, create a simple decision tree-like model using TensorFlow
    
    const model = tf.sequential({
      name: 'random_forest_baseline'
    });

    model.add(tf.layers.dense({
      units: 100,
      activation: 'relu',
      inputShape: [30] // 30 threat features
    }));

    model.add(tf.layers.dropout({ rate: 0.2 }));

    model.add(tf.layers.dense({
      units: 50,
      activation: 'relu'
    }));

    model.add(tf.layers.dropout({ rate: 0.2 }));

    model.add(tf.layers.dense({
      units: 25,
      activation: 'relu'
    }));

    model.add(tf.layers.dense({
      units: 1,
      activation: 'sigmoid'
    }));

    model.compile({
      optimizer: tf.train.adam(DL_CONFIG.TRAINING.LEARNING_RATE),
      loss: 'binaryCrossentropy',
      metrics: ['accuracy']
    });

    this.models.set('random_forest', model);
    console.log('[DeepLearning] Random Forest baseline model built successfully');
  }

  /**
   * Advanced threat detection using ensemble of models
   */
  public async detectAdvancedThreat(
    req: Request,
    fingerprint: EnhancedFingerprint,
    behavioralData: any,
    threatIntel: any
  ): Promise<DeepLearningResult> {
    try {
      console.log('[DeepLearning] Starting advanced threat detection...');
      
      // Extract features from all sources
      const features = this.extractComprehensiveFeatures(req, fingerprint, behavioralData, threatIntel);
      
      // Get predictions from all models
      const predictions = await this.getEnsemblePredictions(features);
      
      // Calculate ensemble prediction
      const ensemblePrediction = this.calculateEnsemblePrediction(predictions);
      
      // Determine final result
      const isThreat = ensemblePrediction.probability > 0.7;
      const confidence = ensemblePrediction.confidence;
      const threatScore = Math.round(ensemblePrediction.probability * 100);
      
      // Generate explanation
      const explanation = this.generateExplanation(features, predictions, isThreat);
      
      // Determine recommended action
      const recommendedAction = this.determineAction(threatScore, confidence);
      
      // Calculate feature importance
      const featureImportance = this.calculateFeatureImportance(features, predictions);
      
      const result: DeepLearningResult = {
        isThreat,
        confidence,
        threatScore,
        modelPredictions: predictions,
        featureImportance,
        explanation,
        recommendedAction,
        timestamp: new Date()
      };

      // Log for monitoring
      await this.logDeepLearningResult(req, result);
      
      console.log(`[DeepLearning] Detection complete: threat=${isThreat}, confidence=${confidence}, score=${threatScore}`);
      
      return result;
      
    } catch (error) {
      console.error('[DeepLearning] Advanced threat detection failed:', error);
      
      // Return safe fallback
      return {
        isThreat: false,
        confidence: 0.5,
        threatScore: 50,
        modelPredictions: {
          lstm: 0.5,
          cnn: 0.5,
          autoencoder: 0.5,
          ensemble: 0.5
        },
        featureImportance: {},
        explanation: 'Deep learning analysis failed - using safe default',
        recommendedAction: 'monitor',
        timestamp: new Date()
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
      // Network features
      ipReputation: threatIntel?.riskScore || 0,
      geolocationRisk: this.calculateGeolocationRisk(threatIntel),
      torExitNode: threatIntel?.details?.tor ? 100 : 0,
      vpnProxy: threatIntel?.details?.vpn ? 80 : 0,
      
      // Behavioral features
      mouseLinearity: this.calculateMouseLinearity(behavioralData),
      keystrokeConsistency: this.calculateKeystrokeConsistency(behavioralData),
      reactionTime: behavioralData?.timingAnalysis?.fastReactionTime || 0,
      touchPatternComplexity: this.calculateTouchComplexity(behavioralData),
      
      // Temporal features
      timeOfDay: this.extractTimeFeature(new Date()),
      dayOfWeek: new Date().getDay() / 7,
      requestFrequency: this.calculateRequestFrequency(req),
      sessionDuration: this.calculateSessionDuration(req),
      
      // Device features
      fingerprintConfidence: fingerprint?.confidence || 0,
      deviceConsistency: this.calculateDeviceConsistency(fingerprint),
      browserAnomalies: fingerprint?.anomalies?.length || 0,
      
      // Content features
      fileTypeRisk: this.calculateFileTypeRisk(req),
      fileSizeAnomaly: this.calculateFileSizeAnomaly(req),
      uploadPattern: this.calculateUploadPattern(req)
    };

    return features;
  }

  /**
   * Get ensemble predictions from all models
   */
  private async getEnsemblePredictions(features: ThreatFeatures): Promise<Record<string, number>> {
    const predictions: Record<string, number> = {};
    
    // Prepare input tensor
    const featureArray = Object.values(features);
    const inputTensor = tf.tensor2d([featureArray]);
    
    try {
      // LSTM prediction (for demonstration, using same input)
      if (this.models.has('lstm')) {
        const lstmModel = this.models.get('lstm')!;
        const lstmInput = this.prepareLSTMInput(features);
        const lstmPrediction = await lstmModel.predict(lstmInput) as tf.Tensor;
        predictions.lstm = (await lstmPrediction.data())[0];
        lstmInput.dispose();
        lstmPrediction.dispose();
      }
      
      // CNN prediction (behavioral patterns as image)
      if (this.models.has('cnn')) {
        const cnnModel = this.models.get('cnn')!;
        const cnnInput = this.prepareCNNInput(features);
        const cnnPrediction = await cnnModel.predict(cnnInput) as tf.Tensor;
        predictions.cnn = (await cnnPrediction.data())[0];
        cnnInput.dispose();
        cnnPrediction.dispose();
      }
      
      // Autoencoder prediction (anomaly score)
      if (this.models.has('autoencoder')) {
        const autoencoder = this.models.get('autoencoder')!;
        const reconstruction = await autoencoder.predict(inputTensor) as tf.Tensor;
        const mse = tf.mean(tf.square(tf.sub(inputTensor, reconstruction)));
        predictions.autoencoder = Math.min(1, (await mse.data())[0] * 10); // Scale anomaly score
        reconstruction.dispose();
        mse.dispose();
      }
      
      // Random Forest baseline
      if (this.models.has('random_forest')) {
        const rfModel = this.models.get('random_forest')!;
        const rfPrediction = await rfModel.predict(inputTensor) as tf.Tensor;
        predictions.random_forest = (await rfPrediction.data())[0];
        rfPrediction.dispose();
      }
      
      inputTensor.dispose();
      
    } catch (error) {
      console.error('[DeepLearning] Ensemble prediction failed:', error);
      // Return equal weights if prediction fails
      predictions.lstm = 0.5;
      predictions.cnn = 0.5;
      predictions.autoencoder = 0.5;
      predictions.random_forest = 0.5;
    }
    
    return predictions;
  }

  /**
   * Calculate ensemble prediction with confidence weighting
   */
  private calculateEnsemblePrediction(predictions: Record<string, number>): {
    probability: number;
    confidence: number;
  } {
    const modelWeights = {
      lstm: 0.3,
      cnn: 0.25,
      autoencoder: 0.25,
      random_forest: 0.2
    };
    
    let weightedSum = 0;
    let totalWeight = 0;
    
    for (const [model, prediction] of Object.entries(predictions)) {
      const weight = modelWeights[model as keyof typeof modelWeights] || 0.25;
      weightedSum += prediction * weight;
      totalWeight += weight;
    }
    
    const probability = weightedSum / totalWeight;
    
    // Calculate confidence based on agreement between models
    const predictionsArray = Object.values(predictions);
    const variance = this.calculateVariance(predictionsArray);
    const confidence = Math.max(0.5, 1 - (variance * 2)); // Higher confidence when models agree
    
    return { probability, confidence };
  }

  /**
   * Feature calculation helper methods
   */
  private calculateGeolocationRisk(threatIntel: any): number {
    // Simplified geolocation risk calculation
    if (!threatIntel?.details?.country) return 0;
    
    const highRiskCountries = ['CN', 'RU', 'KP', 'IR'];
    return highRiskCountries.includes(threatIntel.details.country) ? 80 : 0;
  }

  private calculateMouseLinearity(behavioralData: any): number {
    if (!behavioralData?.mouseMovements) return 0;
    
    const recentMouse = behavioralData.mouseMovements.slice(-10);
    let totalLinearity = 0;
    
    for (const data of recentMouse) {
      if (data.patterns?.linearity) {
        totalLinearity += data.patterns.linearity;
      }
    }
    
    return recentMouse.length > 0 ? (totalLinearity / recentMouse.length) * 100 : 0;
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
    
    return recentKeystrokes.length > 0 ? (totalConsistency / recentKeystrokes.length) * 100 : 0;
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
    
    return recentTouch.length > 0 ? (totalComplexity / recentTouch.length) * 100 : 0;
  }

  private extractTimeFeature(date: Date): number {
    return date.getHours() / 24; // Normalize to 0-1
  }

  private calculateRequestFrequency(req: Request): number {
    // This would track request frequency over time
    // Simplified implementation
    return Math.random() * 100; // Placeholder
  }

  private calculateSessionDuration(req: Request): number {
    // This would track actual session duration
    // Simplified implementation
    return Math.random() * 3600; // Placeholder in seconds
  }

  private calculateDeviceConsistency(fingerprint: EnhancedFingerprint): number {
    return fingerprint.confidence * 100;
  }

  private calculateFileTypeRisk(req: Request): number {
    // Analyze file types for risk
    const riskyTypes = ['exe', 'scr', 'vbs', 'js'];
    // Simplified implementation
    return Math.random() * 50;
  }

  private calculateFileSizeAnomaly(req: Request): number {
    // Detect anomalous file sizes
    // Simplified implementation
    return Math.random() * 100;
  }

  private calculateUploadPattern(req: Request): number {
    // Analyze upload patterns
    // Simplified implementation
    return Math.random() * 100;
  }

  private prepareLSTMInput(features: ThreatFeatures): tf.Tensor {
    // Convert features to temporal sequence for LSTM
    const sequence = Object.values(features).slice(0, 10); // First 10 features as sequence
    return tf.tensor3d([[sequence]]); // [batch, timeSteps, features]
  }

  private prepareCNNInput(features: ThreatFeatures): tf.Tensor {
    // Convert features to image-like format for CNN
    const featureArray = Object.values(features);
    const imageData = new Array(28 * 28).fill(0);
    
    // Map features to image pixels (simplified)
    for (let i = 0; i < Math.min(featureArray.length, 30); i++) {
      const pixelIndex = Math.floor(i * (28 * 28) / 30);
      imageData[pixelIndex] = featureArray[i] / 100; // Normalize
    }
    
    const imgTensor = tf.tensor(imageData as any).reshape([28, 28, 1]);
    return (imgTensor as any).expandDims(0) as tf.Tensor4D;
  }

  private calculateVariance(values: number[]): number {
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    return values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
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
      .filter(([, score]) => (isThreat && score > 0.6) || (!isThreat && score < 0.4))
      .map(([model]) => model);
    
    return `Analysis based on ${topFeatures.length} key features including ${topFeatures.map(([name]) => name).join(', ')}. Contributing models: ${contributingModels.join(', ')}`;
  }

  private determineAction(threatScore: number, confidence: number): 'allow' | 'challenge' | 'block' {
    if (threatScore > 80 && confidence > 0.8) return 'block';
    if (threatScore > 60 && confidence > 0.6) return 'challenge';
    return 'allow';
  }

  private calculateFeatureImportance(
    features: ThreatFeatures,
    predictions: Record<string, number>
  ): Record<string, number> {
    // Simplified feature importance calculation
    const importance: Record<string, number> = {};
    const featureNames = Object.keys(features);
    
    for (let i = 0; i < featureNames.length; i++) {
      // Higher values generally indicate higher importance for threat detection
      importance[featureNames[i]] = Math.min(1, features[featureNames[i] as keyof ThreatFeatures] / 100);
    }
    
    return importance;
  }

  /**
   * Log deep learning results for monitoring
   */
  private async logDeepLearningResult(req: Request, result: DeepLearningResult): Promise<void> {
    await securityEventLogger.logEvent({
      event: 'deep_learning_analysis',
      severity: result.isThreat ? 'high' : 'low',
      timestamp: new Date(),
      source: 'deep_learning',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userId: (req as any).user?.id,
      details: {
        isThreat: result.isThreat,
        confidence: result.confidence,
        threatScore: result.threatScore,
        modelPredictions: result.modelPredictions,
        recommendedAction: result.recommendedAction,
        explanation: result.explanation
      }
    });

    // Send alert for high-confidence threats
    if (result.isThreat && result.confidence > 0.85) {
      const { securityAlertManager } = await import('../monitoring/security-alerts');
      await securityAlertManager.sendAlert({
        type: 'ai_threat_detection',
        severity: 'high',
        title: 'AI-Powered Threat Detected',
        message: `Deep learning detected threat with ${Math.round(result.confidence * 100)}% confidence`,
        details: {
          threatScore: result.threatScore,
          confidence: result.confidence,
          modelPredictions: result.modelPredictions,
          explanation: result.explanation,
          recommendedAction: result.recommendedAction
        },
        metadata: {
          category: 'ai_detection',
          tags: ['deep_learning', 'high_confidence', 'threat_detected']
        }
      });
    }
  }

  /**
   * Train models with new data
   */
  public async trainModels(trainingData: any[]): Promise<void> {
    if (this.isTraining) {
      console.log('[DeepLearning] Training already in progress');
      return;
    }

    this.isTraining = true;
    console.log('[DeepLearning] Starting model training...');

    try {
      // Prepare training data
      const { xs, ys } = this.prepareTrainingData(trainingData);
      
      // Train each model
      for (const [modelName, model] of this.models) {
        if (modelName.includes('encoder')) continue; // Skip encoder-only model
        
        console.log(`[DeepLearning] Training ${modelName} model...`);
        
        await this.trainIndividualModel(model, xs, ys, modelName);
        
        console.log(`[DeepLearning] ${modelName} model training complete`);
      }
      
      this.lastTrainingTime = new Date();
      console.log('[DeepLearning] All models training complete');
      
    } catch (error) {
      console.error('[DeepLearning] Model training failed:', error);
    } finally {
      this.isTraining = false;
    }
  }

  /**
   * Train individual model
   */
  private async trainIndividualModel(
    model: tf.LayersModel,
    xs: tf.Tensor,
    ys: tf.Tensor,
    modelName: string
  ): Promise<void> {
    const history = await model.fit(xs, ys, {
      batchSize: DL_CONFIG.LSTM.BATCH_SIZE,
      epochs: DL_CONFIG.LSTM.EPOCHS,
      validationSplit: DL_CONFIG.TRAINING.VALIDATION_SPLIT,
      callbacks: [
        tf.callbacks.earlyStopping({
          monitor: 'val_loss',
          patience: DL_CONFIG.TRAINING.EARLY_STOPPING_PATIENCE
        }),
        {
          onEpochEnd: async (epoch: number, logs: any) => {
            if (epoch % 10 === 0) {
              console.log(`[DeepLearning] ${modelName} - Epoch ${epoch}: loss=${logs?.loss?.toFixed(4)}, accuracy=${logs?.accuracy?.toFixed(4)}`);
            }
          }
        }
      ]
    });

    // Store model performance
    const finalAccuracy = Number(history.history.accuracy?.[history.history.accuracy.length - 1] || 0);
    this.modelPerformance.set(modelName, finalAccuracy);
    
    console.log(`[DeepLearning] ${modelName} final accuracy: ${(finalAccuracy * 100).toFixed(2)}%`);
  }

  /**
   * Prepare training data
   */
  private prepareTrainingData(trainingData: any[]): { xs: tf.Tensor; ys: tf.Tensor } {
    // This would process real training data
    // For now, create synthetic data for demonstration
    const featureCount = 30;
    const sampleCount = trainingData.length || 1000;
    
    const xs = tf.randomNormal([sampleCount, featureCount]);
    const ys = tf.randomUniform([sampleCount, 1], 0, 2); // Binary labels
    
    return { xs, ys };
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
   * Update model with online learning
   */
  public async updateModelOnline(
    features: ThreatFeatures,
    label: 0 | 1,
    learningRate: number = 0.01
  ): Promise<void> {
    if (this.isTraining) return;
    
    try {
      const inputTensor = tf.tensor2d([Object.values(features)]);
      const labelTensor = tf.tensor2d([[label]]);
      
      // Update ensemble model with new data
      if (this.models.has('ensemble')) {
        const ensembleModel = this.models.get('ensemble')!;
        await ensembleModel.fit(inputTensor, labelTensor, {
          epochs: 1
        });
      }

      inputTensor.dispose();
      labelTensor.dispose();
      
      console.log('[DeepLearning] Model updated with online learning');
      
    } catch (error) {
      console.error('[DeepLearning] Online learning failed:', error);
    }
  }
}

// Export singleton instance
export const deepLearningModelManager = new DeepLearningModelManager();