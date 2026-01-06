/**
 * Team Manager - Team creation and management
 */

import { v4 as uuidv4 } from 'uuid';

export interface TeamMember {
  id: string;
  userId: string;
  email: string;
  name: string;
  role: 'admin' | 'editor' | 'viewer';
  joinedAt: Date;
  lastActive?: Date;
  isActive: boolean;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  ownerId: string;
  members: TeamMember[];
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
  settings: {
    allowFileSharing: boolean;
    allowResultSharing: boolean;
    requireApproval: boolean;
    maxMembers: number;
  };
}

export interface TeamInvitation {
  id: string;
  teamId: string;
  email: string;
  role: 'admin' | 'editor' | 'viewer';
  inviterId: string;
  createdAt: Date;
  expiresAt: Date;
  status: 'pending' | 'accepted' | 'declined' | 'expired';
}

export class TeamManager {
  private teams: Map<string, Team> = new Map();
  private invitations: Map<string, TeamInvitation> = new Map();

  /**
   * Create a new team
   */
  async createTeam(
    name: string,
    description: string | undefined,
    ownerId: string
  ): Promise<Team> {
    const teamId = uuidv4();
    const newTeam: Team = {
      id: teamId,
      name,
      description,
      ownerId,
      members: [
        {
          id: uuidv4(),
          userId: ownerId,
          email: '', // Will be populated from user profile
          name: '', // Will be populated from user profile
          role: 'admin',
          joinedAt: new Date(),
          isActive: true
        }
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
      isActive: true,
      settings: {
        allowFileSharing: true,
        allowResultSharing: true,
        requireApproval: false,
        maxMembers: 10
      }
    };

    this.teams.set(teamId, newTeam);
    return newTeam;
  }

  /**
   * Get a team by ID
   */
  async getTeam(teamId: string): Promise<Team | null> {
    return this.teams.get(teamId) || null;
  }

  /**
   * Update team details
   */
  async updateTeam(
    teamId: string,
    updates: Partial<Omit<Team, 'id' | 'ownerId' | 'members' | 'createdAt' | 'updatedAt'>>
  ): Promise<boolean> {
    const team = this.teams.get(teamId);
    if (!team) return false;

    Object.assign(team, updates, { updatedAt: new Date() });
    return true;
  }

  /**
   * Delete a team
   */
  async deleteTeam(teamId: string): Promise<boolean> {
    const team = this.teams.get(teamId);
    if (!team) return false;

    // Only owner can delete team
    // In a real implementation, you'd check permissions
    this.teams.delete(teamId);
    return true;
  }

  /**
   * Add a member to a team
   */
  async addMember(
    teamId: string,
    userId: string,
    email: string,
    name: string,
    role: 'admin' | 'editor' | 'viewer'
  ): Promise<boolean> {
    const team = this.teams.get(teamId);
    if (!team) return false;

    // Check if user is already a member
    if (team.members.some(member => member.userId === userId)) {
      return false;
    }

    // Check if team has reached max members
    if (team.members.length >= team.settings.maxMembers) {
      return false;
    }

    const newMember: TeamMember = {
      id: uuidv4(),
      userId,
      email,
      name,
      role,
      joinedAt: new Date(),
      isActive: true
    };

    team.members.push(newMember);
    team.updatedAt = new Date();
    return true;
  }

  /**
   * Update a team member's role
   */
  async updateMemberRole(
    teamId: string,
    userId: string,
    newRole: 'admin' | 'editor' | 'viewer'
  ): Promise<boolean> {
    const team = this.teams.get(teamId);
    if (!team) return false;

    const member = team.members.find(m => m.userId === userId);
    if (!member) return false;

    member.role = newRole;
    team.updatedAt = new Date();
    return true;
  }

  /**
   * Remove a member from a team
   */
  async removeMember(teamId: string, userId: string): Promise<boolean> {
    const team = this.teams.get(teamId);
    if (!team) return false;

    // Don't allow removing the owner
    if (team.ownerId === userId) {
      return false;
    }

    const initialLength = team.members.length;
    team.members = team.members.filter(member => member.userId !== userId);
    
    if (team.members.length !== initialLength) {
      team.updatedAt = new Date();
      return true;
    }

    return false;
  }

  /**
   * Invite a user to a team
   */
  async inviteUser(
    teamId: string,
    email: string,
    role: 'admin' | 'editor' | 'viewer',
    inviterId: string
  ): Promise<TeamInvitation | null> {
    const team = this.teams.get(teamId);
    if (!team) return null;

    // Check if user is already a member
    if (team.members.some(member => member.email === email)) {
      return null;
    }

    // Check if there's already a pending invitation
    const existingInvitation = Array.from(this.invitations.values()).find(
      inv => inv.teamId === teamId && inv.email === email && inv.status === 'pending'
    );
    if (existingInvitation) {
      return null;
    }

    const invitationId = uuidv4();
    const newInvitation: TeamInvitation = {
      id: invitationId,
      teamId,
      email,
      role,
      inviterId,
      createdAt: new Date(),
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
      status: 'pending'
    };

    this.invitations.set(invitationId, newInvitation);
    return newInvitation;
  }

  /**
   * Accept an invitation
   */
  async acceptInvitation(invitationId: string, userId: string, name: string): Promise<boolean> {
    const invitation = this.invitations.get(invitationId);
    if (!invitation || invitation.status !== 'pending') {
      return false;
    }

    // Check if invitation is expired
    if (invitation.expiresAt < new Date()) {
      invitation.status = 'expired';
      return false;
    }

    const team = this.teams.get(invitation.teamId);
    if (!team) return false;

    // Add user to team
    const success = await this.addMember(
      invitation.teamId,
      userId,
      invitation.email,
      name,
      invitation.role
    );

    if (success) {
      invitation.status = 'accepted';
      return true;
    }

    return false;
  }

  /**
   * Decline an invitation
   */
  async declineInvitation(invitationId: string): Promise<boolean> {
    const invitation = this.invitations.get(invitationId);
    if (!invitation || invitation.status !== 'pending') {
      return false;
    }

    invitation.status = 'declined';
    return true;
  }

  /**
   * Get invitations for a user
   */
  async getUserInvitations(email: string): Promise<TeamInvitation[]> {
    return Array.from(this.invitations.values()).filter(
      inv => inv.email === email && inv.status === 'pending'
    );
  }

  /**
   * Get teams for a user
   */
  async getUserTeams(userId: string): Promise<Team[]> {
    return Array.from(this.teams.values()).filter(
      team => team.members.some(member => member.userId === userId)
    );
  }

  /**
   * Get team members
   */
  async getTeamMembers(teamId: string): Promise<TeamMember[]> {
    const team = this.teams.get(teamId);
    if (!team) return [];

    return [...team.members];
  }

  /**
   * Update team settings
   */
  async updateTeamSettings(
    teamId: string,
    settings: Partial<Team['settings']>
  ): Promise<boolean> {
    const team = this.teams.get(teamId);
    if (!team) return false;

    Object.assign(team.settings, settings);
    team.updatedAt = new Date();
    return true;
  }

  /**
   * Check if user has permission in team
   */
  hasPermission(
    team: Team,
    userId: string,
    requiredRole: 'admin' | 'editor' | 'viewer'
  ): boolean {
    const member = team.members.find(m => m.userId === userId);
    if (!member) return false;

    const roleHierarchy: Record<string, number> = {
      viewer: 1,
      editor: 2,
      admin: 3
    };

    return roleHierarchy[member.role] >= roleHierarchy[requiredRole];
  }

  /**
   * Get all teams
   */
  getAllTeams(): Team[] {
    return Array.from(this.teams.values());
  }

  /**
   * Get invitation by ID
   */
  getInvitation(invitationId: string): TeamInvitation | undefined {
    return this.invitations.get(invitationId);
  }
}

// Singleton instance
export const teamManager = new TeamManager();

export default teamManager;