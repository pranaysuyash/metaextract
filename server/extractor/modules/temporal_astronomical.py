"""
Temporal and Astronomical Metadata
Sun/moon position, golden hour detection, and astronomical calculations
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import math


def extract_temporal_metadata(filepath: str, exif_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Extract temporal and astronomical metadata for a file.
    
    Args:
        filepath: Path to image/video file
        exif_data: Optional EXIF data containing datetime and GPS
    
    Returns:
        Dictionary with temporal/astronomical metadata
    """
    result = {
        "datetime_analysis": {},
        "sun_position": {},
        "moon_position": {},
        "daylight_analysis": {},
        "golden_hour": {},
        "twilight_periods": {},
        "astronomical_events": {},
        "fields_extracted": 0
    }

    try:
        datetime_original = None
        latitude = None
        longitude = None

        if exif_data:
            datetime_original = (exif_data.get("datetime_original") or 
                                exif_data.get("date_time_original") or
                                exif_data.get("create_date"))
            
            gps = exif_data.get("gps", {})
            if gps:
                latitude = gps.get("latitude_decimal") or gps.get("latitude")
                longitude = gps.get("longitude_decimal") or gps.get("longitude")

        if not datetime_original:
            file_path = Path(filepath)
            if file_path.exists():
                stat = file_path.stat()
                dt = datetime.fromtimestamp(stat.st_mtime)
                datetime_original = dt.isoformat()
                result["datetime_analysis"]["source"] = "filesystem_mtime"
            else:
                datetime_original = datetime.now().isoformat()
                result["datetime_analysis"]["source"] = "current_time"

        result["datetime_analysis"]["original_datetime"] = datetime_original
        result["datetime_analysis"]["datetime_parsed"] = parse_datetime(datetime_original)

        if latitude and longitude:
            dt_parsed = parse_datetime(datetime_original)
            if dt_parsed:
                sun_pos = calculate_sun_position(latitude, longitude, dt_parsed)
                result["sun_position"] = sun_pos

                moon_pos = calculate_moon_position(latitude, longitude, dt_parsed)
                result["moon_position"] = moon_pos

                daylight = calculate_daylight_periods(latitude, longitude, dt_parsed)
                result["daylight_analysis"] = daylight

                golden = calculate_golden_hour(latitude, longitude, dt_parsed)
                result["golden_hour"] = golden

                twilight = calculate_twilight_periods(latitude, longitude, dt_parsed)
                result["twilight_periods"] = twilight

                astro = calculate_astronomical_events(latitude, longitude, dt_parsed)
                result["astronomical_events"] = astro

                result["location_context"] = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "hemisphere": "northern" if float(latitude) > 0 else "southern",
                    "eastern_western": "eastern" if float(longitude) > 0 else "western"
                }

        result["fields_extracted"] = (
            len(result["datetime_analysis"]) +
            len(result["sun_position"]) +
            len(result["moon_position"]) +
            len(result["daylight_analysis"]) +
            len(result["golden_hour"]) +
            len(result["twilight_periods"]) +
            len(result["astronomical_events"]) +
            len(result.get("location_context", {}))
        )

    except Exception as e:
        result["error"] = str(e)[:200]

    return result


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse datetime string into datetime object."""
    if not dt_str:
        return None
    
    try:
        import dateutil.parser
        return dateutil.parser.parse(str(dt_str))
    except Exception as e:
        try:
            for fmt in ["%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(str(dt_str), fmt)
                except Exception as e:
                    continue
        except Exception as e:
            logger.debug(f"Failed to calculate astronomical time data: {e}")
    return None


def calculate_sun_position(lat: float, lon: float, dt: datetime) -> Dict[str, Any]:
    """Calculate sun position (azimuth and altitude)."""
    result = {
        "azimuth_degrees": None,
        "altitude_degrees": None,
        "sunrise_time": None,
        "sunset_time": None,
        "solar_noon_time": None,
        "day_length_hours": None,
        "is_daytime": None
    }

    try:
        lat = float(lat)
        lon = float(lon)

        day_of_year = dt.timetuple().tm_yday
        hour = dt.hour + dt.minute / 60.0

        declination = 23.45 * math.sin(math.radians(360/365 * (day_of_year - 81)))

        hour_angle = 15 * (hour - 12)

        elevation = math.degrees(math.asin(
            math.sin(math.radians(lat)) * math.sin(math.radians(declination)) +
            math.cos(math.radians(lat)) * math.cos(math.radians(declination)) * math.cos(math.radians(hour_angle))
        ))

        azimuth = math.degrees(math.acos(
            (math.sin(math.radians(declination)) - 
             math.sin(math.radians(lat)) * math.sin(math.radians(elevation))) /
            (math.cos(math.radians(lat)) * math.cos(math.radians(elevation)))
        ))

        if hour > 12:
            azimuth = 360 - azimuth

        result["azimuth_degrees"] = round(azimuth, 2)
        result["altitude_degrees"] = round(elevation, 2)

        sunrise, sunset = calculate_sunrise_sunset(lat, lon, dt)
        result["sunrise_time"] = sunrise.isoformat() if sunrise else None
        result["sunset_time"] = sunset.isoformat() if sunset else None

        if sunrise and sunset:
            day_length = (sunset - sunrise).total_seconds() / 3600
            result["day_length_hours"] = round(day_length, 2)
            result["is_daytime"] = sunrise <= dt <= sunset

            solar_noon = sunrise + (sunset - sunrise) / 2
            result["solar_noon_time"] = solar_noon.isoformat()

    except Exception as e:
        result["error"] = str(e)[:100]

    return result


def calculate_sunrise_sunset(lat: float, lon: float, dt: datetime) -> tuple:
    """Calculate sunrise and sunset times."""
    try:
        lat = float(lat)
        
        day_of_year = dt.timetuple().tm_yday
        B = (360/365) * (day_of_year - 81)
        
        EoT = 9.87 * math.sin(math.radians(2 * B)) - 7.53 * math.cos(math.radians(B)) - 1.5 * math.sin(math.radians(B))
        
        LSTM = 15 * (round(lon / 15) if lon else 0)
        
        TC = 4 * (lon - LSTM) + EoT
        
        LST = dt.hour + dt.minute / 60 + TC / 60
        
        H = 0.133 * math.cos(math.radians(0.833 + 0.189 * math.sin(math.radians(360/365 * (day_of_year - 81)))))
        
        sunrise = 6 + (4 * (lat - H) / 60) - TC / 60
        sunset = 18 + (4 * (lat + H) / 60) - TC / 60
        
        sunrise_dt = dt.replace(hour=int(sunrise), minute=int((sunrise % 1) * 60), second=0, microsecond=0)
        sunset_dt = dt.replace(hour=int(sunset), minute=int((sunset % 1) * 60), second=0, microsecond=0)
        
        return sunrise_dt, sunset_dt
    except Exception as e:
        return None, None


def calculate_moon_position(lat: float, lon: float, dt: datetime) -> Dict[str, Any]:
    """Calculate moon position and phase."""
    result = {
        "moon_phase_name": None,
        "moon_phase_degrees": None,
        "moon_azimuth": None,
        "moon_altitude": None,
        "moon_illumination": None,
        "is_moon_visible": None
    }

    try:
        lat = float(lat)
        
        day_of_year = dt.timetuple().tm_yday
        year = dt.year

        moon_age = (day_of_year + dt.hour / 24) % 29.53058867
        moon_phase_degrees = (moon_age / 29.53058867) * 360
        
        if moon_phase_degrees < 10 or moon_phase_degrees > 350:
            phase_name = "New Moon"
        elif moon_phase_degrees < 85:
            phase_name = "Waxing Crescent"
        elif moon_phase_degrees < 95:
            phase_name = "First Quarter"
        elif moon_phase_degrees < 175:
            phase_name = "Waxing Gibbous"
        elif moon_phase_degrees < 185:
            phase_name = "Full Moon"
        elif moon_phase_degrees < 265:
            phase_name = "Waning Gibbous"
        elif moon_phase_degrees < 275:
            phase_name = "Last Quarter"
        else:
            phase_name = "Waning Crescent"

        result["moon_phase_name"] = phase_name
        result["moon_phase_degrees"] = round(moon_phase_degrees, 2)

        illumination = (1 - math.cos(math.radians(moon_phase_degrees))) / 2 * 100
        result["moon_illumination"] = round(illumination, 1)

        result["is_moon_visible"] = illumination > 20 and dt.hour > 18 or dt.hour < 6

    except Exception as e:
        result["error"] = str(e)[:100]

    return result


def calculate_daylight_periods(lat: float, lon: float, dt: datetime) -> Dict[str, Any]:
    """Calculate daylight periods."""
    result = {
        "day_length_hours": None,
        "night_length_hours": None,
        "day_percentage": None,
        "is_northern_hemisphere": None,
        "season": None,
        "day_of_year": None
    }

    try:
        lat = float(lat)
        day_of_year = dt.timetuple().tm_year
        
        result["day_of_year"] = day_of_year
        result["is_northern_hemisphere"] = lat > 0

        if lat > 0:
            if day_of_year < 80 or day_of_year > 355:
                result["season"] = "Winter"
            elif day_of_year < 172:
                result["season"] = "Spring"
            elif day_of_year < 266:
                result["season"] = "Summer"
            else:
                result["season"] = "Autumn"
        else:
            if day_of_year < 80 or day_of_year > 355:
                result["season"] = "Summer"
            elif day_of_year < 172:
                result["season"] = "Autumn"
            elif day_of_year < 266:
                result["season"] = "Winter"
            else:
                result["season"] = "Spring"

        sunrise, sunset = calculate_sunrise_sunset(lat, lon, dt)
        if sunrise and sunset:
            day_length = (sunset - sunrise).total_seconds() / 3600
            result["day_length_hours"] = round(day_length, 2)
            result["night_length_hours"] = round(24 - day_length, 2)
            result["day_percentage"] = round(day_length / 24 * 100, 1)

    except Exception as e:
        result["error"] = str(e)[:100]

    return result


def calculate_golden_hour(lat: float, lon: float, dt: datetime) -> Dict[str, Any]:
    """Calculate golden hour and blue hour periods."""
    result = {
        "morning_golden_hour_start": None,
        "morning_golden_hour_end": None,
        "evening_golden_hour_start": None,
        "evening_golden_hour_end": None,
        "morning_blue_hour_start": None,
        "morning_blue_hour_end": None,
        "evening_blue_hour_start": None,
        "evening_blue_hour_end": None,
        "is_golden_hour": None,
        "is_blue_hour": None
    }

    try:
        lat = float(lat)
        
        sunrise, sunset = calculate_sunrise_sunset(lat, lon, dt)
        if sunrise and sunset:
            morning_gh_start = sunrise - timedelta(minutes=30)
            morning_gh_end = sunrise + timedelta(minutes=30)
            result["morning_golden_hour_start"] = morning_gh_start.isoformat()
            result["morning_golden_hour_end"] = morning_gh_end.isoformat()

            evening_gh_start = sunset - timedelta(minutes=30)
            evening_gh_end = sunset + timedelta(minutes=30)
            result["evening_golden_hour_start"] = evening_gh_start.isoformat()
            result["evening_golden_hour_end"] = evening_gh_end.isoformat()

            morning_bh_start = sunrise - timedelta(minutes=40)
            morning_bh_end = sunrise - timedelta(minutes=10)
            result["morning_blue_hour_start"] = morning_bh_start.isoformat()
            result["morning_blue_hour_end"] = morning_bh_end.isoformat()

            evening_bh_start = sunset + timedelta(minutes=10)
            evening_bh_end = sunset + timedelta(minutes=40)
            result["evening_blue_hour_start"] = evening_bh_start.isoformat()
            result["evening_blue_hour_end"] = evening_bh_end.isoformat()

            result["is_golden_hour"] = (
                (morning_gh_start <= dt <= morning_gh_end) or
                (evening_gh_start <= dt <= evening_gh_end)
            )
            result["is_blue_hour"] = (
                (morning_bh_start <= dt <= morning_bh_end) or
                (evening_bh_start <= dt <= evening_bh_end)
            )

    except Exception as e:
        result["error"] = str(e)[:100]

    return result


def calculate_twilight_periods(lat: float, lon: float, dt: datetime) -> Dict[str, Any]:
    """Calculate civil, nautical, and astronomical twilight periods."""
    result = {
        "civil_twilight_morning_start": None,
        "civil_twilight_morning_end": None,
        "civil_twilight_evening_start": None,
        "civil_twilight_evening_end": None,
        "nautical_twilight_morning_start": None,
        "nautical_twilight_morning_end": None,
        "nautical_twilight_evening_start": None,
        "nautical_twilight_evening_end": None,
        "astronomical_twilight_morning_start": None,
        "astronomical_twilight_morning_end": None,
        "astronomical_twilight_evening_start": None,
        "astronomical_twilight_evening_end": None,
        "is_civil_twilight": None,
        "is_nautical_twilight": None,
        "is_astronomical_twilight": None,
        "is_night": None
    }

    try:
        lat = float(lat)
        
        sunrise, sunset = calculate_sunrise_sunset(lat, lon, dt)
        if sunrise and sunset:
            civil_offset = timedelta(minutes=30)
            nautical_offset = timedelta(minutes=60)
            astro_offset = timedelta(minutes=90)

            result["civil_twilight_morning_start"] = (sunrise - civil_offset).isoformat()
            result["civil_twilight_morning_end"] = sunrise.isoformat()
            result["civil_twilight_evening_start"] = sunset.isoformat()
            result["civil_twilight_evening_end"] = (sunset + civil_offset).isoformat()

            result["nautical_twilight_morning_start"] = (sunrise - nautical_offset).isoformat()
            result["nautical_twilight_morning_end"] = (sunrise - civil_offset).isoformat()
            result["nautical_twilight_evening_start"] = (sunset + civil_offset).isoformat()
            result["nautical_twilight_evening_end"] = (sunset + nautical_offset).isoformat()

            result["astronomical_twilight_morning_start"] = (sunrise - astro_offset).isoformat()
            result["astronomical_twilight_morning_end"] = (sunrise - nautical_offset).isoformat()
            result["astronomical_twilight_evening_start"] = (sunset + nautical_offset).isoformat()
            result["astronomical_twilight_evening_end"] = (sunset + astro_offset).isoformat()

            ct_start = sunrise - civil_offset
            ct_end = sunrise + civil_offset
            result["is_civil_twilight"] = ct_start - timedelta(minutes=15) <= dt <= ct_end + timedelta(minutes=15)

            nt_start = sunrise - nautical_offset
            nt_end = sunrise + nautical_offset
            result["is_nautical_twilight"] = nt_start - timedelta(minutes=15) <= dt <= nt_end + timedelta(minutes=15)

            at_start = sunrise - astro_offset
            at_end = sunrise + astro_offset
            result["is_astronomical_twilight"] = at_start - timedelta(minutes=15) <= dt <= at_end + timedelta(minutes=15)

            result["is_night"] = dt < (sunrise - astro_offset) or dt > (sunset + astro_offset)

    except Exception as e:
        result["error"] = str(e)[:100]

    return result


def calculate_astronomical_events(lat: float, lon: float, dt: datetime) -> Dict[str, Any]:
    """Calculate various astronomical events."""
    result = {
        "meridian_transit": None,
        "hour_angle": None,
        "solar_time": None,
        "equation_of_time": None,
        "analemma_position": None,
        "seasonal_variation": None
    }

    try:
        lat = float(lat)
        day_of_year = dt.timetuple().tm_yday
        
        B = (360/365) * (day_of_year - 81)
        EoT = 9.87 * math.sin(math.radians(2 * B)) - 7.53 * math.cos(math.radians(B)) - 1.5 * math.sin(math.radians(B))
        result["equation_of_time"] = round(EoT, 2)

        hour = dt.hour + dt.minute / 60
        hour_angle = 15 * (hour - 12)
        result["hour_angle"] = round(hour_angle, 2)

        solar_time = hour + EoT / 60
        result["solar_time"] = round(solar_time, 2)

        declination = 23.45 * math.sin(math.radians(360/365 * (day_of_year - 81)))
        result["seasonal_variation"] = {
            "solar_declination": round(declination, 2),
            "tilt_direction": "toward_northern_hemisphere" if declination > 0 else "toward_southern_hemisphere"
        }

    except Exception as e:
        result["error"] = str(e)[:100]

    return result


def get_temporal_field_count() -> int:
    """Return approximate number of temporal/astronomical fields."""
    return 65


def verify_photo_authenticity(temporal_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Verify if photo timing is consistent with visual content."""
    verification = {
        "is_consistent": True,
        "warnings": [],
        "confidence_score": 1.0
    }

    sun_pos = temporal_metadata.get("sun_position", {})
    golden = temporal_metadata.get("golden_hour", {})
    twilight = temporal_metadata.get("twilight_periods", {})

    altitude = sun_pos.get("altitude_degrees", 0)
    is_golden = golden.get("is_golden_hour", False)
    is_twilight = twilight.get("is_civil_twilight", False) or twilight.get("is_nautical_twilight", False)

    if altitude > 10 and is_golden:
        verification["warnings"].append("Golden hour claimed but sun altitude is high")
        verification["confidence_score"] -= 0.1

    if altitude < -18 and (is_golden or is_twilight):
        verification["warnings"].append("Twilight/golden hour claimed but sun is below horizon")

    if sun_pos.get("is_daytime") and twilight.get("is_astronomical_twilight"):
        verification["warnings"].append("Daytime with astronomical twilight - unusual")

    verification["is_consistent"] = len(verification["warnings"]) == 0

    return verification
