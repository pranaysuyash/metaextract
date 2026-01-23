/**
 * Tests for Workflow Automation Engine
 *
 * Tests the WorkflowAutomation class including:
 * - Workflow CRUD operations
 * - Workflow activation/deactivation
 * - Workflow execution
 * - Template usage
 * - Validation
 */

import { v4 as uuidv4 } from 'uuid';

// Mock uuid module
jest.mock('uuid');
const mockedUuidv4 = uuidv4 as jest.Mock;

mockedUuidv4.mockImplementation(
  () => 'test-uuid-' + Math.random().toString(36).substr(2, 9)
);

import {
  WorkflowAutomation,
  Workflow,
  WorkflowTrigger,
  WorkflowAction,
  WorkflowCondition,
  WorkflowVariable,
} from '../workflows/workflow-engine';

describe('WorkflowAutomation', () => {
  let engine: WorkflowAutomation;

  beforeEach(() => {
    engine = new WorkflowAutomation();
  });

  describe('Workflow Creation', () => {
    it('should create a new workflow with minimal config', async () => {
      const workflow = await engine.createWorkflow(
        'user-123',
        'Test Workflow',
        'A test workflow',
        {
          triggers: [
            {
              id: 'trigger-1',
              type: 'manual',
              config: {},
              enabled: true,
            },
          ],
          actions: [
            {
              id: 'action-1',
              type: 'send_email',
              config: { to: 'test@example.com' },
              enabled: true,
            },
          ],
        }
      );

      expect(workflow).toBeDefined();
      expect(workflow.id).toBeDefined();
      expect(workflow.name).toBe('Test Workflow');
      expect(workflow.description).toBe('A test workflow');
      expect(workflow.userId).toBe('user-123');
      expect(workflow.isActive).toBe(true);
      expect(workflow.triggers).toHaveLength(1);
      expect(workflow.actions).toHaveLength(1);
    });

    it('should create workflow with conditions and variables', async () => {
      const conditions: WorkflowCondition[] = [
        {
          id: 'cond-1',
          type: 'confidence_score',
          operator: 'greater_than',
          field: 'score',
          value: 0.8,
          nextActionId: 'action-1',
          enabled: true,
        },
      ];

      const variables: WorkflowVariable[] = [
        {
          id: 'var-1',
          name: 'threshold',
          type: 'number',
          defaultValue: 0.8,
          description: 'Confidence threshold',
        },
      ];

      const workflow = await engine.createWorkflow(
        'user-123',
        'Conditional Workflow',
        'Workflow with conditions',
        {
          triggers: [
            {
              id: 'trigger-1',
              type: 'file_uploaded',
              config: {},
              enabled: true,
            },
          ],
          actions: [
            {
              id: 'action-1',
              type: 'notify_user',
              config: { message: 'High confidence detected' },
              enabled: true,
            },
          ],
          conditions,
          variables,
        }
      );

      expect(workflow.conditions).toHaveLength(1);
      expect(workflow.variables).toHaveLength(1);
      expect(workflow.conditions[0].type).toBe('confidence_score');
    });

    it('should return created workflow', async () => {
      const workflow = await engine.createWorkflow('user-123', 'Test', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      const retrieved = await engine.getWorkflow(workflow.id, 'user-123');
      expect(retrieved).toEqual(workflow);
    });
  });

  describe('Workflow Retrieval', () => {
    it('should return null for non-existent workflow', async () => {
      const result = await engine.getWorkflow('non-existent', 'user-123');
      expect(result).toBeNull();
    });

    it('should return null for workflow belonging to different user', async () => {
      const workflow = await engine.createWorkflow('user-123', 'Test', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      const result = await engine.getWorkflow(workflow.id, 'different-user');
      expect(result).toBeNull();
    });

    it('should return workflow for correct user', async () => {
      const workflow = await engine.createWorkflow('user-123', 'Test', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      const result = await engine.getWorkflow(workflow.id, 'user-123');
      expect(result).not.toBeNull();
      expect(result!.id).toBe(workflow.id);
    });
  });

  describe('Workflow Update', () => {
    it('should update workflow successfully', async () => {
      const workflow = await engine.createWorkflow(
        'user-123',
        'Original Name',
        'Original desc',
        {
          triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
          actions: [
            { id: 'a1', type: 'send_email', config: {}, enabled: true },
          ],
        }
      );

      const updated = await engine.updateWorkflow(workflow.id, 'user-123', {
        name: 'Updated Name',
        description: 'Updated description',
      });

      expect(updated).toBe(true);

      const retrieved = await engine.getWorkflow(workflow.id, 'user-123');
      expect(retrieved!.name).toBe('Updated Name');
      expect(retrieved!.description).toBe('Updated description');
    });

    it('should return false for non-existent workflow', async () => {
      const result = await engine.updateWorkflow('non-existent', 'user-123', {
        name: 'New Name',
      });
      expect(result).toBe(false);
    });
  });

  describe('Workflow Deletion', () => {
    it('should delete workflow successfully', async () => {
      const workflow = await engine.createWorkflow('user-123', 'Test', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      const deleted = await engine.deleteWorkflow(workflow.id, 'user-123');
      expect(deleted).toBe(true);

      const retrieved = await engine.getWorkflow(workflow.id, 'user-123');
      expect(retrieved).toBeNull();
    });

    it('should return false for non-existent workflow', async () => {
      const result = await engine.deleteWorkflow('non-existent', 'user-123');
      expect(result).toBe(false);
    });
  });

  describe('Workflow Activation', () => {
    it('should activate workflow', async () => {
      const workflow = await engine.createWorkflow('user-123', 'Test', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      await engine.updateWorkflow(workflow.id, 'user-123', { isActive: false });

      const activated = await engine.activateWorkflow(workflow.id, 'user-123');
      expect(activated).toBe(true);

      const retrieved = await engine.getWorkflow(workflow.id, 'user-123');
      expect(retrieved!.isActive).toBe(true);
    });

    it('should deactivate workflow', async () => {
      const workflow = await engine.createWorkflow('user-123', 'Test', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      const deactivated = await engine.deactivateWorkflow(
        workflow.id,
        'user-123'
      );
      expect(deactivated).toBe(true);

      const retrieved = await engine.getWorkflow(workflow.id, 'user-123');
      expect(retrieved!.isActive).toBe(false);
    });
  });

  describe('User Workflows', () => {
    it('should return all workflows for user', async () => {
      await engine.createWorkflow('user-123', 'Workflow 1', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      await engine.createWorkflow('user-123', 'Workflow 2', 'Desc', {
        triggers: [{ id: 't2', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a2', type: 'send_email', config: {}, enabled: true }],
      });

      await engine.createWorkflow('user-456', 'Workflow 3', 'Desc', {
        triggers: [{ id: 't3', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a3', type: 'send_email', config: {}, enabled: true }],
      });

      const userWorkflows = await engine.getUserWorkflows('user-123');
      expect(userWorkflows).toHaveLength(2);
      expect(userWorkflows.every(w => w.userId === 'user-123')).toBe(true);
    });

    it('should return empty array for user with no workflows', async () => {
      const workflows = await engine.getUserWorkflows('non-existent-user');
      expect(workflows).toHaveLength(0);
    });
  });

  describe('Templates', () => {
    it('should return all templates', async () => {
      const templates = await engine.getTemplates();
      expect(templates.length).toBeGreaterThan(0);
    });

    it('should return templates by category', async () => {
      const notifications = await engine.getTemplates('notifications');
      const integrations = await engine.getTemplates('integrations');

      expect(notifications.length).toBeGreaterThan(0);
      expect(integrations.length).toBeGreaterThan(0);

      expect(notifications.every(t => t.category === 'notifications')).toBe(
        true
      );
      expect(integrations.every(t => t.category === 'integrations')).toBe(true);
    });

    it('should create workflow from template', async () => {
      const workflow = await engine.createFromTemplate(
        'template-email-notification',
        'user-123',
        'My Email Workflow'
      );

      expect(workflow).toBeDefined();
      expect(workflow.name).toBe('My Email Workflow');
      expect(workflow.triggers.length).toBeGreaterThan(0);
      expect(workflow.actions.length).toBeGreaterThan(0);
    });

    it('should throw error for non-existent template', async () => {
      await expect(
        engine.createFromTemplate('non-existent', 'user-123', 'Name')
      ).rejects.toThrow('Template not found');
    });
  });

  describe('Workflow Execution', () => {
    it('should execute workflow successfully', async () => {
      const workflow = await engine.createWorkflow('user-123', 'Test', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      const execution = await engine.executeWorkflow(workflow.id, 'user-123', {
        type: 'manual',
      });

      expect(execution).toBeDefined();
      expect(execution.id).toBeDefined();
      expect(execution.status).toBe('completed');
      expect(execution.startedAt).toBeInstanceOf(Date);
    });

    it('should fail execution for non-existent workflow', async () => {
      await expect(
        engine.executeWorkflow('non-existent', 'user-123', { type: 'manual' })
      ).rejects.toThrow('Workflow not found or not active');
    });

    it('should fail execution for inactive workflow', async () => {
      const workflow = await engine.createWorkflow('user-123', 'Test', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      await engine.updateWorkflow(workflow.id, 'user-123', { isActive: false });

      await expect(
        engine.executeWorkflow(workflow.id, 'user-123', { type: 'manual' })
      ).rejects.toThrow('Workflow not found or not active');
    });

    it('should increment execution count after execution', async () => {
      const workflow = await engine.createWorkflow('user-123', 'Test', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      expect(workflow.executionCount).toBe(0);

      await engine.executeWorkflow(workflow.id, 'user-123', { type: 'manual' });

      const retrieved = await engine.getWorkflow(workflow.id, 'user-123');
      expect(retrieved!.executionCount).toBe(1);
    });
  });

  describe('Execution History', () => {
    it('should return empty array for non-existent workflow', async () => {
      const history = await engine.getExecutionHistory(
        'non-existent',
        'user-123'
      );
      expect(history).toHaveLength(0);
    });

    it('should return execution history', async () => {
      const workflow = await engine.createWorkflow('user-123', 'Test', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      await engine.executeWorkflow(workflow.id, 'user-123', { type: 'manual' });
      await engine.executeWorkflow(workflow.id, 'user-123', { type: 'manual' });

      const history = await engine.getExecutionHistory(workflow.id, 'user-123');
      expect(history).toHaveLength(2);
    });

    it('should limit execution history', async () => {
      const workflow = await engine.createWorkflow('user-123', 'Test', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      for (let i = 0; i < 5; i++) {
        await engine.executeWorkflow(workflow.id, 'user-123', {
          type: 'manual',
        });
      }

      const history = await engine.getExecutionHistory(
        workflow.id,
        'user-123',
        3
      );
      expect(history).toHaveLength(3);
    });
  });

  describe('Workflow Statistics', () => {
    it('should return null for non-existent workflow', async () => {
      const stats = await engine.getWorkflowStats('non-existent', 'user-123');
      expect(stats).toBeNull();
    });

    it('should calculate statistics correctly', async () => {
      const workflow = await engine.createWorkflow('user-123', 'Test', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      await engine.executeWorkflow(workflow.id, 'user-123', { type: 'manual' });
      await engine.executeWorkflow(workflow.id, 'user-123', { type: 'manual' });
      await engine.executeWorkflow(workflow.id, 'user-123', { type: 'manual' });

      const stats = await engine.getWorkflowStats(workflow.id, 'user-123');
      expect(stats).toBeDefined();
      expect(stats!.totalExecutions).toBe(3);
      expect(stats!.successfulExecutions).toBe(3);
      expect(stats!.failedExecutions).toBe(0);
      expect(stats!.successRate).toBe(100);
    });
  });

  describe('Validation', () => {
    it('should validate workflow with triggers and actions', async () => {
      const workflow: Workflow = {
        id: 'test-123',
        name: 'Test',
        description: 'Desc',
        userId: 'user-123',
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
        conditions: [],
        variables: [],
        executionCount: 0,
        errorCount: 0,
      };

      const result = await engine.validateWorkflow(workflow);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should fail validation without triggers', async () => {
      const workflow: Workflow = {
        id: 'test-123',
        name: 'Test',
        description: 'Desc',
        userId: 'user-123',
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
        triggers: [],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
        conditions: [],
        variables: [],
        executionCount: 0,
        errorCount: 0,
      };

      const result = await engine.validateWorkflow(workflow);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(
        'Workflow must have at least one trigger'
      );
    });

    it('should fail validation without actions', async () => {
      const workflow: Workflow = {
        id: 'test-123',
        name: 'Test',
        description: 'Desc',
        userId: 'user-123',
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [],
        conditions: [],
        variables: [],
        executionCount: 0,
        errorCount: 0,
      };

      const result = await engine.validateWorkflow(workflow);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Workflow must have at least one action');
    });

    it('should validate condition references', async () => {
      const workflow: Workflow = {
        id: 'test-123',
        name: 'Test',
        description: 'Desc',
        userId: 'user-123',
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
        conditions: [
          {
            id: 'cond-1',
            type: 'confidence_score',
            operator: 'greater_than',
            field: 'score',
            value: 0.8,
            nextActionId: 'non-existent-action',
            enabled: true,
          },
        ],
        variables: [],
        executionCount: 0,
        errorCount: 0,
      };

      const result = await engine.validateWorkflow(workflow);
      expect(result.isValid).toBe(false);
      expect(result.errors.some(e => e.includes('non-existent action'))).toBe(
        true
      );
    });
  });

  describe('Active Workflow Count', () => {
    it('should return active workflow count for user', async () => {
      await engine.createWorkflow('user-123', 'Active 1', 'Desc', {
        triggers: [{ id: 't1', type: 'manual', config: {}, enabled: true }],
        actions: [{ id: 'a1', type: 'send_email', config: {}, enabled: true }],
      });

      const inactive = await engine.createWorkflow(
        'user-123',
        'Inactive',
        'Desc',
        {
          triggers: [{ id: 't2', type: 'manual', config: {}, enabled: true }],
          actions: [
            { id: 'a2', type: 'send_email', config: {}, enabled: true },
          ],
        }
      );
      await engine.updateWorkflow(inactive.id, 'user-123', { isActive: false });

      const count = await engine.getActiveWorkflowCount('user-123');
      expect(count).toBe(1);
    });
  });
});
