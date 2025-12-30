"""
Video Keyframe and Scene Analysis
Extract keyframes and detect scene changes in videos
"""

from typing import Dict, Any, Optional, List, Tuple
import os


try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False


def extract_keyframes(
    filepath: str,
    max_keyframes: int = 10,
    method: str = "uniform"
) -> Optional[Dict[str, Any]]:
    """
    Extract keyframes from a video.
    
    Args:
        filepath: Path to video file
        max_keyframes: Maximum number of keyframes to extract
        method: 'uniform', 'content', or 'scene'
    
    Returns:
        Dictionary with keyframe data
    """
    if not CV2_AVAILABLE:
        raise ImportError("opencv-python is required for keyframe extraction")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Video file not found: {filepath}")
    
    try:
        cap = cv2.VideoCapture(filepath)
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        keyframes = []
        frame_indices = []
        
        if method == "uniform":
            step = max(1, total_frames // max_keyframes)
            for i in range(0, total_frames, step):
                if len(keyframes) >= max_keyframes:
                    break
                frame_indices.append(i)
        
        elif method == "content":
            prev_frame = None
            threshold = 30.0
            
            for i in range(0, total_frames, max(1, total_frames // (max_keyframes * 3))):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                if prev_frame is not None:
                    diff = cv2.absdiff(prev_frame, cv2)
                    score = np.mean(diff)
                    
                    if score > threshold:
                        frame_indices.append(i)
                        keyframes.append({
                            "frame_index": i,
                            "timestamp": i / fps if fps > 0 else 0,
                            "change_score": round(score, 2)
                        })
                        prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if len(keyframes) >= max_keyframes:
                    break
        
        elif method == "scene":
            prev_hist = None
            threshold = 0.7
            
            for i in range(0, total_frames, max(1, total_frames // (max_keyframes * 2))):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
                
                if prev_hist is not None:
                    similarity = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                    
                    if similarity < threshold:
                        keyframes.append({
                            "frame_index": i,
                            "timestamp": i / fps if fps > 0 else 0,
                            "similarity_score": round(similarity, 4)
                        })
                        prev_hist = hist
                
                if len(keyframes) >= max_keyframes:
                    break
        
        cap.release()
        
        result = {
            "video_path": filepath,
            "total_frames": total_frames,
            "fps": round(fps, 2),
            "duration_seconds": round(duration, 2),
            "keyframes_extracted": len(keyframes),
            "method": method,
            "keyframes": keyframes,
            "frame_indices": frame_indices
        }
        
        return result
        
    except Exception as e:
        raise RuntimeError(f"Failed to extract keyframes: {str(e)}")


def detect_scene_changes(
    filepath: str,
    threshold: float = 30.0,
    min_scene_length: float = 1.0
) -> Optional[Dict[str, Any]]:
    """
    Detect scene changes in a video.
    
    Args:
        filepath: Path to video file
        threshold: Change detection threshold (0-100)
        min_scene_length: Minimum scene length in seconds
    
    Returns:
        Dictionary with scene detection data
    """
    if not CV2_AVAILABLE:
        raise ImportError("opencv-python is required for scene detection")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Video file not found: {filepath}")
    
    try:
        cap = cv2.VideoCapture(filepath)
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        scenes = []
        prev_gray = None
        scene_start = 0
        scene_changes = []
        
        frame_interval = max(1, int(fps / 2))
        
        for i in range(0, total_frames, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)
                change_score = np.mean(diff)
                
                if change_score > threshold:
                    timestamp = i / fps if fps > 0 else 0
                    scene_changes.append({
                        "frame_index": i,
                        "timestamp": round(timestamp, 2),
                        "change_score": round(change_score, 2)
                    })
            
            prev_gray = gray
        
        min_frames = int(min_scene_length * fps)
        
        for j, change in enumerate(scene_changes):
            if j == 0:
                start_frame = 0
            else:
                start_frame = scene_changes[j - 1]["frame_index"]
            
            end_frame = change["frame_index"] + min_frames
            
            if end_frame > total_frames:
                end_frame = total_frames
            
            scenes.append({
                "scene_number": j + 1,
                "start_frame": start_frame,
                "end_frame": end_frame,
                "start_timestamp": round(start_frame / fps, 2) if fps > 0 else 0,
                "end_timestamp": round(end_frame / fps, 2) if fps > 0 else 0,
                "change_score": change["change_score"]
            })
        
        if scene_changes and scene_changes[-1]["frame_index"] + min_frames < total_frames:
            scenes.append({
                "scene_number": len(scenes) + 1,
                "start_frame": scene_changes[-1]["frame_index"],
                "end_frame": total_frames,
                "start_timestamp": round(scene_changes[-1]["frame_index"] / fps, 2) if fps > 0 else 0,
                "end_timestamp": round(duration, 2),
                "change_score": 0
            })
        
        cap.release()
        
        result = {
            "video_path": filepath,
            "total_frames": total_frames,
            "fps": round(fps, 2),
            "duration_seconds": round(duration, 2),
            "scenes_detected": len(scenes),
            "scene_changes": scene_changes,
            "scenes": scenes,
            "threshold_used": threshold,
            "min_scene_length_seconds": min_scene_length
        }
        
        return result
        
    except Exception as e:
        raise RuntimeError(f"Failed to detect scenes: {str(e)}")


def get_keyframe_field_count() -> int:
    """Return approximate number of keyframe/scene fields."""
    return 20
