/**
 * Browser Fingerprint Storage Layer
 * 
 * Manages persistent storage of browser fingerprints and related data
 * for advanced abuse detection and ML model training
 */

import { Pool } from 'pg';
import { EnhancedFingerprint, FingerprintAnalysis } from '../monitoring/browser-fingerprint';
import { AnomalyResult } from '../monitoring/ml-anomaly-detection';

// Database configuration
const FINGERPRINT_DB_CONFIG = {
  TABLE_FINGERPRINTS: 'browser_fingerprints',
  TABLE_DEVICES: 'devices',
  TABLE_SESSIONS: 'sessions',
  TABLE_ANOMALIES: 'fingerprint_anomalies',
  TABLE_FEEDBACK: 'protection_feedback',
  
  // Retention policies
  FINGERPRINT_RETENTION_DAYS: 90,
  SESSION_RETENTION_DAYS: 30,
  ANOMALY_RETENTION_DAYS: 180,
  
  // Storage limits
  MAX_FINGERPRINTS_PER_DEVICE: 100,
  MAX_SESSIONS_PER_DEVICE: 1000,
  MAX_ANOMALIES_PER_FINGERPRINT: 50
};

// Stored fingerprint data
interface StoredFingerprint {
  id: string;
  deviceId: string;
  sessionId: string;
  userId?: string;
  fingerprintData: EnhancedFingerprint;
  ipAddress: string;
  userAgent: string;
  timestamp: Date;
  confidence: number;
  anomalies: string[];
  analysis?: FingerprintAnalysis;
}

// Device tracking data
interface DeviceData {
  deviceId: string;
  userId?: string;
  firstSeen: Date;
  lastSeen: Date;
  fingerprintCount: number;
  sessionCount: number;
  riskScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  isBlocked: boolean;
  blockReason?: string;
  blockExpiresAt?: Date;
}

// Session data
interface SessionData {
  sessionId: string;
  deviceId: string;
  userId?: string;
  ipAddress: string;
  userAgent: string;
  startedAt: Date;
  lastActivity: Date;
  requestCount: number;
  uploadCount: number;
  anomalyCount: number;
  isActive: boolean;
}

// Anomaly record
interface AnomalyRecord {
  id: string;
  fingerprintId: string;
  sessionId: string;
  deviceId: string;
  userId?: string;
  anomalyType: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: Date;
  confidence: number;
  metadata?: any;
}

// Protection feedback
interface ProtectionFeedback {
  id: string;
  fingerprintId: string;
  sessionId: string;
  decision: 'allow' | 'challenge' | 'block' | 'monitor';
  wasCorrect: boolean;
  feedback?: string;
  context?: any;
  timestamp: Date;
  userId?: string;
  ipAddress: string;
}

/**
 * Fingerprint Storage Manager
 */
export class FingerprintStorage {
  private pool: Pool;

  constructor(pool: Pool) {
    this.pool = pool;
  }

  /**
   * Store browser fingerprint
   */
  public async storeFingerprint(data: StoredFingerprint): Promise<void> {
    const client = await this.pool.connect();
    
    try {
      await client.query('BEGIN');

      // Check storage limits
      await this.enforceStorageLimits(client, data.deviceId);

      // Store fingerprint
      await client.query(`
        INSERT INTO ${FINGERPRINT_DB_CONFIG.TABLE_FINGERPRINTS} (
          id, device_id, session_id, user_id, fingerprint_data, ip_address,
          user_agent, timestamp, confidence, anomalies
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (id) DO UPDATE SET
          session_id = EXCLUDED.session_id,
          timestamp = EXCLUDED.timestamp,
          confidence = EXCLUDED.confidence,
          anomalies = EXCLUDED.anomalies
      `, [
        data.id,
        data.deviceId,
        data.sessionId,
        data.userId,
        JSON.stringify(data.fingerprintData),
        data.ipAddress,
        data.userAgent,
        data.timestamp,
        data.confidence,
        data.anomalies
      ]);

      // Update device tracking
      await this.updateDeviceTracking(client, {
        deviceId: data.deviceId,
        userId: data.userId,
        firstSeen: data.timestamp,
        lastSeen: data.timestamp,
        fingerprintCount: 1,
        sessionCount: 0,
        riskScore: data.analysis?.riskScore || 0,
        riskLevel: (() => {
          const score = data.analysis?.riskScore ?? 0;
          if (score >= 80) return 'critical';
          if (score >= 60) return 'high';
          if (score >= 40) return 'medium';
          return 'low';
        })(),
        isBlocked: false
      });

      // Store anomalies if any
      if (data.anomalies && data.anomalies.length > 0) {
        for (const anomaly of data.anomalies) {
          await this.storeAnomaly(client, {
            id: `anomaly_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            fingerprintId: data.id,
            sessionId: data.sessionId,
            deviceId: data.deviceId,
            userId: data.userId,
            anomalyType: 'fingerprint',
            description: anomaly,
            severity: this.getAnomalySeverity(anomaly),
            timestamp: data.timestamp,
            confidence: data.confidence
          });
        }
      }

      await client.query('COMMIT');
      
      console.log(`[FingerprintStorage] Stored fingerprint ${data.id} for device ${data.deviceId}`);

    } catch (error) {
      await client.query('ROLLBACK');
      console.error('[FingerprintStorage] Error storing fingerprint:', error);
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Get fingerprint by ID
   */
  public async getFingerprintById(id: string): Promise<StoredFingerprint | null> {
    try {
      const result = await this.pool.query(`
        SELECT * FROM ${FINGERPRINT_DB_CONFIG.TABLE_FINGERPRINTS}
        WHERE id = $1
      `, [id]);

      if (result.rows.length === 0) {
        return null;
      }

      const row = result.rows[0];
      return {
        id: row.id,
        deviceId: row.device_id,
        sessionId: row.session_id,
        userId: row.user_id,
        fingerprintData: JSON.parse(row.fingerprint_data),
        ipAddress: row.ip_address,
        userAgent: row.user_agent,
        timestamp: row.timestamp,
        confidence: row.confidence,
        anomalies: row.anomalies
      };
    } catch (error) {
      console.error('[FingerprintStorage] Error getting fingerprint:', error);
      return null;
    }
  }

  /**
   * Find similar fingerprints
   */
  public async findSimilarFingerprints(
    fingerprint: EnhancedFingerprint,
    threshold: number = 0.85
  ): Promise<Array<{
    fingerprintId: string;
    similarity: number;
    lastSeen: Date;
  }>> {
    try {
      // This is a simplified similarity search
      // In a real implementation, you'd use more sophisticated algorithms
      
      const result = await this.pool.query(`
        SELECT id, fingerprint_data, timestamp, confidence
        FROM ${FINGERPRINT_DB_CONFIG.TABLE_FINGERPRINTS}
        WHERE device_id != $1
        AND timestamp > NOW() - INTERVAL '30 days'
        ORDER BY timestamp DESC
        LIMIT 100
      `, [fingerprint.deviceId]);

      const similar: Array<{
        fingerprintId: string;
        similarity: number;
        lastSeen: Date;
      }> = [];

      for (const row of result.rows) {
        const storedFingerprint = JSON.parse(row.fingerprint_data);
        const similarity = this.calculateFingerprintSimilarity(fingerprint, storedFingerprint);
        
        if (similarity >= threshold) {
          similar.push({
            fingerprintId: row.id,
            similarity,
            lastSeen: row.timestamp
          });
        }
      }

      // Sort by similarity (highest first)
      similar.sort((a, b) => b.similarity - a.similarity);

      return similar.slice(0, 10); // Return top 10

    } catch (error) {
      console.error('[FingerprintStorage] Error finding similar fingerprints:', error);
      return [];
    }
  }

  /**
   * Get device information
   */
  public async getDeviceInfo(deviceId: string): Promise<DeviceData | null> {
    try {
      const result = await this.pool.query(`
        SELECT * FROM ${FINGERPRINT_DB_CONFIG.TABLE_DEVICES}
        WHERE device_id = $1
      `, [deviceId]);

      if (result.rows.length === 0) {
        return null;
      }

      const row = result.rows[0];
      return {
        deviceId: row.device_id,
        userId: row.user_id,
        firstSeen: row.first_seen,
        lastSeen: row.last_seen,
        fingerprintCount: row.fingerprint_count,
        sessionCount: row.session_count,
        riskScore: row.risk_score,
        riskLevel: row.risk_level,
        isBlocked: row.is_blocked,
        blockReason: row.block_reason,
        blockExpiresAt: row.block_expires_at
      };
    } catch (error) {
      console.error('[FingerprintStorage] Error getting device info:', error);
      return null;
    }
  }

  /**
   * Store session data
   */
  public async storeSession(session: SessionData): Promise<void> {
    const client = await this.pool.connect();
    
    try {
      await client.query('BEGIN');

      await client.query(`
        INSERT INTO ${FINGERPRINT_DB_CONFIG.TABLE_SESSIONS} (
          session_id, device_id, user_id, ip_address, user_agent,
          started_at, last_activity, request_count, upload_count,
          anomaly_count, is_active
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        ON CONFLICT (session_id) DO UPDATE SET
          last_activity = EXCLUDED.last_activity,
          request_count = EXCLUDED.request_count,
          upload_count = EXCLUDED.upload_count,
          anomaly_count = EXCLUDED.anomaly_count,
          is_active = EXCLUDED.is_active
      `, [
        session.sessionId,
        session.deviceId,
        session.userId,
        session.ipAddress,
        session.userAgent,
        session.startedAt,
        session.lastActivity,
        session.requestCount,
        session.uploadCount,
        session.anomalyCount,
        session.isActive
      ]);

      // Update device session count
      await client.query(`
        UPDATE ${FINGERPRINT_DB_CONFIG.TABLE_DEVICES}
        SET session_count = session_count + 1,
            last_seen = $1
        WHERE device_id = $2
      `, [session.lastActivity, session.deviceId]);

      await client.query('COMMIT');
      
      console.log(`[FingerprintStorage] Stored session ${session.sessionId}`);

    } catch (error) {
      await client.query('ROLLBACK');
      console.error('[FingerprintStorage] Error storing session:', error);
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Store anomaly record
   */
  public async storeAnomaly(
    client: any,
    anomaly: AnomalyRecord
  ): Promise<void> {
    try {
      await client.query(`
        INSERT INTO ${FINGERPRINT_DB_CONFIG.TABLE_ANOMALIES} (
          id, fingerprint_id, session_id, device_id, user_id,
          anomaly_type, description, severity, timestamp,
          confidence, metadata
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
      `, [
        anomaly.id,
        anomaly.fingerprintId,
        anomaly.sessionId,
        anomaly.deviceId,
        anomaly.userId,
        anomaly.anomalyType,
        anomaly.description,
        anomaly.severity,
        anomaly.timestamp,
        anomaly.confidence,
        JSON.stringify(anomaly.metadata || {})
      ]);

      console.log(`[FingerprintStorage] Stored anomaly ${anomaly.id}`);

    } catch (error) {
      console.error('[FingerprintStorage] Error storing anomaly:', error);
      throw error;
    }
  }

  /**
   * Store protection feedback
   */
  public async storeFeedback(feedback: ProtectionFeedback): Promise<void> {
    try {
      await this.pool.query(`
        INSERT INTO ${FINGERPRINT_DB_CONFIG.TABLE_FEEDBACK} (
          id, fingerprint_id, session_id, decision, was_correct,
          feedback, context, timestamp, user_id, ip_address
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      `, [
        feedback.id,
        feedback.fingerprintId,
        feedback.sessionId,
        feedback.decision,
        feedback.wasCorrect,
        feedback.feedback,
        JSON.stringify(feedback.context || {}),
        feedback.timestamp,
        feedback.userId,
        feedback.ipAddress
      ]);

      console.log(`[FingerprintStorage] Stored feedback ${feedback.id}`);

    } catch (error) {
      console.error('[FingerprintStorage] Error storing feedback:', error);
      throw error;
    }
  }

  /**
   * Get device sessions
   */
  public async getDeviceSessions(
    deviceId: string,
    limit: number = 10
  ): Promise<SessionData[]> {
    try {
      const result = await this.pool.query(`
        SELECT * FROM ${FINGERPRINT_DB_CONFIG.TABLE_SESSIONS}
        WHERE device_id = $1
        ORDER BY last_activity DESC
        LIMIT $2
      `, [deviceId, limit]);

      return result.rows.map(row => ({
        sessionId: row.session_id,
        deviceId: row.device_id,
        userId: row.user_id,
        ipAddress: row.ip_address,
        userAgent: row.user_agent,
        startedAt: row.started_at,
        lastActivity: row.last_activity,
        requestCount: row.request_count,
        uploadCount: row.upload_count,
        anomalyCount: row.anomaly_count,
        isActive: row.is_active
      }));
    } catch (error) {
      console.error('[FingerprintStorage] Error getting device sessions:', error);
      return [];
    }
  }

  /**
   * Get recent anomalies for device
   */
  public async getDeviceAnomalies(
    deviceId: string,
    limit: number = 20
  ): Promise<AnomalyRecord[]> {
    try {
      const result = await this.pool.query(`
        SELECT * FROM ${FINGERPRINT_DB_CONFIG.TABLE_ANOMALIES}
        WHERE device_id = $1
        ORDER BY timestamp DESC
        LIMIT $2
      `, [deviceId, limit]);

      return result.rows.map(row => ({
        id: row.id,
        fingerprintId: row.fingerprint_id,
        sessionId: row.session_id,
        deviceId: row.device_id,
        userId: row.user_id,
        anomalyType: row.anomaly_type,
        description: row.description,
        severity: row.severity,
        timestamp: row.timestamp,
        confidence: row.confidence,
        metadata: JSON.parse(row.metadata || '{}')
      }));
    } catch (error) {
      console.error('[FingerprintStorage] Error getting device anomalies:', error);
      return [];
    }
  }

  /**
   * Get statistics for ML model training
   */
  public async getTrainingData(
    limit: number = 1000
  ): Promise<Array<{
    features: any;
    label: 'normal' | 'anomalous';
    confidence: number;
  }>> {
    try {
      // Get recent fingerprints with feedback
      const result = await this.pool.query(`
        SELECT 
          f.fingerprint_data,
          f.confidence,
          fb.decision,
          fb.was_correct,
          COUNT(a.id) as anomaly_count
        FROM ${FINGERPRINT_DB_CONFIG.TABLE_FINGERPRINTS} f
        LEFT JOIN ${FINGERPRINT_DB_CONFIG.TABLE_FEEDBACK} fb ON f.id = fb.fingerprint_id
        LEFT JOIN ${FINGERPRINT_DB_CONFIG.TABLE_ANOMALIES} a ON f.id = a.fingerprint_id
        WHERE f.timestamp > NOW() - INTERVAL '30 days'
        GROUP BY f.id, f.fingerprint_data, f.confidence, fb.decision, fb.was_correct
        ORDER BY f.timestamp DESC
        LIMIT $1
      `, [limit]);

      return result.rows.map(row => {
        const fingerprintData = JSON.parse(row.fingerprint_data);
        
        // Determine label based on feedback and anomalies
        let label: 'normal' | 'anomalous' = 'normal';
        let confidence = row.confidence;

        if (row.was_correct === false) {
          // Feedback indicates incorrect decision
          label = row.decision === 'block' ? 'normal' : 'anomalous';
        } else if (row.anomaly_count > 0 || row.decision === 'block') {
          label = 'anomalous';
        }

        return {
          features: this.extractFeatures(fingerprintData),
          label,
          confidence
        };
      });
    } catch (error) {
      console.error('[FingerprintStorage] Error getting training data:', error);
      return [];
    }
  }

  /**
   * Clean up old data
   */
  public async cleanupOldData(): Promise<{
    fingerprintsRemoved: number;
    sessionsRemoved: number;
    anomaliesRemoved: number;
    feedbackRemoved: number;
  }> {
    const client = await this.pool.connect();
    
    try {
      await client.query('BEGIN');

      // Clean up old fingerprints
      const fingerprintsResult = await client.query(`
        DELETE FROM ${FINGERPRINT_DB_CONFIG.TABLE_FINGERPRINTS}
        WHERE timestamp < NOW() - INTERVAL '${FINGERPRINT_DB_CONFIG.FINGERPRINT_RETENTION_DAYS} days'
        RETURNING id
      `);

      // Clean up old sessions
      const sessionsResult = await client.query(`
        DELETE FROM ${FINGERPRINT_DB_CONFIG.TABLE_SESSIONS}
        WHERE last_activity < NOW() - INTERVAL '${FINGERPRINT_DB_CONFIG.SESSION_RETENTION_DAYS} days'
        RETURNING session_id
      `);

      // Clean up old anomalies
      const anomaliesResult = await client.query(`
        DELETE FROM ${FINGERPRINT_DB_CONFIG.TABLE_ANOMALIES}
        WHERE timestamp < NOW() - INTERVAL '${FINGERPRINT_DB_CONFIG.ANOMALY_RETENTION_DAYS} days'
        RETURNING id
      `);

      // Clean up old feedback
      const feedbackResult = await client.query(`
        DELETE FROM ${FINGERPRINT_DB_CONFIG.TABLE_FEEDBACK}
        WHERE timestamp < NOW() - INTERVAL '${FINGERPRINT_DB_CONFIG.ANOMALY_RETENTION_DAYS} days'
        RETURNING id
      `);

      await client.query('COMMIT');

      const stats = {
        fingerprintsRemoved: fingerprintsResult.rows.length,
        sessionsRemoved: sessionsResult.rows.length,
        anomaliesRemoved: anomaliesResult.rows.length,
        feedbackRemoved: feedbackResult.rows.length
      };

      console.log('[FingerprintStorage] Cleanup completed:', stats);
      return stats;

    } catch (error) {
      await client.query('ROLLBACK');
      console.error('[FingerprintStorage] Error during cleanup:', error);
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Helper methods
   */

  private async enforceStorageLimits(client: any, deviceId: string): Promise<void> {
    // Enforce fingerprint limit
    const fingerprintCount = await client.query(`
      SELECT COUNT(*) as count
      FROM ${FINGERPRINT_DB_CONFIG.TABLE_FINGERPRINTS}
      WHERE device_id = $1
    `, [deviceId]);

    if (parseInt(fingerprintCount.rows[0].count) >= FINGERPRINT_DB_CONFIG.MAX_FINGERPRINTS_PER_DEVICE) {
      // Remove oldest fingerprints
      await client.query(`
        DELETE FROM ${FINGERPRINT_DB_CONFIG.TABLE_FINGERPRINTS}
        WHERE device_id = $1
        AND id IN (
          SELECT id FROM ${FINGERPRINT_DB_CONFIG.TABLE_FINGERPRINTS}
          WHERE device_id = $1
          ORDER BY timestamp ASC
          LIMIT 10
        )
      `, [deviceId]);
    }
  }

  private async updateDeviceTracking(client: any, device: DeviceData): Promise<void> {
    await client.query(`
      INSERT INTO ${FINGERPRINT_DB_CONFIG.TABLE_DEVICES} (
        device_id, user_id, first_seen, last_seen, fingerprint_count,
        session_count, risk_score, risk_level, is_blocked, block_reason, block_expires_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
      ON CONFLICT (device_id) DO UPDATE SET
        user_id = COALESCE(EXCLUDED.user_id, ${FINGERPRINT_DB_CONFIG.TABLE_DEVICES}.user_id),
        last_seen = EXCLUDED.last_seen,
        fingerprint_count = ${FINGERPRINT_DB_CONFIG.TABLE_DEVICES}.fingerprint_count + EXCLUDED.fingerprint_count,
        session_count = ${FINGERPRINT_DB_CONFIG.TABLE_DEVICES}.session_count + EXCLUDED.session_count,
        risk_score = EXCLUDED.risk_score,
        risk_level = EXCLUDED.risk_level,
        is_blocked = EXCLUDED.is_blocked,
        block_reason = EXCLUDED.block_reason,
        block_expires_at = EXCLUDED.block_expires_at
    `, [
      device.deviceId,
      device.userId,
      device.firstSeen,
      device.lastSeen,
      device.fingerprintCount,
      device.sessionCount,
      device.riskScore,
      device.riskLevel,
      device.isBlocked,
      device.blockReason,
      device.blockExpiresAt
    ]);
  }

  private calculateFingerprintSimilarity(fp1: EnhancedFingerprint, fp2: EnhancedFingerprint): number {
    let similarity = 0;
    let factors = 0;

    // Compare basic properties
    const basicProps = ['userAgent', 'platform', 'language', 'timezone'];
    basicProps.forEach(prop => {
      factors++;
      if ((fp1 as any)[prop] === (fp2 as any)[prop]) similarity++;
    });

    // Compare canvas hashes
    if (fp1.canvas && fp2.canvas) {
      factors++;
      if (fp1.canvas === fp2.canvas) similarity++;
    }

    // Compare WebGL hashes
    if (fp1.webgl && fp2.webgl) {
      factors++;
      if (fp1.webgl === fp2.webgl) similarity++;
    }

    // Compare screen resolution
    if (fp1.screen && fp2.screen) {
      factors++;
      if (fp1.screen === fp2.screen) similarity++;
    }

    return factors > 0 ? similarity / factors : 0;
  }

  private getAnomalySeverity(anomaly: string): 'low' | 'medium' | 'high' | 'critical' {
    if (anomaly.includes('Headless browser')) return 'high';
    if (anomaly.includes('Minimal browser fingerprint')) return 'medium';
    if (anomaly.includes('Mobile UA but no touch')) return 'low';
    if (anomaly.includes('Do Not Track')) return 'low';
    return 'medium';
  }

  private extractFeatures(fingerprintData: any): any {
    // Extract relevant features for ML training
    return {
      canvasHash: fingerprintData.canvas?.hash,
      webglHash: fingerprintData.webgl?.webglHash,
      audioHash: fingerprintData.audio?.oscillator,
      fontCount: fingerprintData.fonts?.count,
      pluginCount: fingerprintData.plugins?.count,
      screenResolution: `${fingerprintData.screen?.width}x${fingerprintData.screen?.height}`,
      timezone: fingerprintData.timezone?.timezone,
      language: fingerprintData.language,
      platform: fingerprintData.platform,
      userAgent: fingerprintData.userAgent,
      touchSupport: fingerprintData.touch?.touchEvent,
      deviceMemory: fingerprintData.hardware?.deviceMemory,
      hardwareConcurrency: fingerprintData.hardware?.hardwareConcurrency
    };
  }
}

// Export singleton instance
export let fingerprintStorage: FingerprintStorage;

export function initializeFingerprintStorage(pool: Pool): void {
  fingerprintStorage = new FingerprintStorage(pool);
}