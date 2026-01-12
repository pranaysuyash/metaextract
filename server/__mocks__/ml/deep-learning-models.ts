// Manual mock for deep learning models to avoid native tfjs bindings in tests

export const deepLearningModelManager = {
  models: new Map<string, any>(),
  detectAdvancedThreat: jest.fn().mockImplementation(async () => ({
    isThreat: false,
    confidence: 0.5,
    threatScore: 0,
    modelPredictions: {},
    explanation: 'safe default: model unavailable in test environment',
    recommendedAction: 'allow',
    featureImportance: {},
    timestamp: new Date(),
  })),
};

export default deepLearningModelManager;
