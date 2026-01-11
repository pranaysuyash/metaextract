/**
 * Team Analytics - Team metrics and activity tracking
 */

export interface TeamActivity {
  id: string;
  teamId: string;
  userId: string;
  action: string;
  resourceType: string;
  resourceId?: string;
  timestamp: Date;
  metadata?: any;
}

export interface TeamMetrics {
  teamId: string;
  period: {
    start: Date;
    end: Date;
  };
  metrics: {
    totalUsers: number;
    activeUsers: number;
    totalSharedResults: number;
    sharedResultsViews: number;
    totalComments: number;
    collaborationEvents: number;
    fileUploads: number;
    extractionCount: number;
    apiRequests: number;
    storageUsed: number; // in MB
  };
  userEngagement: {
    userId: string;
    name: string;
    activityCount: number;
    lastActive: Date;
    engagementScore: number; // 0-100
  }[];
  resourceUsage: {
    resourceType: string;
    count: number;
    change: number; // compared to previous period
  }[];
}

export interface TeamReport {
  id: string;
  teamId: string;
  title: string;
  description: string;
  generatedAt: Date;
  generatedBy: string;
  period: {
    start: Date;
    end: Date;
  };
  metrics: TeamMetrics;
  insights: string[];
  recommendations: string[];
}

export class TeamAnalytics {
  private teamActivities: Map<string, TeamActivity[]> = new Map();
  private teamMetricsCache: Map<string, TeamMetrics> = new Map();

  /**
   * Log a team activity
   */
  async logActivity(
    teamId: string,
    userId: string,
    action: string,
    resourceType: string,
    resourceId?: string,
    metadata?: any
  ): Promise<string> {
    const activityId = `activity-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const activity: TeamActivity = {
      id: activityId,
      teamId,
      userId,
      action,
      resourceType,
      resourceId,
      timestamp: new Date(),
      metadata
    };

    if (!this.teamActivities.has(teamId)) {
      this.teamActivities.set(teamId, []);
    }

    const activities = this.teamActivities.get(teamId)!;
    activities.push(activity);

    // Invalidate metrics cache for this team
    this.teamMetricsCache.delete(teamId);

    return activityId;
  }

  /**
   * Get team activities for a period
   */
  async getTeamActivities(
    teamId: string,
    startDate: Date,
    endDate: Date
  ): Promise<TeamActivity[]> {
    const allActivities = this.teamActivities.get(teamId) || [];
    return allActivities.filter(activity => 
      activity.timestamp >= startDate && activity.timestamp <= endDate
    );
  }

  /**
   * Calculate team metrics for a period
   */
  async calculateTeamMetrics(
    teamId: string,
    startDate: Date,
    endDate: Date
  ): Promise<TeamMetrics> {
    // Check if we have cached metrics for this period
    const cacheKey = `${teamId}-${startDate.toISOString()}-${endDate.toISOString()}`;
    const cached = this.teamMetricsCache.get(cacheKey);
    if (cached) {
      return cached;
    }

    const activities = await this.getTeamActivities(teamId, startDate, endDate);

    // Calculate basic metrics
    const uniqueUsers = new Set(activities.map(a => a.userId));
    const activeUsers = new Set<string>();
    const userActivityCount = new Map<string, number>();
    
    let sharedResultsCount = 0;
    let sharedResultsViews = 0;
    let commentsCount = 0;
    let collaborationEvents = 0;
    let fileUploads = 0;
    let extractionCount = 0;
    let apiRequests = 0;

    for (const activity of activities) {
      activeUsers.add(activity.userId);
      
      // Count user activities
      userActivityCount.set(
        activity.userId, 
        (userActivityCount.get(activity.userId) || 0) + 1
      );

      // Count different types of activities
      if (activity.resourceType === 'shared_result') {
        sharedResultsCount++;
        if (activity.action === 'view') sharedResultsViews++;
      }
      
      if (activity.action === 'comment') commentsCount++;
      if (activity.action.includes('collaborate')) collaborationEvents++;
      if (activity.action === 'upload') fileUploads++;
      if (activity.action === 'extract') extractionCount++;
      if (activity.resourceType === 'api') apiRequests++;
    }

    // Calculate user engagement
    const userEngagement = Array.from(uniqueUsers).map(userId => {
      const activityCount = userActivityCount.get(userId) || 0;
      // Engagement score based on activity count (simplified calculation)
      const engagementScore = Math.min(100, Math.round((activityCount / 10) * 20));
      
      // Find last active date for this user
      const userActivities = activities.filter(a => a.userId === userId);
      const lastActive = userActivities.length > 0 
        ? userActivities.reduce((latest, current) => 
            current.timestamp > latest ? current.timestamp : latest, 
            new Date(0)
          )
        : new Date(0);

      return {
        userId,
        name: `User ${userId.substring(0, 8)}`, // In real app, get from user service
        activityCount,
        lastActive,
        engagementScore
      };
    });

    // Calculate resource usage
    const resourceUsage = Array.from(
      activities.reduce((acc, activity) => {
        const count = acc.get(activity.resourceType) || 0;
        acc.set(activity.resourceType, count + 1);
        return acc;
      }, new Map<string, number>())
    ).map(([resourceType, count]) => ({
      resourceType,
      count,
      change: 0 // Would compare to previous period in real implementation
    }));

    const metrics: TeamMetrics = {
      teamId,
      period: { start: startDate, end: endDate },
      metrics: {
        totalUsers: uniqueUsers.size,
        activeUsers: activeUsers.size,
        totalSharedResults: sharedResultsCount,
        sharedResultsViews,
        totalComments: commentsCount,
        collaborationEvents,
        fileUploads,
        extractionCount,
        apiRequests,
        storageUsed: 0 // Would come from storage service
      },
      userEngagement,
      resourceUsage
    };

    // Cache the metrics
    this.teamMetricsCache.set(cacheKey, metrics);

    return metrics;
  }

  /**
   * Generate a team report
   */
  async generateTeamReport(
    teamId: string,
    title: string,
    description: string,
    startDate: Date,
    endDate: Date,
    generatedBy: string
  ): Promise<TeamReport> {
    const metrics = await this.calculateTeamMetrics(teamId, startDate, endDate);
    
    // Generate insights based on metrics
    const insights = this.generateInsights(metrics);
    
    // Generate recommendations based on metrics
    const recommendations = this.generateRecommendations(metrics);

    const report: TeamReport = {
      id: `report-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      teamId,
      title,
      description,
      generatedAt: new Date(),
      generatedBy,
      period: { start: startDate, end: endDate },
      metrics,
      insights,
      recommendations
    };

    return report;
  }

  /**
   * Generate insights from metrics
   */
  private generateInsights(metrics: TeamMetrics): string[] {
    const insights: string[] = [];
    const m = metrics.metrics;

    // User engagement insights
    if (m.activeUsers / m.totalUsers > 0.8) {
      insights.push('High team engagement with 80%+ of members active');
    } else if (m.activeUsers / m.totalUsers < 0.3) {
      insights.push('Low team engagement with less than 30% of members active');
    }

    // Collaboration insights
    if (m.totalComments > 0) {
      insights.push(`Team is actively collaborating with ${m.totalComments} comments`);
    }

    if (m.sharedResultsViews > 0) {
      insights.push(`Shared results viewed ${m.sharedResultsViews} times`);
    }

    // Activity insights
    if (m.extractionCount > 100) {
      insights.push(`High usage with ${m.extractionCount} extractions performed`);
    }

    // Top contributors
    if (metrics.userEngagement.length > 0) {
      const topContributor = metrics.userEngagement
        .sort((a, b) => b.activityCount - a.activityCount)[0];
      
      if (topContributor.activityCount > 10) {
        insights.push(`${topContributor.name} is the most active contributor`);
      }
    }

    return insights;
  }

  /**
   * Generate recommendations from metrics
   */
  private generateRecommendations(metrics: TeamMetrics): string[] {
    const recommendations: string[] = [];
    const m = metrics.metrics;

    // Engagement recommendations
    if (m.activeUsers / m.totalUsers < 0.5) {
      recommendations.push('Consider onboarding activities to increase team engagement');
    }

    // Collaboration recommendations
    if (m.totalComments < 5) {
      recommendations.push('Encourage more collaboration through shared result discussions');
    }

    // Usage recommendations
    if (m.extractionCount < 10) {
      recommendations.push('Explore ways to increase platform usage within the team');
    }

    // Resource recommendations
    if (metrics.resourceUsage.length > 0) {
      const topResource = metrics.resourceUsage
        .sort((a, b) => b.count - a.count)[0];
      
      if (topResource.count > 20) {
        recommendations.push(`Focus on ${topResource.resourceType} resources as they're most used`);
      }
    }

    // User-specific recommendations
    if (metrics.userEngagement.length > 0) {
      const leastActive = metrics.userEngagement
        .sort((a, b) => a.activityCount - b.activityCount)[0];
      
      if (leastActive.activityCount === 0) {
        recommendations.push(`Reach out to ${leastActive.name} to understand their needs`);
      }
    }

    return recommendations;
  }

  /**
   * Get team activity trends
   */
  async getActivityTrends(
    teamId: string,
    period: 'daily' | 'weekly' | 'monthly',
    startDate: Date,
    endDate: Date
  ) {
    const activities = await this.getTeamActivities(teamId, startDate, endDate);
    
    // Group activities by the specified period
    const groupedActivities: Record<string, TeamActivity[]> = {};
    
    for (const activity of activities) {
      let key: string;
      
      switch (period) {
        case 'daily':
          key = activity.timestamp.toISOString().split('T')[0];
          break;
        case 'weekly': {
          const weekStart = new Date(activity.timestamp);
          weekStart.setDate(weekStart.getDate() - weekStart.getDay());
          key = weekStart.toISOString().split('T')[0];
          break;
        }
        case 'monthly':
          key = `${activity.timestamp.getFullYear()}-${activity.timestamp.getMonth() + 1}`;
          break;
        default:
          key = activity.timestamp.toISOString();
      }
      
      if (!groupedActivities[key]) {
        groupedActivities[key] = [];
      }
      
      groupedActivities[key].push(activity);
    }
    
    // Convert to chart-ready format
    const trendData = Object.entries(groupedActivities).map(([periodKey, acts]) => ({
      period: periodKey,
      totalActivities: acts.length,
      uniqueUsers: new Set(acts.map(a => a.userId)).size,
      actions: Array.from(
        acts.reduce((acc, act) => {
          const count = acc.get(act.action) || 0;
          acc.set(act.action, count + 1);
          return acc;
        }, new Map<string, number>())
      ).map(([action, count]) => ({ action, count }))
    }));
    
    return trendData;
  }

  /**
   * Get user activity summary
   */
  async getUserActivitySummary(
    teamId: string,
    userId: string,
    startDate: Date,
    endDate: Date
  ) {
    const activities = await this.getTeamActivities(teamId, startDate, endDate);
    const userActivities = activities.filter(a => a.userId === userId);
    
    const actionCounts = userActivities.reduce((acc, activity) => {
      const count = acc[activity.action] || 0;
      acc[activity.action] = count + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return {
      userId,
      totalActivities: userActivities.length,
      actionBreakdown: actionCounts,
      lastActive: userActivities.length > 0 
        ? userActivities[userActivities.length - 1].timestamp 
        : null
    };
  }

  /**
   * Get resource usage statistics
   */
  async getResourceUsageStats(
    teamId: string,
    startDate: Date,
    endDate: Date
  ) {
    const activities = await this.getTeamActivities(teamId, startDate, endDate);
    
    const resourceStats = activities.reduce((acc, activity) => {
      const resourceType = activity.resourceType;
      if (!acc[resourceType]) {
        acc[resourceType] = {
          count: 0,
          actions: {} as Record<string, number>
        };
      }
      
      acc[resourceType].count++;
      
      const actionCount = acc[resourceType].actions[activity.action] || 0;
      acc[resourceType].actions[activity.action] = actionCount + 1;
      
      return acc;
    }, {} as Record<string, { count: number; actions: Record<string, number> }>);

    return resourceStats;
  }

  /**
   * Get team comparison metrics
   */
  async getTeamComparison(
    teamIds: string[],
    startDate: Date,
    endDate: Date
  ) {
    const comparisons = await Promise.all(
      teamIds.map(async teamId => {
        const metrics = await this.calculateTeamMetrics(teamId, startDate, endDate);
        return {
          teamId,
          metrics: metrics.metrics,
          userEngagementAvg: metrics.userEngagement.length > 0
            ? metrics.userEngagement.reduce((sum, u) => sum + u.engagementScore, 0) / metrics.userEngagement.length
            : 0
        };
      })
    );

    return comparisons;
  }
}

// Singleton instance
export const teamAnalytics = new TeamAnalytics();

export default teamAnalytics;
