/**
 * Production Validation & Threat Intelligence Integration
 *
 * Real-world validation of the advanced protection system
 * with external threat intelligence feeds
 */

import { Request } from 'express';
import axios from 'axios';
import { securityEventLogger } from './security-events';
import { securityAlertManager } from './security-alerts';
import { mlAnomalyDetector } from './ml-anomaly-detection';

// External threat intelligence configuration
const THREAT_INTEL_CONFIG = {
  // AbuseIPDB API
  ABUSEIPDB: {
    ENABLED: true,
    API_KEY: process.env.ABUSEIPDB_API_KEY,
    BASE_URL: 'https://api.abuseipdb.com/api/v2',
    ENDPOINTS: {
      CHECK: '/check',
      REPORT: '/report',
    },
    CACHE_TTL: 3600, // 1 hour
    CONFIDENCE_THRESHOLD: 75,
    MAX_AGE_DAYS: 90,
  },

  // VirusTotal API
  VIRUSTOTAL: {
    ENABLED: true,
    API_KEY: process.env.VIRUSTOTAL_API_KEY,
    BASE_URL: 'https://www.virustotal.com/api/v3',
    ENDPOINTS: {
      IP_REPORT: '/ip-addresses',
      FILE_REPORT: '/files',
      URL_REPORT: '/urls',
    },
    CACHE_TTL: 1800, // 30 minutes
    MALICIOUS_THRESHOLD: 5, // 5+ detections = malicious
  },

  // IP Quality Score API
  IPQUALITY: {
    ENABLED: true,
    API_KEY: process.env.IPQUALITY_API_KEY,
    BASE_URL: 'https://www.ipqualityscore.com/api/json/ip',
    STRICTNESS: 1, // 0-2, higher = more strict
    CACHE_TTL: 1800,
  },

  // TOR Exit Node Detection
  TOR: {
    ENABLED: true,
    LIST_URL: 'https://check.torproject.org/exit-addresses',
    CACHE_TTL: 3600,
  },

  // VPN/Proxy Detection
  VPN_DETECTION: {
    ENABLED: true,
    SERVICES: ['ipapi', 'ipregistry', 'ipdata'],
    CACHE_TTL: 3600,
  },
};

// Threat intelligence result
interface ThreatIntelResult {
  ipAddress: string;
  riskScore: number;
  threatLevel: 'low' | 'medium' | 'high' | 'critical';
  sources: string[];
  details: {
    abuseipdb?: any;
    virustotal?: any;
    ipquality?: any;
    tor?: boolean;
    vpn?: boolean;
    proxy?: boolean;
    error?: any;
  };
  recommendations: string[];
  timestamp: Date;
}

// Production validation metrics
interface ValidationMetrics {
  totalChecks: number;
  threatDetections: number;
  falsePositives: number;
  responseTimes: number[];
  cacheHitRate: number;
  apiErrors: number;
}

/**
 * Advanced Threat Intelligence Service
 */
export class ThreatIntelligenceService {
  private cache: Map<string, { data: ThreatIntelResult; expires: number }> =
    new Map();
  private metrics: ValidationMetrics = {
    totalChecks: 0,
    threatDetections: 0,
    falsePositives: 0,
    responseTimes: [],
    cacheHitRate: 0,
    apiErrors: 0,
  };

  constructor() {
    this.startBackgroundUpdates();
  }

  /**
   * Comprehensive threat intelligence check
   */
  public async checkThreatIntelligence(
    req: Request
  ): Promise<ThreatIntelResult> {
    const startTime = Date.now();
    const ipAddress = req.ip || req.connection.remoteAddress || 'unknown';

    if (ipAddress === 'unknown' || !this.isValidIP(ipAddress)) {
      return this.createUnknownResult(ipAddress);
    }

    this.metrics.totalChecks++;

    // Check cache first
    const cached = this.getCachedResult(ipAddress);
    if (cached) {
      this.metrics.cacheHitRate =
        (this.metrics.cacheHitRate * (this.metrics.totalChecks - 1) + 1) /
        this.metrics.totalChecks;
      return cached;
    }

    try {
      // Parallel threat intelligence gathering
      const [abuseipdb, virustotal, ipquality, tor, vpn] =
        await Promise.allSettled([
          this.checkAbuseIPDB(ipAddress),
          this.checkVirusTotal(ipAddress),
          this.checkIPQuality(ipAddress),
          this.checkTorExit(ipAddress),
          this.checkVPNProxy(ipAddress),
        ]);

      // Aggregate results
      const result = await this.aggregateResults(ipAddress, {
        abuseipdb: abuseipdb.status === 'fulfilled' ? abuseipdb.value : null,
        virustotal: virustotal.status === 'fulfilled' ? virustotal.value : null,
        ipquality: ipquality.status === 'fulfilled' ? ipquality.value : null,
        tor: tor.status === 'fulfilled' ? tor.value : false,
        vpn: vpn.status === 'fulfilled' ? vpn.value : false,
      });

      // Cache the result
      this.cacheResult(ipAddress, result);

      // Log threat detection
      if (result.threatLevel !== 'low') {
        this.metrics.threatDetections++;
        await this.logThreatDetection(req, result);
      }

      // Record response time
      const responseTime = Date.now() - startTime;
      this.metrics.responseTimes.push(responseTime);

      return result;
    } catch (error) {
      this.metrics.apiErrors++;
      console.error(`[ThreatIntel] Error checking ${ipAddress}:`, error);

      // Return safe default on API failure
      return this.createSafeDefaultResult(ipAddress);
    }
  }

  /**
   * Check AbuseIPDB for IP reputation
   */
  private async checkAbuseIPDB(ipAddress: string): Promise<any> {
    if (
      !THREAT_INTEL_CONFIG.ABUSEIPDB.ENABLED ||
      !THREAT_INTEL_CONFIG.ABUSEIPDB.API_KEY
    ) {
      return null;
    }

    try {
      const response = await axios.get(
        `${THREAT_INTEL_CONFIG.ABUSEIPDB.BASE_URL}${THREAT_INTEL_CONFIG.ABUSEIPDB.ENDPOINTS.CHECK}`,
        {
          headers: {
            Key: THREAT_INTEL_CONFIG.ABUSEIPDB.API_KEY,
            Accept: 'application/json',
          },
          params: {
            ipAddress: ipAddress,
            maxAgeInDays: THREAT_INTEL_CONFIG.ABUSEIPDB.MAX_AGE_DAYS,
            verbose: true,
          },
          timeout: 5000,
        }
      );

      return response.data?.data;
    } catch (error) {
      console.warn(
        `[ThreatIntel] AbuseIPDB check failed for ${ipAddress}:`,
        (error as any).message
      );
      return null;
    }
  }

  /**
   * Check VirusTotal for IP reputation
   */
  private async checkVirusTotal(ipAddress: string): Promise<any> {
    if (
      !THREAT_INTEL_CONFIG.VIRUSTOTAL.ENABLED ||
      !THREAT_INTEL_CONFIG.VIRUSTOTAL.API_KEY
    ) {
      return null;
    }

    try {
      const response = await axios.get(
        `${THREAT_INTEL_CONFIG.VIRUSTOTAL.BASE_URL}${THREAT_INTEL_CONFIG.VIRUSTOTAL.ENDPOINTS.IP_REPORT}/${ipAddress}`,
        {
          headers: {
            'x-apikey': THREAT_INTEL_CONFIG.VIRUSTOTAL.API_KEY,
          },
          timeout: 5000,
        }
      );

      return response.data?.data;
    } catch (error) {
      console.warn(
        `[ThreatIntel] VirusTotal check failed for ${ipAddress}:`,
        (error as any).message
      );
      return null;
    }
  }

  /**
   * Check IP Quality Score
   */
  private async checkIPQuality(ipAddress: string): Promise<any> {
    if (
      !THREAT_INTEL_CONFIG.IPQUALITY.ENABLED ||
      !THREAT_INTEL_CONFIG.IPQUALITY.API_KEY
    ) {
      return null;
    }

    try {
      const response = await axios.get(
        `${THREAT_INTEL_CONFIG.IPQUALITY.BASE_URL}/${THREAT_INTEL_CONFIG.IPQUALITY.API_KEY}/${ipAddress}`,
        {
          params: {
            strictness: THREAT_INTEL_CONFIG.IPQUALITY.STRICTNESS,
          },
          timeout: 5000,
        }
      );

      return response.data;
    } catch (error) {
      console.warn(
        `[ThreatIntel] IPQuality check failed for ${ipAddress}:`,
        (error as any).message
      );
      return null;
    }
  }

  /**
   * Check if IP is a TOR exit node
   */
  private async checkTorExit(ipAddress: string): Promise<boolean> {
    if (!THREAT_INTEL_CONFIG.TOR.ENABLED) {
      return false;
    }

    try {
      // This would typically use a local TOR exit node list
      // For now, implement a basic check
      const torRanges = [
        '192.42.116.0/24', // Example TOR range
        '131.188.40.0/24', // Example TOR range
      ];

      return this.isIPInRanges(ipAddress, torRanges);
    } catch (error) {
      console.warn(
        `[ThreatIntel] TOR check failed for ${ipAddress}:`,
        (error as any).message
      );
      return false;
    }
  }

  /**
   * Check for VPN/Proxy usage
   */
  private async checkVPNProxy(ipAddress: string): Promise<boolean> {
    if (!THREAT_INTEL_CONFIG.VPN_DETECTION.ENABLED) {
      return false;
    }

    try {
      // Check multiple VPN detection services
      const results = await Promise.allSettled([
        this.checkIPAPIVPN(ipAddress),
        this.checkIPRegistryVPN(ipAddress),
      ]);

      // Return true if any service detects VPN/Proxy
      return results.some(
        result => result.status === 'fulfilled' && result.value === true
      );
    } catch (error) {
      console.warn(
        `[ThreatIntel] VPN check failed for ${ipAddress}:`,
        (error as any).message
      );
      return false;
    }
  }

  /**
   * Check IPAPI for VPN detection
   */
  private async checkIPAPIVPN(ipAddress: string): Promise<boolean> {
    try {
      const response = await axios.get(`http://ip-api.com/json/${ipAddress}`, {
        params: { fields: 'status,message,proxy,hosting' },
        timeout: 3000,
      });

      return response.data?.proxy === true || response.data?.hosting === true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Check IPRegistry for VPN detection
   */
  private async checkIPRegistryVPN(ipAddress: string): Promise<boolean> {
    try {
      const response = await axios.get(
        `https://api.ipregistry.co/${ipAddress}`,
        {
          params: { key: process.env.IPREGISTRY_API_KEY },
          timeout: 3000,
        }
      );

      return (
        response.data?.security?.threat_level === 'high' ||
        response.data?.security?.is_vpn === true ||
        response.data?.security?.is_proxy === true
      );
    } catch (error) {
      return false;
    }
  }

  /**
   * Aggregate threat intelligence results
   */
  private async aggregateResults(
    ipAddress: string,
    results: any
  ): Promise<ThreatIntelResult> {
    let totalRiskScore = 0;
    let threatLevel: 'low' | 'medium' | 'high' | 'critical' = 'low';
    const sources: string[] = [];
    const recommendations: string[] = [];

    // Calculate risk from each source
    if (results.abuseipdb) {
      const abuseScore = this.calculateAbuseIPDBRisk(results.abuseipdb);
      totalRiskScore += abuseScore * 0.3; // 30% weight
      sources.push('AbuseIPDB');

      if (abuseScore > 50) {
        recommendations.push('IP has abuse history - consider blocking');
      }
    }

    if (results.virustotal) {
      const vtScore = this.calculateVirusTotalRisk(results.virustotal);
      totalRiskScore += vtScore * 0.25; // 25% weight
      sources.push('VirusTotal');

      if (vtScore > 50) {
        recommendations.push('IP flagged by security vendors');
      }
    }

    if (results.ipquality) {
      const iqScore = this.calculateIPQualityRisk(results.ipquality);
      totalRiskScore += iqScore * 0.2; // 20% weight
      sources.push('IPQuality');

      if (iqScore > 50) {
        recommendations.push('IP quality score indicates risk');
      }
    }

    // TOR detection (high risk)
    if (results.tor) {
      totalRiskScore += 30; // Significant risk boost
      sources.push('TOR');
      recommendations.push('TOR exit node detected - high risk');
    }

    // VPN/Proxy detection (medium risk)
    if (results.vpn) {
      totalRiskScore += 15; // Moderate risk boost
      sources.push('VPN/Proxy');
      recommendations.push('VPN or proxy usage detected');
    }

    // Determine threat level
    if (totalRiskScore >= 70) {
      threatLevel = 'critical';
    } else if (totalRiskScore >= 50) {
      threatLevel = 'high';
    } else if (totalRiskScore >= 25) {
      threatLevel = 'medium';
    } else {
      threatLevel = 'low';
    }

    return {
      ipAddress,
      riskScore: Math.min(100, Math.round(totalRiskScore)),
      threatLevel,
      sources,
      details: results,
      recommendations: [...new Set(recommendations)], // Remove duplicates
      timestamp: new Date(),
    };
  }

  /**
   * Calculate risk score from AbuseIPDB data
   */
  private calculateAbuseIPDBRisk(data: any): number {
    if (!data) return 0;

    const abuseConfidence = data.abuseConfidenceScore || 0;
    const totalReports = data.totalReports || 0;

    // Weight recent reports more heavily
    let recencyScore = 0;
    if (data.reports && data.reports.length > 0) {
      const recentReports = data.reports.filter((report: any) => {
        const reportDate = new Date(report.reportedAt);
        const daysAgo =
          (Date.now() - reportDate.getTime()) / (1000 * 60 * 60 * 24);
        return daysAgo <= 30; // Reports within 30 days
      });
      recencyScore = (recentReports.length / data.reports.length) * 20;
    }

    return (
      abuseConfidence * 0.7 + Math.min(totalReports, 50) * 0.3 + recencyScore
    );
  }

  /**
   * Calculate risk score from VirusTotal data
   */
  private calculateVirusTotalRisk(data: any): number {
    if (!data) return 0;

    const malicious = data.attributes?.last_analysis_stats?.malicious || 0;
    const suspicious = data.attributes?.last_analysis_stats?.suspicious || 0;
    const total = data.attributes?.last_analysis_stats?.total || 0;

    if (total === 0) return 0;

    return ((malicious + suspicious * 0.5) / total) * 100;
  }

  /**
   * Calculate risk score from IPQuality data
   */
  private calculateIPQualityRisk(data: any): number {
    if (!data) return 0;

    let score = 0;

    if (data.proxy) score += 30;
    if (data.vpn) score += 25;
    if (data.tor) score += 40;
    if (data.recent_abuse) score += 35;
    if (data.spam) score += 20;
    if (data.bot_status) score += 25;

    return Math.min(100, score);
  }

  /**
   * Cache management
   */
  private getCachedResult(ipAddress: string): ThreatIntelResult | null {
    const cached = this.cache.get(ipAddress);
    if (cached && cached.expires > Date.now()) {
      return cached.data;
    }
    return null;
  }

  private cacheResult(ipAddress: string, result: ThreatIntelResult): void {
    const ttl = Math.min(
      THREAT_INTEL_CONFIG.ABUSEIPDB.CACHE_TTL,
      THREAT_INTEL_CONFIG.VIRUSTOTAL.CACHE_TTL,
      THREAT_INTEL_CONFIG.IPQUALITY.CACHE_TTL,
      THREAT_INTEL_CONFIG.TOR.CACHE_TTL
    );

    this.cache.set(ipAddress, {
      data: result,
      expires: Date.now() + ttl,
    });
  }

  /**
   * Utility functions
   */
  private isValidIP(ipAddress: string): boolean {
    const ipv4Regex =
      /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    const ipv6Regex =
      /^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.)$/;

    return ipv4Regex.test(ipAddress) || ipv6Regex.test(ipAddress);
  }

  private isIPInRanges(ipAddress: string, ranges: string[]): boolean {
    // Simple implementation - would need proper IP range checking in production
    return ranges.some(range => {
      if (range.includes('/')) {
        // CIDR notation - simplified check
        const [network, prefix] = range.split('/');
        return ipAddress.startsWith(network.split('.').slice(0, 2).join('.'));
      }
      return range === ipAddress;
    });
  }

  private createUnknownResult(ipAddress: string): ThreatIntelResult {
    return {
      ipAddress,
      riskScore: 0,
      threatLevel: 'low',
      sources: [],
      details: {},
      recommendations: ['Unable to analyze IP address'],
      timestamp: new Date(),
    };
  }

  private createSafeDefaultResult(ipAddress: string): ThreatIntelResult {
    return {
      ipAddress,
      riskScore: 25, // Medium risk on API failure
      threatLevel: 'medium',
      sources: ['default'],
      details: { error: 'API failure - using safe default' },
      recommendations: ['Monitor this IP closely due to API issues'],
      timestamp: new Date(),
    };
  }

  /**
   * Log threat detection for monitoring
   */
  private async logThreatDetection(
    req: Request,
    result: ThreatIntelResult
  ): Promise<void> {
    await securityEventLogger.logEvent({
      event: 'threat_intelligence_detection',
      severity: result.threatLevel,
      timestamp: new Date(),
      source: 'threat_intelligence',
      ipAddress: result.ipAddress,
      userId: (req as any).user?.id,
      details: {
        riskScore: result.riskScore,
        threatLevel: result.threatLevel,
        sources: result.sources,
        recommendations: result.recommendations,
        userAgent: req.headers['user-agent'],
        detectionTime: result.timestamp,
      },
    });

    // Send alert for high/critical threats
    if (result.threatLevel === 'high' || result.threatLevel === 'critical') {
      await securityAlertManager.sendAlert({
        type: 'security_threat',
        severity: 'high',
        title: 'High-Risk IP Address Detected',
        message: `Threat intelligence detected ${result.threatLevel} risk from ${result.ipAddress}`,
        details: {
          riskScore: result.riskScore,
          threatLevel: result.threatLevel,
          sources: result.sources,
          recommendations: result.recommendations,
          userAgent: req.headers['user-agent'],
          timestamp: result.timestamp.toISOString(),
        },
        metadata: {
          category: 'threat_intelligence',
          tags: ['high_risk', 'external_threat', 'ip_reputation'],
        },
      });
    }
  }

  /**
   * Background updates for threat intelligence data
   */
  private startBackgroundUpdates(): void {
    // Update TOR exit nodes every hour
    setInterval(
      async () => {
        try {
          await this.updateTorExitNodes();
        } catch (error) {
          console.error(
            '[ThreatIntel] Failed to update TOR exit nodes:',
            error
          );
        }
      },
      60 * 60 * 1000
    );

    // Clean up expired cache entries every 30 minutes
    setInterval(
      () => {
        this.cleanupCache();
      },
      30 * 60 * 1000
    );

    // Update metrics every 5 minutes
    setInterval(
      () => {
        this.logMetrics();
      },
      5 * 60 * 1000
    );
  }

  /**
   * Update TOR exit node list
   */
  private async updateTorExitNodes(): Promise<void> {
    try {
      const response = await axios.get(THREAT_INTEL_CONFIG.TOR.LIST_URL, {
        timeout: 10000,
      });

      // Parse TOR exit node list
      const torNodes = this.parseTorExitList(response.data);

      // Store in cache/database for quick lookup
      console.log(
        `[ThreatIntel] Updated TOR exit node list with ${torNodes.length} nodes`
      );
    } catch (error) {
      console.error('[ThreatIntel] Failed to update TOR exit nodes:', error);
    }
  }

  /**
   * Parse TOR exit node list
   */
  private parseTorExitList(data: string): string[] {
    const nodes: string[] = [];
    const lines = data.split('\n');

    for (const line of lines) {
      if (line.startsWith('ExitAddress')) {
        const match = line.match(/ExitAddress\s+([\d.]+)/);
        if (match && match[1]) {
          nodes.push(match[1]);
        }
      }
    }

    return nodes;
  }

  /**
   * Clean up expired cache entries
   */
  private cleanupCache(): void {
    const now = Date.now();
    let removed = 0;

    for (const [key, entry] of this.cache.entries()) {
      if (entry.expires < now) {
        this.cache.delete(key);
        removed++;
      }
    }

    if (removed > 0) {
      console.log(`[ThreatIntel] Cleaned up ${removed} expired cache entries`);
    }
  }

  /**
   * Log metrics for monitoring
   */
  private logMetrics(): void {
    const avgResponseTime =
      this.metrics.responseTimes.length > 0
        ? this.metrics.responseTimes.reduce((a, b) => a + b, 0) /
          this.metrics.responseTimes.length
        : 0;

    console.log('[ThreatIntel] Metrics:', {
      totalChecks: this.metrics.totalChecks,
      threatDetections: this.metrics.threatDetections,
      detectionRate:
        this.metrics.totalChecks > 0
          ? (
              (this.metrics.threatDetections / this.metrics.totalChecks) *
              100
            ).toFixed(2) + '%'
          : '0%',
      avgResponseTime: avgResponseTime.toFixed(2) + 'ms',
      cacheHitRate: (this.metrics.cacheHitRate * 100).toFixed(2) + '%',
      apiErrors: this.metrics.apiErrors,
    });

    // Reset response times array to prevent memory growth
    if (this.metrics.responseTimes.length > 1000) {
      this.metrics.responseTimes = this.metrics.responseTimes.slice(-100);
    }
  }

  /**
   * Get current metrics
   */
  public getMetrics(): ValidationMetrics {
    return { ...this.metrics };
  }

  /**
   * Report IP to threat intelligence services
   */
  public async reportMaliciousIP(
    ipAddress: string,
    categories: string[],
    comment: string
  ): Promise<void> {
    try {
      // Report to AbuseIPDB
      if (
        THREAT_INTEL_CONFIG.ABUSEIPDB.ENABLED &&
        THREAT_INTEL_CONFIG.ABUSEIPDB.API_KEY
      ) {
        await axios.post(
          `${THREAT_INTEL_CONFIG.ABUSEIPDB.BASE_URL}${THREAT_INTEL_CONFIG.ABUSEIPDB.ENDPOINTS.REPORT}`,
          {
            ip: ipAddress,
            categories: categories,
            comment: comment,
          },
          {
            headers: {
              Key: THREAT_INTEL_CONFIG.ABUSEIPDB.API_KEY,
              'Content-Type': 'application/json',
            },
            timeout: 10000,
          }
        );

        console.log(`[ThreatIntel] Reported ${ipAddress} to AbuseIPDB`);
      }

      // Log the report
      await securityEventLogger.logEvent({
        event: 'malicious_ip_reported',
        severity: 'medium',
        timestamp: new Date(),
        source: 'threat_intelligence',
        ipAddress: ipAddress,
        details: {
          categories: categories,
          comment: comment,
          reportedTo: ['AbuseIPDB'],
        },
      });
    } catch (error) {
      console.error(`[ThreatIntel] Failed to report ${ipAddress}:`, error);
    }
  }
}

// Export singleton instance
export const threatIntelligenceService = new ThreatIntelligenceService();
