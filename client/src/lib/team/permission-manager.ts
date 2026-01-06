/**
 * Permission Manager - Role-based access control for teams
 */

export interface Permission {
  id: string;
  name: string;
  description: string;
  resource: string;
  action: string;
  attributes?: string[];
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[]; // Permission IDs
  systemRole: boolean; // Whether this is a built-in system role
}

export interface UserTeamRole {
  userId: string;
  teamId: string;
  roleId: string;
  assignedAt: Date;
  assignedBy: string;
}

export interface ResourceAccess {
  resourceId: string;
  resourceType: string;
  teamId: string;
  allowedActions: string[];
  allowedAttributes?: string[];
}

export class PermissionManager {
  private roles: Map<string, Role> = new Map();
  private permissions: Map<string, Permission> = new Map();
  private userTeamRoles: Map<string, UserTeamRole[]> = new Map(); // userId -> roles
  private resourceAccess: Map<string, ResourceAccess[]> = new Map(); // teamId -> resources

  constructor() {
    this.initializeDefaultRoles();
    this.initializeDefaultPermissions();
  }

  /**
   * Initialize default roles
   */
  private initializeDefaultRoles(): void {
    const defaultRoles: Role[] = [
      {
        id: 'role-admin',
        name: 'Administrator',
        description: 'Full access to all team resources',
        permissions: [
          'team.manage',
          'member.manage',
          'resource.create',
          'resource.read',
          'resource.update',
          'resource.delete',
          'settings.manage'
        ],
        systemRole: true
      },
      {
        id: 'role-editor',
        name: 'Editor',
        description: 'Can create, read, and update team resources',
        permissions: [
          'resource.create',
          'resource.read',
          'resource.update',
          'member.read'
        ],
        systemRole: true
      },
      {
        id: 'role-viewer',
        name: 'Viewer',
        description: 'Can only read team resources',
        permissions: [
          'resource.read',
          'member.read'
        ],
        systemRole: true
      }
    ];

    defaultRoles.forEach(role => {
      this.roles.set(role.id, role);
    });
  }

  /**
   * Initialize default permissions
   */
  private initializeDefaultPermissions(): void {
    const defaultPermissions: Permission[] = [
      {
        id: 'team.manage',
        name: 'Manage Team',
        description: 'Full control over team settings and members',
        resource: 'team',
        action: 'manage'
      },
      {
        id: 'member.manage',
        name: 'Manage Members',
        description: 'Add, remove, and modify team members',
        resource: 'member',
        action: 'manage'
      },
      {
        id: 'member.read',
        name: 'Read Members',
        description: 'View team member information',
        resource: 'member',
        action: 'read'
      },
      {
        id: 'resource.create',
        name: 'Create Resources',
        description: 'Create new resources in the team',
        resource: 'resource',
        action: 'create'
      },
      {
        id: 'resource.read',
        name: 'Read Resources',
        description: 'View resources in the team',
        resource: 'resource',
        action: 'read'
      },
      {
        id: 'resource.update',
        name: 'Update Resources',
        description: 'Modify existing resources in the team',
        resource: 'resource',
        action: 'update'
      },
      {
        id: 'resource.delete',
        name: 'Delete Resources',
        description: 'Remove resources from the team',
        resource: 'resource',
        action: 'delete'
      },
      {
        id: 'settings.manage',
        name: 'Manage Settings',
        description: 'Change team settings and configurations',
        resource: 'settings',
        action: 'manage'
      }
    ];

    defaultPermissions.forEach(permission => {
      this.permissions.set(permission.id, permission);
    });
  }

  /**
   * Assign a role to a user in a team
   */
  async assignRole(userId: string, teamId: string, roleId: string, assignedBy: string): Promise<boolean> {
    const role = this.roles.get(roleId);
    if (!role) {
      console.error(`Role with ID ${roleId} not found`);
      return false;
    }

    // Get existing roles for user
    let userRoles = this.userTeamRoles.get(userId) || [];
    
    // Check if user already has a role in this team
    const existingRoleIndex = userRoles.findIndex(ur => ur.teamId === teamId);
    
    if (existingRoleIndex !== -1) {
      // Update existing role
      userRoles[existingRoleIndex] = {
        userId,
        teamId,
        roleId,
        assignedAt: new Date(),
        assignedBy
      };
    } else {
      // Add new role
      userRoles.push({
        userId,
        teamId,
        roleId,
        assignedAt: new Date(),
        assignedBy
      });
    }

    this.userTeamRoles.set(userId, userRoles);
    return true;
  }

  /**
   * Remove a role from a user in a team
   */
  async removeRole(userId: string, teamId: string): Promise<boolean> {
    const userRoles = this.userTeamRoles.get(userId) || [];
    const filteredRoles = userRoles.filter(ur => ur.teamId !== teamId);
    
    if (filteredRoles.length !== userRoles.length) {
      this.userTeamRoles.set(userId, filteredRoles);
      return true;
    }
    
    return false;
  }

  /**
   * Check if a user has a specific permission in a team
   */
  async hasPermission(userId: string, teamId: string, permissionId: string): Promise<boolean> {
    // Get user's role in the team
    const userRoles = this.userTeamRoles.get(userId) || [];
    const userTeamRole = userRoles.find(ur => ur.teamId === teamId);
    
    if (!userTeamRole) {
      return false;
    }

    // Get the role
    const role = this.roles.get(userTeamRole.roleId);
    if (!role) {
      return false;
    }

    // Check if the role has the required permission
    return role.permissions.includes(permissionId);
  }

  /**
   * Check if a user can perform an action on a resource
   */
  async canUserPerformAction(
    userId: string,
    teamId: string,
    resourceType: string,
    action: string
  ): Promise<boolean> {
    // Construct permission ID based on resource and action
    const permissionId = `${resourceType}.${action}`;
    
    return await this.hasPermission(userId, teamId, permissionId);
  }

  /**
   * Get all permissions for a user in a team
   */
  async getUserPermissions(userId: string, teamId: string): Promise<Permission[]> {
    const userRoles = this.userTeamRoles.get(userId) || [];
    const userTeamRole = userRoles.find(ur => ur.teamId === teamId);
    
    if (!userTeamRole) {
      return [];
    }

    const role = this.roles.get(userTeamRole.roleId);
    if (!role) {
      return [];
    }

    return role.permissions
      .map(permissionId => this.permissions.get(permissionId))
      .filter((permission): permission is Permission => permission !== undefined);
  }

  /**
   * Get all roles for a user in a team
   */
  async getUserRoles(userId: string, teamId: string): Promise<Role[]> {
    const userRoles = this.userTeamRoles.get(userId) || [];
    const userTeamRole = userRoles.find(ur => ur.teamId === teamId);
    
    if (!userTeamRole) {
      return [];
    }

    const role = this.roles.get(userTeamRole.roleId);
    if (!role) {
      return [];
    }

    return [role];
  }

  /**
   * Create a custom role
   */
  async createCustomRole(
    name: string,
    description: string,
    permissions: string[],
    teamId: string
  ): Promise<Role | null> {
    // Validate permissions exist
    for (const permId of permissions) {
      if (!this.permissions.has(permId)) {
        console.error(`Permission ${permId} does not exist`);
        return null;
      }
    }

    const roleId = `role-${teamId}-${Date.now()}`;
    const newRole: Role = {
      id: roleId,
      name,
      description,
      permissions,
      systemRole: false
    };

    this.roles.set(roleId, newRole);
    return newRole;
  }

  /**
   * Update a custom role
   */
  async updateRole(roleId: string, updates: Partial<Role>): Promise<boolean> {
    const role = this.roles.get(roleId);
    if (!role || role.systemRole) {
      // Cannot update system roles
      return false;
    }

    // If updating permissions, validate them
    if (updates.permissions) {
      for (const permId of updates.permissions) {
        if (!this.permissions.has(permId)) {
          console.error(`Permission ${permId} does not exist`);
          return false;
        }
      }
    }

    Object.assign(role, updates);
    return true;
  }

  /**
   * Delete a custom role
   */
  async deleteRole(roleId: string): Promise<boolean> {
    const role = this.roles.get(roleId);
    if (!role || role.systemRole) {
      // Cannot delete system roles
      return false;
    }

    // Check if any users have this role
    for (const [userId, userRoles] of this.userTeamRoles) {
      if (userRoles.some(ur => ur.roleId === roleId)) {
        // Move users to default role (viewer) or return error
        const updatedRoles = userRoles.filter(ur => ur.roleId !== roleId);
        this.userTeamRoles.set(userId, updatedRoles);
      }
    }

    this.roles.delete(roleId);
    return true;
  }

  /**
   * Get all roles in a team
   */
  async getTeamRoles(teamId: string): Promise<Role[]> {
    // For system roles, return all of them
    // For custom roles, we'd need to track which roles belong to which team
    // In this simplified version, we'll return all roles
    return Array.from(this.roles.values());
  }

  /**
   * Get all system roles
   */
  getSystemRoles(): Role[] {
    return Array.from(this.roles.values()).filter(role => role.systemRole);
  }

  /**
   * Get all custom roles for a team
   */
  getCustomRoles(teamId: string): Role[] {
    // In a real implementation, we'd track which custom roles belong to which team
    // For now, return all non-system roles
    return Array.from(this.roles.values()).filter(role => !role.systemRole);
  }

  /**
   * Get all permissions
   */
  getAllPermissions(): Permission[] {
    return Array.from(this.permissions.values());
  }

  /**
   * Create a new permission
   */
  async createPermission(
    name: string,
    description: string,
    resource: string,
    action: string
  ): Promise<Permission | null> {
    // Generate a unique ID for the permission
    const permissionId = `perm-${resource}-${action}-${Date.now()}`;
    
    const newPermission: Permission = {
      id: permissionId,
      name,
      description,
      resource,
      action
    };

    this.permissions.set(permissionId, newPermission);
    return newPermission;
  }

  /**
   * Check multiple permissions at once
   */
  async checkMultiplePermissions(
    userId: string,
    teamId: string,
    permissionIds: string[]
  ): Promise<Record<string, boolean>> {
    const results: Record<string, boolean> = {};
    
    for (const permId of permissionIds) {
      results[permId] = await this.hasPermission(userId, teamId, permId);
    }
    
    return results;
  }

  /**
   * Get effective permissions for a user in a team
   * This would combine role-based permissions with any direct resource permissions
   */
  async getEffectivePermissions(userId: string, teamId: string): Promise<Permission[]> {
    // Get role-based permissions
    const rolePermissions = await this.getUserPermissions(userId, teamId);
    
    // In a real implementation, we'd also check for direct resource permissions
    // For now, just return role-based permissions
    return rolePermissions;
  }
}

// Singleton instance
export const permissionManager = new PermissionManager();

export default permissionManager;