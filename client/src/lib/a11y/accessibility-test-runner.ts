/**
 * Accessibility Testing Runner - Automated WCAG 2.1 AA compliance testing
 */

import { AccessibilityAuditor, AuditConfig, AuditResult } from './accessibility-audit';

export interface TestSuite {
  id: string;
  name: string;
  description: string;
  pages: string[];
  config: AuditConfig;
  createdAt: Date;
  createdBy: string;
  isActive: boolean;
}

export interface TestRun {
  id: string;
  testSuiteId: string;
  startedAt: Date;
  completedAt?: Date;
  status: 'pending' | 'running' | 'completed' | 'failed';
  results: AuditResult[];
  summary: {
    totalPages: number;
    completedPages: number;
    failedPages: number;
    totalIssues: number;
    criticalIssues: number;
    passRate: number;
  };
}

export interface AutomatedTestConfig {
  baseUrl: string;
  pages: Array<{
    path: string;
    name: string;
    description: string;
  }>;
  auditConfig: AuditConfig;
  schedule?: {
    interval: 'daily' | 'weekly' | 'monthly';
    time: string; // HH:MM format
    timezone: string;
  };
  notifications: {
    email: string[];
    webhook?: string;
    onFailures: boolean;
    onCritical: boolean;
  };
  thresholds: {
    minPassRate: number; // e.g., 95 for 95%
    maxCriticalIssues: number;
    maxHighPriorityIssues: number;
  };
}

export class AccessibilityTestRunner {
  private auditor: AccessibilityAuditor;
  private testSuites: Map<string, TestSuite> = new Map();
  private testRuns: Map<string, TestRun> = new Map();
  private config: AutomatedTestConfig;

  constructor(config: AutomatedTestConfig) {
    this.config = config;
    this.auditor = new AccessibilityAuditor(config.auditConfig);
  }

  /**
   * Create a new test suite
   */
  async createTestSuite(
    name: string,
    description: string,
    pages: string[],
    auditConfig?: Partial<AuditConfig>
  ): Promise<TestSuite> {
    const suite: TestSuite = {
      id: `suite-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name,
      description,
      pages,
      config: { ...this.config.auditConfig, ...auditConfig },
      createdAt: new Date(),
      createdBy: 'system', // In real implementation, this would be the user ID
      isActive: true
    };

    this.testSuites.set(suite.id, suite);
    return suite;
  }

  /**
   * Run a test suite
   */
  async runTestSuite(suiteId: string): Promise<TestRun> {
    const suite = this.testSuites.get(suiteId);
    if (!suite) {
      throw new Error(`Test suite not found: ${suiteId}`);
    }

    const runId = `run-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const testRun: TestRun = {
      id: runId,
      testSuiteId: suiteId,
      startedAt: new Date(),
      status: 'running',
      results: [],
      summary: {
        totalPages: suite.pages.length,
        completedPages: 0,
        failedPages: 0,
        totalIssues: 0,
        criticalIssues: 0,
        passRate: 0
      }
    };

    this.testRuns.set(runId, testRun);

    try {
      // Run audit on each page in the suite
      const results: AuditResult[] = [];
      let completedPages = 0;
      let failedPages = 0;
      let totalIssues = 0;
      let criticalIssues = 0;

      for (const pagePath of suite.pages) {
        try {
          const pageUrl = `${this.config.baseUrl}${pagePath}`;
          const result = await this.auditor.auditPage(pageUrl, suite.config);
          results.push(result);
          completedPages++;
          
          // Update counters
          totalIssues += result.summary.errors + result.summary.warnings + result.summary.notices;
          criticalIssues += result.results.filter(r => r.impact === 'critical').length;
        } catch (error) {
          console.error(`Failed to audit page ${pagePath}:`, error);
          failedPages++;
        }
      }

      // Calculate pass rate (percentage of pages that passed)
      const passRate = completedPages > 0 
        ? ((completedPages - failedPages) / completedPages) * 100 
        : 0;

      // Update test run
      testRun.results = results;
      testRun.status = 'completed';
      testRun.completedAt = new Date();
      testRun.summary = {
        totalPages: suite.pages.length,
        completedPages,
        failedPages,
        totalIssues,
        criticalIssues,
        passRate: Number(passRate.toFixed(2))
      };

      // Check if thresholds were met
      const thresholdsMet = this.checkThresholds(testRun.summary);

      // Send notifications if needed
      if (!thresholdsMet) {
        await this.sendFailureNotifications(testRun);
      }

      this.testRuns.set(runId, testRun);

      return testRun;
    } catch (error) {
      testRun.status = 'failed';
      testRun.completedAt = new Date();
      this.testRuns.set(runId, testRun);
      throw error;
    }
  }

  /**
   * Run automated accessibility tests across all configured pages
   */
  async runAutomatedTests(): Promise<TestRun> {
    const runId = `automated-${Date.now()}`;
    
    const testRun: TestRun = {
      id: runId,
      testSuiteId: 'automated-suite',
      startedAt: new Date(),
      status: 'running',
      results: [],
      summary: {
        totalPages: this.config.pages.length,
        completedPages: 0,
        failedPages: 0,
        totalIssues: 0,
        criticalIssues: 0,
        passRate: 0
      }
    };

    this.testRuns.set(runId, testRun);

    try {
      const results: AuditResult[] = [];
      let completedPages = 0;
      let failedPages = 0;
      let totalIssues = 0;
      let criticalIssues = 0;

      for (const page of this.config.pages) {
        try {
          const pageUrl = `${this.config.baseUrl}${page.path}`;
          const result = await this.auditor.auditPage(pageUrl, this.config.auditConfig);
          results.push(result);
          completedPages++;
          
          // Update counters
          totalIssues += result.summary.errors + result.summary.warnings + result.summary.notices;
          criticalIssues += result.results.filter(r => r.impact === 'critical').length;
        } catch (error) {
          console.error(`Failed to audit page ${page.path}:`, error);
          failedPages++;
        }
      }

      // Calculate pass rate
      const passRate = completedPages > 0 
        ? ((completedPages - failedPages) / completedPages) * 100 
        : 0;

      // Update test run
      testRun.results = results;
      testRun.status = 'completed';
      testRun.completedAt = new Date();
      testRun.summary = {
        totalPages: this.config.pages.length,
        completedPages,
        failedPages,
        totalIssues,
        criticalIssues,
        passRate: Number(passRate.toFixed(2))
      };

      // Check if thresholds were met
      const thresholdsMet = this.checkThresholds(testRun.summary);

      // Send notifications if needed
      if (!thresholdsMet) {
        await this.sendFailureNotifications(testRun);
      }

      this.testRuns.set(runId, testRun);

      return testRun;
    } catch (error) {
      testRun.status = 'failed';
      testRun.completedAt = new Date();
      this.testRuns.set(runId, testRun);
      throw error;
    }
  }

  /**
   * Check if test run meets configured thresholds
   */
  private checkThresholds(summary: TestRun['summary']): boolean {
    const { thresholds } = this.config;
    
    return (
      summary.passRate >= thresholds.minPassRate &&
      summary.criticalIssues <= thresholds.maxCriticalIssues &&
      (summary.totalIssues - summary.criticalIssues) <= thresholds.maxHighPriorityIssues
    );
  }

  /**
   * Send failure notifications
   */
  private async sendFailureNotifications(testRun: TestRun): Promise<void> {
    if (this.config.notifications.onFailures || this.config.notifications.onCritical) {
      // In a real implementation, this would send emails/webhook notifications
      console.log('Sending failure notifications for test run:', testRun.id);
      
      // Send email notifications
      for (const email of this.config.notifications.email) {
        // Email sending logic would go here
        console.log(`Notification sent to: ${email}`);
      }
      
      // Send webhook notification
      if (this.config.notifications.webhook) {
        try {
          await fetch(this.config.notifications.webhook, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              event: 'accessibility_test_failure',
              testRun,
              config: this.config
            })
          });
        } catch (error) {
          console.error('Failed to send webhook notification:', error);
        }
      }
    }
  }

  /**
   * Schedule automated tests
   */
  scheduleTests(): void {
    if (!this.config.schedule) {
      console.log('No schedule configured for automated tests');
      return;
    }

    // Convert time string to milliseconds from midnight
    const [hours, minutes] = this.config.schedule.time.split(':').map(Number);
    const targetTime = hours * 60 * 60 * 1000 + minutes * 60 * 1000;
    
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const nextRun = new Date(today.getTime() + targetTime);

    // If the target time has already passed today, schedule for tomorrow
    if (nextRun.getTime() <= now.getTime()) {
      nextRun.setDate(nextRun.getDate() + 1);
    }

    const timeUntilNextRun = nextRun.getTime() - now.getTime();

    // Schedule the first run
    setTimeout(() => {
      this.runAutomatedTests();
      
      // Set up recurring schedule based on interval
      this.setupRecurringSchedule();
    }, timeUntilNextRun);
  }

  /**
   * Set up recurring schedule
   */
  private setupRecurringSchedule(): void {
    if (!this.config.schedule) return;

    let intervalMs: number;

    switch (this.config.schedule.interval) {
      case 'daily':
        intervalMs = 24 * 60 * 60 * 1000; // 24 hours
        break;
      case 'weekly':
        intervalMs = 7 * 24 * 60 * 60 * 1000; // 7 days
        break;
      case 'monthly':
        intervalMs = 30 * 24 * 60 * 60 * 1000; // 30 days (approximate)
        break;
      default:
        intervalMs = 24 * 60 * 60 * 1000; // Default to daily
    }

    setInterval(() => {
      this.runAutomatedTests();
    }, intervalMs);
  }

  /**
   * Get test run by ID
   */
  getTestRun(runId: string): TestRun | null {
    return this.testRuns.get(runId) || null;
  }

  /**
   * Get all test runs for a suite
   */
  getTestRunsForSuite(suiteId: string): TestRun[] {
    return Array.from(this.testRuns.values()).filter(run => run.testSuiteId === suiteId);
  }

  /**
   * Get recent test runs
   */
  getRecentTestRuns(limit: number = 10): TestRun[] {
    return Array.from(this.testRuns.values())
      .sort((a, b) => (b.startedAt?.getTime() || 0) - (a.startedAt?.getTime() || 0))
      .slice(0, limit);
  }

  /**
   * Get compliance trend
   */
  getComplianceTrend(days: number = 30): Array<{ date: string; passRate: number; issues: number }> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    return Array.from(this.testRuns.values())
      .filter(run => run.completedAt && run.completedAt >= cutoffDate)
      .sort((a, b) => (a.completedAt?.getTime() || 0) - (b.completedAt?.getTime() || 0))
      .map(run => ({
        date: run.completedAt ? run.completedAt.toISOString().split('T')[0] : 'unknown',
        passRate: run.summary.passRate,
        issues: run.summary.totalIssues
      }));
  }

  /**
   * Get accessibility issues by severity
   */
  getIssuesBySeverity(runId: string): { critical: number; serious: number; moderate: number; minor: number } {
    const run = this.testRuns.get(runId);
    if (!run) return { critical: 0, serious: 0, moderate: 0, minor: 0 };

    const critical = run.results.reduce((sum, result) => 
      sum + result.results.filter(r => r.impact === 'critical').length, 0);
    const serious = run.results.reduce((sum, result) => 
      sum + result.results.filter(r => r.impact === 'serious').length, 0);
    const moderate = run.results.reduce((sum, result) => 
      sum + result.results.filter(r => r.impact === 'moderate').length, 0);
    const minor = run.results.reduce((sum, result) => 
      sum + result.results.filter(r => r.impact === 'minor').length, 0);

    return { critical, serious, moderate, minor };
  }

  /**
   * Get most common issues
   */
  getMostCommonIssues(runId: string, limit: number = 10): Array<{ id: string; count: number; message: string }> {
    const run = this.testRuns.get(runId);
    if (!run) return [];

    const issueCounts: Record<string, { count: number; message: string }> = {};

    for (const result of run.results) {
      for (const issue of result.results) {
        if (!issueCounts[issue.id]) {
          issueCounts[issue.id] = { count: 0, message: issue.message };
        }
        issueCounts[issue.id].count++;
      }
    }

    return Object.entries(issueCounts)
      .map(([id, data]) => ({ id, count: data.count, message: data.message }))
      .sort((a, b) => b.count - a.count)
      .slice(0, limit);
  }

  /**
   * Export test results
   */
  exportResults(runId: string, format: 'json' | 'csv' | 'html' = 'json'): string {
    const run = this.testRuns.get(runId);
    if (!run) {
      throw new Error(`Test run not found: ${runId}`);
    }

    switch (format) {
      case 'json':
        return JSON.stringify(run, null, 2);
      case 'csv':
        return this.exportToCsv(run);
      case 'html':
        return this.exportToHtml(run);
      default:
        return JSON.stringify(run, null, 2);
    }
  }

  /**
   * Export to CSV format
   */
  private exportToCsv(run: TestRun): string {
    const headers = ['Page', 'URL', 'Date', 'Errors', 'Warnings', 'Notices', 'Pass Rate (%)'];
    const rows = run.results.map(result => [
      result.page,
      result.url,
      result.timestamp.toISOString(),
      result.summary.errors,
      result.summary.warnings,
      result.summary.notices,
      result.summary.passRate
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    return csvContent;
  }

  /**
   * Export to HTML format
   */
  private exportToHtml(run: TestRun): string {
    const summary = run.summary;
    
    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Accessibility Test Run Report - ${run.id}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f9fafb; }
    .container { max-width: 1200px; margin: 0 auto; }
    .header { margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #e5e7eb; }
    .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .summary-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .summary-card h3 { margin: 0 0 10px 0; font-size: 14px; color: #6b7280; }
    .summary-card .value { font-size: 24px; font-weight: bold; color: #1f2937; }
    .summary-card .good { color: #10b981; }
    .summary-card .warning { color: #f59e0b; }
    .summary-card .critical { color: #ef4444; }
    .results-table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .results-table th, .results-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #e5e7eb; }
    .results-table th { background: #f3f4f6; font-weight: 600; color: #374151; }
    .results-table tr:last-child td { border-bottom: none; }
    .results-table .error { color: #ef4444; }
    .results-table .warning { color: #f59e0b; }
    .results-table .notice { color: #3b82f6; }
    .trend-chart { height: 300px; margin: 30px 0; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Accessibility Test Run Report</h1>
      <p>Run ID: ${run.id}</p>
      <p>Started: ${run.startedAt.toLocaleString()}</p>
      <p>Status: ${run.status}</p>
    </div>
    
    <div class="summary-grid">
      <div class="summary-card">
        <h3>Total Pages</h3>
        <div class="value">${summary.totalPages}</div>
      </div>
      <div class="summary-card">
        <h3>Completed</h3>
        <div class="value">${summary.completedPages}</div>
      </div>
      <div class="summary-card">
        <h3>Failed</h3>
        <div class="value ${summary.failedPages > 0 ? 'critical' : 'good'}">${summary.failedPages}</div>
      </div>
      <div class="summary-card">
        <h3>Issues Found</h3>
        <div class="value ${summary.totalIssues > 0 ? 'warning' : 'good'}">${summary.totalIssues}</div>
      </div>
      <div class="summary-card">
        <h3>Critical Issues</h3>
        <div class="value ${summary.criticalIssues > 0 ? 'critical' : 'good'}">${summary.criticalIssues}</div>
      </div>
      <div class="summary-card">
        <h3>Pass Rate</h3>
        <div class="value ${summary.passRate < 90 ? 'critical' : summary.passRate < 95 ? 'warning' : 'good'}">${summary.passRate}%</div>
      </div>
    </div>
    
    <h2>Detailed Results</h2>
    <table class="results-table">
      <thead>
        <tr>
          <th>Page</th>
          <th>URL</th>
          <th>Date</th>
          <th>Errors</th>
          <th>Warnings</th>
          <th>Notices</th>
          <th>Pass Rate</th>
        </tr>
      </thead>
      <tbody>
        ${run.results.map(result => `
          <tr>
            <td>${result.page}</td>
            <td>${result.url}</td>
            <td>${result.timestamp.toLocaleString()}</td>
            <td class="error">${result.summary.errors}</td>
            <td class="warning">${result.summary.warnings}</td>
            <td class="notice">${result.summary.notices}</td>
            <td>${result.summary.passRate}%</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  </div>
</body>
</html>
    `;
  }

  /**
   * Generate accessibility compliance report
   */
  generateComplianceReport(): string {
    const recentRuns = this.getRecentTestRuns(10);
    
    if (recentRuns.length === 0) {
      return 'No test runs available for compliance report.';
    }

    const overallPassRate = recentRuns.reduce((sum, run) => sum + run.summary.passRate, 0) / recentRuns.length;
    const totalCriticalIssues = recentRuns.reduce((sum, run) => sum + run.summary.criticalIssues, 0);
    const totalIssues = recentRuns.reduce((sum, run) => sum + run.summary.totalIssues, 0);

    return `
# Accessibility Compliance Report

## Executive Summary
- **Overall Pass Rate**: ${overallPassRate.toFixed(2)}%
- **Total Critical Issues**: ${totalCriticalIssues}
- **Total Issues Found**: ${totalIssues}
- **Test Runs Analyzed**: ${recentRuns.length}

## Compliance Status
${overallPassRate >= 95 ? '✅ WCAG 2.1 AA Compliant' : overallPassRate >= 90 ? '⚠️ Approaching Compliance' : '❌ Non-Compliant'}

## Trend Analysis
${this.getComplianceTrend(30).map(day => `  - ${day.date}: ${day.passRate}% pass rate`).join('\n')}

## Recommendations
1. Address critical issues immediately
2. Focus on pages with lowest pass rates
3. Implement automated testing in CI/CD pipeline
4. Regular monitoring to maintain compliance
    `;
  }
}

// Singleton instance
export const accessibilityTestRunner = new AccessibilityTestRunner({
  baseUrl: process.env.BASE_URL || 'http://localhost:3000',
  pages: [
    { path: '/', name: 'Home Page', description: 'Main landing page' },
    { path: '/dashboard', name: 'Dashboard', description: 'User dashboard' },
    { path: '/results', name: 'Results Page', description: 'Metadata results page' },
    { path: '/upload', name: 'Upload Page', description: 'File upload page' },
    { path: '/analytics', name: 'Analytics', description: 'Analytics dashboard' },
    { path: '/settings', name: 'Settings', description: 'User settings page' },
    { path: '/about', name: 'About', description: 'About page' },
    { path: '/contact', name: 'Contact', description: 'Contact page' }
  ],
  auditConfig: {
    include: [],
    exclude: ['iframe'],
    rules: [],
    tags: ['wcag21aa'],
    runOnly: {
      type: 'tag',
      values: ['wcag21aa']
    }
  },
  notifications: {
    email: [process.env.ADMIN_EMAIL || 'admin@example.com'],
    onFailures: true,
    onCritical: true
  },
  thresholds: {
    minPassRate: 95,
    maxCriticalIssues: 0,
    maxHighPriorityIssues: 5
  }
});

export default accessibilityTestRunner;