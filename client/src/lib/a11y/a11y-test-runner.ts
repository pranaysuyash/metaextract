/**
 * Accessibility Testing Suite - Automated testing for WCAG 2.1 AA compliance
 */

import { AxePuppeteer } from '@axe-core/puppeteer';
import { Page } from 'puppeteer';

export interface A11yTestResult {
  url: string;
  violations: any[];
  incomplete: any[];
  passes: any[];
  timestamp: number;
  wcagLevel: 'A' | 'AA' | 'AAA';
}

export interface A11yAuditConfig {
  include?: string[];
  exclude?: string[];
  tags?: string[];
  runOnly?: string[];
  resultTypes?: ('violations' | 'incomplete' | 'passes' | 'inapplicable')[];
}

export class A11yTestRunner {
  /**
   * Run accessibility test on a page
   */
  static async runAccessibilityTest(
    page: Page,
    config: A11yAuditConfig = {}
  ): Promise<A11yTestResult> {
    try {
      const runner = new AxePuppeteer(page);
      
      if (config.include) {
        config.include.forEach(selector => runner.include(selector));
      }
      
      if (config.exclude) {
        config.exclude.forEach(selector => runner.exclude(selector));
      }
      
      if (config.runOnly) {
        runner.options({
          runOnly: {
            type: 'tag',
            values: config.runOnly,
          },
        });
      }
      
      const results = await runner.analyze();
      
      return {
        url: page.url(),
        violations: results.violations,
        incomplete: results.incomplete,
        passes: results.passes,
        timestamp: Date.now(),
        wcagLevel: 'AA', // Default to AA for our compliance
      };
    } catch (error) {
      console.error('Accessibility test failed:', error);
      throw error;
    }
  }

  /**
   * Run comprehensive audit
   */
  static async runComprehensiveAudit(
    page: Page,
    config: A11yAuditConfig = {}
  ): Promise<A11yTestResult> {
    // Run standard accessibility test
    const result = await this.runAccessibilityTest(page, {
      ...config,
      runOnly: config.runOnly || ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'],
    });

    // Additional custom checks
    const customViolations = await this.runCustomChecks(page);
    result.violations = [...result.violations, ...customViolations];

    return result;
  }

  /**
   * Run custom accessibility checks
   */
  private static async runCustomChecks(page: Page): Promise<any[]> {
    const customChecks = [];

    // Check for focus indicators
    const hasFocusStyles = await page.evaluate(() => {
      const styleSheets = Array.from(document.styleSheets);
      return styleSheets.some(sheet => {
        try {
          const rules = Array.from(sheet.cssRules);
          return rules.some(rule => 
            rule instanceof CSSStyleRule && 
            rule.selectorText?.includes(':focus')
          );
        } catch {
          return false;
        }
      });
    });

    if (!hasFocusStyles) {
      customChecks.push({
        id: 'focus-styles',
        impact: 'serious',
        tags: ['cat.keyboard'],
        description: 'No focus styles found',
        help: 'Provide a visible focus indicator for keyboard users',
        nodes: [{ html: 'document', target: ['document'] }],
      });
    }

    // Check for color contrast
    const lowContrastElements = await page.evaluate(() => {
      // This is a simplified check - in practice, you'd want a more comprehensive solution
      const elements = Array.from(document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6, a, button, input, label'));
      const lowContrast = [];
      
      // Simplified contrast check (would need proper algorithm in real implementation)
      for (const element of elements) {
        const style = window.getComputedStyle(element);
        const bgColor = style.backgroundColor;
        const textColor = style.color;
        
        // Placeholder for actual contrast calculation
        if (element.textContent && element.textContent.trim().length > 10) {
          // In a real implementation, calculate contrast ratio
          // For now, just return elements as potential issues
          lowContrast.push(element.outerHTML.substring(0, 100));
        }
      }
      
      return lowContrast;
    });

    if (lowContrastElements.length > 0) {
      customChecks.push({
        id: 'color-contrast',
        impact: 'serious',
        tags: ['cat.color-contract'],
        description: 'Possible low contrast elements found',
        help: 'Ensure sufficient color contrast between text and background',
        nodes: lowContrastElements.map(html => ({ html, target: [html.substring(0, 20)] })),
      });
    }

    return customChecks;
  }

  /**
   * Generate accessibility report
   */
  static generateReport(results: A11yTestResult[]): string {
    const totalViolations = results.reduce((sum, result) => sum + result.violations.length, 0);
    const totalIncomplete = results.reduce((sum, result) => sum + result.incomplete.length, 0);
    
    let report = `# Accessibility Report\n\n`;
    report += `**Generated:** ${new Date().toISOString()}\n`;
    report += `**Total Violations:** ${totalViolations}\n`;
    report += `**Total Incomplete:** ${totalIncomplete}\n\n`;
    
    for (const result of results) {
      report += `## Page: ${result.url}\n`;
      report += `**Violations:** ${result.violations.length}\n`;
      report += `**Incomplete:** ${result.incomplete.length}\n\n`;
      
      if (result.violations.length > 0) {
        report += `### Violations\n`;
        for (const violation of result.violations) {
          report += `- **${violation.id}** (${violation.impact}): ${violation.description}\n`;
          report += `  - ${violation.nodes.length} element(s) affected\n`;
        }
        report += `\n`;
      }
    }
    
    return report;
  }
}

export default A11yTestRunner;