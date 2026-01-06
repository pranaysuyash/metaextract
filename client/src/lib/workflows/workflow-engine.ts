/**
 * Workflow Automation System - Visual workflow builder and execution engine
 */

import { v4 as uuidv4 } from 'uuid';

export interface Workflow {
  id: string;
  name: string;
  description: string;
  userId: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  triggers: WorkflowTrigger[];
  actions: WorkflowAction[];
  conditions: WorkflowCondition[];
  variables: WorkflowVariable[];
  executionCount: number;
  lastExecutedAt?: Date;
  errorCount: number;
  lastError?: string;
}

export interface WorkflowTrigger {
  id: string;
  type:
    | 'file_uploaded'
    | 'extraction_completed'
    | 'schedule'
    | 'manual'
    | 'webhook';
  config: Record<string, any>;
  enabled: boolean;
}

export interface WorkflowAction {
  id: string;
  type:
    | 'send_email'
    | 'export_data'
    | 'call_webhook'
    | 'update_database'
    | 'notify_user';
  config: Record<string, any>;
  nextActionId?: string; // For sequential execution
  enabled: boolean;
}

export interface WorkflowCondition {
  id: string;
  type: 'field_value' | 'file_type' | 'processing_time' | 'confidence_score';
  operator:
    | 'equals'
    | 'not_equals'
    | 'greater_than'
    | 'less_than'
    | 'contains'
    | 'matches_regex';
  field: string;
  value: any;
  nextActionId: string;
  elseActionId?: string;
  enabled: boolean;
}

export interface WorkflowVariable {
  id: string;
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  defaultValue: any;
  description: string;
}

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  triggerEvent: any;
  startedAt: Date;
  completedAt?: Date;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  results: any[];
  error?: string;
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  triggers: WorkflowTrigger[];
  actions: WorkflowAction[];
  conditions: WorkflowCondition[];
  variables: WorkflowVariable[];
  isBuiltIn: boolean;
}

export class WorkflowAutomation {
  private workflows: Map<string, Workflow> = new Map();
  private executions: Map<string, WorkflowExecution> = new Map();
  private templates: WorkflowTemplate[] = [];
  private activeExecutions: Set<string> = new Set();

  constructor() {
    this.initializeBuiltInTemplates();
  }

  /**
   * Initialize built-in workflow templates
   */
  private initializeBuiltInTemplates(): void {
    this.templates = [
      {
        id: 'template-email-notification',
        name: 'Email Notification on Extraction Complete',
        description:
          'Send an email notification when metadata extraction is completed',
        category: 'notifications',
        isBuiltIn: true,
        triggers: [
          {
            id: 'trigger-extraction-complete',
            type: 'extraction_completed',
            config: {},
            enabled: true,
          },
        ],
        actions: [
          {
            id: 'action-send-email',
            type: 'send_email',
            config: {
              to: '{{user.email}}',
              subject: 'Metadata extraction completed for {{file.name}}',
              body: 'Your metadata extraction for {{file.name}} is complete. View results at: {{result.url}}',
            },
            enabled: true,
          },
        ],
        conditions: [],
        variables: [
          {
            id: 'var-user-email',
            name: 'user.email',
            type: 'string',
            defaultValue: '',
            description: 'Email of the user who initiated the extraction',
          },
          {
            id: 'var-file-name',
            name: 'file.name',
            type: 'string',
            defaultValue: '',
            description: 'Name of the file that was processed',
          },
          {
            id: 'var-result-url',
            name: 'result.url',
            type: 'string',
            defaultValue: '',
            description: 'URL to view the extraction results',
          },
        ],
      },
      {
        id: 'template-webhook-on-gps-found',
        name: 'Webhook on GPS Data Found',
        description:
          'Call a webhook when GPS coordinates are found in metadata',
        category: 'integrations',
        isBuiltIn: true,
        triggers: [
          {
            id: 'trigger-file-uploaded',
            type: 'file_uploaded',
            config: {},
            enabled: true,
          },
        ],
        actions: [
          {
            id: 'action-call-webhook',
            type: 'call_webhook',
            config: {
              url: '{{webhook.url}}',
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: {
                event: 'gps_found',
                file: '{{file}}',
                gps_coordinates: '{{metadata.gps}}',
                timestamp: '{{timestamp}}',
              },
            },
            enabled: true,
          },
        ],
        conditions: [
          {
            id: 'condition-gps-present',
            type: 'field_value',
            operator: 'not_equals',
            field: 'metadata.gps.latitude',
            value: null,
            nextActionId: 'action-call-webhook',
            enabled: true,
          },
        ],
        variables: [
          {
            id: 'var-webhook-url',
            name: 'webhook.url',
            type: 'string',
            defaultValue: '',
            description: 'URL of the webhook endpoint',
          },
          {
            id: 'var-file',
            name: 'file',
            type: 'object',
            defaultValue: {},
            description: 'File object containing metadata',
          },
          {
            id: 'var-metadata-gps',
            name: 'metadata.gps',
            type: 'object',
            defaultValue: {},
            description: 'GPS metadata from the file',
          },
          {
            id: 'var-timestamp',
            name: 'timestamp',
            type: 'string',
            defaultValue: new Date().toISOString(),
            description: 'Timestamp of the event',
          },
        ],
      },
      {
        id: 'template-batch-export',
        name: 'Batch Export on Schedule',
        description:
          'Automatically export metadata for all files in a folder on a schedule',
        category: 'automation',
        isBuiltIn: true,
        triggers: [
          {
            id: 'trigger-schedule',
            type: 'schedule',
            config: {
              cron: '0 9 * * 1', // Every Monday at 9 AM
              timezone: 'UTC',
            },
            enabled: true,
          },
        ],
        actions: [
          {
            id: 'action-export-data',
            type: 'export_data',
            config: {
              format: 'json',
              destination: 'folder',
              folderPath: '{{export.folder}}',
            },
            enabled: true,
          },
        ],
        conditions: [],
        variables: [
          {
            id: 'var-export-folder',
            name: 'export.folder',
            type: 'string',
            defaultValue: '/exports/weekly',
            description: 'Folder path for exporting data',
          },
        ],
      },
    ];
  }

  /**
   * Create a new workflow
   */
  async createWorkflow(
    userId: string,
    name: string,
    description: string,
    config: {
      triggers: WorkflowTrigger[];
      actions: WorkflowAction[];
      conditions?: WorkflowCondition[];
      variables?: WorkflowVariable[];
    }
  ): Promise<Workflow> {
    const workflow: Workflow = {
      id: uuidv4(),
      name,
      description,
      userId,
      isActive: true,
      createdAt: new Date(),
      updatedAt: new Date(),
      triggers: config.triggers,
      actions: config.actions,
      conditions: config.conditions || [],
      variables: config.variables || [],
      executionCount: 0,
      errorCount: 0,
    };

    this.workflows.set(workflow.id, workflow);
    return workflow;
  }

  /**
   * Get a workflow by ID
   */
  async getWorkflow(
    workflowId: string,
    userId: string
  ): Promise<Workflow | null> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow || workflow.userId !== userId) {
      return null;
    }
    return workflow;
  }

  /**
   * Update a workflow
   */
  async updateWorkflow(
    workflowId: string,
    userId: string,
    updates: Partial<Workflow>
  ): Promise<boolean> {
    const workflow = await this.getWorkflow(workflowId, userId);
    if (!workflow) return false;

    Object.assign(workflow, updates, { updatedAt: new Date() });
    return true;
  }

  /**
   * Delete a workflow
   */
  async deleteWorkflow(workflowId: string, userId: string): Promise<boolean> {
    const workflow = await this.getWorkflow(workflowId, userId);
    if (!workflow) return false;

    this.workflows.delete(workflowId);
    return true;
  }

  /**
   * Activate a workflow
   */
  async activateWorkflow(workflowId: string, userId: string): Promise<boolean> {
    const workflow = await this.getWorkflow(workflowId, userId);
    if (!workflow) return false;

    workflow.isActive = true;
    workflow.updatedAt = new Date();
    return true;
  }

  /**
   * Deactivate a workflow
   */
  async deactivateWorkflow(
    workflowId: string,
    userId: string
  ): Promise<boolean> {
    const workflow = await this.getWorkflow(workflowId, userId);
    if (!workflow) return false;

    workflow.isActive = false;
    workflow.updatedAt = new Date();
    return true;
  }

  /**
   * Get user workflows
   */
  async getUserWorkflows(userId: string): Promise<Workflow[]> {
    return Array.from(this.workflows.values()).filter(w => w.userId === userId);
  }

  /**
   * Get workflow templates
   */
  async getTemplates(category?: string): Promise<WorkflowTemplate[]> {
    if (category) {
      return this.templates.filter(t => t.category === category);
    }
    return [...this.templates];
  }

  /**
   * Execute a workflow manually
   */
  async executeWorkflow(
    workflowId: string,
    userId: string,
    triggerEvent: any
  ): Promise<WorkflowExecution> {
    const workflow = await this.getWorkflow(workflowId, userId);
    if (!workflow || !workflow.isActive) {
      throw new Error('Workflow not found or not active');
    }

    const executionId = uuidv4();
    const execution: WorkflowExecution = {
      id: executionId,
      workflowId,
      triggerEvent,
      startedAt: new Date(),
      status: 'running',
      results: [],
    };

    this.executions.set(executionId, execution);
    this.activeExecutions.add(executionId);

    try {
      // Process workflow triggers
      for (const trigger of workflow.triggers) {
        if (!trigger.enabled) continue;

        // Check if trigger matches the event
        if (this.isTriggerMatch(trigger, triggerEvent)) {
          // Execute workflow actions
          const result = await this.executeActions(workflow, triggerEvent);
          execution.results.push(result);
        }
      }

      execution.status = 'completed';
      execution.completedAt = new Date();
      workflow.executionCount++;
      workflow.lastExecutedAt = new Date();
    } catch (error) {
      execution.status = 'failed';
      execution.completedAt = new Date();
      execution.error = (error as Error).message;
      workflow.errorCount++;
      workflow.lastError = (error as Error).message;
    } finally {
      this.activeExecutions.delete(executionId);
      workflow.updatedAt = new Date();
    }

    return execution;
  }

  /**
   * Check if a trigger matches an event
   */
  private isTriggerMatch(trigger: WorkflowTrigger, event: any): boolean {
    switch (trigger.type) {
      case 'file_uploaded':
        return event.type === 'file_uploaded';
      case 'extraction_completed':
        return event.type === 'extraction_completed';
      case 'webhook':
        return (
          event.type === 'webhook' && event.source === trigger.config.source
        );
      case 'schedule':
        // For scheduled triggers, we'd check against cron schedule
        // This is a simplified implementation
        return true;
      case 'manual':
        // Manual triggers are always considered matching when executed manually
        return true;
      default:
        return false;
    }
  }

  /**
   * Execute workflow actions
   */
  private async executeActions(
    workflow: Workflow,
    triggerEvent: any
  ): Promise<any> {
    // Create context with variables and event data
    const context: Record<string, any> = {
      ...this.createVariableContext(workflow.variables),
      event: triggerEvent,
      timestamp: new Date().toISOString(),
    };

    let result = null;

    // Execute actions sequentially
    for (const action of workflow.actions) {
      if (!action.enabled) continue;

      try {
        result = await this.executeAction(action, context);
        (context as Record<string, any>)[action.id] = result; // Store result in context for next action
      } catch (error) {
        console.error(`Error executing action ${action.id}:`, error);
        throw error;
      }
    }

    return result;
  }

  /**
   * Execute a single action
   */
  private async executeAction(
    action: WorkflowAction,
    context: any
  ): Promise<any> {
    // Replace variables in action config
    const resolvedConfig = this.resolveVariables(action.config, context);

    switch (action.type) {
      case 'send_email':
        return await this.executeEmailAction(resolvedConfig);
      case 'export_data':
        return await this.executeExportAction(resolvedConfig);
      case 'call_webhook':
        return await this.executeWebhookAction(resolvedConfig);
      case 'update_database':
        return await this.executeDatabaseAction(resolvedConfig);
      case 'notify_user':
        return await this.executeNotificationAction(resolvedConfig);
      default:
        throw new Error(`Unknown action type: ${action.type}`);
    }
  }

  /**
   * Execute email action
   */
  private async executeEmailAction(config: any): Promise<boolean> {
    // In a real implementation, this would send an email
    console.log('Sending email:', config);
    return true;
  }

  /**
   * Execute export action
   */
  private async executeExportAction(config: any): Promise<any> {
    // In a real implementation, this would export data
    console.log('Exporting data:', config);
    return { success: true, exportedAt: new Date() };
  }

  /**
   * Execute webhook action
   */
  private async executeWebhookAction(config: any): Promise<any> {
    // In a real implementation, this would call a webhook
    console.log('Calling webhook:', config);
    return { success: true, response: 'Webhook called successfully' };
  }

  /**
   * Execute database action
   */
  private async executeDatabaseAction(config: any): Promise<any> {
    // In a real implementation, this would update a database
    console.log('Updating database:', config);
    return { success: true, recordsAffected: 1 };
  }

  /**
   * Execute notification action
   */
  private async executeNotificationAction(config: any): Promise<any> {
    // In a real implementation, this would send a notification
    console.log('Sending notification:', config);
    return { success: true, notificationId: uuidv4() };
  }

  /**
   * Create variable context from workflow variables
   */
  private createVariableContext(
    variables: WorkflowVariable[]
  ): Record<string, any> {
    const context: Record<string, any> = {};

    for (const variable of variables) {
      context[variable.name] = variable.defaultValue;
    }

    return context;
  }

  /**
   * Resolve variables in a configuration object
   */
  private resolveVariables(config: any, context: any): any {
    if (typeof config === 'string') {
      // Simple variable replacement: {{variable.name}}
      return config.replace(/\{\{([^}]+)\}\}/g, (match, varName) => {
        return context[varName.trim()] || match;
      });
    } else if (Array.isArray(config)) {
      return config.map(item => this.resolveVariables(item, context));
    } else if (typeof config === 'object' && config !== null) {
      const resolved: Record<string, any> = {};
      for (const [key, value] of Object.entries(config)) {
        resolved[key] = this.resolveVariables(value, context);
      }
      return resolved;
    }
    return config;
  }

  /**
   * Get workflow execution history
   */
  async getExecutionHistory(
    workflowId: string,
    userId: string,
    limit: number = 50
  ): Promise<WorkflowExecution[]> {
    const workflow = await this.getWorkflow(workflowId, userId);
    if (!workflow) return [];

    return Array.from(this.executions.values())
      .filter(e => e.workflowId === workflowId)
      .sort((a, b) => b.startedAt.getTime() - a.startedAt.getTime())
      .slice(0, limit);
  }

  /**
   * Get workflow statistics
   */
  async getWorkflowStats(
    workflowId: string,
    userId: string
  ): Promise<{
    totalExecutions: number;
    successfulExecutions: number;
    failedExecutions: number;
    successRate: number;
    avgExecutionTime: number;
    lastExecution: Date | null;
  } | null> {
    const workflow = await this.getWorkflow(workflowId, userId);
    if (!workflow) return null;

    const executions = await this.getExecutionHistory(workflowId, userId, 1000);

    const total = executions.length;
    const successful = executions.filter(e => e.status === 'completed').length;
    const failed = executions.filter(e => e.status === 'failed').length;

    const successRate = total > 0 ? (successful / total) * 100 : 0;

    const avgExecutionTime =
      executions.length > 0
        ? executions.reduce((sum, e) => {
            if (e.completedAt && e.startedAt) {
              return sum + (e.completedAt.getTime() - e.startedAt.getTime());
            }
            return sum;
          }, 0) / executions.length
        : 0;

    const lastExecution =
      executions.length > 0 ? executions[0].startedAt : null;

    return {
      totalExecutions: total,
      successfulExecutions: successful,
      failedExecutions: failed,
      successRate,
      avgExecutionTime,
      lastExecution,
    };
  }

  /**
   * Create workflow from template
   */
  async createFromTemplate(
    templateId: string,
    userId: string,
    name: string,
    configOverrides: Partial<Workflow> = {}
  ): Promise<Workflow> {
    const template = this.templates.find(t => t.id === templateId);
    if (!template) {
      throw new Error(`Template not found: ${templateId}`);
    }

    const workflow: Workflow = {
      id: uuidv4(),
      name,
      description: template.description,
      userId,
      isActive: true,
      createdAt: new Date(),
      updatedAt: new Date(),
      triggers: JSON.parse(JSON.stringify(template.triggers)), // Deep clone
      actions: JSON.parse(JSON.stringify(template.actions)), // Deep clone
      conditions: JSON.parse(JSON.stringify(template.conditions || [])), // Deep clone
      variables: JSON.parse(JSON.stringify(template.variables || [])), // Deep clone
      executionCount: 0,
      errorCount: 0,
      ...configOverrides,
    };

    this.workflows.set(workflow.id, workflow);
    return workflow;
  }

  /**
   * Validate workflow configuration
   */
  async validateWorkflow(
    workflow: Workflow
  ): Promise<{ isValid: boolean; errors: string[] }> {
    const errors: string[] = [];

    // Validate triggers
    if (!workflow.triggers || workflow.triggers.length === 0) {
      errors.push('Workflow must have at least one trigger');
    }

    // Validate actions
    if (!workflow.actions || workflow.actions.length === 0) {
      errors.push('Workflow must have at least one action');
    }

    // Validate trigger/action references in conditions
    for (const condition of workflow.conditions) {
      if (
        condition.nextActionId &&
        !workflow.actions.some(a => a.id === condition.nextActionId)
      ) {
        errors.push(
          `Condition ${condition.id} references non-existent action: ${condition.nextActionId}`
        );
      }
      if (
        condition.elseActionId &&
        !workflow.actions.some(a => a.id === condition.elseActionId)
      ) {
        errors.push(
          `Condition ${condition.id} references non-existent else action: ${condition.elseActionId}`
        );
      }
    }

    // Validate action sequence references
    for (const action of workflow.actions) {
      if (
        action.nextActionId &&
        !workflow.actions.some(a => a.id === action.nextActionId)
      ) {
        errors.push(
          `Action ${action.id} references non-existent next action: ${action.nextActionId}`
        );
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Get active workflow count for a user
   */
  async getActiveWorkflowCount(userId: string): Promise<number> {
    return Array.from(this.workflows.values()).filter(
      w => w.userId === userId && w.isActive
    ).length;
  }
}

// Singleton instance
export const workflowAutomation = new WorkflowAutomation();

export default workflowAutomation;
