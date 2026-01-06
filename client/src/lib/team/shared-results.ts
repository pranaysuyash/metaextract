/**
 * Shared Results - Collaborative analysis and shared extractions
 */

import { v4 as uuidv4 } from 'uuid';

export interface SharedResult {
  id: string;
  resultId: string; // Reference to the original extraction result
  teamId: string;
  sharedBy: string; // User ID of the person who shared
  sharedAt: Date;
  permissions: 'view' | 'comment' | 'edit';
  expirationDate?: Date;
  viewers: string[]; // User IDs who can view
  editors: string[]; // User IDs who can edit
  title: string;
  description?: string;
  tags: string[];
  metadata: any; // The actual shared metadata result
  accessCount: number;
  lastAccessed?: Date;
  isArchived: boolean;
}

export interface SharedResultComment {
  id: string;
  sharedResultId: string;
  authorId: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
  resolved: boolean;
  parentCommentId?: string; // For threaded comments
}

export interface SharedResultAccessLog {
  id: string;
  sharedResultId: string;
  userId: string;
  action: 'view' | 'download' | 'comment' | 'edit';
  timestamp: Date;
  metadata?: any; // Additional context about the access
}

export interface SharedResultNotification {
  id: string;
  sharedResultId: string;
  userId: string; // The user to notify
  type: 'new_comment' | 'result_updated' | 'access_revoked' | 'mention';
  message: string;
  read: boolean;
  createdAt: Date;
}

export class SharedResultsManager {
  private sharedResults: Map<string, SharedResult> = new Map();
  private comments: Map<string, SharedResultComment[]> = new Map();
  private accessLogs: Map<string, SharedResultAccessLog[]> = new Map();
  private notifications: Map<string, SharedResultNotification[]> = new Map();

  /**
   * Share a result with a team
   */
  async shareResult(
    resultId: string,
    teamId: string,
    sharedBy: string,
    title: string,
    description: string | undefined,
    permissions: 'view' | 'comment' | 'edit',
    expirationDate?: Date,
    tags: string[] = []
  ): Promise<SharedResult | null> {
    const sharedResultId = uuidv4();
    
    const newSharedResult: SharedResult = {
      id: sharedResultId,
      resultId,
      teamId,
      sharedBy,
      sharedAt: new Date(),
      permissions,
      expirationDate,
      viewers: [sharedBy], // Original sharer can always view
      editors: permissions === 'edit' ? [sharedBy] : [],
      title,
      description,
      tags,
      metadata: {}, // This would be populated with the actual result data
      accessCount: 0,
      isArchived: false
    };

    this.sharedResults.set(sharedResultId, newSharedResult);
    return newSharedResult;
  }

  /**
   * Get a shared result by ID
   */
  async getSharedResult(sharedResultId: string): Promise<SharedResult | null> {
    const result = this.sharedResults.get(sharedResultId);
    
    // Check if result is expired
    if (result && result.expirationDate && result.expirationDate < new Date()) {
      // In a real implementation, we'd remove expired results
      // For now, just return null to indicate it's not accessible
      return null;
    }
    
    return result || null;
  }

  /**
   * Check if a user can access a shared result
   */
  async canUserAccess(userId: string, sharedResultId: string): Promise<boolean> {
    const result = await this.getSharedResult(sharedResultId);
    if (!result) return false;

    // Check if user is in the appropriate permission list
    if (result.permissions === 'edit') {
      return result.editors.includes(userId);
    } else if (result.permissions === 'comment') {
      return result.editors.includes(userId) || result.viewers.includes(userId);
    } else { // view only
      return result.viewers.includes(userId);
    }
  }

  /**
   * Add a user to a shared result
   */
  async addUserToSharedResult(
    sharedResultId: string,
    userId: string,
    permission: 'view' | 'comment' | 'edit'
  ): Promise<boolean> {
    const result = this.sharedResults.get(sharedResultId);
    if (!result) return false;

    // Add user to appropriate list based on permission
    if (permission === 'edit') {
      if (!result.editors.includes(userId)) {
        result.editors.push(userId);
      }
      if (!result.viewers.includes(userId)) {
        result.viewers.push(userId);
      }
    } else if (permission === 'comment') {
      if (!result.editors.includes(userId)) {
        // Don't add to editors, but ensure they can view
        if (!result.viewers.includes(userId)) {
          result.viewers.push(userId);
        }
      }
    } else { // view
      if (!result.viewers.includes(userId)) {
        result.viewers.push(userId);
      }
    }

    result.accessCount += 1; // Increment access count when adding users
    return true;
  }

  /**
   * Remove a user from a shared result
   */
  async removeUserFromSharedResult(sharedResultId: string, userId: string): Promise<boolean> {
    const result = this.sharedResults.get(sharedResultId);
    if (!result) return false;

    // Remove user from all permission lists
    result.viewers = result.viewers.filter(id => id !== userId);
    result.editors = result.editors.filter(id => id !== userId);

    return true;
  }

  /**
   * Get all shared results for a team
   */
  async getTeamSharedResults(teamId: string): Promise<SharedResult[]> {
    return Array.from(this.sharedResults.values())
      .filter(result => result.teamId === teamId && !result.isArchived)
      .sort((a, b) => b.sharedAt.getTime() - a.sharedAt.getTime());
  }

  /**
   * Get all shared results accessible to a user
   */
  async getUserAccessibleResults(userId: string): Promise<SharedResult[]> {
    return Array.from(this.sharedResults.values())
      .filter(result => 
        (result.viewers.includes(userId) || result.editors.includes(userId)) && 
        !result.isArchived &&
        (!result.expirationDate || result.expirationDate > new Date())
      )
      .sort((a, b) => b.sharedAt.getTime() - a.sharedAt.getTime());
  }

  /**
   * Add a comment to a shared result
   */
  async addComment(
    sharedResultId: string,
    authorId: string,
    content: string,
    parentCommentId?: string
  ): Promise<SharedResultComment | null> {
    if (!(await this.canUserAccess(authorId, sharedResultId))) {
      return null;
    }

    const commentId = uuidv4();
    const newComment: SharedResultComment = {
      id: commentId,
      sharedResultId,
      authorId,
      content,
      createdAt: new Date(),
      updatedAt: new Date(),
      resolved: false,
      parentCommentId
    };

    if (!this.comments.has(sharedResultId)) {
      this.comments.set(sharedResultId, []);
    }

    const commentList = this.comments.get(sharedResultId)!;
    commentList.push(newComment);

    // Update access count for the shared result
    const result = this.sharedResults.get(sharedResultId);
    if (result) {
      result.accessCount += 1;
    }

    // Create notification for other collaborators
    await this.createNotification(
      sharedResultId,
      authorId,
      'new_comment',
      `New comment on "${this.sharedResults.get(sharedResultId)?.title || 'shared result'}"`
    );

    return newComment;
  }

  /**
   * Get comments for a shared result
   */
  async getComments(sharedResultId: string): Promise<SharedResultComment[]> {
    return this.comments.get(sharedResultId) || [];
  }

  /**
   * Update a comment
   */
  async updateComment(
    commentId: string,
    sharedResultId: string,
    authorId: string,
    newContent: string
  ): Promise<boolean> {
    const commentList = this.comments.get(sharedResultId) || [];
    const commentIndex = commentList.findIndex(c => c.id === commentId && c.authorId === authorId);

    if (commentIndex === -1) return false;

    commentList[commentIndex].content = newContent;
    commentList[commentIndex].updatedAt = new Date();
    return true;
  }

  /**
   * Delete a comment
   */
  async deleteComment(
    commentId: string,
    sharedResultId: string,
    authorId: string
  ): Promise<boolean> {
    const commentList = this.comments.get(sharedResultId) || [];
    const commentIndex = commentList.findIndex(c => c.id === commentId && c.authorId === authorId);

    if (commentIndex === -1) return false;

    commentList.splice(commentIndex, 1);
    return true;
  }

  /**
   * Log access to a shared result
   */
  async logAccess(
    sharedResultId: string,
    userId: string,
    action: 'view' | 'download' | 'comment' | 'edit',
    metadata?: any
  ): Promise<boolean> {
    const accessLogId = uuidv4();
    const newLog: SharedResultAccessLog = {
      id: accessLogId,
      sharedResultId,
      userId,
      action,
      timestamp: new Date(),
      metadata
    };

    if (!this.accessLogs.has(sharedResultId)) {
      this.accessLogs.set(sharedResultId, []);
    }

    const logList = this.accessLogs.get(sharedResultId)!;
    logList.push(newLog);

    // Update access count for the shared result
    const result = this.sharedResults.get(sharedResultId);
    if (result) {
      result.accessCount += 1;
      result.lastAccessed = new Date();
    }

    return true;
  }

  /**
   * Get access logs for a shared result
   */
  async getAccessLogs(sharedResultId: string): Promise<SharedResultAccessLog[]> {
    return this.accessLogs.get(sharedResultId) || [];
  }

  /**
   * Create a notification
   */
  async createNotification(
    sharedResultId: string,
    userId: string,
    type: 'new_comment' | 'result_updated' | 'access_revoked' | 'mention',
    message: string
  ): Promise<SharedResultNotification | null> {
    const notificationId = uuidv4();
    const newNotification: SharedResultNotification = {
      id: notificationId,
      sharedResultId,
      userId, // The user to notify (in this simplified version, it's the same as the action performer)
      type,
      message,
      read: false,
      createdAt: new Date()
    };

    if (!this.notifications.has(userId)) {
      this.notifications.set(userId, []);
    }

    const notificationList = this.notifications.get(userId)!;
    notificationList.push(newNotification);

    return newNotification;
  }

  /**
   * Get notifications for a user
   */
  async getUserNotifications(userId: string): Promise<SharedResultNotification[]> {
    return this.notifications.get(userId) || [];
  }

  /**
   * Mark a notification as read
   */
  async markNotificationAsRead(notificationId: string, userId: string): Promise<boolean> {
    const notificationList = this.notifications.get(userId) || [];
    const notification = notificationList.find(n => n.id === notificationId);

    if (!notification) return false;

    notification.read = true;
    return true;
  }

  /**
   * Update shared result metadata
   */
  async updateSharedResultMetadata(
    sharedResultId: string,
    userId: string,
    newMetadata: any
  ): Promise<boolean> {
    const result = this.sharedResults.get(sharedResultId);
    if (!result) return false;

    // Check if user has edit permissions
    if (!result.editors.includes(userId)) {
      return false;
    }

    result.metadata = { ...result.metadata, ...newMetadata };
    result.accessCount += 1; // Increment access count when updating

    // Create notification for other collaborators
    await this.createNotification(
      sharedResultId,
      userId,
      'result_updated',
      `Shared result "${result.title}" has been updated`
    );

    return true;
  }

  /**
   * Archive a shared result
   */
  async archiveSharedResult(sharedResultId: string, userId: string): Promise<boolean> {
    const result = this.sharedResults.get(sharedResultId);
    if (!result) return false;

    // Only editors or the original sharer can archive
    if (result.sharedBy !== userId && !result.editors.includes(userId)) {
      return false;
    }

    result.isArchived = true;
    return true;
  }

  /**
   * Search shared results by tags or title
   */
  async searchSharedResults(
    userId: string,
    searchTerm: string,
    tags?: string[]
  ): Promise<SharedResult[]> {
    const userResults = await this.getUserAccessibleResults(userId);
    
    return userResults.filter(result => {
      // Check search term in title or description
      const matchesSearch = !searchTerm || 
        result.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (result.description && result.description.toLowerCase().includes(searchTerm.toLowerCase()));
      
      // Check tags
      const matchesTags = !tags || tags.every(tag => result.tags.includes(tag));
      
      return matchesSearch && matchesTags;
    });
  }

  /**
   * Get shared result statistics for a team
   */
  async getTeamStats(teamId: string) {
    const teamResults = await this.getTeamSharedResults(teamId);
    
    return {
      totalShared: teamResults.length,
      totalViews: teamResults.reduce((sum, result) => sum + result.accessCount, 0),
      totalComments: Array.from(this.comments.values()).flat().length,
      activeResults: teamResults.filter(r => !r.isArchived).length
    };
  }
}

// Singleton instance
export const sharedResultsManager = new SharedResultsManager();

export default sharedResultsManager;