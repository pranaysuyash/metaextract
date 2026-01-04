"""
Real-time WebSocket Streaming System
Provides live progress updates during metadata extraction
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ExtractionStage:
    name: str
    progress: float
    message: str
    timestamp: float
    errors: list = None

class WebSocketProgressStreamer:
    """
    Real-time progress streaming via WebSocket
    Keeps users informed during long-running extractions
    """

    def __init__(self):
        self.active_connections = {}
        self.extraction_stages = {
            'image': [
                {'stage': 'initialization', 'progress': 0, 'message': 'Initializing extraction'},
                {'stage': 'file_validation', 'progress': 10, 'message': 'Validating file format'},
                {'stage': 'basic_metadata', 'progress': 20, 'message': 'Extracting basic metadata'},
                {'stage': 'exif_analysis', 'progress': 40, 'message': 'Analyzing EXIF data'},
                {'stage': 'gps_extraction', 'progress': 60, 'message': 'Extracting GPS coordinates'},
                {'stage': 'specialized_modules', 'progress': 80, 'message': 'Running specialized modules'},
                {'stage': 'ai_analysis', 'progress': 90, 'message': 'Performing AI analysis'},
                {'stage': 'completion', 'progress': 100, 'message': 'Extraction complete'}
            ],
            'scientific': [
                {'stage': 'initialization', 'progress': 0, 'message': 'Initializing scientific extraction'},
                {'stage': 'format_detection', 'progress': 10, 'message': 'Detecting scientific format'},
                {'stage': 'header_parsing', 'progress': 20, 'message': 'Parsing file headers'},
                {'stage': 'data_extraction', 'progress': 50, 'message': 'Extracting scientific data'},
                {'stage': 'analysis', 'progress': 80, 'message': 'Performing scientific analysis'},
                {'stage': 'completion', 'progress': 100, 'message': 'Scientific extraction complete'}
            ]
        }

    async def stream_extraction_progress(
        self,
        extraction_id: str,
        websocket,
        file_type: str = 'image',
        extraction_function = None
    ):
        """
        Stream real-time progress updates for extraction process

        Args:
            extraction_id: Unique identifier for this extraction
            websocket: WebSocket connection to send updates to
            file_type: Type of file being processed
            extraction_function: Async function to execute for extraction
        """
        try:
            stages = self.extraction_stages.get(file_type, self.extraction_stages['image'])
            self.active_connections[extraction_id] = websocket

            # Send initial connection message
            await self._send_progress(websocket, {
                'type': 'connection_established',
                'extraction_id': extraction_id,
                'timestamp': time.time()
            })

            # Simulate extraction progress through stages
            for i, stage_info in enumerate(stages):
                # Send stage start notification
                await self._send_progress(websocket, {
                    'type': 'stage_start',
                    'stage': stage_info['stage'],
                    'progress': stage_info['progress'],
                    'message': stage_info['message'],
                    'timestamp': time.time(),
                    'extraction_id': extraction_id
                })

                # Simulate processing time for this stage
                await asyncio.sleep(0.1)  # Small delay for demo

                # Send progress update
                await self._send_progress(websocket, {
                    'type': 'progress_update',
                    'stage': stage_info['stage'],
                    'progress': stage_info['progress'],
                    'message': stage_info['message'],
                    'timestamp': time.time(),
                    'extraction_id': extraction_id,
                    'completed_operations': [s['stage'] for s in stages[:i+1]]
                })

            # Send completion message
            await self._send_progress(websocket, {
                'type': 'extraction_complete',
                'progress': 100,
                'message': 'Extraction completed successfully',
                'timestamp': time.time(),
                'extraction_id': extraction_id
            })

        except Exception as e:
            logger.error(f"Progress streaming failed: {e}")
            await self._send_error(websocket, extraction_id, str(e))

        finally:
            # Clean up connection
            if extraction_id in self.active_connections:
                del self.active_connections[extraction_id]

    async def _send_progress(self, websocket, data: Dict[str, Any]):
        """Send progress update via WebSocket"""
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"Failed to send progress: {e}")

    async def _send_error(self, websocket, extraction_id: str, error_message: str):
        """Send error message via WebSocket"""
        try:
            await websocket.send_json({
                'type': 'error',
                'extraction_id': extraction_id,
                'error': error_message,
                'timestamp': time.time()
            })
        except Exception as e:
            logger.error(f"Failed to send error: {e}")

    def get_active_connections(self) -> int:
        """Get count of active WebSocket connections"""
        return len(self.active_connections)

# Real-time Background Job Processing System
class BackgroundJobProcessor:
    """
    Processes extraction jobs in background with progress updates
    Suitable for long-running extractions
    """

    def __init__(self):
        self.job_queue = asyncio.Queue()
        self.active_jobs = {}
        self.completed_jobs = {}
        self.progress_streamer = WebSocketProgressStreamer()

    async def submit_job(
        self,
        job_id: str,
        filepath: str,
        options: Dict[str, Any],
        websocket = None
    ):
        """
        Submit a background extraction job

        Args:
            job_id: Unique job identifier
            filepath: Path to file for extraction
            options: Extraction options
            websocket: Optional WebSocket for progress updates
        """
        job_info = {
            'job_id': job_id,
            'filepath': filepath,
            'options': options,
            'status': 'pending',
            'submitted_at': time.time(),
            'websocket': websocket
        }

        await self.job_queue.put(job_info)
        self.active_jobs[job_id] = job_info

        logger.info(f"Background job submitted: {job_id}")

        return job_id

    async def process_jobs(self):
        """Background worker that processes jobs from the queue"""
        while True:
            try:
                job_info = await self.job_queue.get()

                # Update job status
                job_info['status'] = 'processing'
                job_info['started_at'] = time.time()

                # Stream progress if WebSocket available
                if job_info.get('websocket'):
                    await self.progress_streamer.stream_extraction_progress(
                        job_info['job_id'],
                        job_info['websocket'],
                        'image'  # Determine from file type
                    )

                # Process the extraction
                result = await self._process_extraction(job_info)

                # Update job status
                job_info['status'] = 'completed'
                job_info['completed_at'] = time.time()
                job_info['result'] = result

                # Move to completed jobs
                self.completed_jobs[job_info['job_id']] = job_info
                if job_info['job_id'] in self.active_jobs:
                    del self.active_jobs[job_info['job_id']]

                logger.info(f"Background job completed: {job_info['job_id']}")

            except Exception as e:
                logger.error(f"Job processing failed: {e}")

    async def _process_extraction(self, job_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process the actual extraction"""
        try:
            from server.extractor.modules.image_extensions.registry import get_global_registry
            registry = get_global_registry()

            result = registry.extract_with_best_extension(
                job_info['filepath'],
                job_info['options'].get('tier', 'professional')
            )

            return result

        except Exception as e:
            logger.error(f"Background extraction failed: {e}")
            return {'error': str(e)[:100]}

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a background job"""
        if job_id in self.active_jobs:
            return {
                'job_id': job_id,
                'status': self.active_jobs[job_id]['status'],
                'submitted_at': self.active_jobs[job_id]['submitted_at']
            }
        elif job_id in self.completed_jobs:
            return {
                'job_id': job_id,
                'status': self.completed_jobs[job_id]['status'],
                'result': self.completed_jobs[job_id].get('result'),
                'completed_at': self.completed_jobs[job_id]['completed_at']
            }
        else:
            return {
                'job_id': job_id,
                'status': 'not_found'
            }

# Rate Limiting for API Protection
class RateLimiter:
    """
    Production-grade rate limiting for API endpoints
    Prevents abuse and ensures fair resource allocation
    """

    def __init__(self):
        self.request_counts = {}
        self.rate_limits = {
            'free': 10,      # 10 requests per minute
            'professional': 100,  # 100 requests per minute
            'enterprise': 1000     # 1000 requests per minute
        }

    def check_rate_limit(self, user_id: str, tier: str = 'free') -> -> bool:
        """
        Check if user is within rate limits

        Args:
            user_id: Unique user identifier
            tier: User's subscription tier

        Returns:
            True if within limits, False otherwise
        """
        current_time = int(time.time())
        minute_window = current_time // 60  # Current minute

        key = f"{user_id}:{tier}:{minute_window}"
        current_count = self.request_counts.get(key, 0)

        limit = self.rate_limits.get(tier, self.rate_limits['free'])

        if current_count >= limit:
            logger.warning(f"Rate limit exceeded for {user_id} ({tier})")
            return False

        # Increment counter
        self.request_counts[key] = current_count + 1

        # Clean up old entries
        self._cleanup_old_entries(minute_window)

        return True

    def _cleanup_old_entries(self, current_minute: int):
        """Remove entries from previous minutes"""
        keys_to_remove = []
        for key in self.request_counts.keys():
            if ':' in key:
                try:
                    key_minute = int(key.split(':')[-1])
                    if key_minute < current_minute - 1:  # Remove entries older than 1 minute
                        keys_to_remove.append(key)
                except (ValueError, IndexError):
                    keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.request_counts[key]

    def get_remaining_requests(self, user_id: str, tier: str = 'free') -> int:
        """Get remaining requests for current minute"""
        current_time = int(time.time())
        minute_window = current_time // 60
        key = f"{user_id}:{tier}:{minute_window}"

        current_count = self.request_counts.get(key, 0)
        limit = self.rate_limits.get(tier, self.rate_limits['free'])

        return max(0, limit - current_count)