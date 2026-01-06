/**
 * Accessibility Audit - WCAG 2.1 AA compliance checking
 */

import { runAccessibilityCheck, AccessibilityCheckResult } from './accessibility-utils';

export interface AuditResult {
  id: string;
  timestamp: Date;
  url: string;
  page: string;
  results: AccessibilityCheckResult[];
  summary: {
    total: number;
    errors: number;
    warnings: number;
    notices: number;
    passRate: number;
  };
  metadata: {
    userAgent: string;
    viewport: { width: number; height: number };
    colorScheme: 'light' | 'dark' | 'no-preference';
    reducedMotion: boolean;
    reducedTransparency: boolean;
    highContrast: boolean;
  };
}

export interface AuditConfig {
  include: string[];  // CSS selectors to include in audit
  exclude: string[];  // CSS selectors to exclude from audit
  rules: string[];    // Specific rules to check
  tags: string[];     // WCAG levels to check (wcag2a, wcag2aa, wcag21a, wcag21aa)
  runOnly: {
    type: 'tag' | 'rule';
    values: string[];
  };
}

export const DEFAULT_AUDIT_CONFIG: AuditConfig = {
  include: [],
  exclude: ['iframe'], // Exclude iframes by default
  rules: [],
  tags: ['wcag21aa'], // Target WCAG 2.1 AA compliance
  runOnly: {
    type: 'tag',
    values: ['wcag21aa']
  }
};

export class AccessibilityAuditor {
  private config: AuditConfig;
  private auditHistory: AuditResult[] = [];

  constructor(config?: Partial<AuditConfig>) {
    this.config = { ...DEFAULT_AUDIT_CONFIG, ...config };
  }

  /**
   * Run accessibility audit on a page
   */
  async auditPage(
    pageUrl: string,
    element?: HTMLElement,
    customConfig?: Partial<AuditConfig>
  ): Promise<AuditResult> {
    const auditConfig = { ...this.config, ...customConfig };
    
    // In a real implementation, this would run axe-core or similar
    // For now, we'll simulate the process
    const results: AccessibilityCheckResult[] = await this.simulateAudit(element || document.body, auditConfig);
    
    const summary = this.generateSummary(results);
    const metadata = this.getMetadata();
    
    const auditResult: AuditResult = {
      id: `audit-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      url: pageUrl,
      page: this.getPageName(pageUrl),
      results,
      summary,
      metadata
    };
    
    this.auditHistory.push(auditResult);
    
    return auditResult;
  }

  /**
   * Simulate accessibility audit (for demo purposes)
   */
  private async simulateAudit(element: HTMLElement, config: AuditConfig): Promise<AccessibilityCheckResult[]> {
    // This is a simulation - in a real implementation, this would run axe-core
    // or another accessibility testing library
    
    const simulatedResults: AccessibilityCheckResult[] = [];
    
    // Check for common accessibility issues
    const allElements = Array.from(element.querySelectorAll('*'));
    
    // Check for missing alt text on images
    const images = allElements.filter(el => el.tagName === 'IMG') as HTMLImageElement[];
    for (const img of images) {
      if (!img.alt || img.alt.trim() === '') {
        simulatedResults.push({
          id: 'image-alt-missing',
          type: 'error',
          message: `Image missing alt text: ${img.src || 'unknown source'}`,
          element: img,
          impact: 'critical'
        });
      }
    }
    
    // Check for low contrast text
    const textElements = allElements.filter(el => 
      window.getComputedStyle(el).color && 
      window.getComputedStyle(el).backgroundColor
    ) as HTMLElement[];
    
    for (const el of textElements) {
      const style = window.getComputedStyle(el);
      const fgColor = this.parseColor(style.color);
      const bgColor = this.parseColor(style.backgroundColor);
      
      if (fgColor && bgColor) {
        const contrast = this.calculateContrast(fgColor, bgColor);
        
        if (contrast < 4.5) {
          simulatedResults.push({
            id: 'low-contrast',
            type: 'error',
            message: `Text element has low contrast ratio: ${contrast}:1`,
            element: el,
            impact: 'serious'
          });
        }
      }
    }
    
    // Check for focusable elements without proper labels
    const focusableElements = allElements.filter(el => 
      (el as HTMLElement).tabIndex >= 0 || 
      ['BUTTON', 'INPUT', 'TEXTAREA', 'SELECT', 'A'].includes(el.tagName)
    ) as HTMLElement[];
    
    for (const el of focusableElements) {
      if (!el.getAttribute('aria-label') && !el.getAttribute('aria-labelledby')) {
        // Check if it has a visible label
        const hasVisibleLabel = this.hasVisibleLabel(el);
        if (!hasVisibleLabel) {
          simulatedResults.push({
            id: 'focusable-no-label',
            type: 'error',
            message: `Focusable element missing accessible label: ${el.tagName.toLowerCase()}`,
            element: el,
            impact: 'moderate'
          });
        }
      }
    }
    
    // Check for proper heading hierarchy
    const headings = allElements.filter(el => 
      ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'].includes(el.tagName)
    );
    
    if (headings.length > 0) {
      let lastLevel = 0;
      for (const heading of headings) {
        const level = parseInt(heading.tagName.charAt(1));
        if (level > lastLevel + 1) {
          simulatedResults.push({
            id: 'heading-skipped-level',
            type: 'warning',
            message: `Heading level skipped from H${lastLevel} to H${level}`,
            element: heading,
            impact: 'moderate'
          });
        }
        lastLevel = level;
      }
    }
    
    return simulatedResults;
  }

  /**
   * Parse color string to RGB values
   */
  private parseColor(color: string): { r: number; g: number; b: number } | null {
    if (!color) return null;
    
    // Handle hex colors
    if (color.startsWith('#')) {
      const hex = color.slice(1);
      if (hex.length === 3) {
        const [r, g, b] = hex.split('').map(c => parseInt(c + c, 16));
        return { r, g, b };
      } else if (hex.length === 6) {
        const [r, g, b] = hex.match(/.{2}/g)!.map(c => parseInt(c, 16));
        return { r, g, b };
      }
    }
    
    // Handle rgb/rgba colors
    if (color.startsWith('rgb')) {
      const values = color.match(/\d+/g);
      if (values && values.length >= 3) {
        return {
          r: parseInt(values[0]),
          g: parseInt(values[1]),
          b: parseInt(values[2])
        };
      }
    }
    
    return null;
  }

  /**
   * Calculate contrast ratio between two colors
   */
  private calculateContrast(
    color1: { r: number; g: number; b: number },
    color2: { r: number; g: number; b: number }
  ): number {
    const luminance = (color: { r: number; g: number; b: number }) => {
      const [r, g, b] = [color.r, color.g, color.b].map(val => {
        const srgb = val / 255;
        return srgb <= 0.03928 ? srgb / 12.92 : Math.pow((srgb + 0.055) / 1.055, 2.4);
      });
      
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };

    const lum1 = luminance(color1) + 0.05;
    const lum2 = luminance(color2) + 0.05;
    const ratio = Math.max(lum1, lum2) / Math.min(lum1, lum2);

    return Number(ratio.toFixed(2));
  }

  /**
   * Check if element has a visible label
   */
  private hasVisibleLabel(element: HTMLElement): boolean {
    // Check for associated label
    if (element.id) {
      const associatedLabel = document.querySelector(`label[for="${element.id}"]`);
      if (associatedLabel && (associatedLabel as HTMLElement).innerText.trim()) {
        return true;
      }
    }
    
    // Check for aria-labelledby
    const labelledBy = element.getAttribute('aria-labelledby');
    if (labelledBy) {
      const labelElement = document.getElementById(labelledBy);
      if (labelElement && labelElement.innerText.trim()) {
        return true;
      }
    }
    
    // Check for title attribute
    const title = element.getAttribute('title');
    if (title && title.trim()) {
      return true;
    }
    
    return false;
  }

  /**
   * Generate audit summary
   */
  private generateSummary(results: AccessibilityCheckResult[]): AuditResult['summary'] {
    const total = results.length;
    const errors = results.filter(r => r.type === 'error').length;
    const warnings = results.filter(r => r.type === 'warning').length;
    const notices = results.filter(r => r.type === 'notice').length;
    
    const passRate = total > 0 ? ((total - errors) / total) * 100 : 100;
    
    return {
      total,
      errors,
      warnings,
      notices,
      passRate: Number(passRate.toFixed(2))
    };
  }

  /**
   * Get metadata about the current environment
   */
  private getMetadata(): AuditResult['metadata'] {
    return {
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      colorScheme: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
      reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
      reducedTransparency: window.matchMedia('(prefers-reduced-transparency: reduce)').matches,
      highContrast: window.matchMedia('(prefers-contrast: high)').matches
    };
  }

  /**
   * Get page name from URL
   */
  private getPageName(url: string): string {
    try {
      const path = new URL(url).pathname;
      return path.split('/').pop() || path || 'home';
    } catch {
      return 'unknown';
    }
  }

  /**
   * Get audit history
   */
  getAuditHistory(): AuditResult[] {
    return [...this.auditHistory];
  }

  /**
   * Get latest audit result
   */
  getLatestAudit(): AuditResult | null {
    return this.auditHistory.length > 0 
      ? this.auditHistory[this.auditHistory.length - 1] 
      : null;
  }

  /**
   * Get audit by ID
   */
  getAuditById(id: string): AuditResult | null {
    return this.auditHistory.find(audit => audit.id === id) || null;
  }

  /**
   * Get audits by page
   */
  getAuditsByPage(page: string): AuditResult[] {
    return this.auditHistory.filter(audit => audit.page === page);
  }

  /**
   * Get audits by date range
   */
  getAuditsByDateRange(startDate: Date, endDate: Date): AuditResult[] {
    return this.auditHistory.filter(
      audit => audit.timestamp >= startDate && audit.timestamp <= endDate
    );
  }

  /**
   * Get compliance summary across all audits
   */
  getComplianceSummary(): {
    totalPagesAudited: number;
    avgPassRate: number;
    totalIssues: number;
    criticalIssues: number;
    highPriorityIssues: number;
    complianceTrend: Array<{ date: Date; passRate: number }>;
  } {
    if (this.auditHistory.length === 0) {
      return {
        totalPagesAudited: 0,
        avgPassRate: 0,
        totalIssues: 0,
        criticalIssues: 0,
        highPriorityIssues: 0,
        complianceTrend: []
      };
    }

    const totalPagesAudited = this.auditHistory.length;
    const avgPassRate = this.auditHistory.reduce((sum, audit) => sum + audit.summary.passRate, 0) / totalPagesAudited;
    
    const totalIssues = this.auditHistory.reduce((sum, audit) => sum + audit.summary.errors, 0);
    const criticalIssues = this.auditHistory.reduce((sum, audit) => 
      sum + audit.results.filter(r => r.impact === 'critical').length, 0);
    const highPriorityIssues = this.auditHistory.reduce((sum, audit) => 
      sum + audit.results.filter(r => r.impact === 'critical' || r.impact === 'serious').length, 0);

    // Generate compliance trend
    const trend = this.auditHistory
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
      .map(audit => ({
        date: audit.timestamp,
        passRate: audit.summary.passRate
      }));

    return {
      totalPagesAudited,
      avgPassRate: Number(avgPassRate.toFixed(2)),
      totalIssues,
      criticalIssues,
      highPriorityIssues,
      complianceTrend: trend
    };
  }

  /**
   * Export audit results as JSON
   */
  exportResults(format: 'json' | 'csv' | 'html' = 'json'): string {
    switch (format) {
      case 'json':
        return JSON.stringify(this.auditHistory, null, 2);
      case 'csv':
        return this.exportToCsv();
      case 'html':
        return this.exportToHtml();
      default:
        return JSON.stringify(this.auditHistory, null, 2);
    }
  }

  /**
   * Export to CSV format
   */
  private exportToCsv(): string {
    const headers = ['Page', 'URL', 'Date', 'Errors', 'Warnings', 'Notices', 'Pass Rate (%)'];
    const rows = this.auditHistory.map(audit => [
      audit.page,
      audit.url,
      audit.timestamp.toISOString(),
      audit.summary.errors,
      audit.summary.warnings,
      audit.summary.notices,
      audit.summary.passRate
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
  private exportToHtml(): string {
    const summary = this.getComplianceSummary();
    
    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Accessibility Audit Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .header { margin-bottom: 30px; }
    .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    .audit-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    .audit-table th, .audit-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    .audit-table th { background-color: #f2f2f2; }
    .error { color: #d32f2f; }
    .warning { color: #f57c00; }
    .notice { color: #1976d2; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Accessibility Audit Report</h1>
    <p>Generated on ${new Date().toISOString()}</p>
  </div>
  
  <div class="summary">
    <h2>Overall Summary</h2>
    <p>Total Pages Audited: ${summary.totalPagesAudited}</p>
    <p>Average Pass Rate: ${summary.avgPassRate}%</p>
    <p>Total Issues: ${summary.totalIssues}</p>
    <p>Critical Issues: ${summary.criticalIssues}</p>
    <p>High Priority Issues: ${summary.highPriorityIssues}</p>
  </div>
  
  <h2>Detailed Results</h2>
  <table class="audit-table">
    <thead>
      <tr>
        <th>Page</th>
        <th>Date</th>
        <th>Errors</th>
        <th>Warnings</th>
        <th>Notices</th>
        <th>Pass Rate</th>
      </tr>
    </thead>
    <tbody>
      ${this.auditHistory.map(audit => `
        <tr>
          <td>${audit.page}</td>
          <td>${audit.timestamp.toLocaleString()}</td>
          <td class="error">${audit.summary.errors}</td>
          <td class="warning">${audit.summary.warnings}</td>
          <td class="notice">${audit.summary.notices}</td>
          <td>${audit.summary.passRate}%</td>
        </tr>
      `).join('')}
    </tbody>
  </table>
</body>
</html>
    `;
  }

  /**
   * Update audit configuration
   */
  updateConfig(newConfig: Partial<AuditConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * Reset audit history
   */
  resetHistory(): void {
    this.auditHistory = [];
  }
}

// Singleton instance
export const accessibilityAuditor = new AccessibilityAuditor();

export default accessibilityAuditor;