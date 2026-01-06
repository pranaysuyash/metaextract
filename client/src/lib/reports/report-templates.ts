/**
 * Report Templates - Pre-built report formats
 */

import { ReportData, ReportTemplate } from './report-generator';

export interface ReportTemplateData {
  id: string;
  name: string;
  description: string;
  category: 'executive' | 'operational' | 'analytical' | 'compliance';
  metrics: string[];
  charts: string[];
  tables: string[];
  insights: string[];
  recommendations: string[];
  defaultDateRange: [number, number]; // Days from today
}

export class ReportTemplates {
  /**
   * Get all available report templates
   */
  static getTemplates(): ReportTemplateData[] {
    return [
      {
        id: 'executive-summary',
        name: 'Executive Summary',
        description: 'High-level overview with key metrics and insights for leadership',
        category: 'executive',
        metrics: [
          'total-uploads',
          'successful-extractions',
          'revenue',
          'active-users',
          'conversion-rate',
          'avg-processing-time'
        ],
        charts: [
          'uploads-trend',
          'revenue-trend',
          'user-growth',
          'conversion-rate-trend'
        ],
        tables: [
          'top-performing-segments',
          'feature-usage-summary',
          'geographic-distribution'
        ],
        insights: [
          'Upload volume increased by 12.5% compared to previous period',
          'Enterprise tier users show highest engagement and conversion rates',
          'Processing performance has improved with reduced error rates',
          'New feature adoption is driving increased user engagement'
        ],
        recommendations: [
          'Consider expanding enterprise tier features to drive higher revenue',
          'Investigate conversion funnel to improve free-to-paid conversion',
          'Plan capacity expansion based on growth trends',
          'Focus marketing efforts on high-converting user segments'
        ],
        defaultDateRange: [30, 0] // Last 30 days
      },
      {
        id: 'operational-metrics',
        name: 'Operational Metrics',
        description: 'Detailed metrics for operational teams and system performance',
        category: 'operational',
        metrics: [
          'system-uptime',
          'error-rate',
          'avg-processing-time',
          'throughput',
          'queue-size',
          'resource-usage'
        ],
        charts: [
          'performance-trend',
          'error-rate-trend',
          'resource-usage-trend',
          'throughput-trend'
        ],
        tables: [
          'system-metrics',
          'error-breakdown',
          'resource-usage-breakdown'
        ],
        insights: [
          'System uptime remained above 99.9% during reporting period',
          'Processing queue showed no significant bottlenecks',
          'Error rates decreased by 15% compared to previous period',
          'Resource usage remains within acceptable limits'
        ],
        recommendations: [
          'Continue monitoring system performance as user base grows',
          'Implement additional error handling for edge cases',
          'Optimize resource allocation based on usage patterns',
          'Plan for capacity expansion during peak usage times'
        ],
        defaultDateRange: [7, 0] // Last 7 days
      },
      {
        id: 'user-analytics',
        name: 'User Analytics',
        description: 'User behavior, engagement, and feature usage metrics',
        category: 'analytical',
        metrics: [
          'new-users',
          'retention-rate',
          'session-duration',
          'conversion-rate',
          'feature-usage',
          'user-satisfaction'
        ],
        charts: [
          'user-growth',
          'engagement-trend',
          'feature-usage-trend',
          'retention-trend'
        ],
        tables: [
          'user-segmentation',
          'feature-usage-breakdown',
          'user-journey-analysis'
        ],
        insights: [
          'User engagement increased by 8% with new feature adoption',
          'Free tier users show potential for conversion to paid tiers',
          'Geographic distribution of users remains consistent',
          'Most popular features are metadata extraction and file comparison'
        ],
        recommendations: [
          'Develop targeted onboarding for free tier users',
          'Analyze feature usage to prioritize development efforts',
          'Create user cohorts for more granular analysis',
          'Improve onboarding flow for new users'
        ],
        defaultDateRange: [30, 0] // Last 30 days
      },
      {
        id: 'compliance-report',
        name: 'Compliance Report',
        description: 'Regulatory and compliance metrics for auditing purposes',
        category: 'compliance',
        metrics: [
          'data-retention',
          'access-audits',
          'privacy-compliance',
          'security-incident',
          'gdpr-requests',
          'data-breach-incident'
        ],
        charts: [
          'compliance-trend',
          'audit-logs',
          'privacy-requests-trend',
          'security-incident-trend'
        ],
        tables: [
          'access-logs',
          'data-retention',
          'compliance-violations',
          'gdpr-request-summary'
        ],
        insights: [
          'All data retention policies were followed during reporting period',
          'No security incidents were reported',
          'Access logs show normal usage patterns',
          'Privacy compliance metrics remain within acceptable limits'
        ],
        recommendations: [
          'Review and update security protocols quarterly',
          'Conduct regular compliance audits',
          'Ensure data retention policies are properly enforced',
          'Update privacy policies as needed'
        ],
        defaultDateRange: [90, 0] // Last 90 days
      },
      {
        id: 'api-usage',
        name: 'API Usage Report',
        description: 'API consumption and performance metrics for enterprise users',
        category: 'analytical',
        metrics: [
          'api-requests',
          'api-errors',
          'response-time',
          'rate-limiting',
          'api-usage-by-client',
          'api-usage-by-endpoint'
        ],
        charts: [
          'api-requests-trend',
          'response-time-trend',
          'error-rate-trend',
          'usage-by-client'
        ],
        tables: [
          'top-api-clients',
          'api-endpoint-usage',
          'error-breakdown',
          'rate-limiting-events'
        ],
        insights: [
          'API usage increased by 22% compared to previous period',
          'Response times remain under 200ms average',
          'Most common errors are related to rate limiting',
          'Top clients account for 60% of total API usage'
        ],
        recommendations: [
          'Monitor rate limiting to ensure fair usage',
          'Optimize endpoints with higher error rates',
          'Consider API versioning for breaking changes',
          'Provide usage analytics to enterprise clients'
        ],
        defaultDateRange: [30, 0] // Last 30 days
      },
      {
        id: 'team-collaboration',
        name: 'Team Collaboration Report',
        description: 'Team usage and collaboration metrics for enterprise accounts',
        category: 'analytical',
        metrics: [
          'team-activity',
          'shared-results',
          'collaboration-events',
          'team-growth',
          'feature-usage-by-team',
          'collaboration-success-rate'
        ],
        charts: [
          'team-activity-trend',
          'collaboration-events-trend',
          'team-growth',
          'feature-usage-by-team'
        ],
        tables: [
          'top-active-teams',
          'collaboration-breakdown',
          'team-engagement',
          'feature-usage-summary'
        ],
        insights: [
          'Team collaboration increased by 35% compared to previous period',
          'Most active teams are using shared results feature',
          'Collaboration success rate is above 90%',
          'Team growth is driving overall platform adoption'
        ],
        recommendations: [
          'Enhance collaboration features based on team feedback',
          'Provide team-based analytics and reporting',
          'Create team onboarding materials',
          'Develop team-based feature recommendations'
        ],
        defaultDateRange: [30, 0] // Last 30 days
      }
    ];
  }

  /**
   * Get a specific template by ID
   */
  static getTemplateById(id: string): ReportTemplateData | undefined {
    return this.getTemplates().find(template => template.id === id);
  }

  /**
   * Get templates by category
   */
  static getTemplatesByCategory(category: ReportTemplateData['category']): ReportTemplateData[] {
    return this.getTemplates().filter(template => template.category === category);
  }

  /**
   * Generate a report based on a template
   */
  static generateReportFromTemplate(
    templateId: string,
    startDate?: Date,
    endDate?: Date
  ): ReportData {
    const template = this.getTemplateById(templateId);
    if (!template) {
      throw new Error(`Template with ID ${templateId} not found`);
    }

    // Calculate date range if not provided
    const end = endDate || new Date();
    const start = startDate || new Date(end);
    start.setDate(start.getDate() - template.defaultDateRange[0]);

    // Generate mock data based on template
    return {
      title: template.name,
      description: template.description,
      dateRange: [start, end],
      metrics: this.generateMockMetrics(template.metrics),
      charts: this.generateMockCharts(template.charts),
      tables: this.generateMockTables(template.tables),
      insights: template.insights,
      recommendations: template.recommendations,
      metadata: {
        generatedAt: new Date(),
        generatedBy: 'System',
        reportId: `report-${templateId}-${Date.now()}`
      }
    };
  }

  /**
   * Generate mock metrics based on template requirements
   */
  private static generateMockMetrics(metricTypes: string[]): any[] {
    const metrics: any[] = [];
    
    for (const type of metricTypes) {
      switch (type) {
        case 'total-uploads':
          metrics.push({
            name: 'Total Uploads',
            value: Math.floor(Math.random() * 10000) + 5000,
            change: `+${(Math.random() * 10).toFixed(1)}%`,
            trend: 'up',
            description: 'Total number of files uploaded'
          });
          break;
        case 'successful-extractions':
          metrics.push({
            name: 'Successful Extractions',
            value: Math.floor(Math.random() * 8000) + 4000,
            change: `+${(Math.random() * 8).toFixed(1)}%`,
            trend: 'up',
            description: 'Successfully processed metadata extractions'
          });
          break;
        case 'revenue':
          metrics.push({
            name: 'Revenue',
            value: `$${(Math.random() * 50000 + 10000).toFixed(0)}`,
            change: `+${(Math.random() * 15).toFixed(1)}%`,
            trend: 'up',
            description: 'Monthly recurring revenue'
          });
          break;
        case 'active-users':
          metrics.push({
            name: 'Active Users',
            value: Math.floor(Math.random() * 2000) + 500,
            change: `+${(Math.random() * 6).toFixed(1)}%`,
            trend: 'up',
            description: 'Unique active users in period'
          });
          break;
        case 'conversion-rate':
          metrics.push({
            name: 'Conversion Rate',
            value: `${(Math.random() * 10 + 2).toFixed(2)}%`,
            change: `+${(Math.random() * 2).toFixed(1)}%`,
            trend: 'up',
            description: 'Percentage of free users converting to paid'
          });
          break;
        case 'avg-processing-time':
          metrics.push({
            name: 'Avg. Processing Time',
            value: `${(Math.random() * 3 + 1).toFixed(2)}s`,
            change: `-${(Math.random() * 5).toFixed(1)}%`,
            trend: 'down',
            description: 'Average time to process a file'
          });
          break;
        case 'system-uptime':
          metrics.push({
            name: 'System Uptime',
            value: `${(Math.random() * 0.9 + 99).toFixed(2)}%`,
            change: `+${(Math.random() * 0.1).toFixed(1)}%`,
            trend: 'up',
            description: 'System availability percentage'
          });
          break;
        case 'error-rate':
          metrics.push({
            name: 'Error Rate',
            value: `${(Math.random() * 2).toFixed(2)}%`,
            change: `-${(Math.random() * 10).toFixed(1)}%`,
            trend: 'down',
            description: 'Percentage of failed operations'
          });
          break;
        case 'new-users':
          metrics.push({
            name: 'New Users',
            value: Math.floor(Math.random() * 500) + 100,
            change: `+${(Math.random() * 12).toFixed(1)}%`,
            trend: 'up',
            description: 'New user registrations'
          });
          break;
        case 'retention-rate':
          metrics.push({
            name: 'Retention Rate',
            value: `${(Math.random() * 30 + 60).toFixed(1)}%`,
            change: `+${(Math.random() * 3).toFixed(1)}%`,
            trend: 'up',
            description: 'User retention after 30 days'
          });
          break;
        case 'session-duration':
          metrics.push({
            name: 'Avg. Session Duration',
            value: `${Math.floor(Math.random() * 20 + 5)} min`,
            change: `+${(Math.random() * 8).toFixed(1)}%`,
            trend: 'up',
            description: 'Average time users spend on platform'
          });
          break;
        case 'user-satisfaction':
          metrics.push({
            name: 'User Satisfaction',
            value: `${(Math.random() * 1 + 4).toFixed(1)}/5`,
            change: `+${(Math.random() * 0.2).toFixed(1)}`,
            trend: 'up',
            description: 'Based on user feedback surveys'
          });
          break;
        case 'api-requests':
          metrics.push({
            name: 'API Requests',
            value: Math.floor(Math.random() * 50000) + 10000,
            change: `+${(Math.random() * 25).toFixed(1)}%`,
            trend: 'up',
            description: 'Total API requests processed'
          });
          break;
        case 'api-errors':
          metrics.push({
            name: 'API Errors',
            value: Math.floor(Math.random() * 500) + 50,
            change: `-${(Math.random() * 15).toFixed(1)}%`,
            trend: 'down',
            description: 'API requests that resulted in errors'
          });
          break;
        case 'response-time':
          metrics.push({
            name: 'Avg. Response Time',
            value: `${Math.floor(Math.random() * 150 + 50)}ms`,
            change: `-${(Math.random() * 10).toFixed(1)}%`,
            trend: 'down',
            description: 'Average API response time'
          });
          break;
        case 'team-activity':
          metrics.push({
            name: 'Team Activity',
            value: Math.floor(Math.random() * 1000) + 200,
            change: `+${(Math.random() * 35).toFixed(1)}%`,
            trend: 'up',
            description: 'Team collaboration events'
          });
          break;
        case 'shared-results':
          metrics.push({
            name: 'Shared Results',
            value: Math.floor(Math.random() * 800) + 150,
            change: `+${(Math.random() * 40).toFixed(1)}%`,
            trend: 'up',
            description: 'Results shared between team members'
          });
          break;
        default:
          metrics.push({
            name: type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            value: Math.floor(Math.random() * 1000),
            change: `+${(Math.random() * 5).toFixed(1)}%`,
            trend: Math.random() > 0.5 ? 'up' : 'down',
            description: 'General metric'
          });
      }
    }
    
    return metrics;
  }

  /**
   * Generate mock charts based on template requirements
   */
  private static generateMockCharts(chartTypes: string[]): any[] {
    const charts: any[] = [];
    
    for (const type of chartTypes) {
      switch (type) {
        case 'uploads-trend':
          charts.push({
            title: 'Uploads Trend',
            type: 'line',
            data: Array.from({ length: 30 }, (_, i) => ({
              date: `Day ${i + 1}`,
              uploads: Math.floor(Math.random() * 500) + 200
            })),
            labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
          });
          break;
        case 'revenue-trend':
          charts.push({
            title: 'Revenue Trend',
            type: 'area',
            data: Array.from({ length: 12 }, (_, i) => ({
              month: `Month ${i + 1}`,
              revenue: Math.floor(Math.random() * 10000) + 5000
            })),
            labels: Array.from({ length: 12 }, (_, i) => `Month ${i + 1}`)
          });
          break;
        case 'user-growth':
          charts.push({
            title: 'User Growth',
            type: 'bar',
            data: Array.from({ length: 7 }, (_, i) => ({
              day: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
              users: Math.floor(Math.random() * 200) + 50
            })),
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
          });
          break;
        case 'conversion-rate-trend':
          charts.push({
            title: 'Conversion Rate Trend',
            type: 'line',
            data: Array.from({ length: 30 }, (_, i) => ({
              date: `Day ${i + 1}`,
              rate: (Math.random() * 5 + 2).toFixed(2)
            })),
            labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
          });
          break;
        case 'performance-trend':
          charts.push({
            title: 'Performance Trend',
            type: 'line',
            data: Array.from({ length: 7 }, (_, i) => ({
              day: `Day ${i + 1}`,
              responseTime: Math.floor(Math.random() * 100) + 50,
              uptime: (Math.random() * 0.9 + 99).toFixed(2)
            })),
            labels: Array.from({ length: 7 }, (_, i) => `Day ${i + 1}`)
          });
          break;
        case 'error-rate-trend':
          charts.push({
            title: 'Error Rate Trend',
            type: 'line',
            data: Array.from({ length: 30 }, (_, i) => ({
              date: `Day ${i + 1}`,
              rate: (Math.random() * 2).toFixed(2)
            })),
            labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
          });
          break;
        case 'engagement-trend':
          charts.push({
            title: 'User Engagement Trend',
            type: 'area',
            data: Array.from({ length: 30 }, (_, i) => ({
              date: `Day ${i + 1}`,
              engagement: Math.floor(Math.random() * 80) + 20
            })),
            labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
          });
          break;
        case 'retention-trend':
          charts.push({
            title: 'User Retention Trend',
            type: 'line',
            data: Array.from({ length: 12 }, (_, i) => ({
              month: `Month ${i + 1}`,
              retention: (Math.random() * 30 + 60).toFixed(1)
            })),
            labels: Array.from({ length: 12 }, (_, i) => `Month ${i + 1}`)
          });
          break;
        case 'api-requests-trend':
          charts.push({
            title: 'API Requests Trend',
            type: 'line',
            data: Array.from({ length: 30 }, (_, i) => ({
              date: `Day ${i + 1}`,
              requests: Math.floor(Math.random() * 2000) + 500
            })),
            labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
          });
          break;
        case 'response-time-trend':
          charts.push({
            title: 'API Response Time Trend',
            type: 'line',
            data: Array.from({ length: 30 }, (_, i) => ({
              date: `Day ${i + 1}`,
              responseTime: Math.floor(Math.random() * 100) + 50
            })),
            labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
          });
          break;
        case 'team-activity-trend':
          charts.push({
            title: 'Team Activity Trend',
            type: 'area',
            data: Array.from({ length: 30 }, (_, i) => ({
              date: `Day ${i + 1}`,
              activity: Math.floor(Math.random() * 100) + 20
            })),
            labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
          });
          break;
        default:
          charts.push({
            title: type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            type: 'bar',
            data: Array.from({ length: 5 }, (_, i) => ({
              category: `Category ${i + 1}`,
              value: Math.floor(Math.random() * 100)
            })),
            labels: Array.from({ length: 5 }, (_, i) => `Category ${i + 1}`)
          });
      }
    }
    
    return charts;
  }

  /**
   * Generate mock tables based on template requirements
   */
  private static generateMockTables(tableTypes: string[]): any[] {
    const tables: any[] = [];
    
    for (const type of tableTypes) {
      switch (type) {
        case 'top-performing-segments':
          tables.push({
            title: 'Top Performing Segments',
            headers: ['Segment', 'Users', 'Conversions', 'Conversion Rate'],
            rows: [
              ['Enterprise', '1,200', '800', '66.7%'],
              ['Pro', '3,500', '1,200', '34.3%'],
              ['Starter', '5,200', '450', '8.7%'],
              ['Free', '12,000', '120', '1.0%']
            ]
          });
          break;
        case 'feature-usage-summary':
          tables.push({
            title: 'Feature Usage Summary',
            headers: ['Feature', 'Usage Count', 'Engagement'],
            rows: [
              ['Metadata Extraction', '24,568', 'High'],
              ['File Comparison', '8,432', 'Medium'],
              ['Batch Processing', '3,210', 'Medium'],
              ['Timeline View', '1,876', 'Low']
            ]
          });
          break;
        case 'geographic-distribution':
          tables.push({
            title: 'Geographic Distribution',
            headers: ['Region', 'Users', 'Uploads'],
            rows: [
              ['North America', '8,500', '45,231'],
              ['Europe', '6,200', '32,109'],
              ['Asia-Pacific', '4,800', '28,765'],
              ['Other', '2,400', '12,345']
            ]
          });
          break;
        case 'system-metrics':
          tables.push({
            title: 'System Metrics',
            headers: ['Metric', 'Value', 'Status'],
            rows: [
              ['CPU Usage', '45%', 'Normal'],
              ['Memory Usage', '62%', 'Normal'],
              ['Disk Usage', '78%', 'Normal'],
              ['Network I/O', 'Low', 'Normal']
            ]
          });
          break;
        case 'error-breakdown':
          tables.push({
            title: 'Error Breakdown',
            headers: ['Error Type', 'Count', 'Severity'],
            rows: [
              ['File Upload', '120', 'Low'],
              ['Processing', '45', 'Medium'],
              ['Database', '8', 'High'],
              ['Authentication', '23', 'Medium']
            ]
          });
          break;
        case 'user-segmentation':
          tables.push({
            title: 'User Segmentation',
            headers: ['Tier', 'Users', 'Activity', 'Revenue'],
            rows: [
              ['Enterprise', '1,200', 'High', '$15,000'],
              ['Pro', '3,500', 'Medium', '$10,500'],
              ['Starter', '5,200', 'Low', '$2,600'],
              ['Free', '12,000', 'Very Low', '$0']
            ]
          });
          break;
        case 'feature-usage-breakdown':
          tables.push({
            title: 'Feature Usage Breakdown',
            headers: ['Feature', 'Usage', 'Growth'],
            rows: [
              ['Metadata Extraction', '24,568', '+12%'],
              ['File Comparison', '8,432', '+8%'],
              ['Batch Processing', '3,210', '+15%'],
              ['Timeline View', '1,876', '+22%']
            ]
          });
          break;
        case 'top-api-clients':
          tables.push({
            title: 'Top API Clients',
            headers: ['Client', 'Requests', 'Errors'],
            rows: [
              ['Client A', '12,456', '23'],
              ['Client B', '9,876', '12'],
              ['Client C', '7,654', '8'],
              ['Client D', '5,432', '15']
            ]
          });
          break;
        case 'api-endpoint-usage':
          tables.push({
            title: 'API Endpoint Usage',
            headers: ['Endpoint', 'Calls', 'Avg. Response'],
            rows: [
              ['/api/extract', '24,568', '120ms'],
              ['/api/upload', '18,765', '210ms'],
              ['/api/results', '15,432', '80ms'],
              ['/api/batch', '3,210', '450ms']
            ]
          });
          break;
        case 'top-active-teams':
          tables.push({
            title: 'Top Active Teams',
            headers: ['Team', 'Members', 'Activity', 'Shared Results'],
            rows: [
              ['Team Alpha', '12', 'High', '456'],
              ['Team Beta', '8', 'Medium', '234'],
              ['Team Gamma', '15', 'High', '678'],
              ['Team Delta', '5', 'Low', '89']
            ]
          });
          break;
        case 'collaboration-breakdown':
          tables.push({
            title: 'Collaboration Breakdown',
            headers: ['Activity', 'Count', 'Success Rate'],
            rows: [
              ['File Sharing', '1,234', '98.5%'],
              ['Result Comments', '876', '95.2%'],
              ['Team Invites', '234', '92.1%'],
              ['Collaborative Editing', '567', '96.8%']
            ]
          });
          break;
        default:
          tables.push({
            title: type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            headers: ['Category', 'Value', 'Change'],
            rows: [
              ['Category A', '100', '+5%'],
              ['Category B', '200', '-2%'],
              ['Category C', '150', '+12%'],
              ['Category D', '300', '+8%']
            ]
          });
      }
    }
    
    return tables;
  }
}

export default ReportTemplates;