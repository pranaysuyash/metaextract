/**
 * Async Worker Queue Adapter
 * 
 * Abstraction for offloading heavy tasks.
 * MVP: In-memory async execution
 * Production: Redis (BullMQ) or Cloud Tasks
 */

import { v4 as uuidv4 } from 'uuid';

export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface JobOptions {
  timeoutMs?: number;    // Execution timeout (Resource Limit)
  retries?: number;      // Max retries (Retry Strategy)
  backoffMs?: number;    // Delay between retries
}

export interface Job<T = any> {
  id: string;
  type: string;
  data: T;
  status: JobStatus;
  result?: any;
  error?: string;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  attempts: number;      // Current attempt count
  maxAttempts: number;   // Max retries allowed
}

// In-memory job store for MVP
const jobs = new Map<string, Job>();

// Default options
const DEFAULT_OPTIONS: JobOptions = {
  timeoutMs: 60000, // 1 minute default timeout
  retries: 3,       // 3 retries
  backoffMs: 1000,
};

/**
 * Add a job to the queue.
 */
export async function addJob<T>(type: string, data: T, options?: JobOptions): Promise<Job<T>> {
  const id = uuidv4();
  const opts = { ...DEFAULT_OPTIONS, ...options };
  
  const job: Job<T> = {
    id,
    type,
    data,
    status: 'pending',
    createdAt: new Date(),
    attempts: 0,
    maxAttempts: opts.retries || 0,
  };
  
  jobs.set(id, job);

  // In MVP, trigger processing immediately (async)
  processNext(id, opts);

  return job;
}

/**
 * Get job status/result.
 */
export async function getJob(id: string): Promise<Job | undefined> {
  return jobs.get(id);
}

// Mock processor registry
const processors = new Map<string, (job: Job) => Promise<any>>();

export function registerProcessor(type: string, handler: (job: Job) => Promise<any>) {
  processors.set(type, handler);
}

async function processNext(jobId: string, options: JobOptions) {
  const job = jobs.get(jobId);
  if (!job) return;

  const processor = processors.get(job.type);
  if (!processor) {
    job.status = 'failed';
    job.error = `No processor for type ${job.type}`;
    return;
  }

  // Retry Logic
  while (job.attempts <= job.maxAttempts) {
    job.attempts++;
    job.status = 'processing';
    job.startedAt = new Date(); // Update start time for each attempt

    try {
      // Resource Limit: Timeout enforcement
      const result = await Promise.race([
        processor(job),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Job timeout exceeded')), options.timeoutMs)
        )
      ]);

      // Success
      job.status = 'completed';
      job.result = result;
      job.completedAt = new Date();
      return; // Exit loop

    } catch (err: any) {
      console.warn(`Job ${jobId} failed attempt ${job.attempts}/${job.maxAttempts + 1}: ${err.message}`);
      job.error = err.message || 'Unknown error';
      
      // If retries remaining, wait before next attempt
      if (job.attempts <= job.maxAttempts) {
        job.status = 'pending'; // Reset status for visibility
        await new Promise(resolve => setTimeout(resolve, options.backoffMs));
      } else {
        // Final failure
        job.status = 'failed';
        job.completedAt = new Date();
      }
    }
  }
}

/**
 * Autoscale Metrics
 * Returns current metrics for Horizontal Pod Autoscaler (HPA) or CloudWatch.
 */
export function getQueueMetrics() {
  const pending = Array.from(jobs.values()).filter(j => j.status === 'pending').length;
  const processing = Array.from(jobs.values()).filter(j => j.status === 'processing').length;
  
  // Calculate average processing time for completed jobs (last 100)
  const completed = Array.from(jobs.values())
    .filter(j => j.status === 'completed' && j.startedAt && j.completedAt)
    .sort((a, b) => b.completedAt!.getTime() - a.completedAt!.getTime()) // Newest first
    .slice(0, 100);

  const avgProcessingTimeMs = completed.reduce((acc, job) => {
    return acc + (job.completedAt!.getTime() - job.startedAt!.getTime());
  }, 0) / (completed.length || 1);

  return {
    queueDepth: pending,
    activeWorkers: processing,
    avgProcessingTimeMs,
    scalingRecommendation: pending > 50 ? 'scale_up' : pending < 5 ? 'scale_down' : 'hold'
  };
}
