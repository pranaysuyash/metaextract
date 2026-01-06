/**
 * Notification System - In-app and push notifications
 */

import { v4 as uuidv4 } from 'uuid';

export interface Notification {
  id: string;
  userId: string;
  type: 'info' | 'success' | 'warning' | 'error' | 'system';
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  read: boolean;
  createdAt: Date;
  expiresAt?: Date;
  actionUrl?: string;
  actionLabel?: string;
  metadata?: Record<string, any>;
}

export interface NotificationPreferences {
  userId: string;
  emailNotifications: boolean;
  inAppNotifications: boolean;
  pushNotifications: boolean;
  notificationChannels: {
    extractionCompleted: boolean;
    systemUpdates: boolean;
    securityAlerts: boolean;
    billing: boolean;
    featureUpdates: boolean;
  };
  createdAt: Date;
  updatedAt: Date;
}

export interface NotificationChannel {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  userId?: string; // If null/undefined, applies globally
  createdAt: Date;
  updatedAt: Date;
}

export class NotificationSystem {
  private notifications: Map<string, Notification[]> = new Map();
  private preferences: Map<string, NotificationPreferences> = new Map();
  private channels: Map<string, NotificationChannel[]> = new Map();
  private unreadCounts: Map<string, number> = new Map();

  /**
   * Send a notification to a user
   */
  async sendNotification(
    userId: string,
    type: Notification['type'],
    title: string,
    message: string,
    options: {
      priority?: Notification['priority'];
      actionUrl?: string;
      actionLabel?: string;
      expiresAt?: Date;
      metadata?: Record<string, any>;
    } = {}
  ): Promise<string> {
    const notificationId = uuidv4();
    
    const notification: Notification = {
      id: notificationId,
      userId,
      type,
      title,
      message,
      priority: options.priority || 'medium',
      read: false,
      createdAt: new Date(),
      expiresAt: options.expiresAt,
      actionUrl: options.actionUrl,
      actionLabel: options.actionLabel,
      metadata: options.metadata
    };

    if (!this.notifications.has(userId)) {
      this.notifications.set(userId, []);
    }

    const userNotifications = this.notifications.get(userId)!;
    userNotifications.unshift(notification);

    // Update unread count
    const currentUnread = this.unreadCounts.get(userId) || 0;
    this.unreadCounts.set(userId, currentUnread + 1);

    return notificationId;
  }

  /**
   * Get notifications for a user
   */
  async getUserNotifications(
    userId: string,
    options: {
      limit?: number;
      offset?: number;
      type?: Notification['type'];
      priority?: Notification['priority'];
      read?: boolean;
      includeExpired?: boolean;
    } = {}
  ): Promise<Notification[]> {
    const allNotifications = this.notifications.get(userId) || [];
    
    let filtered = allNotifications.filter(notif => {
      // Filter by type
      if (options.type && notif.type !== options.type) {
        return false;
      }
      
      // Filter by priority
      if (options.priority && notif.priority !== options.priority) {
        return false;
      }
      
      // Filter by read status
      if (options.read !== undefined && notif.read !== options.read) {
        return false;
      }
      
      // Filter by expiration
      if (!options.includeExpired && notif.expiresAt && notif.expiresAt < new Date()) {
        return false;
      }
      
      return true;
    });

    // Apply pagination
    if (options.offset) {
      filtered = filtered.slice(options.offset);
    }
    
    if (options.limit) {
      filtered = filtered.slice(0, options.limit);
    }

    return filtered;
  }

  /**
   * Mark a notification as read
   */
  async markAsRead(userId: string, notificationId: string): Promise<boolean> {
    const notifications = this.notifications.get(userId) || [];
    const notification = notifications.find(n => n.id === notificationId && n.userId === userId);
    
    if (!notification) {
      return false;
    }

    notification.read = true;
    
    // Update unread count
    const currentUnread = this.unreadCounts.get(userId) || 0;
    if (!notification.read) { // If it was previously unread
      this.unreadCounts.set(userId, Math.max(0, currentUnread - 1));
    }

    return true;
  }

  /**
   * Mark all notifications as read for a user
   */
  async markAllAsRead(userId: string): Promise<boolean> {
    const notifications = this.notifications.get(userId) || [];
    let updatedCount = 0;

    for (const notification of notifications) {
      if (!notification.read) {
        notification.read = true;
        updatedCount++;
      }
    }

    this.unreadCounts.set(userId, 0);
    return true;
  }

  /**
   * Delete a notification
   */
  async deleteNotification(userId: string, notificationId: string): Promise<boolean> {
    const notifications = this.notifications.get(userId) || [];
    const initialLength = notifications.length;
    
    const updated = notifications.filter(n => n.id !== notificationId);
    this.notifications.set(userId, updated);

    const removedCount = initialLength - updated.length;
    
    if (removedCount > 0) {
      // Update unread count if the deleted notification was unread
      const deletedNotif = notifications.find(n => n.id === notificationId);
      if (deletedNotif && !deletedNotif.read) {
        const currentUnread = this.unreadCounts.get(userId) || 0;
        this.unreadCounts.set(userId, Math.max(0, currentUnread - 1));
      }
    }

    return removedCount > 0;
  }

  /**
   * Get unread notification count for a user
   */
  async getUnreadCount(userId: string): Promise<number> {
    return this.unreadCounts.get(userId) || 0;
  }

  /**
   * Get user's notification preferences
   */
  async getPreferences(userId: string): Promise<NotificationPreferences> {
    if (!this.preferences.has(userId)) {
      // Create default preferences
      const defaultPrefs: NotificationPreferences = {
        userId,
        emailNotifications: true,
        inAppNotifications: true,
        pushNotifications: false, // Disabled by default
        notificationChannels: {
          extractionCompleted: true,
          systemUpdates: true,
          securityAlerts: true,
          billing: true,
          featureUpdates: true
        },
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      this.preferences.set(userId, defaultPrefs);
      return defaultPrefs;
    }

    return this.preferences.get(userId)!;
  }

  /**
   * Update user's notification preferences
   */
  async updatePreferences(userId: string, updates: Partial<NotificationPreferences>): Promise<boolean> {
    const currentPrefs = await this.getPreferences(userId);
    
    // Update preferences
    Object.assign(currentPrefs, updates, { updatedAt: new Date() });
    this.preferences.set(userId, currentPrefs);
    
    return true;
  }

  /**
   * Toggle a specific notification channel
   */
  async toggleNotificationChannel(
    userId: string,
    channel: keyof NotificationPreferences['notificationChannels'],
    enabled: boolean
  ): Promise<boolean> {
    const prefs = await this.getPreferences(userId);
    prefs.notificationChannels[channel] = enabled;
    prefs.updatedAt = new Date();
    
    this.preferences.set(userId, prefs);
    return true;
  }

  /**
   * Create a notification channel
   */
  async createChannel(
    name: string,
    description: string,
    enabled: boolean,
    userId?: string
  ): Promise<NotificationChannel> {
    const channel: NotificationChannel = {
      id: uuidv4(),
      name,
      description,
      enabled,
      userId,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    if (!this.channels.has(userId || 'global')) {
      this.channels.set(userId || 'global', []);
    }

    const channelList = this.channels.get(userId || 'global')!;
    channelList.push(channel);

    return channel;
  }

  /**
   * Get notification channels for a user
   */
  async getUserChannels(userId: string): Promise<NotificationChannel[]> {
    const userChannels = this.channels.get(userId) || [];
    const globalChannels = this.channels.get('global') || [];
    
    return [...globalChannels, ...userChannels];
  }

  /**
   * Bulk send notifications to multiple users
   */
  async bulkSend(
    userIds: string[],
    type: Notification['type'],
    title: string,
    message: string,
    options: {
      priority?: Notification['priority'];
      actionUrl?: string;
      actionLabel?: string;
      expiresAt?: Date;
      metadata?: Record<string, any>;
    } = {}
  ): Promise<{ success: number; failed: number; ids: string[] }> {
    const results = await Promise.all(
      userIds.map(async userId => {
        try {
          const id = await this.sendNotification(userId, type, title, message, options);
          return { success: true, id };
        } catch (error) {
          return { success: false, error };
        }
      })
    );

    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);

    return {
      success: successful.length,
      failed: failed.length,
      ids: successful.map(r => (r as any).id)
    };
  }

  /**
   * Send system-wide notification
   */
  async broadcast(
    type: Notification['type'],
    title: string,
    message: string,
    options: {
      priority?: Notification['priority'];
      actionUrl?: string;
      actionLabel?: string;
      expiresAt?: Date;
      metadata?: Record<string, any>;
    } = {}
  ): Promise<{ success: number; failed: number; ids: string[] }> {
    const allUserIds = Array.from(this.notifications.keys());
    return await this.bulkSend(allUserIds, type, title, message, options);
  }

  /**
   * Clean up expired notifications
   */
  async cleanupExpired(): Promise<number> {
    const now = new Date();
    let cleanedCount = 0;

    for (const [userId, userNotifications] of this.notifications.entries()) {
      const initialCount = userNotifications.length;
      const activeNotifications = userNotifications.filter(
        notif => !notif.expiresAt || notif.expiresAt > now
      );
      
      this.notifications.set(userId, activeNotifications);
      cleanedCount += initialCount - activeNotifications.length;
    }

    return cleanedCount;
  }

  /**
   * Get notification statistics
   */
  async getStats(userId: string): Promise<{
    total: number;
    unread: number;
    read: number;
    byType: Record<string, number>;
    byPriority: Record<string, number>;
    recent: number; // Last 24 hours
  }> {
    const allNotifications = this.notifications.get(userId) || [];
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    const stats = {
      total: allNotifications.length,
      unread: 0,
      read: 0,
      byType: {} as Record<string, number>,
      byPriority: {} as Record<string, number>,
      recent: 0
    };

    for (const notif of allNotifications) {
      if (notif.read) {
        stats.read++;
      } else {
        stats.unread++;
      }

      // Count by type
      stats.byType[notif.type] = (stats.byType[notif.type] || 0) + 1;

      // Count by priority
      stats.byPriority[notif.priority] = (stats.byPriority[notif.priority] || 0) + 1;

      // Count recent (last 24 hours)
      if (notif.createdAt > yesterday) {
        stats.recent++;
      }
    }

    return stats;
  }

  /**
   * Subscribe to notification events
   */
  onNotificationReceived(
    userId: string,
    callback: (notification: Notification) => void
  ): () => void {
    // In a real implementation, this would use an event emitter
    // For now, we'll return a dummy unsubscribe function
    return () => {
      // Unsubscribe logic would go here
    };
  }
}

// Singleton instance
export const notificationSystem = new NotificationSystem();

export default notificationSystem;