/**
 * Simple Mutex for in-memory locking
 * Used to prevent race conditions in memory storage operations
 */

export class Mutex {
  private locks: Map<string, Promise<void>> = new Map();

  /**
   * Execute a function with exclusive lock for the given key
   */
  async runExclusive<T>(key: string, fn: () => Promise<T> | T): Promise<T> {
    // Wait for any existing lock on this key
    const existingLock = this.locks.get(key);
    if (existingLock) {
      await existingLock;
    }

    // Create new lock
    let releaseLock: () => void;
    const lockPromise = new Promise<void>(resolve => {
      releaseLock = resolve;
    });

    this.locks.set(key, lockPromise);

    try {
      const result = await fn();
      return result;
    } finally {
      // Release lock
      releaseLock!();
      // Clean up if no new lock was added
      if (this.locks.get(key) === lockPromise) {
        this.locks.delete(key);
      }
    }
  }

  /**
   * Execute a function with exclusive lock (using a constant key for global lock)
   */
  async withLock<T>(fn: () => Promise<T> | T): Promise<T> {
    return this.runExclusive('__global__', fn);
  }

  /**
   * Clear all locks (for testing or shutdown)
   */
  clear(): void {
    this.locks.clear();
  }
}

// Singleton instance for credit operations
export const creditMutex = new Mutex();
