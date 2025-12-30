"""
Time-Based Metadata (Golden Hour, Seasons, Sun Position)
Using ephem library for astronomical calculations
"""

from datetime import datetime
from typing import Dict, Any, Optional


try:
    from ephem import Observer, Sun, Moon
    EPHEM_AVAILABLE = True
except ImportError:
    EPHEM_AVAILABLE = False


def _azimuth_to_compass(azimuth_degrees: float) -> str:
    """Convert azimuth in degrees to compass direction."""
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = round(azimuth_degrees / 360.0 * 16) % 16
    return directions[index]


def _get_season(month: int, hemisphere: str = "northern") -> str:
    """Determine season from month."""
    if hemisphere == "northern":
        seasons = {
            12: "winter", 1: "winter", 2: "winter",
            3: "spring", 4: "spring", 5: "spring",
            6: "summer", 7: "summer", 8: "summer",
            9: "autumn", 10: "autumn", 11: "autumn"
        }
    else:
        seasons = {
            12: "summer", 1: "summer", 2: "summer",
            3: "autumn", 4: "autumn", 5: "autumn",
            6: "winter", 7: "winter", 8: "winter",
            9: "spring", 10: "spring", 11: "spring"
        }
    return seasons.get(month, "unknown")


def _get_moon_phase_name(phase: float) -> str:
    """Get moon phase name from phase value (0-1)."""
    if phase < 0.1 or phase > 0.9:
        return "full_moon"
    elif phase > 0.4 and phase < 0.6:
        return "new_moon"
    elif phase < 0.5:
        return "waxing"
    else:
        return "waning"


def extract_time_based_metadata(timestamp: str, gps_data: Optional[Dict] = None,
                               hemisphere: str = "northern") -> Optional[Dict[str, Any]]:
    """
    Calculate time-of-day, golden hour, sun position, moon phase, season.
    
    Args:
        timestamp: Image capture timestamp (ISO format)
        gps_data: Optional GPS data (latitude, longitude)
        hemisphere: Hemisphere for season calculation ("northern" or "southern")
    
    Returns:
        Dictionary with time-based metadata
    """
    if not EPHEM_AVAILABLE:
        return {"error": "ephem library not installed"}
    
    try:
        # Parse timestamp
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace(' ', 'T'))
            except ValueError:
                dt = datetime.strptime(timestamp, "%Y:%m:%d %H:%M:%S")
        else:
            dt = timestamp
        
        result = {
            "timestamp": dt.isoformat(),
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": dt.hour,
            "minute": dt.minute,
            "second": dt.second,
            "weekday": dt.strftime("%A"),
            "season": _get_season(dt.month, hemisphere),
            "has_sun_data": False,
            "has_moon_data": False
        }
        
        # Calculate sun/moon data if GPS is available
        if gps_data and 'latitude' in gps_data and 'longitude' in gps_data:
            lat = float(gps_data['latitude'])
            lon = float(gps_data['longitude'])
            
            # Create observer
            obs = Observer()
            obs.lat = str(lat)
            obs.lon = str(lon)
            obs.date = dt
            
            # Sun position
            sun = Sun(obs)
            sun_alt = float(sun.alt) * 180.0 / 3.14159
            sun_az = float(sun.az) * 180.0 / 3.14159
            
            # Time of day classification
            if sun_alt < -18:
                time_of_day = "night"
            elif sun_alt < -6:
                time_of_day = "blue_hour"
            elif sun_alt < 6:
                time_of_day = "golden_hour"
            elif sun_alt < 30:
                time_of_day = "sunrise_sunset"
            elif sun_alt < 60:
                time_of_day = "morning_afternoon"
            else:
                time_of_day = "midday"
            
            result.update({
                "has_sun_data": True,
                "time_of_day": time_of_day,
                "sun_position": {
                    "altitude": round(sun_alt, 2),
                    "azimuth": round(sun_az, 2),
                    "direction": _azimuth_to_compass(sun_az)
                },
                "golden_hour": -6 < sun_alt < 6,
                "blue_hour": -18 < sun_alt < -6,
                "is_night": sun_alt < -18
            })
            
            # Moon position
            moon = Moon(obs)
            moon_phase = float(moon.phase)
            
            result.update({
                "has_moon_data": True,
                "moon": {
                    "phase": round(moon_phase, 2),
                    "phase_name": _get_moon_phase_name(moon_phase),
                    "illumination": round(moon_phase * 100, 1)
                }
            })
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to calculate time-based metadata: {str(e)}"}


def get_time_based_field_count() -> int:
    """Return approximate number of time-based fields."""
    return 11
