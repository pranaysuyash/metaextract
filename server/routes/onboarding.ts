/**
 * Onboarding API Routes
 *
 * Handles onboarding session management, progress tracking, and user profile persistence.
 */

import type { Express, Request, Response } from 'express';
import { storage } from '../storage/index';
import type { AuthRequest } from '../auth';

// ============================================================================
// Types
// ============================================================================

interface OnboardingSession {
  id: string;
  userId?: string;
  startedAt: Date;
  completedAt?: Date;
  currentStep: number;
  pathId: string;
  userProfile: string; // JSON string
  progress: string; // JSON string
  interactions: string; // JSON array string
  isActive: boolean;
}

interface OnboardingInteraction {
  timestamp: Date;
  type: 'step-complete' | 'skip' | 'help-request' | 'feature-try' | 'error';
  stepId?: string;
  featureId?: string;
  duration?: number;
  metadata: Record<string, any>;
}

// ============================================================================
// Route Handlers
// ============================================================================

/**
 * Get onboarding status for current user
 */
async function getOnboardingStatus(req: Request, res: Response) {
  try {
    const authReq = req as AuthRequest;
    const userId = authReq.user?.id;

    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    // Get active or most recent onboarding session
    const session = await storage.getOnboardingSession(userId);

    res.json({
      hasSession: !!session,
      session: session || null,
      isComplete: session?.completedAt != null,
      isActive: session?.isActive || false,
    });
  } catch (error) {
    console.error('Failed to get onboarding status:', error);
    res.status(500).json({ error: 'Failed to retrieve onboarding status' });
  }
}

/**
 * Start a new onboarding session
 */
async function startOnboarding(req: Request, res: Response) {
  try {
    const authReq = req as AuthRequest;
    const userId = authReq.user?.id;

    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { pathId, userProfile, progress, interactions } = req.body;

    if (!pathId || !userProfile) {
      return res.status(400).json({
        error: 'Missing required fields: pathId, userProfile',
      });
    }

    // Create new onboarding session
    const session = await storage.createOnboardingSession({
      userId,
      startedAt: new Date(),
      currentStep: 0,
      pathId,
      userProfile: JSON.stringify(userProfile),
      progress: JSON.stringify(progress || {}),
      interactions: JSON.stringify(interactions || []),
      isActive: true,
    });

    res.json({
      success: true,
      session,
    });
  } catch (error) {
    console.error('Failed to start onboarding:', error);
    res.status(500).json({ error: 'Failed to start onboarding session' });
  }
}

/**
 * Update onboarding progress
 */
async function updateProgress(req: Request, res: Response) {
  try {
    const authReq = req as AuthRequest;
    const userId = authReq.user?.id;

    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { session } = req.body;

    if (!session) {
      return res.status(400).json({ error: 'Session data required' });
    }

    // Update session in database
    await storage.updateOnboardingSession(session.id, {
      currentStep: session.progress.currentStepIndex,
      progress: JSON.stringify(session.progress),
      interactions: JSON.stringify(session.interactions),
      isActive: session.isActive,
    });

    res.json({
      success: true,
      message: 'Progress updated successfully',
    });
  } catch (_error) {
    console.error('Failed to update progress:', _error);
    res.status(500).json({ error: 'Failed to update onboarding progress' });
  }
}

/**
 * Pause onboarding session
 */
async function pauseOnboarding(req: Request, res: Response) {
  try {
    const authReq = req as AuthRequest;
    const userId = authReq.user?.id;

    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { sessionId } = req.body;

    if (!sessionId) {
      return res.status(400).json({ error: 'Session ID required' });
    }

    await storage.updateOnboardingSession(sessionId, {
      isActive: false,
    });

    res.json({
      success: true,
      message: 'Onboarding paused',
    });
  } catch (_error) {
    console.error('Failed to pause onboarding:', _error);
    res.status(500).json({ error: 'Failed to pause onboarding' });
  }
}

/**
 * Resume onboarding session
 */
async function resumeOnboarding(req: Request, res: Response) {
  try {
    const authReq = req as AuthRequest;
    const userId = authReq.user?.id;

    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { sessionId } = req.body;

    if (!sessionId) {
      return res.status(400).json({ error: 'Session ID required' });
    }

    await storage.updateOnboardingSession(sessionId, {
      isActive: true,
    });

    res.json({
      success: true,
      message: 'Onboarding resumed',
    });
  } catch (_error) {
    console.error('Failed to resume onboarding:', _error);
    res.status(500).json({ error: 'Failed to resume onboarding' });
  }
}

/**
 * Complete onboarding session
 */
async function completeOnboarding(req: Request, res: Response) {
  try {
    const authReq = req as AuthRequest;
    const userId = authReq.user?.id;

    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { sessionId } = req.body;

    if (!sessionId) {
      return res.status(400).json({ error: 'Session ID required' });
    }

    await storage.updateOnboardingSession(sessionId, {
      completedAt: new Date(),
      isActive: false,
    });

    res.json({
      success: true,
      message: 'Onboarding completed',
    });
  } catch (_error) {
    console.error('Failed to complete onboarding:', _error);
    res.status(500).json({ error: 'Failed to complete onboarding' });
  }
}

/**
 * Get onboarding analytics for user
 */
async function getOnboardingAnalytics(req: Request, res: Response) {
  try {
    const authReq = req as AuthRequest;
    const userId = authReq.user?.id;

    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const session = await storage.getOnboardingSession(userId);

    if (!session) {
      return res.json({
        hasData: false,
        analytics: null,
      });
    }

    const progress = JSON.parse(session.progress);
    const interactions = JSON.parse(session.interactions);
    const userProfile = JSON.parse(session.userProfile);

    res.json({
      hasData: true,
      analytics: {
        timeSpent: progress.timeSpent || 0,
        stepsCompleted: progress.stepsCompleted?.length || 0,
        completionRate: progress.completionRate || 0,
        interactions: interactions || [],
        userProfile,
        pathId: session.pathId,
        isComplete: !!session.completedAt,
        startedAt: session.startedAt,
        completedAt: session.completedAt,
      },
    });
  } catch (_error) {
    console.error('Failed to get onboarding analytics:', _error);
    res.status(500).json({ error: 'Failed to retrieve analytics' });
  }
}

// ============================================================================
// Route Registration
// ============================================================================

export function registerOnboardingRoutes(app: Express): void {
  // Get onboarding status
  app.get('/api/onboarding/status', getOnboardingStatus);

  // Start new onboarding session
  app.post('/api/onboarding/start', startOnboarding);

  // Update progress
  app.post('/api/onboarding/progress', updateProgress);

  // Pause onboarding
  app.post('/api/onboarding/pause', pauseOnboarding);

  // Resume onboarding
  app.post('/api/onboarding/resume', resumeOnboarding);

  // Complete onboarding
  app.post('/api/onboarding/complete', completeOnboarding);

  // Get analytics
  app.get('/api/onboarding/analytics', getOnboardingAnalytics);
}
