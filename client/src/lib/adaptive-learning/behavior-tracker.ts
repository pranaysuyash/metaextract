/**
 * Adaptive Learning System - Tracks user behavior and adapts to expertise level
 */

export interface UserBehavior {
  userId: string;
  pageViews: number;
  featureUses: Record<string, number>;
  timeSpent: Record<string, number>; // in seconds
  errorsEncountered: number;
  helpAccessed: number;
  tutorialCompletions: number;
  lastActive: Date;
  totalSessions: number;
  avgSessionDuration: number;
  preferredFeatures: string[];
}

export interface SkillAssessment {
  userId: string;
  expertiseLevel: 'beginner' | 'intermediate' | 'advanced';
  skillScores: Record<string, number>; // 0-100 for different skills
  assessmentDate: Date;
  confidence: number; // 0-100
}

export interface LearningPath {
  id: string;
  name: string;
  description: string;
  targetLevel: 'beginner' | 'intermediate' | 'advanced';
  steps: LearningStep[];
  estimatedTime: number; // in minutes
  prerequisites: string[];
}

export interface LearningStep {
  id: string;
  title: string;
  description: string;
  type: 'tutorial' | 'practice' | 'assessment';
  contentId: string;
  duration: number; // in minutes
  requiresCompletion: boolean;
}

export interface PathRecommendation {
  userId: string;
  pathId: string;
  reason: string;
  priority: 'low' | 'medium' | 'high';
  recommendedAt: Date;
  completed: boolean;
}

export interface DifficultyAdjustment {
  userId: string;
  featureId: string;
  currentDifficulty: 'simple' | 'detailed' | 'expert';
  adjustmentReason: string;
  lastAdjusted: Date;
}

export class AdaptiveLearningSystem {
  private userBehaviors: Map<string, UserBehavior> = new Map();
  private skillAssessments: Map<string, SkillAssessment> = new Map();
  private learningPaths: Map<string, LearningPath> = new Map();
  private pathRecommendations: Map<string, PathRecommendation[]> = new Map();
  private difficultyAdjustments: Map<string, DifficultyAdjustment[]> = new Map();

  constructor() {
    this.initializeDefaultLearningPaths();
  }

  /**
   * Initialize default learning paths
   */
  private initializeDefaultLearningPaths(): void {
    const defaultPaths: LearningPath[] = [
      {
        id: 'path-beginner-basics',
        name: 'Getting Started with Metadata Extraction',
        description: 'Learn the basics of extracting metadata from files',
        targetLevel: 'beginner',
        estimatedTime: 30,
        prerequisites: [],
        steps: [
          {
            id: 'step-upload',
            title: 'Uploading Files',
            description: 'Learn how to upload files for metadata extraction',
            type: 'tutorial',
            contentId: 'tutorial-upload-basics',
            duration: 10,
            requiresCompletion: true
          },
          {
            id: 'step-view-results',
            title: 'Viewing Results',
            description: 'Understand how to view and interpret extraction results',
            type: 'tutorial',
            contentId: 'tutorial-results-basics',
            duration: 10,
            requiresCompletion: true
          },
          {
            id: 'step-download',
            title: 'Downloading Results',
            description: 'Learn how to download your extracted metadata',
            type: 'tutorial',
            contentId: 'tutorial-download-basics',
            duration: 5,
            requiresCompletion: true
          },
          {
            id: 'step-practice',
            title: 'Practice Session',
            description: 'Try extracting metadata from sample files',
            type: 'practice',
            contentId: 'practice-session-basics',
            duration: 5,
            requiresCompletion: false
          }
        ]
      },
      {
        id: 'path-intermediate-advanced',
        name: 'Advanced Metadata Analysis',
        description: 'Dive deeper into advanced metadata analysis features',
        targetLevel: 'intermediate',
        estimatedTime: 60,
        prerequisites: ['path-beginner-basics'],
        steps: [
          {
            id: 'step-gps',
            title: 'GPS and Location Data',
            description: 'Analyze GPS coordinates and location metadata',
            type: 'tutorial',
            contentId: 'tutorial-gps-analysis',
            duration: 15,
            requiresCompletion: true
          },
          {
            id: 'step-camera',
            title: 'Camera Settings Analysis',
            description: 'Understand camera settings and EXIF data',
            type: 'tutorial',
            contentId: 'tutorial-camera-analysis',
            duration: 15,
            requiresCompletion: true
          },
          {
            id: 'step-forensics',
            title: 'Basic Forensic Analysis',
            description: 'Introduction to forensic metadata analysis',
            type: 'tutorial',
            contentId: 'tutorial-forensics-basics',
            duration: 20,
            requiresCompletion: true
          },
          {
            id: 'step-assessment',
            title: 'Knowledge Check',
            description: 'Test your understanding of advanced concepts',
            type: 'assessment',
            contentId: 'assessment-advanced',
            duration: 10,
            requiresCompletion: true
          }
        ]
      },
      {
        id: 'path-advanced-forensics',
        name: 'Forensic Metadata Analysis',
        description: 'Master forensic analysis techniques',
        targetLevel: 'advanced',
        estimatedTime: 120,
        prerequisites: ['path-intermediate-advanced'],
        steps: [
          {
            id: 'step-steganography',
            title: 'Steganography Detection',
            description: 'Detect hidden data in files',
            type: 'tutorial',
            contentId: 'tutorial-steganography',
            duration: 25,
            requiresCompletion: true
          },
          {
            id: 'step-manipulation',
            title: 'Manipulation Detection',
            description: 'Identify signs of file manipulation',
            type: 'tutorial',
            contentId: 'tutorial-manipulation',
            duration: 25,
            requiresCompletion: true
          },
          {
            id: 'step-ai-detection',
            title: 'AI Generation Detection',
            description: 'Identify AI-generated content',
            type: 'tutorial',
            contentId: 'tutorial-ai-detection',
            duration: 25,
            requiresCompletion: true
          },
          {
            id: 'step-timeline',
            title: 'Timeline Reconstruction',
            description: 'Reconstruct chronological events',
            type: 'tutorial',
            contentId: 'tutorial-timeline',
            duration: 25,
            requiresCompletion: true
          },
          {
            id: 'step-mastery',
            title: 'Mastery Assessment',
            description: 'Comprehensive test of forensic skills',
            type: 'assessment',
            contentId: 'assessment-mastery',
            duration: 20,
            requiresCompletion: true
          }
        ]
      }
    ];

    defaultPaths.forEach(path => {
      this.learningPaths.set(path.id, path);
    });
  }

  /**
   * Track user behavior
   */
  async trackBehavior(userId: string, action: string, metadata?: any): Promise<void> {
    if (!this.userBehaviors.has(userId)) {
      this.userBehaviors.set(userId, {
        userId,
        pageViews: 0,
        featureUses: {},
        timeSpent: {},
        errorsEncountered: 0,
        helpAccessed: 0,
        tutorialCompletions: 0,
        lastActive: new Date(),
        totalSessions: 0,
        avgSessionDuration: 0,
        preferredFeatures: []
      });
    }

    const behavior = this.userBehaviors.get(userId)!;

    // Update behavior based on action
    switch (action) {
      case 'page_view':
        behavior.pageViews++;
        break;
      case 'feature_use':
        const featureId = metadata?.featureId;
        if (featureId) {
          behavior.featureUses[featureId] = (behavior.featureUses[featureId] || 0) + 1;
        }
        break;
      case 'time_spent':
        const pageId = metadata?.pageId;
        const duration = metadata?.duration || 0;
        if (pageId) {
          behavior.timeSpent[pageId] = (behavior.timeSpent[pageId] || 0) + duration;
        }
        break;
      case 'error_encountered':
        behavior.errorsEncountered++;
        break;
      case 'help_accessed':
        behavior.helpAccessed++;
        break;
      case 'tutorial_completed':
        behavior.tutorialCompletions++;
        break;
      case 'session_start':
        behavior.totalSessions++;
        break;
    }

    behavior.lastActive = new Date();

    // Update preferred features based on usage
    const topFeatures = Object.entries(behavior.featureUses)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([feature]) => feature);
    
    behavior.preferredFeatures = topFeatures;
  }

  /**
   * Assess user skill level
   */
  async assessSkillLevel(userId: string): Promise<SkillAssessment> {
    const behavior = this.userBehaviors.get(userId);
    
    if (!behavior) {
      // New user - default to beginner
      const assessment: SkillAssessment = {
        userId,
        expertiseLevel: 'beginner',
        skillScores: {
          'basic_navigation': 20,
          'file_upload': 20,
          'result_interpretation': 20,
          'advanced_features': 10,
          'forensic_analysis': 5
        },
        assessmentDate: new Date(),
        confidence: 70
      };
      
      this.skillAssessments.set(userId, assessment);
      return assessment;
    }

    // Calculate skill scores based on behavior
    const featureUseCount = Object.values(behavior.featureUses).reduce((sum, count) => sum + count, 0);
    const timeSpentTotal = Object.values(behavior.timeSpent).reduce((sum, time) => sum + time, 0);
    
    // Calculate scores for different skills
    const skillScores: Record<string, number> = {};
    
    // Basic navigation score
    skillScores['basic_navigation'] = Math.min(100, 
      20 + (behavior.pageViews * 2) + (behavior.tutorialCompletions * 15)
    );
    
    // File upload score
    skillScores['file_upload'] = Math.min(100,
      20 + (behavior.featureUses['upload'] || 0) * 5
    );
    
    // Result interpretation score
    skillScores['result_interpretation'] = Math.min(100,
      20 + (behavior.featureUses['view_results'] || 0) * 3 + behavior.tutorialCompletions * 10
    );
    
    // Advanced features score
    const advancedFeatures = ['gps_analysis', 'camera_settings', 'forensic_tools'];
    const advancedUse = advancedFeatures.reduce((sum, feature) => 
      sum + (behavior.featureUses[feature] || 0), 0);
    skillScores['advanced_features'] = Math.min(100, advancedUse * 8);
    
    // Forensic analysis score
    const forensicFeatures = ['steganography', 'manipulation_detection', 'ai_detection'];
    const forensicUse = forensicFeatures.reduce((sum, feature) => 
      sum + (behavior.featureUses[feature] || 0), 0);
    skillScores['forensic_analysis'] = Math.min(100, forensicUse * 12);
    
    // Determine expertise level based on average score
    const avgScore = Object.values(skillScores).reduce((sum, score) => sum + score, 0) / 
                    Object.keys(skillScores).length;
    
    let expertiseLevel: 'beginner' | 'intermediate' | 'advanced' = 'beginner';
    if (avgScore >= 70) {
      expertiseLevel = 'advanced';
    } else if (avgScore >= 40) {
      expertiseLevel = 'intermediate';
    }
    
    // Calculate confidence based on data amount
    const confidence = Math.min(100, 
      30 + (featureUseCount * 2) + (behavior.tutorialCompletions * 10)
    );

    const assessment: SkillAssessment = {
      userId,
      expertiseLevel,
      skillScores,
      assessmentDate: new Date(),
      confidence
    };

    this.skillAssessments.set(userId, assessment);
    return assessment;
  }

  /**
   * Get personalized learning path for user
   */
  async getPersonalizedPath(userId: string): Promise<LearningPath | null> {
    const assessment = await this.assessSkillLevel(userId);
    
    // Find the most appropriate path based on skill level
    const paths = Array.from(this.learningPaths.values());
    
    // Filter paths by target level and prerequisites
    const availablePaths = paths.filter(path => {
      // Check if target level matches or is appropriate
      const levelMatch = 
        (assessment.expertiseLevel === 'beginner' && path.targetLevel === 'beginner') ||
        (assessment.expertiseLevel === 'intermediate' && 
          (path.targetLevel === 'beginner' || path.targetLevel === 'intermediate')) ||
        (assessment.expertiseLevel === 'advanced' && 
          (path.targetLevel === 'beginner' || path.targetLevel === 'intermediate' || path.targetLevel === 'advanced'));
      
      // Check prerequisites
      const hasPrerequisites = path.prerequisites.every(prereq => {
        const recommendations = this.pathRecommendations.get(userId) || [];
        return recommendations.some(r => r.pathId === prereq && r.completed);
      });
      
      return levelMatch && hasPrerequisites;
    });
    
    // If no paths match, suggest the next logical path
    if (availablePaths.length === 0) {
      if (assessment.expertiseLevel === 'beginner') {
        return this.learningPaths.get('path-beginner-basics') || null;
      } else if (assessment.expertiseLevel === 'intermediate') {
        return this.learningPaths.get('path-intermediate-advanced') || null;
      } else {
        return this.learningPaths.get('path-advanced-forensics') || null;
      }
    }
    
    // Return the most appropriate path
    return availablePaths[0];
  }

  /**
   * Recommend learning paths to user
   */
  async recommendPaths(userId: string): Promise<PathRecommendation[]> {
    const assessment = await this.assessSkillLevel(userId);
    const allPaths = Array.from(this.learningPaths.values());
    const userRecommendations = this.pathRecommendations.get(userId) || [];
    
    const recommendations: PathRecommendation[] = [];
    
    for (const path of allPaths) {
      // Skip if already completed
      if (userRecommendations.some(r => r.pathId === path.id && r.completed)) {
        continue;
      }
      
      // Determine priority based on skill gaps
      let priority: 'low' | 'medium' | 'high' = 'low';
      let reason = '';
      
      if (path.targetLevel === assessment.expertiseLevel) {
        priority = 'high';
        reason = `Matches your current skill level (${assessment.expertiseLevel})`;
      } else if (
        path.prerequisites.length === 0 || 
        path.prerequisites.every(prereq => 
          userRecommendations.some(r => r.pathId === prereq && r.completed)
        )
      ) {
        priority = 'medium';
        reason = 'Builds on your existing knowledge';
      } else {
        priority = 'low';
        reason = 'Prerequisites not yet completed';
      }
      
      recommendations.push({
        userId,
        pathId: path.id,
        reason,
        priority,
        recommendedAt: new Date(),
        completed: userRecommendations.some(r => r.pathId === path.id && r.completed)
      });
    }
    
    // Sort by priority
    recommendations.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
    
    this.pathRecommendations.set(userId, recommendations);
    return recommendations;
  }

  /**
   * Mark a learning path as completed
   */
  async completePath(userId: string, pathId: string): Promise<boolean> {
    const recommendations = this.pathRecommendations.get(userId) || [];
    const pathIndex = recommendations.findIndex(r => r.pathId === pathId);
    
    if (pathIndex === -1) {
      return false;
    }
    
    recommendations[pathIndex].completed = true;
    recommendations[pathIndex].recommendedAt = new Date();
    
    this.pathRecommendations.set(userId, recommendations);
    
    // Update skill assessment after completing a path
    await this.assessSkillLevel(userId);
    
    return true;
  }

  /**
   * Adjust content difficulty for user
   */
  async adjustDifficulty(userId: string, featureId: string): Promise<DifficultyAdjustment> {
    const assessment = await this.assessSkillLevel(userId);
    
    // Determine appropriate difficulty based on skill level
    let difficulty: 'simple' | 'detailed' | 'expert';
    let reason = '';
    
    if (assessment.expertiseLevel === 'beginner') {
      difficulty = 'simple';
      reason = 'Based on beginner skill level';
    } else if (assessment.expertiseLevel === 'intermediate') {
      difficulty = 'detailed';
      reason = 'Based on intermediate skill level';
    } else {
      difficulty = 'expert';
      reason = 'Based on advanced skill level';
    }
    
    // Check if we already have an adjustment for this feature
    let adjustments = this.difficultyAdjustments.get(userId) || [];
    const existingIndex = adjustments.findIndex(adj => adj.featureId === featureId);
    
    if (existingIndex !== -1) {
      // Update existing adjustment
      adjustments[existingIndex].currentDifficulty = difficulty;
      adjustments[existingIndex].adjustmentReason = reason;
      adjustments[existingIndex].lastAdjusted = new Date();
    } else {
      // Create new adjustment
      const newAdjustment: DifficultyAdjustment = {
        userId,
        featureId,
        currentDifficulty: difficulty,
        adjustmentReason: reason,
        lastAdjusted: new Date()
      };
      adjustments.push(newAdjustment);
    }
    
    this.difficultyAdjustments.set(userId, adjustments);
    
    return {
      userId,
      featureId,
      currentDifficulty: difficulty,
      adjustmentReason: reason,
      lastAdjusted: new Date()
    };
  }

  /**
   * Get current difficulty setting for a feature
   */
  async getDifficulty(userId: string, featureId: string): Promise<'simple' | 'detailed' | 'expert'> {
    const adjustments = this.difficultyAdjustments.get(userId) || [];
    const adjustment = adjustments.find(adj => adj.featureId === featureId);
    
    if (adjustment) {
      return adjustment.currentDifficulty;
    }
    
    // If no specific adjustment, determine based on skill level
    const assessment = await this.assessSkillLevel(userId);
    
    if (assessment.expertiseLevel === 'beginner') {
      return 'simple';
    } else if (assessment.expertiseLevel === 'intermediate') {
      return 'detailed';
    } else {
      return 'expert';
    }
  }

  /**
   * Get user behavior analytics
   */
  async getUserAnalytics(userId: string) {
    const behavior = this.userBehaviors.get(userId);
    const assessment = this.skillAssessments.get(userId);
    
    if (!behavior) {
      return null;
    }
    
    // Calculate engagement metrics
    const totalFeatureUses = Object.values(behavior.featureUses).reduce((sum, count) => sum + count, 0);
    const totalTimeSpent = Object.values(behavior.timeSpent).reduce((sum, time) => sum + time, 0);
    
    return {
      userId,
      engagement: {
        pageViews: behavior.pageViews,
        featureUses: totalFeatureUses,
        timeSpent: totalTimeSpent,
        errors: behavior.errorsEncountered,
        helpAccessed: behavior.helpAccessed,
        tutorialsCompleted: behavior.tutorialCompletions
      },
      skillLevel: assessment?.expertiseLevel || 'beginner',
      preferredFeatures: behavior.preferredFeatures,
      lastActive: behavior.lastActive,
      avgTimePerFeature: totalFeatureUses > 0 ? totalTimeSpent / totalFeatureUses : 0
    };
  }

  /**
   * Get all learning paths
   */
  getAllLearningPaths(): LearningPath[] {
    return Array.from(this.learningPaths.values());
  }

  /**
   * Get a specific learning path
   */
  getLearningPath(pathId: string): LearningPath | undefined {
    return this.learningPaths.get(pathId);
  }

  /**
   * Get user's learning progress
   */
  async getUserProgress(userId: string) {
    const recommendations = this.pathRecommendations.get(userId) || [];
    const assessment = await this.assessSkillLevel(userId);
    
    return {
      skillLevel: assessment.expertiseLevel,
      completedPaths: recommendations.filter(r => r.completed).length,
      totalPaths: recommendations.length,
      recommendedPaths: recommendations,
      skillScores: assessment.skillScores
    };
  }
}

// Singleton instance
export const adaptiveLearningSystem = new AdaptiveLearningSystem();

export default adaptiveLearningSystem;