/**
 * Contextual Help System - Help content and display management
 */

export interface HelpContent {
  id: string;
  title: string;
  content: string;
  contentType: 'tooltip' | 'modal' | 'guide' | 'video' | 'faq';
  context: string; // The page/feature this help is for
  keywords: string[];
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime?: number; // in minutes
  relatedContent?: string[]; // IDs of related help content
  lastUpdated: Date;
}

export interface HelpTrigger {
  id: string;
  elementSelector: string;
  triggerType: 'hover' | 'click' | 'focus' | 'dwell';
  dwellTime?: number; // time in ms for dwell triggers
  helpContentId: string;
  position?: 'top' | 'bottom' | 'left' | 'right' | 'auto';
  enabled: boolean;
}

export interface HelpDisplay {
  id: string;
  userId: string;
  helpContentId: string;
  displayType: 'tooltip' | 'modal' | 'sidebar' | 'overlay';
  displayedAt: Date;
  interaction: 'viewed' | 'interacted' | 'dismissed' | 'skipped';
  timeSpent?: number; // in seconds
  feedback?: {
    rating: number; // 1-5
    comment?: string;
    helpful: boolean;
  };
}

export interface HelpPreference {
  userId: string;
  autoShowHelp: boolean;
  helpFrequency: 'always' | 'often' | 'sometimes' | 'rarely' | 'never';
  preferredDifficulty: 'beginner' | 'intermediate' | 'advanced';
  disabledTriggers: string[];
  lastUpdated: Date;
}

export class ContextualHelpSystem {
  private helpContents: Map<string, HelpContent> = new Map();
  private helpTriggers: Map<string, HelpTrigger> = new Map();
  private helpDisplays: Map<string, HelpDisplay[]> = new Map();
  private helpPreferences: Map<string, HelpPreference> = new Map();

  constructor() {
    this.initializeDefaultHelpContent();
  }

  /**
   * Initialize default help content
   */
  private initializeDefaultHelpContent(): void {
    const defaultHelpContent: HelpContent[] = [
      {
        id: 'help-upload-basics',
        title: 'Uploading Files',
        content: 'To upload a file, click the upload area or drag and drop your file. We support images, documents, and other file types. The file will be processed to extract metadata.',
        contentType: 'tooltip',
        context: 'upload-page',
        keywords: ['upload', 'file', 'drag', 'drop', 'process'],
        category: 'basic',
        difficulty: 'beginner',
        lastUpdated: new Date()
      },
      {
        id: 'help-results-basics',
        title: 'Understanding Results',
        content: 'Your extracted metadata is organized into sections. The most important information is shown first. Click on sections to expand and see more details.',
        contentType: 'tooltip',
        context: 'results-page',
        keywords: ['results', 'metadata', 'sections', 'expand'],
        category: 'basic',
        difficulty: 'beginner',
        lastUpdated: new Date()
      },
      {
        id: 'help-gps-analysis',
        title: 'GPS and Location Data',
        content: 'GPS coordinates show where a photo was taken. You can see the location on a map and get address information. Accuracy varies based on the device.',
        contentType: 'guide',
        context: 'results-page',
        keywords: ['gps', 'location', 'coordinates', 'map', 'accuracy'],
        category: 'analysis',
        difficulty: 'intermediate',
        estimatedTime: 5,
        lastUpdated: new Date()
      },
      {
        id: 'help-camera-settings',
        title: 'Camera Settings Analysis',
        content: 'Camera settings like aperture, ISO, and shutter speed affect photo quality. These are stored in EXIF data and can tell you about the shooting conditions.',
        contentType: 'guide',
        context: 'results-page',
        keywords: ['camera', 'settings', 'exif', 'aperture', 'iso', 'shutter'],
        category: 'analysis',
        difficulty: 'intermediate',
        estimatedTime: 7,
        lastUpdated: new Date()
      },
      {
        id: 'help-forensics-basics',
        title: 'Forensic Analysis',
        content: 'Forensic analysis looks for signs of manipulation, hidden data, or AI generation. Results include confidence scores and detailed findings.',
        contentType: 'guide',
        context: 'results-page',
        keywords: ['forensics', 'manipulation', 'hidden', 'ai', 'authenticity'],
        category: 'forensics',
        difficulty: 'advanced',
        estimatedTime: 10,
        lastUpdated: new Date()
      },
      {
        id: 'help-steganography',
        title: 'Steganography Detection',
        content: 'Steganography is the practice of hiding information within other files. Our tools scan for common steganographic techniques.',
        contentType: 'guide',
        context: 'forensics-page',
        keywords: ['steganography', 'hidden', 'data', 'detection', 'security'],
        category: 'forensics',
        difficulty: 'advanced',
        estimatedTime: 12,
        lastUpdated: new Date()
      },
      {
        id: 'help-manipulation-detection',
        title: 'Manipulation Detection',
        content: 'We analyze images for signs of editing, compositing, or other manipulations by examining statistical properties and inconsistencies.',
        contentType: 'guide',
        context: 'forensics-page',
        keywords: ['manipulation', 'editing', 'photoshop', 'tampering', 'analysis'],
        category: 'forensics',
        difficulty: 'advanced',
        estimatedTime: 15,
        lastUpdated: new Date()
      },
      {
        id: 'help-ai-detection',
        title: 'AI Generation Detection',
        content: 'Our tools identify characteristics common in AI-generated images, such as unusual patterns or statistical anomalies.',
        contentType: 'guide',
        context: 'forensics-page',
        keywords: ['ai', 'generation', 'synthetic', 'detection', 'machine-learning'],
        category: 'forensics',
        difficulty: 'advanced',
        estimatedTime: 10,
        lastUpdated: new Date()
      },
      {
        id: 'help-timeline',
        title: 'Timeline Reconstruction',
        content: 'Reconstruct chronological events from metadata timestamps, GPS data, and file creation/modification times.',
        contentType: 'guide',
        context: 'timeline-page',
        keywords: ['timeline', 'chronology', 'timestamps', 'events', 'sequence'],
        category: 'analysis',
        difficulty: 'intermediate',
        estimatedTime: 8,
        lastUpdated: new Date()
      },
      {
        id: 'help-privacy-settings',
        title: 'Privacy Settings',
        content: 'Control what metadata is visible and how your data is used. Review these settings regularly to protect your privacy.',
        contentType: 'guide',
        context: 'settings-page',
        keywords: ['privacy', 'settings', 'metadata', 'control', 'protection'],
        category: 'privacy',
        difficulty: 'beginner',
        estimatedTime: 5,
        lastUpdated: new Date()
      }
    ];

    defaultHelpContent.forEach(content => {
      this.helpContents.set(content.id, content);
    });

    // Initialize default triggers
    const defaultTriggers: HelpTrigger[] = [
      {
        id: 'trigger-upload-area',
        elementSelector: '[data-testid="upload-zone"]',
        triggerType: 'hover',
        helpContentId: 'help-upload-basics',
        position: 'bottom',
        enabled: true
      },
      {
        id: 'trigger-results-overview',
        elementSelector: '[data-testid="results-container"]',
        triggerType: 'hover',
        helpContentId: 'help-results-basics',
        position: 'top',
        enabled: true
      },
      {
        id: 'trigger-gps-section',
        elementSelector: '[data-testid="gps-section"]',
        triggerType: 'hover',
        helpContentId: 'help-gps-analysis',
        position: 'right',
        enabled: true
      },
      {
        id: 'trigger-exif-section',
        elementSelector: '[data-testid="exif-section"]',
        triggerType: 'hover',
        helpContentId: 'help-camera-settings',
        position: 'right',
        enabled: true
      },
      {
        id: 'trigger-forensics-section',
        elementSelector: '[data-testid="forensics-section"]',
        triggerType: 'hover',
        helpContentId: 'help-forensics-basics',
        position: 'right',
        enabled: true
      }
    ];

    defaultTriggers.forEach(trigger => {
      this.helpTriggers.set(trigger.id, trigger);
    });
  }

  /**
   * Get help content by ID
   */
  async getHelpContent(contentId: string): Promise<HelpContent | null> {
    return this.helpContents.get(contentId) || null;
  }

  /**
   * Search help content
   */
  async searchHelpContent(query: string, context?: string, difficulty?: string): Promise<HelpContent[]> {
    const allContent = Array.from(this.helpContents.values());
    
    return allContent.filter(content => {
      const matchesQuery = 
        content.title.toLowerCase().includes(query.toLowerCase()) ||
        content.content.toLowerCase().includes(query.toLowerCase()) ||
        content.keywords.some(keyword => 
          keyword.toLowerCase().includes(query.toLowerCase())
        );
      
      const matchesContext = !context || content.context === context;
      const matchesDifficulty = !difficulty || content.difficulty === difficulty;
      
      return matchesQuery && matchesContext && matchesDifficulty;
    });
  }

  /**
   * Get help content for a specific context
   */
  async getContextHelp(context: string): Promise<HelpContent[]> {
    return Array.from(this.helpContents.values())
      .filter(content => content.context === context)
      .sort((a, b) => {
        // Sort by difficulty (beginner first)
        const difficultyOrder = { beginner: 1, intermediate: 2, advanced: 3 };
        return difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty];
      });
  }

  /**
   * Get help trigger by element selector
   */
  async getTriggerForElement(elementSelector: string): Promise<HelpTrigger | null> {
    const triggers = Array.from(this.helpTriggers.values());
    const trigger = triggers.find(t => t.elementSelector === elementSelector && t.enabled);
    return trigger || null;
  }

  /**
   * Record help display and interaction
   */
  async recordHelpDisplay(
    userId: string,
    helpContentId: string,
    displayType: 'tooltip' | 'modal' | 'sidebar' | 'overlay',
    interaction: 'viewed' | 'interacted' | 'dismissed' | 'skipped',
    timeSpent?: number
  ): Promise<string> {
    const displayId = `display-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const display: HelpDisplay = {
      id: displayId,
      userId,
      helpContentId,
      displayType,
      displayedAt: new Date(),
      interaction,
      timeSpent
    };

    if (!this.helpDisplays.has(userId)) {
      this.helpDisplays.set(userId, []);
    }

    const userDisplays = this.helpDisplays.get(userId)!;
    userDisplays.push(display);

    return displayId;
  }

  /**
   * Get user's help history
   */
  async getUserHelpHistory(userId: string): Promise<HelpDisplay[]> {
    return this.helpDisplays.get(userId) || [];
  }

  /**
   * Provide feedback on help content
   */
  async provideFeedback(
    userId: string,
    displayId: string,
    rating: number,
    comment?: string,
    helpful?: boolean
  ): Promise<boolean> {
    const userDisplays = this.helpDisplays.get(userId) || [];
    const displayIndex = userDisplays.findIndex(d => d.id === displayId);

    if (displayIndex === -1) {
      return false;
    }

    userDisplays[displayIndex].feedback = {
      rating,
      comment,
      helpful: helpful ?? rating >= 4
    };

    return true;
  }

  /**
   * Get user's help preferences
   */
  async getUserPreferences(userId: string): Promise<HelpPreference> {
    if (!this.helpPreferences.has(userId)) {
      // Create default preferences
      const defaultPreferences: HelpPreference = {
        userId,
        autoShowHelp: true,
        helpFrequency: 'sometimes',
        preferredDifficulty: 'intermediate',
        disabledTriggers: [],
        lastUpdated: new Date()
      };

      this.helpPreferences.set(userId, defaultPreferences);
      return defaultPreferences;
    }

    return this.helpPreferences.get(userId)!;
  }

  /**
   * Update user's help preferences
   */
  async updateUserPreferences(userId: string, updates: Partial<HelpPreference>): Promise<boolean> {
    const currentPrefs = await this.getUserPreferences(userId);
    const newPrefs: HelpPreference = {
      ...currentPrefs,
      ...updates,
      lastUpdated: new Date()
    };

    this.helpPreferences.set(userId, newPrefs);
    return true;
  }

  /**
   * Get contextual help for a user and context
   */
  async getContextualHelp(userId: string, context: string): Promise<HelpContent[]> {
    const preferences = await this.getUserPreferences(userId);
    
    // Get help content for the context
    const contextHelp = await this.getContextHelp(context);
    
    // Filter by user's preferred difficulty level and below
    const difficultyOrder = { beginner: 1, intermediate: 2, advanced: 3 };
    const userDifficultyLevel = difficultyOrder[preferences.preferredDifficulty];
    
    return contextHelp.filter(content => 
      difficultyOrder[content.difficulty] <= userDifficultyLevel
    );
  }

  /**
   * Get help content by category
   */
  async getHelpByCategory(category: string, difficulty?: 'beginner' | 'intermediate' | 'advanced'): Promise<HelpContent[]> {
    return Array.from(this.helpContents.values())
      .filter(content => 
        content.category === category && 
        (!difficulty || content.difficulty === difficulty)
      );
  }

  /**
   * Get popular help content (most viewed)
   */
  async getPopularHelpContent(limit: number = 5): Promise<HelpContent[]> {
    // In a real implementation, we'd count how often each help content is displayed
    // For now, return the most recently added content
    const allContent = Array.from(this.helpContents.values())
      .sort((a, b) => b.lastUpdated.getTime() - a.lastUpdated.getTime());
    
    return allContent.slice(0, limit);
  }

  /**
   * Get trending help content (most interacted with)
   */
  async getTrendingHelpContent(limit: number = 5): Promise<HelpContent[]> {
    // In a real implementation, we'd analyze interaction data
    // For now, return content with the most keywords (indicating comprehensiveness)
    const allContent = Array.from(this.helpContents.values())
      .sort((a, b) => b.keywords.length - a.keywords.length);
    
    return allContent.slice(0, limit);
  }

  /**
   * Create custom help content
   */
  async createCustomHelpContent(
    title: string,
    content: string,
    context: string,
    category: string,
    keywords: string[],
    contentType: 'tooltip' | 'modal' | 'guide' | 'video' | 'faq' = 'guide',
    difficulty: 'beginner' | 'intermediate' | 'advanced' = 'intermediate'
  ): Promise<HelpContent> {
    const contentId = `custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const newContent: HelpContent = {
      id: contentId,
      title,
      content,
      contentType,
      context,
      keywords,
      category,
      difficulty,
      lastUpdated: new Date()
    };

    this.helpContents.set(contentId, newContent);
    return newContent;
  }

  /**
   * Update help content
   */
  async updateHelpContent(contentId: string, updates: Partial<HelpContent>): Promise<boolean> {
    const content = this.helpContents.get(contentId);
    if (!content) return false;

    Object.assign(content, updates, { lastUpdated: new Date() });
    return true;
  }

  /**
   * Get help content analytics
   */
  async getHelpAnalytics(contentId: string) {
    const displays = Array.from(this.helpDisplays.values()).flat();
    const contentDisplays = displays.filter(d => d.helpContentId === contentId);
    
    const viewed = contentDisplays.filter(d => d.interaction === 'viewed').length;
    const interacted = contentDisplays.filter(d => d.interaction === 'interacted').length;
    const dismissed = contentDisplays.filter(d => d.interaction === 'dismissed').length;
    
    // Calculate average time spent
    const totalViewTime = contentDisplays.reduce((sum, d) => 
      sum + (d.timeSpent || 0), 0);
    const avgTimeSpent = contentDisplays.length > 0 
      ? totalViewTime / contentDisplays.length 
      : 0;
    
    // Calculate feedback metrics
    const feedbacks = contentDisplays
      .filter(d => d.feedback)
      .map(d => d.feedback!);
    
    const avgRating = feedbacks.length > 0
      ? feedbacks.reduce((sum, f) => sum + f.rating, 0) / feedbacks.length
      : 0;
    
    const helpfulCount = feedbacks.filter(f => f.helpful).length;
    const helpfulPercentage = feedbacks.length > 0
      ? (helpfulCount / feedbacks.length) * 100
      : 0;

    return {
      contentId,
      totalViews: contentDisplays.length,
      viewed,
      interacted,
      dismissed,
      avgTimeSpent,
      avgRating,
      helpfulPercentage,
      feedbackCount: feedbacks.length
    };
  }

  /**
   * Get user's help engagement
   */
  async getUserHelpEngagement(userId: string) {
    const displays = this.helpDisplays.get(userId) || [];
    
    const totalViews = displays.length;
    const interacted = displays.filter(d => d.interaction === 'interacted').length;
    const dismissed = displays.filter(d => d.interaction === 'dismissed').length;
    const skipped = displays.filter(d => d.interaction === 'skipped').length;
    
    // Calculate engagement rate
    const engagementRate = totalViews > 0 
      ? (interacted / totalViews) * 100 
      : 0;
    
    // Get most viewed categories
    const categoryCounts: Record<string, number> = {};
    for (const display of displays) {
      const content = this.helpContents.get(display.helpContentId);
      if (content) {
        categoryCounts[content.category] = (categoryCounts[content.category] || 0) + 1;
      }
    }
    
    const topCategory = Object.entries(categoryCounts)
      .sort((a, b) => b[1] - a[1])[0]?.[0] || 'none';
    
    // Get most common feedback
    const feedbacks = displays.filter(d => d.feedback).map(d => d.feedback!);
    const avgRating = feedbacks.length > 0
      ? feedbacks.reduce((sum, f) => sum + f.rating, 0) / feedbacks.length
      : 0;

    return {
      userId,
      totalHelpViews: totalViews,
      interactedCount: interacted,
      dismissedCount: dismissed,
      skippedCount: skipped,
      engagementRate,
      avgRating,
      topCategory,
      lastHelpViewed: displays.length > 0 
        ? displays[displays.length - 1].displayedAt 
        : null
    };
  }

  /**
   * Get help content for a specific user based on their skill level
   */
  async getPersonalizedHelp(userId: string, context: string): Promise<HelpContent[]> {
    const preferences = await this.getUserPreferences(userId);
    const allHelp = await this.getContextualHelp(userId, context);
    
    // Sort by relevance to user's skill level
    return allHelp.sort((a, b) => {
      // Prioritize content matching user's preferred difficulty
      const aMatch = a.difficulty === preferences.preferredDifficulty ? 1 : 0;
      const bMatch = b.difficulty === preferences.preferredDifficulty ? 1 : 0;
      
      if (aMatch !== bMatch) {
        return bMatch - aMatch; // Higher priority for matching difficulty
      }
      
      // If same difficulty match, sort by difficulty level (beginner first)
      const difficultyOrder = { beginner: 1, intermediate: 2, advanced: 3 };
      return difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty];
    });
  }
}

// Singleton instance
export const contextualHelpSystem = new ContextualHelpSystem();

export default contextualHelpSystem;