/**
 * Accessibility Reporter - Issue reporting and tracking
 */

import { A11yTestResult, A11yAuditResult } from './a11y-audit';

export interface A11yIssue {
  id: string;
  type: 'violation' | 'incomplete' | 'recommendation';
  severity: 'critical' | 'serious' | 'moderate' | 'minor';
  description: string;
  help: string;
  url: string;
  element?: string;
  impact?: string;
  tags: string[];
  timestamp: number;
  resolved: boolean;
  resolvedAt?: number;
  resolvedBy?: string;
}

export interface A11yReport {
  id: string;
  title: string;
  description: string;
  issues: A11yIssue[];
  summary: {
    total: number;
    critical: number;
    serious: number;
    moderate: number;
    minor: number;
    resolved: number;
  };
  createdAt: number;
  updatedAt: number;
  generatedBy: string;
}

export class A11yReporter {
  private static storageKey = 'a11y_reports';
  
  /**
   * Create a report from test results
   */
  static createReportFromTest(
    testResult: A11yTestResult,
    title: string,
    description: string,
    generatedBy: string
  ): A11yReport {
    const issues: A11yIssue[] = [];
    
    // Convert violations to issues
    for (const violation of testResult.violations) {
      for (const node of violation.nodes) {
        issues.push({
          id: `${violation.id}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: 'violation',
          severity: violation.impact as any,
          description: violation.description,
          help: violation.help,
          url: testResult.url,
          element: node.html,
          impact: violation.impact,
          tags: violation.tags,
          timestamp: testResult.timestamp,
          resolved: false,
        });
      }
    }
    
    // Convert incomplete items to issues
    for (const incomplete of testResult.incomplete) {
      for (const node of incomplete.nodes) {
        issues.push({
          id: `${incomplete.id}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: 'incomplete',
          severity: incomplete.impact as any,
          description: incomplete.description,
          help: incomplete.help,
          url: testResult.url,
          element: node.html,
          impact: incomplete.impact,
          tags: incomplete.tags,
          timestamp: testResult.timestamp,
          resolved: false,
        });
      }
    }
    
    // Calculate summary
    const summary = {
      total: issues.length,
      critical: issues.filter(i => i.severity === 'critical').length,
      serious: issues.filter(i => i.severity === 'serious').length,
      moderate: issues.filter(i => i.severity === 'moderate').length,
      minor: issues.filter(i => i.severity === 'minor').length,
      resolved: issues.filter(i => i.resolved).length,
    };
    
    const report: A11yReport = {
      id: `report-${Date.now()}`,
      title,
      description,
      issues,
      summary,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      generatedBy,
    };
    
    return report;
  }
  
  /**
   * Create a report from audit results
   */
  static createReportFromAudit(
    auditResult: A11yAuditResult,
    title: string,
    description: string,
    generatedBy: string
  ): A11yReport {
    const issues: A11yIssue[] = [];
    
    // Convert failed criteria to issues
    for (const criteria of auditResult.failedCriteria) {
      issues.push({
        id: `criteria-${criteria.replace(/\s+/g, '-').toLowerCase()}-${Date.now()}`,
        type: 'violation',
        severity: 'serious', // Default severity for failed criteria
        description: `WCAG 2.1 ${auditResult.wcagLevel} criteria not met: ${criteria}`,
        help: `Ensure compliance with ${criteria}`,
        url: auditResult.pageUrl,
        tags: ['wcag', auditResult.wcagLevel.toLowerCase()],
        timestamp: auditResult.timestamp,
        resolved: false,
      });
    }
    
    // Convert needs review items to issues
    for (const item of auditResult.needsReviewCriteria) {
      issues.push({
        id: `review-${item.replace(/\s+/g, '-').toLowerCase()}-${Date.now()}`,
        type: 'recommendation',
        severity: 'moderate',
        description: `WCAG 2.1 ${auditResult.wcagLevel} item needs review: ${item}`,
        help: `Review and ensure compliance with ${item}`,
        url: auditResult.pageUrl,
        tags: ['wcag', 'review', auditResult.wcagLevel.toLowerCase()],
        timestamp: auditResult.timestamp,
        resolved: false,
      });
    }
    
    const summary = {
      total: issues.length,
      critical: issues.filter(i => i.severity === 'critical').length,
      serious: issues.filter(i => i.severity === 'serious').length,
      moderate: issues.filter(i => i.severity === 'moderate').length,
      minor: issues.filter(i => i.severity === 'minor').length,
      resolved: issues.filter(i => i.resolved).length,
    };
    
    const report: A11yReport = {
      id: `report-${Date.now()}`,
      title,
      description,
      issues,
      summary,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      generatedBy,
    };
    
    return report;
  }
  
  /**
   * Save report to storage
   */
  static saveReport(report: A11yReport): void {
    try {
      const existingReports = this.getStoredReports();
      existingReports.push(report);
      
      localStorage.setItem(
        this.storageKey,
        JSON.stringify(existingReports)
      );
    } catch (error) {
      console.error('Failed to save accessibility report:', error);
    }
  }
  
  /**
   * Get stored reports
   */
  static getStoredReports(): A11yReport[] {
    try {
      const stored = localStorage.getItem(this.storageKey);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Failed to load accessibility reports:', error);
      return [];
    }
  }
  
  /**
   * Get report by ID
   */
  static getReportById(id: string): A11yReport | undefined {
    const reports = this.getStoredReports();
    return reports.find(report => report.id === id);
  }
  
  /**
   * Mark issue as resolved
   */
  static resolveIssue(reportId: string, issueId: string, resolvedBy: string): boolean {
    try {
      const reports = this.getStoredReports();
      const reportIndex = reports.findIndex(r => r.id === reportId);
      
      if (reportIndex === -1) {
        return false;
      }
      
      const issueIndex = reports[reportIndex].issues.findIndex(i => i.id === issueId);
      if (issueIndex === -1) {
        return false;
      }
      
      reports[reportIndex].issues[issueIndex].resolved = true;
      reports[reportIndex].issues[issueIndex].resolvedAt = Date.now();
      reports[reportIndex].issues[issueIndex].resolvedBy = resolvedBy;
      reports[reportIndex].updatedAt = Date.now();
      
      // Update summary
      reports[reportIndex].summary.resolved = reports[reportIndex].issues.filter(
        i => i.resolved
      ).length;
      
      localStorage.setItem(
        this.storageKey,
        JSON.stringify(reports)
      );
      
      return true;
    } catch (error) {
      console.error('Failed to resolve accessibility issue:', error);
      return false;
    }
  }
  
  /**
   * Generate HTML report
   */
  static generateHtmlReport(report: A11yReport): string {
    let html = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${report.title}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .header { margin-bottom: 30px; }
          .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
          .issue { border: 1px solid #ddd; margin-bottom: 10px; border-radius: 5px; }
          .issue-header { background: #f9f9f9; padding: 10px; cursor: pointer; }
          .issue-content { padding: 15px; display: none; }
          .critical { border-left: 5px solid #dc3545; }
          .serious { border-left: 5px solid #fd7e14; }
          .moderate { border-left: 5px solid #ffc107; }
          .minor { border-left: 5px solid #17a2b8; }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>${report.title}</h1>
          <p>${report.description}</p>
          <p><strong>Generated:</strong> ${new Date(report.createdAt).toLocaleString()}</p>
        </div>
        
        <div class="summary">
          <h2>Summary</h2>
          <p><strong>Total Issues:</strong> ${report.summary.total}</p>
          <p><strong>Critical:</strong> ${report.summary.critical} | 
             <strong>Serious:</strong> ${report.summary.serious} | 
             <strong>Moderate:</strong> ${report.summary.moderate} | 
             <strong>Minor:</strong> ${report.summary.minor}</p>
          <p><strong>Resolved:</strong> ${report.summary.resolved}/${report.summary.total}</p>
        </div>
    `;
    
    for (const issue of report.issues) {
      const severityClass = issue.severity;
      const resolvedText = issue.resolved 
        ? ` <span style="color: green;">(RESOLVED ${new Date(issue.resolvedAt!).toLocaleDateString()})</span>`
        : '';
      
      html += `
        <div class="issue ${severityClass}">
          <div class="issue-header">
            <strong>${issue.severity.toUpperCase()}: ${issue.description}</strong>
            ${resolvedText}
          </div>
          <div class="issue-content">
            <p><strong>Help:</strong> ${issue.help}</p>
            <p><strong>URL:</strong> ${issue.url}</p>
            <p><strong>Tags:</strong> ${issue.tags.join(', ')}</p>
            ${issue.element ? `<p><strong>Element:</strong> <code>${issue.element}</code></p>` : ''}
          </div>
        </div>
      `;
    }
    
    html += `
      </body>
      </html>
    `;
    
    return html;
  }
  
  /**
   * Export report as JSON
   */
  static exportReportJson(report: A11yReport): string {
    return JSON.stringify(report, null, 2);
  }
  
  /**
   * Export report as CSV
   */
  static exportReportCsv(report: A11yReport): string {
    let csv = 'ID,Type,Severity,Description,Help,URL,Element,Tags,Resolved\n';
    
    for (const issue of report.issues) {
      const row = [
        issue.id,
        issue.type,
        issue.severity,
        `"${issue.description.replace(/"/g, '""')}"`,
        `"${issue.help.replace(/"/g, '""')}"`,
        issue.url,
        issue.element ? `"${issue.element.replace(/"/g, '""')}"` : '',
        `"${issue.tags.join(';').replace(/"/g, '""')}"`,
        issue.resolved ? 'Yes' : 'No'
      ].join(',');
      
      csv += row + '\n';
    }
    
    return csv;
  }
}

export default A11yReporter;