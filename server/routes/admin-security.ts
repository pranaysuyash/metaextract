/**
 * Admin Security Routes
 *
 * Phase 2 Implementation: Security monitoring and statistics endpoints
 */

import { Router, Request, Response } from 'express';
import {
  getRecentSecurityEvents,
  getSecurityStats,
} from '../utils/enhanced-quota-handler';

const router = Router();

/**
 * GET /api/admin/security-events
 * Get recent security events for monitoring
 */
router.get('/security-events', async (req: Request, res: Response) => {
  try {
    const limit = parseInt(req.query.limit as string) || 50;
    const severity = req.query.severity as string;
    const event = req.query.event as string;

    const events = await getRecentSecurityEvents(limit);

    // Filter if requested
    let filteredEvents = events;
    if (severity) {
      filteredEvents = filteredEvents.filter(e => e.severity === severity);
    }
    if (event) {
      filteredEvents = filteredEvents.filter(e => e.event === event);
    }

    res.json({
      success: true,
      events: filteredEvents,
      count: filteredEvents.length,
      timestamp: new Date()
    });
  } catch (error) {
    console.error('[AdminSecurityEvents] Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/admin/security-stats
 * Get security statistics
 */
router.get('/security-stats', async (req: Request, res: Response) => {
  try {
    const stats = await getSecurityStats();

    res.json({
      success: true,
      stats,
      timestamp: new Date()
    });
  } catch (error) {
    console.error('[AdminSecurityStats] Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GET /api/admin/security-dashboard
 * Get comprehensive security dashboard data
 */
router.get('/security-dashboard', async (req: Request, res: Response) => {
  try {
    const [events, stats] = await Promise.all([
      getRecentSecurityEvents(20),
      getSecurityStats()
    ]);

    // Calculate additional metrics
    const criticalEvents = events.filter(e => e.severity === 'critical' || e.severity === 'high');
    const recentAlerts = criticalEvents.slice(0, 5);

    res.json({
      success: true,
      dashboard: {
        stats,
        recentEvents: events.slice(0, 10),
        recentAlerts,
        threatLevel: stats.criticalEvents > 5 ? 'high' : stats.highRiskEvents > 10 ? 'elevated' : 'normal'
      },
      timestamp: new Date()
    });
  } catch (error) {
    console.error('[AdminSecurityDashboard] Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;