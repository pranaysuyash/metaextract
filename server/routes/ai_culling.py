"""
AI Photo Culling API Endpoint
============================

REST API endpoints for AI-powered photo culling:
- Batch analysis for culling recommendations
- Individual photo scoring
- User preference management
- Performance optimization for large batches

Author: MetaExtract Team
Version: 1.0.0
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
import json

from ...modules.ai_culling_engine import AICullingEngine, analyze_photos_for_culling
from ...modules.focus_exposure_analyzer import FocusAnalyzer, ExposureAnalyzer
from ..dependencies import get_current_user, get_db
from ..models import User

logger = logging.getLogger(__name__)

# Pydantic models for request/response
class PhotoMetadata(BaseModel):
    """Photo metadata model for culling analysis."""
    filename: str = Field(..., description="Photo filename")
    filepath: str = Field(..., description="Full path to photo file")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    exif: Optional[Dict[str, Any]] = Field(None, description="EXIF metadata")
    image_quality_analysis: Optional[Dict[str, Any]] = Field(None, description="Quality analysis")
    gps: Optional[Dict[str, Any]] = Field(None, description="GPS metadata")
    icc_profile: Optional[Dict[str, Any]] = Field(None, description="ICC profile info")
    file_size: Optional[int] = Field(None, description="File size in bytes")

class CullingRequest(BaseModel):
    """Request model for batch culling analysis."""
    photos: List[PhotoMetadata] = Field(..., description="List of photos to analyze")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User culling preferences")
    quick_mode: bool = Field(False, description="Use quick analysis for large batches")
    batch_id: Optional[str] = Field(None, description="Batch ID for tracking")

class CullingPreferences(BaseModel):
    """User preferences model for culling."""
    focus_weight: float = Field(0.3, ge=0, le=1, description="Weight for focus scoring")
    exposure_weight: float = Field(0.25, ge=0, le=1, description="Weight for exposure scoring")
    composition_weight: float = Field(0.2, ge=0, le=1, description="Weight for composition scoring")
    technical_weight: float = Field(0.15, ge=0, le=1, description="Weight for technical quality scoring")
    aesthetic_weight: float = Field(0.1, ge=0, le=1, description="Weight for aesthetic scoring")
    min_overall_score: float = Field(60.0, ge=0, le=100, description="Minimum score to keep")
    auto_cull_below_score: bool = Field(False, description="Auto-cull photos below threshold")
    prefer_face_detection: bool = Field(True, description="Prefer photos with detected faces")
    prefer_eye_focus: bool = Field(True, description="Prefer photos with eye AF")

class SinglePhotoScore(BaseModel):
    """Single photo scoring result."""
    filename: str
    overall_score: float
    focus_score: float
    exposure_score: float
    composition_score: float
    technical_score: float
    aesthetic_score: float
    confidence: float
    recommendations: List[str]

class CullingResponse(BaseModel):
    """Response model for culling analysis."""
    success: bool
    groups: List[Dict[str, Any]]
    total_photos: int
    recommendations: List[Dict[str, Any]]
    processing_time: float
    scoring_weights: Dict[str, float]
    batch_id: Optional[str] = None
    error: Optional[str] = None

# Create router
router = APIRouter(prefix="/ai-culling", tags=["AI Culling"])

# In-memory storage for active batches (in production, use Redis)
active_batches: Dict[str, Dict[str, Any]] = {}

@router.post("/analyze", response_model=CullingResponse)
async def analyze_photos_for_culling_endpoint(
    request: CullingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Analyze photos for AI-powered culling recommendations.
    
    This endpoint processes a batch of photos and returns:
    - Grouped similar photos
    - Quality scores for each photo
    - Recommendations for keep/cull/review
    - Best shot selection within each group
    """
    
    # Validate request
    if not request.photos:
        raise HTTPException(status_code=400, detail="No photos provided for analysis")
    
    if len(request.photos) > 1000:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 1000 photos per batch. Use batch processing for larger sets."
        )
    
    # Generate batch ID if not provided
    batch_id = request.batch_id or f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(request.photos)}"
    
    try:
        # Convert request to photo metadata dicts
        photo_dicts = [photo.dict() for photo in request.photos]
        
        # Add user preferences
        user_prefs = request.user_preferences or {}
        if not user_prefs:
            # Try to get saved preferences from database
            user_prefs = await get_user_culling_preferences(current_user.id, db)
        
        # Process analysis
        if request.quick_mode and len(request.photos) > 100:
            # For large batches, use background processing
            result = await process_culling_background(batch_id, photo_dicts, user_prefs, background_tasks)
        else:
            # Direct processing for smaller batches
            result = analyze_photos_for_culling(photo_dicts, user_prefs)
        
        # Store batch results for potential retrieval
        active_batches[batch_id] = {
            'result': result,
            'timestamp': datetime.now(),
            'user_id': current_user.id,
            'photo_count': len(request.photos)
        }
        
        # Log analysis for analytics
        await log_culling_analysis(current_user.id, batch_id, len(request.photos), result, db)
        
        return CullingResponse(
            success=result.get('success', False),
            groups=result.get('groups', []),
            total_photos=result.get('total_photos', 0),
            recommendations=result.get('recommendations', []),
            processing_time=result.get('processing_time', 0),
            scoring_weights=result.get('scoring_weights', {}),
            batch_id=batch_id,
            error=result.get('error')
        )
        
    except Exception as e:
        logger.error(f"Error in culling analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/score-single", response_model=SinglePhotoScore)
async def score_single_photo(
    photo: PhotoMetadata,
    current_user: User = Depends(get_current_user)
):
    """
    Score a single photo for culling purposes.
    
    Returns detailed scoring across all dimensions and recommendations.
    """
    try:
        from ...modules.ai_culling_engine import score_single_photo
        
        # Get user preferences
        user_prefs = await get_user_culling_preferences(current_user.id, db=None)
        
        # Score the photo
        culling_score = score_single_photo(photo.dict(), user_prefs)
        
        # Get additional recommendations
        from ...modules.focus_exposure_analyzer import (
            analyze_focus_quality, 
            analyze_exposure_quality
        )
        
        focus_analysis = analyze_focus_quality(photo.dict())
        exposure_analysis = analyze_exposure_quality(photo.dict())
        
        # Combine recommendations
        all_recommendations = []
        all_recommendations.extend(focus_analysis.focus_recommendations)
        all_recommendations.extend(exposure_analysis.exposure_recommendations)
        
        return SinglePhotoScore(
            filename=photo.filename,
            overall_score=culling_score.overall_score,
            focus_score=culling_score.focus_score,
            exposure_score=culling_score.exposure_score,
            composition_score=culling_score.composition_score,
            technical_score=culling_score.technical_score,
            aesthetic_score=culling_score.aesthetic_score,
            confidence=culling_score.confidence,
            recommendations=list(set(all_recommendations))  # Remove duplicates
        )
        
    except Exception as e:
        logger.error(f"Error scoring photo {photo.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Photo scoring failed: {str(e)}"
        )

@router.get("/batch/{batch_id}", response_model=CullingResponse)
async def get_batch_results(
    batch_id: str,
    current_user: User = Depends(get_current_user)
):
    """Retrieve results for a previous batch analysis."""
    
    batch_data = active_batches.get(batch_id)
    
    if not batch_data:
        raise HTTPException(
            status_code=404,
            detail="Batch not found or expired"
        )
    
    if batch_data['user_id'] != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this batch"
        )
    
    result = batch_data['result']
    
    return CullingResponse(
        success=result.get('success', False),
        groups=result.get('groups', []),
        total_photos=result.get('total_photos', 0),
        recommendations=result.get('recommendations', []),
        processing_time=result.get('processing_time', 0),
        scoring_weights=result.get('scoring_weights', {}),
        batch_id=batch_id,
        error=result.get('error')
    )

@router.get("/preferences", response_model=CullingPreferences)
async def get_culling_preferences(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's culling preferences."""
    try:
        preferences = await get_user_culling_preferences(current_user.id, db)
        return CullingPreferences(**preferences)
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        return CullingPreferences()

@router.post("/preferences", response_model=CullingPreferences)
async def update_culling_preferences(
    preferences: CullingPreferences,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update user's culling preferences."""
    try:
        await save_user_culling_preferences(current_user.id, preferences.dict(), db)
        return preferences
    except Exception as e:
        logger.error(f"Error saving preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to save preferences"
        )

@router.delete("/batch/{batch_id}")
async def delete_batch_results(
    batch_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete batch analysis results."""
    
    batch_data = active_batches.get(batch_id)
    
    if not batch_data:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )
    
    if batch_data['user_id'] != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this batch"
        )
    
    del active_batches[batch_id]
    
    return {"message": "Batch results deleted successfully"}

@router.get("/analytics/usage")
async def get_culling_analytics(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get analytics about user's culling usage."""
    try:
        analytics = await get_user_culling_analytics(current_user.id, db)
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return {
            "total_photos_analyzed": 0,
            "total_batches_processed": 0,
            "average_batch_size": 0,
            "success_rate": 0,
            "processing_time_total": 0
        }

# Helper functions
async def get_user_culling_preferences(user_id: int, db) -> Dict[str, Any]:
    """Get user's culling preferences from database."""
    try:
        if db:
            # Query database for user preferences
            query = "SELECT preferences FROM user_culling_prefs WHERE user_id = %s"
            cursor = db.cursor()
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if result:
                return json.loads(result[0])
        
        # Default preferences
        return {
            "focus_weight": 0.3,
            "exposure_weight": 0.25,
            "composition_weight": 0.2,
            "technical_weight": 0.15,
            "aesthetic_weight": 0.1,
            "min_overall_score": 60.0,
            "auto_cull_below_score": False,
            "prefer_face_detection": True,
            "prefer_eye_focus": True
        }
    except Exception as e:
        logger.error(f"Error getting user preferences: {str(e)}")
        return {}

async def save_user_culling_preferences(user_id: int, preferences: Dict[str, Any], db):
    """Save user's culling preferences to database."""
    try:
        if db:
            query = """
                INSERT INTO user_culling_prefs (user_id, preferences, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (user_id) 
                DO UPDATE SET preferences = %s, updated_at = NOW()
            """
            cursor = db.cursor()
            cursor.execute(query, (user_id, json.dumps(preferences), json.dumps(preferences)))
            db.commit()
    except Exception as e:
        logger.error(f"Error saving user preferences: {str(e)}")
        raise

async def process_culling_background(
    batch_id: str, 
    photo_dicts: List[Dict[str, Any]], 
    user_prefs: Dict[str, Any],
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Process culling analysis in background for large batches."""
    
    # Store initial status
    active_batches[batch_id] = {
        'result': {'status': 'processing'},
        'timestamp': datetime.now(),
        'user_id': current_user.id,
        'photo_count': len(photo_dicts)
    }
    
    # Schedule background processing
    background_tasks.add_task(
        run_culling_analysis_background,
        batch_id,
        photo_dicts,
        user_prefs
    )
    
    return {
        'success': True,
        'status': 'processing',
        'message': f'Processing {len(photo_dicts)} photos in background',
        'processing_time': 0
    }

async def run_culling_analysis_background(
    batch_id: str,
    photo_dicts: List[Dict[str, Any]],
    user_prefs: Dict[str, Any]
):
    """Background task for culling analysis."""
    try:
        result = analyze_photos_for_culling(photo_dicts, user_prefs)
        
        # Update batch results
        if batch_id in active_batches:
            active_batches[batch_id]['result'] = result
        
    except Exception as e:
        logger.error(f"Background culling analysis failed: {str(e)}")
        
        # Store error result
        if batch_id in active_batches:
            active_batches[batch_id]['result'] = {
                'success': False,
                'error': str(e),
                'processing_time': 0
            }

async def log_culling_analysis(user_id: int, batch_id: str, photo_count: int, result: Dict[str, Any], db):
    """Log culling analysis for analytics."""
    try:
        if db:
            query = """
                INSERT INTO culling_analytics 
                (user_id, batch_id, photo_count, processing_time, success, recommendations_count, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            cursor = db.cursor()
            cursor.execute(
                query,
                (
                    user_id,
                    batch_id,
                    photo_count,
                    result.get('processing_time', 0),
                    result.get('success', False),
                    len(result.get('recommendations', []))
                )
            )
            db.commit()
    except Exception as e:
        logger.error(f"Error logging culling analytics: {str(e)}")

async def get_user_culling_analytics(user_id: int, db) -> Dict[str, Any]:
    """Get culling analytics for user."""
    try:
        if db:
            query = """
                SELECT 
                    COUNT(*) as total_batches,
                    SUM(photo_count) as total_photos,
                    AVG(processing_time) as avg_processing_time,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END)::float / COUNT(*) as success_rate
                FROM culling_analytics 
                WHERE user_id = %s
            """
            cursor = db.cursor()
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    "total_batches_processed": result[0] or 0,
                    "total_photos_analyzed": result[1] or 0,
                    "average_processing_time": float(result[2]) or 0,
                    "success_rate": float(result[3]) or 0,
                    "average_batch_size": (result[1] / result[0]) if result[0] > 0 else 0
                }
        
        return {
            "total_batches_processed": 0,
            "total_photos_analyzed": 0,
            "average_processing_time": 0,
            "success_rate": 0,
            "average_batch_size": 0
        }
    except Exception as e:
        logger.error(f"Error getting user analytics: {str(e)}")
        return {}

# Cleanup old batches (could be run as a periodic task)
async def cleanup_old_batches():
    """Remove old batch results from memory."""
    from datetime import timedelta
    
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    expired_batches = [
        batch_id for batch_id, batch_data in active_batches.items()
        if batch_data['timestamp'] < cutoff_time
    ]
    
    for batch_id in expired_batches:
        del active_batches[batch_id]
    
    logger.info(f"Cleaned up {len(expired_batches)} expired culling batches")