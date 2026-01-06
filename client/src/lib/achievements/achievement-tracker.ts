/**
 * Achievement System - Badge system for onboarding and engagement
 */

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  points: number;
  category: 'onboarding' | 'exploration' | 'expertise' | 'engagement' | 'collaboration';
  requirements: AchievementRequirement[];
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  unlockedAt?: Date;
  unlockedBy?: string;
}

export interface AchievementRequirement {
  type: 'action_count' | 'time_spent' | 'feature_used' | 'tutorial_completed' | 'result_shared' | 'team_activity';
  action: string;
  targetValue: number;
  currentValue: number;
  completed: boolean;
}

export interface UserAchievement {
  userId: string;
  achievementId: string;
  unlockedAt: Date;
  progress: number; // For achievements that have progress
  completed: boolean;
  pointsEarned: number;
}

export interface AchievementProgress {
  userId: string;
  achievementId: string;
  currentProgress: number;
  targetProgress: number;
  percentage: number;
  lastUpdated: Date;
}

export interface Milestone {
  id: string;
  name: string;
  description: string;
  threshold: number; // Points threshold
  unlockedAt?: Date;
  badge: 'bronze' | 'silver' | 'gold' | 'platinum';
}

export class AchievementSystem {
  private achievements: Map<string, Achievement> = new Map();
  private userAchievements: Map<string, UserAchievement[]> = new Map();
  private achievementProgress: Map<string, AchievementProgress[]> = new Map();
  private milestones: Map<string, Milestone> = new Map();

  constructor() {
    this.initializeDefaultAchievements();
    this.initializeDefaultMilestones();
  }

  /**
   * Initialize default achievements
   */
  private initializeDefaultAchievements(): void {
    const defaultAchievements: Achievement[] = [
      {
        id: 'ach-first-upload',
        name: 'First Upload',
        description: 'Uploaded your first file for metadata extraction',
        icon: '📤',
        points: 10,
        category: 'onboarding',
        requirements: [
          {
            type: 'action_count',
            action: 'file_upload',
            targetValue: 1,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'common'
      },
      {
        id: 'ach-first-results',
        name: 'First Results',
        description: 'Successfully extracted metadata from a file',
        icon: '🔍',
        points: 15,
        category: 'onboarding',
        requirements: [
          {
            type: 'action_count',
            action: 'view_results',
            targetValue: 1,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'common'
      },
      {
        id: 'ach-five-uploads',
        name: 'Early Adopter',
        description: 'Uploaded 5 files for extraction',
        icon: '🚀',
        points: 25,
        category: 'exploration',
        requirements: [
          {
            type: 'action_count',
            action: 'file_upload',
            targetValue: 5,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'common'
      },
      {
        id: 'ach-gps-discovery',
        name: 'Location Detective',
        description: 'Explored GPS and location data in results',
        icon: '🗺️',
        points: 30,
        category: 'exploration',
        requirements: [
          {
            type: 'feature_used',
            action: 'view_gps_data',
            targetValue: 1,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'uncommon'
      },
      {
        id: 'ach-camera-expert',
        name: 'Camera Expert',
        description: 'Analyzed camera settings and EXIF data',
        icon: '📷',
        points: 35,
        category: 'expertise',
        requirements: [
          {
            type: 'feature_used',
            action: 'analyze_camera_settings',
            targetValue: 1,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'uncommon'
      },
      {
        id: 'ach-tutorial-master',
        name: 'Tutorial Master',
        description: 'Completed 5 onboarding tutorials',
        icon: '🎓',
        points: 50,
        category: 'onboarding',
        requirements: [
          {
            type: 'tutorial_completed',
            action: 'complete_tutorial',
            targetValue: 5,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'rare'
      },
      {
        id: 'ach-forensic-beginner',
        name: 'Forensic Beginner',
        description: 'Performed your first forensic analysis',
        icon: '🕵️',
        points: 40,
        category: 'expertise',
        requirements: [
          {
            type: 'feature_used',
            action: 'forensic_analysis',
            targetValue: 1,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'uncommon'
      },
      {
        id: 'ach-ai-detection',
        name: 'AI Detective',
        description: 'Used AI generation detection feature',
        icon: '🤖',
        points: 45,
        category: 'expertise',
        requirements: [
          {
            type: 'feature_used',
            action: 'ai_detection',
            targetValue: 1,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'rare'
      },
      {
        id: 'ach-steganography',
        name: 'Steganography Hunter',
        description: 'Detected hidden data using steganography tools',
        icon: '🔍',
        points: 55,
        category: 'expertise',
        requirements: [
          {
            type: 'feature_used',
            action: 'steganography_detection',
            targetValue: 1,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'rare'
      },
      {
        id: 'ach-team-collaborator',
        name: 'Team Collaborator',
        description: 'Shared results with your team',
        icon: '👥',
        points: 35,
        category: 'collaboration',
        requirements: [
          {
            type: 'result_shared',
            action: 'share_result',
            targetValue: 1,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'uncommon'
      },
      {
        id: 'ach-power-user',
        name: 'Power User',
        description: 'Used 10 different features',
        icon: '⚡',
        points: 60,
        category: 'engagement',
        requirements: [
          {
            type: 'feature_used',
            action: 'use_feature',
            targetValue: 10,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'rare'
      },
      {
        id: 'ach-weekly-regular',
        name: 'Weekly Regular',
        description: 'Used the platform 5 days in one week',
        icon: '📅',
        points: 50,
        category: 'engagement',
        requirements: [
          {
            type: 'action_count',
            action: 'daily_login',
            targetValue: 5,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'uncommon'
      },
      {
        id: 'ach-monthly-veteran',
        name: 'Monthly Veteran',
        description: 'Used the platform for 20 days in one month',
        icon: '🎖️',
        points: 80,
        category: 'engagement',
        requirements: [
          {
            type: 'action_count',
            action: 'daily_login',
            targetValue: 20,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'epic'
      },
      {
        id: 'ach-helpful-contributor',
        name: 'Helpful Contributor',
        description: 'Provided feedback on 5 help articles',
        icon: '💬',
        points: 40,
        category: 'engagement',
        requirements: [
          {
            type: 'action_count',
            action: 'help_feedback',
            targetValue: 5,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'rare'
      },
      {
        id: 'ach-perfectionist',
        name: 'Perfectionist',
        description: 'Achieved 100% completion in onboarding',
        icon: '💯',
        points: 100,
        category: 'onboarding',
        requirements: [
          {
            type: 'tutorial_completed',
            action: 'complete_all_tutorials',
            targetValue: 1,
            currentValue: 0,
            completed: false
          }
        ],
        rarity: 'epic'
      }
    ];

    defaultAchievements.forEach(achievement => {
      this.achievements.set(achievement.id, { ...achievement });
    });
  }

  /**
   * Initialize default milestones
   */
  private initializeDefaultMilestones(): void {
    const defaultMilestones: Milestone[] = [
      {
        id: 'ms-bronze',
        name: 'Bronze Explorer',
        description: 'Reached 100 achievement points',
        threshold: 100,
        badge: 'bronze'
      },
      {
        id: 'ms-silver',
        name: 'Silver Analyst',
        description: 'Reached 500 achievement points',
        threshold: 500,
        badge: 'silver'
      },
      {
        id: 'ms-gold',
        name: 'Gold Expert',
        description: 'Reached 1000 achievement points',
        threshold: 1000,
        badge: 'gold'
      },
      {
        id: 'ms-platinum',
        name: 'Platinum Master',
        description: 'Reached 2000 achievement points',
        threshold: 2000,
        badge: 'platinum'
      }
    ];

    defaultMilestones.forEach(milestone => {
      this.milestones.set(milestone.id, milestone);
    });
  }

  /**
   * Track user action for achievements
   */
  async trackUserAction(userId: string, action: string, value: number = 1): Promise<void> {
    // Update user's progress toward achievements
    const userAchievements = this.userAchievements.get(userId) || [];
    const userProgress = this.achievementProgress.get(userId) || [];

    // Get all achievements that match this action
    const relevantAchievements = Array.from(this.achievements.values()).filter(
      ach => ach.requirements.some(req => req.action === action)
    );

    for (const achievement of relevantAchievements) {
      const req = achievement.requirements.find(r => r.action === action);
      if (!req) continue;

      // Update progress
      req.currentValue += value;

      // Check if requirement is now complete
      if (req.currentValue >= req.targetValue && !req.completed) {
        req.completed = true;

        // Check if entire achievement is now complete
        const allCompleted = achievement.requirements.every(r => r.completed);
        if (allCompleted) {
          // Award the achievement
          await this.awardAchievement(userId, achievement.id);
        }
      }

      // Update progress tracking
      const progressId = `${userId}-${achievement.id}`;
      let progress = userProgress.find(p => p.achievementId === achievement.id);
      
      if (progress) {
        progress.currentProgress = req.currentValue;
        progress.percentage = Math.min(100, Math.round((req.currentValue / req.targetValue) * 100));
        progress.lastUpdated = new Date();
      } else {
        progress = {
          userId,
          achievementId: achievement.id,
          currentProgress: req.currentValue,
          targetProgress: req.targetValue,
          percentage: Math.min(100, Math.round((req.currentValue / req.targetValue) * 100)),
          lastUpdated: new Date()
        };
        userProgress.push(progress);
      }
    }

    // Update the maps
    this.userAchievements.set(userId, userAchievements);
    this.achievementProgress.set(userId, userProgress);
  }

  /**
   * Award an achievement to a user
   */
  async awardAchievement(userId: string, achievementId: string): Promise<boolean> {
    const achievement = this.achievements.get(achievementId);
    if (!achievement) return false;

    // Check if user already has this achievement
    const userAchievements = this.userAchievements.get(userId) || [];
    if (userAchievements.some(ua => ua.achievementId === achievementId)) {
      return false; // Already awarded
    }

    // Create new user achievement
    const userAchievement: UserAchievement = {
      userId,
      achievementId,
      unlockedAt: new Date(),
      progress: 100, // 100% since it's completed
      completed: true,
      pointsEarned: achievement.points
    };

    userAchievements.push(userAchievement);
    this.userAchievements.set(userId, userAchievements);

    // Update achievement status
    const updatedAchievement = { ...achievement };
    updatedAchievement.unlockedAt = new Date();
    updatedAchievement.unlockedBy = userId;
    this.achievements.set(achievementId, updatedAchievement);

    // Check for milestone unlocks
    await this.checkMilestones(userId);

    return true;
  }

  /**
   * Get user's achievements
   */
  async getUserAchievements(userId: string): Promise<UserAchievement[]> {
    return this.userAchievements.get(userId) || [];
  }

  /**
   * Get user's achievement progress
   */
  async getUserProgress(userId: string): Promise<AchievementProgress[]> {
    return this.achievementProgress.get(userId) || [];
  }

  /**
   * Get all available achievements
   */
  getAllAchievements(): Achievement[] {
    return Array.from(this.achievements.values());
  }

  /**
   * Get achievements by category
   */
  getAchievementsByCategory(category: string): Achievement[] {
    return Array.from(this.achievements.values()).filter(
      ach => ach.category === category
    );
  }

  /**
   * Get user's total achievement points
   */
  async getUserPoints(userId: string): Promise<number> {
    const userAchievements = await this.getUserAchievements(userId);
    return userAchievements.reduce((sum, ua) => sum + ua.pointsEarned, 0);
  }

  /**
   * Check if user has unlocked a specific achievement
   */
  async hasAchievement(userId: string, achievementId: string): Promise<boolean> {
    const userAchievements = await this.getUserAchievements(userId);
    return userAchievements.some(ua => ua.achievementId === achievementId);
  }

  /**
   * Get user's unlocked achievements
   */
  async getUnlockedAchievements(userId: string): Promise<UserAchievement[]> {
    const userAchievements = await this.getUserAchievements(userId);
    return userAchievements.filter(ua => ua.completed);
  }

  /**
   * Get user's locked achievements
   */
  async getLockedAchievements(userId: string): Promise<Achievement[]> {
    const userAchievements = await this.getUserAchievements(userId);
    const unlockedIds = new Set(userAchievements.map(ua => ua.achievementId));
    
    return Array.from(this.achievements.values())
      .filter(ach => !unlockedIds.has(ach.id));
  }

  /**
   * Get user's achievement statistics
   */
  async getUserAchievementStats(userId: string) {
    const allAchievements = await this.getUserAchievements(userId);
    const unlocked = allAchievements.filter(ua => ua.completed);
    const totalPoints = unlocked.reduce((sum, ua) => sum + ua.pointsEarned, 0);
    
    // Count by category
    const categoryCounts: Record<string, number> = {};
    for (const ua of unlocked) {
      const achievement = this.achievements.get(ua.achievementId);
      if (achievement) {
        categoryCounts[achievement.category] = (categoryCounts[achievement.category] || 0) + 1;
      }
    }
    
    // Count by rarity
    const rarityCounts: Record<string, number> = {};
    for (const ua of unlocked) {
      const achievement = this.achievements.get(ua.achievementId);
      if (achievement) {
        rarityCounts[achievement.rarity] = (rarityCounts[achievement.rarity] || 0) + 1;
      }
    }
    
    return {
      totalUnlocked: unlocked.length,
      totalAvailable: this.achievements.size,
      totalPoints,
      completionRate: this.achievements.size > 0 
        ? (unlocked.length / this.achievements.size) * 100 
        : 0,
      categoryBreakdown: categoryCounts,
      rarityBreakdown: rarityCounts,
      lastUnlocked: unlocked.length > 0 
        ? unlocked[unlocked.length - 1].unlockedAt 
        : null
    };
  }

  /**
   * Check for milestone unlocks
   */
  async checkMilestones(userId: string): Promise<Milestone[]> {
    const userPoints = await this.getUserPoints(userId);
    const userAchievements = this.userAchievements.get(userId) || [];
    
    const unlockedMilestones: Milestone[] = [];
    
    for (const [milestoneId, milestone] of this.milestones) {
      // Check if user has enough points and milestone isn't already unlocked
      if (userPoints >= milestone.threshold) {
        const isAlreadyUnlocked = userAchievements.some(ua => 
          ua.achievementId === milestoneId && ua.completed
        );
        
        if (!isAlreadyUnlocked) {
          // Award milestone as a special achievement
          const milestoneAchievement: UserAchievement = {
            userId,
            achievementId: milestoneId,
            unlockedAt: new Date(),
            progress: 100,
            completed: true,
            pointsEarned: 0 // Milestones don't give extra points
          };
          
          userAchievements.push(milestoneAchievement);
          unlockedMilestones.push(milestone);
          
          // Update milestone status
          const updatedMilestone = { ...milestone, unlockedAt: new Date() };
          this.milestones.set(milestoneId, updatedMilestone);
        }
      }
    }
    
    this.userAchievements.set(userId, userAchievements);
    return unlockedMilestones;
  }

  /**
   * Get user's milestones
   */
  async getUserMilestones(userId: string): Promise<Milestone[]> {
    const userAchievements = this.userAchievements.get(userId) || [];
    const unlockedMilestoneIds = userAchievements
      .filter(ua => this.milestones.has(ua.achievementId))
      .map(ua => ua.achievementId);
    
    return Array.from(this.milestones.values())
      .filter(m => unlockedMilestoneIds.includes(m.id));
  }

  /**
   * Get achievement by ID
   */
  getAchievement(achievementId: string): Achievement | undefined {
    return this.achievements.get(achievementId);
  }

  /**
   * Get user's progress toward a specific achievement
   */
  async getUserAchievementProgress(userId: string, achievementId: string): Promise<AchievementProgress | null> {
    const userProgress = this.achievementProgress.get(userId) || [];
    return userProgress.find(p => p.achievementId === achievementId) || null;
  }

  /**
   * Get top users by achievement points
   */
  getLeaderboard(limit: number = 10): Array<{ userId: string; points: number; achievements: number }> {
    const leaderboard: Array<{ userId: string; points: number; achievements: number }> = [];
    
    for (const [userId, userAchievements] of this.userAchievements) {
      const points = userAchievements.reduce((sum, ua) => sum + ua.pointsEarned, 0);
      const achievementCount = userAchievements.length;
      
      leaderboard.push({ userId, points, achievements: achievementCount });
    }
    
    return leaderboard
      .sort((a, b) => b.points - a.points)
      .slice(0, limit);
  }

  /**
   * Get achievements by rarity
   */
  getAchievementsByRarity(rarity: string): Achievement[] {
    return Array.from(this.achievements.values()).filter(
      ach => ach.rarity === rarity
    );
  }

  /**
   * Get recent achievements
   */
  getRecentAchievements(limit: number = 5): Achievement[] {
    return Array.from(this.achievements.values())
      .filter(ach => ach.unlockedAt)
      .sort((a, b) => 
        (b.unlockedAt?.getTime() || 0) - (a.unlockedAt?.getTime() || 0)
      )
      .slice(0, limit);
  }

  /**
   * Create a custom achievement
   */
  async createCustomAchievement(
    name: string,
    description: string,
    icon: string,
    points: number,
    category: string,
    requirements: AchievementRequirement[],
    rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary' = 'common'
  ): Promise<Achievement> {
    const achievementId = `custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const newAchievement: Achievement = {
      id: achievementId,
      name,
      description,
      icon,
      points,
      category: category as any,
      requirements,
      rarity,
      unlockedAt: undefined,
      unlockedBy: undefined
    };

    this.achievements.set(achievementId, newAchievement);
    return newAchievement;
  }

  /**
   * Get personalized achievement recommendations for user
   */
  async getPersonalizedRecommendations(userId: string): Promise<Achievement[]> {
    const userAchievements = await this.getUserAchievements(userId);
    const unlockedIds = new Set(userAchievements.map(ua => ua.achievementId));
    
    // Get locked achievements
    const lockedAchievements = Array.from(this.achievements.values())
      .filter(ach => !unlockedIds.has(ach.id));
    
    // Prioritize achievements based on user's activity
    const userProgress = await this.getUserProgress(userId);
    
    // Calculate scores based on how close user is to completing achievements
    const scoredAchievements = lockedAchievements.map(ach => {
      // Find the user's progress for this achievement
      const progress = userProgress.find(p => p.achievementId === ach.id);
      
      // Calculate completion percentage
      const percentage = progress ? progress.percentage : 0;
      
      // Prioritize achievements the user is close to completing
      return {
        achievement: ach,
        score: percentage
      };
    });
    
    // Sort by score (highest first) and return top 5
    return scoredAchievements
      .sort((a, b) => b.score - a.score)
      .slice(0, 5)
      .map(item => item.achievement);
  }
}

// Singleton instance
export const achievementSystem = new AchievementSystem();

export default achievementSystem;