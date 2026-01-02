"""
Transportation and Automotive Metadata Extraction
Extracts vehicle telemetry, GPS tracking, and automotive diagnostic data
"""

from typing import Dict, Any, Optional
import json
import subprocess
import shutil
import logging

logger = logging.getLogger(__name__)

EXIFTOOL_PATH = shutil.which("exiftool")
EXIFTOOL_AVAILABLE = EXIFTOOL_PATH is not None


def extract_transportation_metadata(filepath: str, **kwargs) -> Dict[str, Any]:
    """
    Extract transportation and automotive metadata from file.
    
    Args:
        filepath: Path to the file to extract metadata from
        **kwargs: Additional arguments (unused, for API compatibility)
        
    Returns:
        Dictionary of extracted transportation metadata
    """
    result = {}
    
    # Try ExifTool extraction
    exif_data = _run_exiftool_transportation(filepath)
    if exif_data:
        result.update(_normalize_exif_data(exif_data))
    
    return result


def get_transportation_field_count() -> int:
    """Return count of available transportation fields."""
    return len(VEHICLE_TELEMETRY)


def _run_exiftool_transportation(filepath: str) -> Optional[Dict[str, Any]]:
    """Run exiftool to extract GPS and vehicle metadata."""
    if not EXIFTOOL_AVAILABLE or EXIFTOOL_PATH is None:
        return None

    try:
        # Extract GPS and XMP vehicle data
        cmd = [
            EXIFTOOL_PATH,
            "-j",
            "-n",
            "-G1",
            "-s",
            "-a",
            "-u",
            "-f",
            filepath,
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            logger.warning(f"ExifTool failed for {filepath}: {result.stderr}")
            return None
            
        parsed = json.loads(result.stdout)
        if isinstance(parsed, list) and parsed:
            return parsed[0]
        return None
        
    except subprocess.TimeoutExpired:
        logger.error(f"ExifTool timeout for {filepath}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse ExifTool output for {filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"ExifTool extraction error for {filepath}: {e}")
        return None


def _normalize_exif_data(exif_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize EXIF data using vehicle telemetry mappings.
    
    Args:
        exif_data: Raw EXIF data from exiftool
        
    Returns:
        Normalized metadata dictionary
    """
    normalized = {}
    
    for xmp_field, standard_field in VEHICLE_TELEMETRY.items():
        # Match keys that may have group prefixes
        for key, value in exif_data.items():
            if xmp_field in key or key.endswith(xmp_field.split("-")[-1]):
                # Only add if value is meaningful
                if value is not None and value != "":
                    try:
                        # Try to convert numeric values
                        if isinstance(value, str) and value.replace(".", "").replace("-", "").isdigit():
                            normalized[standard_field] = float(value) if "." in value else int(value)
                        else:
                            normalized[standard_field] = value
                    except (ValueError, AttributeError):
                        normalized[standard_field] = value
                    break
    
    return normalized


# Complete vehicle telemetry and GPS field mappings
# Organized by category for maintainability
VEHICLE_TELEMETRY = {
    # GPS Position & Navigation
    "XMP-GPSLatitude": "gps_latitude",
    "XMP-GPSLongitude": "gps_longitude",
    "XMP-GPSAltitude": "gps_altitude",
    "XMP-GPSSpeed": "gps_speed",
    "XMP-GPSTrack": "gps_track",
    "XMP-GPSTrackRef": "gps_track_ref",
    "XMP-GPSDateTime": "gps_datetime",
    "XMP-GPSDateStamp": "gps_date",
    "XMP-GPSTimeStamp": "gps_time",
    "XMP-GPSLatitudeRef": "gps_latitude_ref",
    "XMP-GPSLongitudeRef": "gps_longitude_ref",
    "XMP-GPSAltitudeRef": "gps_altitude_ref",
    "XMP-GPSSpeedRef": "gps_speed_ref",
    
    # GPS Accuracy & Precision
    "XMP-GPSHPositioningError": "gps_horizontal_accuracy",
    "XMP-GPSVPositioningError": "gps_vertical_accuracy",
    "XMP-GPSDOP": "gps_dilution_of_precision",
    "XMP-GPSMapDatum": "gps_map_datum",
    "XMP-GPSVersionID": "gps_version",
    "XMP-GPSPositionType": "gps_position_type",
    "XMP-GPSTransitStatus": "gps_transit_status",
    
    # Destination Information
    "XMP-GPSDestDistance": "destination_distance",
    "XMP-GPSDestBearing": "destination_bearing",
    "XMP-GPSDestLatitude": "destination_latitude",
    "XMP-GPSDestLongitude": "destination_longitude",
    "XMP-GPSDestBearingRef": "destination_bearing_ref",
    "XMP-GPSDestDistanceRef": "destination_distance_ref",
    "XMP-GPSDestLatitudeRef": "destination_latitude_ref",
    "XMP-GPSDestLongitudeRef": "destination_longitude_ref",
    "XMP-GPSImgDirection": "image_direction",
    "XMP-GPSImgDirectionRef": "image_direction_ref",
    
    # Vehicle Dynamics & Motion
    "XMP-GPSVehicleSpeed": "vehicle_speed_kmh",
    "XMP-GPSVehicleHeading": "vehicle_heading_degrees",
    "XMP-GPSVehicleAcceleration": "vehicle_acceleration",
    "XMP-GPSVehicleBraking": "vehicle_braking_intensity",
    "XMP-GPSVehicleYawRate": "vehicle_yaw_rate",
    "XMP-GPSVehiclePitch": "vehicle_pitch_angle",
    "XMP-GPSVehicleRoll": "vehicle_roll_angle",
    "XMP-GPSVehicleSteeringAngle": "steering_wheel_angle",
    "XMP-GPSVehicleThrottlePosition": "throttle_position_percent",
    
    # Engine & Powertrain
    "XMP-GPSVehicleEngineRPM": "engine_rpm",
    "XMP-GPSVehicleEngineTemp": "engine_temperature_celsius",
    "XMP-GPSVehicleEngineType": "engine_type",
    "XMP-GPSVehicleTransmission": "transmission_type",
    "XMP-GPSVehicleTransmissionTemp": "transmission_temperature",
    "XMP-GPSVehicleGearPosition": "current_gear",
    "XMP-GPSVehicleFuelType": "fuel_type",
    "XMP-GPSVehicleDrivetrain": "drivetrain_type",
    
    # Fluid Levels & Pressures
    "XMP-GPSVehicleFuelLevel": "fuel_level_percent",
    "XMP-GPSVehicleCoolantLevel": "coolant_level_percent",
    "XMP-GPSVehicleOilLevel": "oil_level_percent",
    "XMP-GPSVehicleOilPressure": "oil_pressure_bar",
    "XMP-GPSVehicleBrakePressure": "brake_system_pressure",
    
    # Tire & Suspension
    "XMP-GPSVehicleTirePressure": "tire_pressure_bar",
    "XMP-GPSVehicleTireTemp": "tire_temperature_celsius",
    "XMP-GPSVehicleTireCondition": "tire_wear_percent",
    "XMP-GPSVehicleSuspension": "suspension_height",
    "XMP-GPSVehicleAlignment": "wheel_alignment_status",
    
    # Environmental Sensors
    "XMP-GPSVehicleAmbientTemp": "ambient_temperature_celsius",
    "XMP-GPSVehicleHumidity": "relative_humidity_percent",
    "XMP-GPSVehicleAltitudeChange": "altitude_change_rate",
    "XMP-GPSVehicleGForce": "g_force_measurement",
    
    # Safety Systems Status
    "XMP-GPSVehicleAirbagStatus": "airbag_system_status",
    "XMP-GPSVehicleSeatbeltStatus": "seatbelt_fastened",
    "XMP-GPSVehicleABS": "abs_system_active",
    "XMP-GPSVehicleESP": "esp_traction_control_active",
    "XMP-GPSVehicleTractionControl": "traction_control_status",
    "XMP-GPSVehicleStabilityControl": "stability_control_active",
    
    # Comfort & Convenience Features
    "XMP-GPSVehicleClimateControl": "climate_control_status",
    "XMP-GPSVehicleHVAC": "hvac_mode",
    "XMP-GPSVehicleDefroster": "defroster_status",
    "XMP-GPSVehicleHeatedSeats": "heated_seats_active",
    "XMP-GPSVehicleCruiseControl": "cruise_control_active",
    "XMP-GPSVehicleAdaptiveCruise": "adaptive_cruise_status",
    
    # Driver Assistance Systems
    "XMP-GPSVehicleLaneDeparture": "lane_departure_warning_active",
    "XMP-GPSVehicleCollisionWarning": "collision_warning_active",
    "XMP-GPSVehicleBlindSpot": "blind_spot_warning_active",
    "XMP-GPSVehicleParkingSensors": "parking_sensor_distance",
    "XMP-GPSVehicleBackupCamera": "backup_camera_active",
    "XMP-GPSVehicleNavigation": "navigation_system_status",
    
    # Vehicle Status & Conditions
    "XMP-GPSVehicleDoorStatus": "door_lock_status",
    "XMP-GPSVehicleWindowStatus": "window_status",
    "XMP-GPSVehicleTrunkStatus": "trunk_open_status",
    "XMP-GPSVehicleHoodStatus": "hood_open_status",
    "XMP-GPSVehicleLightsStatus": "lights_status",
    "XMP-GPSVehicleWipersStatus": "wipers_status",
    
    # Vehicle Identification
    "XMP-GPSVehicleVIN": "vehicle_vin",
    "XMP-GPSVehicleLicensePlate": "license_plate",
    "XMP-GPSVehicleMake": "vehicle_make",
    "XMP-GPSVehicleModel": "vehicle_model",
    "XMP-GPSVehicleYear": "vehicle_year",
    "XMP-GPSVehicleColor": "vehicle_color",
    
    # Vehicle Specifications
    "XMP-GPSVehicleBodyStyle": "body_style",
    "XMP-GPSVehicleDoors": "door_count",
    "XMP-GPSVehicleSeats": "seat_count",
    "XMP-GPSVehicleWeight": "vehicle_weight_kg",
    "XMP-GPSVehicleTowingCapacity": "towing_capacity_kg",
    "XMP-GPSVehiclePayload": "payload_capacity_kg",
    "XMP-GPSVehicleRange": "vehicle_range_km",
    "XMP-GPSVehicleSpeedLimit": "speed_limit_kmh",
    
    # Trip & Journey Metrics
    "XMP-GPSVehicleTripStart": "trip_start_timestamp",
    "XMP-GPSVehicleTripEnd": "trip_end_timestamp",
    "XMP-GPSVehicleTripDistance": "trip_distance_km",
    "XMP-GPSVehicleTripDuration": "trip_duration_seconds",
    "XMP-GPSVehicleOdometer": "odometer_reading_km",
    "XMP-GPSVehicleIdleTime": "idle_time_seconds",
    
    # Fuel & Emissions
    "XMP-GPSVehicleFuelConsumed": "fuel_consumed_liters",
    "XMP-GPSVehicleEfficiency": "fuel_efficiency_kmpl",
    "XMP-GPSVehicleCO2Emissions": "co2_emissions_grams",
    "XMP-GPSVehicleIdleFuel": "idle_fuel_consumed_liters",
    "XMP-GPSVehicleEcoScore": "eco_score",
    "XMP-GPSVehiclePerformanceScore": "performance_score",
    "XMP-GPSVehicleSafetyRating": "safety_rating",
    
    # Maintenance & Service
    "XMP-GPSVehicleMaintenance": "maintenance_required",
    "XMP-GPSVehicleServiceDue": "service_due_km",
    "XMP-GPSVehicleOilChange": "oil_change_due_km",
    "XMP-GPSVehicleTireRotation": "tire_rotation_due_km",
    "XMP-GPSVehicleBrakeService": "brake_service_due_km",
    "XMP-GPSVehicleInspection": "inspection_due_date",
    "XMP-GPSVehicleDiagnostic": "diagnostic_codes",
    "XMP-GPSVehicleEmissions": "emissions_test_status",
    
    # Legal & Compliance
    "XMP-GPSVehicleInsurance": "insurance_active",
    "XMP-GPSVehicleInsurancePolicy": "insurance_policy_number",
    "XMP-GPSVehicleInsuranceCompany": "insurance_company",
    "XMP-GPSVehicleInsuranceExpiry": "insurance_expiry_date",
    "XMP-GPSVehicleRegistration": "registration_active",
    "XMP-GPSVehicleTaxStatus": "tax_payment_status",
    "XMP-GPSVehicleTaxExpiry": "tax_expiry_date",
    "XMP-GPSVehicleRoadTax": "road_tax_amount",
    "XMP-GPSVehicleRoadWorthy": "road_worthy_certificate",
    "XMP-GPSVehicleRoadWorthyExpiry": "road_worthy_expiry_date",
    
    # Driver Behavior Monitoring
    "XMP-GPSVehicleDriverID": "driver_id",
    "XMP-GPSVehicleDriverName": "driver_name",
    "XMP-GPSVehicleDriverLicense": "driver_license_number",
    "XMP-GPSVehicleDriverStatus": "driver_status",
    "XMP-GPSVehicleDriverScore": "driver_safety_score",
    "XMP-GPSVehicleDriverFatigue": "driver_fatigue_level",
    "XMP-GPSVehicleDriverDistraction": "driver_distraction_detected",
    "XMP-GPSVehicleDriverBehavior": "driver_behavior_rating",
    
    # Trip Classification
    "XMP-GPSVehicleTripPurpose": "trip_purpose",
    "XMP-GPSVehicleTripCategory": "trip_category",
    "XMP-GPSVehicleHardBraking": "hard_braking_count",
    "XMP-GPSVehicleHardAcceleration": "hard_acceleration_count",
    "XMP-GPSVehicleOverSpeeding": "overspeeding_count",
    
    # Fleet Operations
    "XMP-GPSVehicleFleetID": "fleet_id",
    "XMP-GPSVehicleFleetName": "fleet_name",
    "XMP-GPSVehicleCompany": "company_name",
    "XMP-GPSVehicleDepartment": "department",
    "XMP-GPSVehicleCostCenter": "cost_center",
    "XMP-GPSVehicleProject": "project_assignment",
    "XMP-GPSVehicleUsageType": "vehicle_usage_type",
    "XMP-GPSVehicleLeaseStatus": "lease_active",
    "XMP-GPSVehicleLeaseCompany": "lease_company",
    "XMP-GPSVehicleLeaseStart": "lease_start_date",
    "XMP-GPSVehicleLeaseEnd": "lease_end_date",
    "XMP-GPSVehicleLeaseMileage": "lease_mileage_limit",
    
    # Route & Navigation Planning
    "XMP-GPSVehicleRoute": "route_identifier",
    "XMP-GPSVehicleRouteDistance": "route_planned_distance_km",
    "XMP-GPSVehicleRouteDuration": "route_planned_duration_minutes",
    "XMP-GPSVehicleRouteStops": "planned_stops_count",
    "XMP-GPSVehicleRouteWaypoints": "waypoints_count",
    "XMP-GPSVehicleRouteStart": "route_start_location",
    "XMP-GPSVehicleRouteEnd": "route_end_location",
    "XMP-GPSVehicleRouteEstimatedArrival": "estimated_arrival_time",
    "XMP-GPSVehicleRouteRemainingDistance": "remaining_distance_km",
    "XMP-GPSVehicleRouteRemainingTime": "remaining_time_minutes",
    
    # Route Conditions
    "XMP-GPSVehicleRouteTraffic": "route_traffic_conditions",
    "XMP-GPSVehicleRouteWeather": "route_weather_conditions",
    "XMP-GPSVehicleRouteRoadConditions": "route_road_surface_conditions",
    "XMP-GPSVehicleRouteHazards": "route_hazards_detected",
    
    # Route Services & Facilities
    "XMP-GPSVehicleRouteServices": "route_services_available",
    "XMP-GPSVehicleRouteFuelStops": "fuel_stop_locations",
    "XMP-GPSVehicleRouteRestStops": "rest_stop_locations",
    "XMP-GPSVehicleRouteChargingStops": "charging_stop_locations",
    "XMP-GPSVehicleRouteParking": "parking_availability",
    "XMP-GPSVehicleRouteAccommodation": "accommodation_options",
    "XMP-GPSVehicleRoutePointsOfInterest": "poi_on_route",
    
    # Route Emergency Services
    "XMP-GPSVehicleRouteEmergency": "emergency_services_nearby",
    "XMP-GPSVehicleRoutePolice": "police_station_nearby",
    "XMP-GPSVehicleRouteAmbulance": "ambulance_service_nearby",
    "XMP-GPSVehicleRouteFire": "fire_station_nearby",
    "XMP-GPSVehicleRouteTowing": "towing_service_nearby",
    "XMP-GPSVehicleRouteMechanic": "mechanic_service_nearby",
    "XMP-GPSVehicleRouteHospital": "hospital_nearby",
    "XMP-GPSVehicleRoutePharmacy": "pharmacy_nearby",
    
    # Route Business Services
    "XMP-GPSVehicleRouteGasStation": "gas_station_locations",
    "XMP-GPSVehicleRouteRestaurant": "restaurant_options",
    "XMP-GPSVehicleRouteHotel": "hotel_options",
    "XMP-GPSVehicleRouteMotel": "motel_options",
    "XMP-GPSVehicleRouteCampground": "campground_options",
    
    # Route Parking & Charging
    "XMP-GPSVehicleRouteParkingGarage": "parking_garage_locations",
    "XMP-GPSVehicleRouteParkingLot": "parking_lot_locations",
    "XMP-GPSVehicleRouteChargingStation": "ev_charging_station_locations",
    "XMP-GPSVehicleRouteEVCharging": "ev_charging_available",
    "XMP-GPSVehicleRouteFastCharging": "fast_charging_available",
    "XMP-GPSVehicleRouteSuperCharging": "super_charging_available",
    
    # Route Energy & Range
    "XMP-GPSVehicleRouteBatteryLevel": "estimated_battery_level_percent",
    "XMP-GPSVehicleRouteRange": "estimated_range_remaining_km",
    "XMP-GPSVehicleRouteRangeRemaining": "range_remaining_to_destination_km",
    "XMP-GPSVehicleRouteRangeToEmpty": "range_to_empty_km",
    "XMP-GPSVehicleRouteRangeToFull": "range_to_full_charge_km",
    "XMP-GPSVehicleRouteEfficiency": "route_energy_efficiency",
    
    # Route Preferences & Options
    "XMP-GPSVehicleRouteOptimization": "route_optimization_type",
    "XMP-GPSVehicleRouteAlternative": "alternative_routes_available",
    "XMP-GPSVehicleRouteScenic": "scenic_route_available",
    "XMP-GPSVehicleRouteFastest": "fastest_route_available",
    "XMP-GPSVehicleRouteShortest": "shortest_route_available",
    "XMP-GPSVehicleRouteEco": "eco_friendly_route_available",
    
    # Route Restrictions & Avoidances
    "XMP-GPSVehicleRouteAvoidTolls": "avoid_toll_roads",
    "XMP-GPSVehicleRouteAvoidHighways": "avoid_highways",
    "XMP-GPSVehicleRouteAvoidFerries": "avoid_ferries",
    "XMP-GPSVehicleRouteAvoidUnpaved": "avoid_unpaved_roads",
    "XMP-GPSVehicleRouteAvoidDifficultTurns": "avoid_difficult_turns",
    "XMP-GPSVehicleRouteAvoidConstruction": "avoid_construction_zones",
    "XMP-GPSVehicleRouteAvoidCongestion": "avoid_congestion_areas",
    "XMP-GPSVehicleRouteAvoidWeather": "avoid_severe_weather",
    "XMP-GPSVehicleRouteAvoidHazards": "avoid_hazardous_areas",
    "XMP-GPSVehicleRouteAvoidAccidents": "avoid_accident_prone_areas",
    "XMP-GPSVehicleRouteAvoidRoadClosures": "avoid_closed_roads",
    
    # Route Restrictions (Vehicle Size & Weight)
    "XMP-GPSVehicleRouteRestrictions": "route_restrictions_apply",
    "XMP-GPSVehicleRouteAvoidWeightLimits": "avoid_weight_restricted_roads",
    "XMP-GPSVehicleRouteAvoidHeightLimits": "avoid_height_restricted_roads",
    "XMP-GPSVehicleRouteAvoidWidthLimits": "avoid_width_restricted_roads",
    "XMP-GPSVehicleRouteAvoidLengthLimits": "avoid_length_restricted_roads",
    "XMP-GPSVehicleRouteAvoidAxleWeight": "avoid_axle_weight_restricted_roads",
    
    # Route Special Restrictions
    "XMP-GPSVehicleRouteAvoidTrailers": "avoid_trailer_prohibited_roads",
    "XMP-GPSVehicleRouteAvoidTunnels": "avoid_tunnel_roads",
    "XMP-GPSVehicleRouteAvoidBridges": "avoid_bridge_roads",
    "XMP-GPSVehicleRouteAvoidCarShuttles": "avoid_car_shuttle_areas",
    
    # Route Toll Management
    "XMP-GPSVehicleRouteTolls": "toll_road_present",
    "XMP-GPSVehicleRouteFees": "toll_fees_estimated",
    "XMP-GPSVehicleRouteAvoidTollGates": "avoid_toll_gates",
    "XMP-GPSVehicleRouteAvoidCashTolls": "avoid_cash_tolls_only",
    "XMP-GPSVehicleRouteAvoidTollRoads": "avoid_all_toll_roads",
    
    # Route Highway & Motorway Management
    "XMP-GPSVehicleRouteAvoidFreeways": "avoid_freeways",
    "XMP-GPSVehicleRouteAvoidMotorways": "avoid_motorways",
    "XMP-GPSVehicleRouteAvoidStreets": "avoid_residential_streets",
    
    # Route Zone Restrictions
    "XMP-GPSVehicleRouteAvoidPedestrianZones": "avoid_pedestrian_zones",
    "XMP-GPSVehicleRouteAvoidLowEmissionZones": "avoid_low_emission_zones",
    "XMP-GPSVehicleRouteAvoidCongestionCharging": "avoid_congestion_charge_zones",
    "XMP-GPSVehicleRouteAvoidUlez": "avoid_ulez_zones",
    "XMP-GPSVehicleRouteAvoidCleanAirZones": "avoid_clean_air_zones",
    
    # Route Parking Restrictions
    "XMP-GPSVehicleRouteAvoidParkingRestrictions": "parking_restricted_on_route",
    
    # Route Oversize Handling & Review States
    "XMP-GPSVehicleRouteAvoidOversize": "route_avoids_oversize_vehicles",
    "XMP-GPSVehicleRouteAvoidOversizeAxle": "avoid_oversize_axle_restrictions",
    "XMP-GPSVehicleRouteAvoidOversizeTires": "avoid_oversize_tire_restrictions",
    "XMP-GPSVehicleRouteAvoidOversizeLoad": "avoid_oversize_load_restrictions",
    "XMP-GPSVehicleRouteAvoidOversizeWidth": "avoid_oversize_width_restrictions",
    "XMP-GPSVehicleRouteAvoidOversizeHeight": "avoid_oversize_height_restrictions",
    "XMP-GPSVehicleRouteAvoidOversizeLength": "avoid_oversize_length_restrictions",
    "XMP-GPSVehicleRouteAvoidOversizeWeight": "avoid_oversize_weight_restrictions",
    "XMP-GPSVehicleRouteAvoidOversizeAxleWeight": "avoid_oversize_axle_weight_restrictions",
    "XMP-GPSVehicleRouteAvoidOversizeGrossWeight": "avoid_oversize_gross_weight_restrictions",
    "XMP-GPSVehicleRouteAvoidOversizeOverweight": "avoid_overweight_restrictions",
    
    # Route Oversize Permitting & Documentation
    "XMP-GPSVehicleRouteAvoidOversizePermit": "oversize_permit_required",
    "XMP-GPSVehicleRouteAvoidOversizePermitted": "oversize_permitted_on_route",
    "XMP-GPSVehicleRouteAvoidOversizeEscort": "oversize_escort_required",
    "XMP-GPSVehicleRouteAvoidOversizePolice": "oversize_police_notification_required",
    "XMP-GPSVehicleRouteAvoidOversizeAuthority": "oversize_authority_approval_required",
    "XMP-GPSVehicleRouteAvoidOversizeNotification": "oversize_advance_notification_required",
    "XMP-GPSVehicleRouteAvoidOversizeDocumentation": "oversize_documentation_required",
    
    # Route Oversize Special Handling
    "XMP-GPSVehicleRouteAvoidOversizeSpecial": "special_routing_for_oversize",
    "XMP-GPSVehicleRouteAvoidOversizePlanning": "oversize_route_planning_required",
    "XMP-GPSVehicleRouteAvoidOversizeCoordination": "oversize_coordination_required",
    "XMP-GPSVehicleRouteAvoidOversizeCommunication": "oversize_communication_protocol",
    
    # Route Oversize Insurance & Liability
    "XMP-GPSVehicleRouteAvoidOversizeInsurance": "oversize_special_insurance_required",
    "XMP-GPSVehicleRouteAvoidOversizeLiability": "oversize_liability_coverage",
    "XMP-GPSVehicleRouteAvoidOversizeCompensation": "oversize_damage_compensation_available",
    "XMP-GPSVehicleRouteAvoidOversizeDamage": "oversize_damage_protection_coverage",
    
    # Route Oversize Maintenance & Inspection
    "XMP-GPSVehicleRouteAvoidOversizeRepair": "oversize_repair_facility_required",
    "XMP-GPSVehicleRouteAvoidOversizeMaintenance": "oversize_maintenance_required",
    "XMP-GPSVehicleRouteAvoidOversizeInspection": "oversize_pre_route_inspection_required",
    "XMP-GPSVehicleRouteAvoidOversizeCertification": "oversize_certification_required",
    
    # Route Oversize Registration & Compliance
    "XMP-GPSVehicleRouteAvoidOversizeRegistration": "oversize_vehicle_registration_required",
    "XMP-GPSVehicleRouteAvoidOversizeLicensing": "oversize_special_licensing_required",
    "XMP-GPSVehicleRouteAvoidOversizePermitting": "oversize_permitting_agency_approval",
    "XMP-GPSVehicleRouteAvoidOversizeRegulatory": "oversize_regulatory_compliance_required",
    "XMP-GPSVehicleRouteAvoidOversizeCompliance": "oversize_compliance_verification_status",
    "XMP-GPSVehicleRouteAvoidOversizeStandards": "oversize_industry_standards_compliance",
    "XMP-GPSVehicleRouteAvoidOversizeSpecifications": "oversize_technical_specifications_met",
    "XMP-GPSVehicleRouteAvoidOversizeRequirements": "oversize_all_requirements_met",
    "XMP-GPSVehicleRouteAvoidOversizeConditions": "oversize_route_conditions",
    
    # Route Oversize Restrictions & Prohibitions
    "XMP-GPSVehicleRouteAvoidOversizeLimitations": "oversize_limitations_on_route",
    "XMP-GPSVehicleRouteAvoidOversizeConstraints": "oversize_constraints_apply",
    "XMP-GPSVehicleRouteAvoidOversizeProhibitions": "oversize_prohibitions_in_effect",
    "XMP-GPSVehicleRouteAvoidOversizeBans": "oversize_bans_in_effect",
    "XMP-GPSVehicleRouteAvoidOversizeExclusions": "oversize_exclusion_zones",
    "XMP-GPSVehicleRouteAvoidOversizeExceptions": "oversize_exceptions_granted",
    "XMP-GPSVehicleRouteAvoidOversizeWaivers": "oversize_waivers_obtained",
    "XMP-GPSVehicleRouteAvoidOversizeExemptions": "oversize_exemptions_granted",
    
    # Route Oversize Approval Status
    "XMP-GPSVehicleRouteAvoidOversizeAuthorized": "oversize_route_authorized",
    "XMP-GPSVehicleRouteAvoidOversizeApproved": "oversize_route_approved",
    "XMP-GPSVehicleRouteAvoidOversizeValidated": "oversize_route_validated",
    "XMP-GPSVehicleRouteAvoidOversizeVerified": "oversize_route_verified",
    "XMP-GPSVehicleRouteAvoidOversizeConfirmed": "oversize_route_confirmed",
    "XMP-GPSVehicleRouteAvoidOversizeAccepted": "oversize_route_accepted",
    "XMP-GPSVehicleRouteAvoidOversizeGranted": "oversize_route_granted",
    "XMP-GPSVehicleRouteAvoidOversizeIssued": "oversize_approval_issued",
    "XMP-GPSVehicleRouteAvoidOversizeReceived": "oversize_approval_received",
    "XMP-GPSVehicleRouteAvoidOversizeApplied": "oversize_approval_applied",
    
    # Route Oversize Processing Status
    "XMP-GPSVehicleRouteAvoidOversizeSubmitted": "oversize_permit_submitted",
    "XMP-GPSVehicleRouteAvoidOversizeRequested": "oversize_approval_requested",
    "XMP-GPSVehicleRouteAvoidOversizePending": "oversize_approval_pending",
    "XMP-GPSVehicleRouteAvoidOversizeProcessing": "oversize_approval_processing",
    "XMP-GPSVehicleRouteAvoidOversizeUnderReview": "oversize_approval_under_review",
    "XMP-GPSVehicleRouteAvoidOversizeInReview": "oversize_approval_in_review",
    
    # Route Oversize Review Status (Positive)
    "XMP-GPSVehicleRouteAvoidOversizeReviewRequired": "oversize_review_required",
    "XMP-GPSVehicleRouteAvoidOversizeReviewApproved": "oversize_review_approved",
    "XMP-GPSVehicleRouteAvoidOversizeReviewComplete": "oversize_review_complete",
    "XMP-GPSVehicleRouteAvoidOversizeReviewStarted": "oversize_review_started",
    "XMP-GPSVehicleRouteAvoidOversizeReviewInProgress": "oversize_review_in_progress",
    "XMP-GPSVehicleRouteAvoidOversizeReviewFinished": "oversize_review_finished",
    "XMP-GPSVehicleRouteAvoidOversizeReviewCompleted": "oversize_review_completed",
    "XMP-GPSVehicleRouteAvoidOversizeReviewSuccessful": "oversize_review_successful",
    "XMP-GPSVehicleRouteAvoidOversizeReviewPassed": "oversize_review_passed",
    "XMP-GPSVehicleRouteAvoidOversizeReviewValid": "oversize_review_valid",
    "XMP-GPSVehicleRouteAvoidOversizeReviewActive": "oversize_review_active",
    
    # Route Oversize Review Status (Negative)
    "XMP-GPSVehicleRouteAvoidOversizeReviewRejected": "oversize_review_rejected",
    "XMP-GPSVehicleRouteAvoidOversizeReviewCancelled": "oversize_review_cancelled",
    "XMP-GPSVehicleRouteAvoidOversizeReviewExpired": "oversize_review_expired",
    "XMP-GPSVehicleRouteAvoidOversizeReviewVoided": "oversize_review_voided",
    "XMP-GPSVehicleRouteAvoidOversizeReviewRevoked": "oversize_review_revoked",
    "XMP-GPSVehicleRouteAvoidOversizeReviewSuspended": "oversize_review_suspended",
    "XMP-GPSVehicleRouteAvoidOversizeReviewFailed": "oversize_review_failed",
    
    # Route Oversize Review Status (Negation - "Not" states)
    # Preserved for completeness, though typically boolean flags are preferred
    "XMP-GPSVehicleRouteAvoidOversizeReviewNotPassed": "oversize_review_not_passed",
    "XMP-GPSVehicleRouteAvoidOversizeReviewNotFailed": "oversize_review_not_failed",
    "XMP-GPSVehicleRouteAvoidOversizeReviewNotSuccessful": "oversize_review_not_successful",
    "XMP-GPSVehicleRouteAvoidOversizeReviewNotComplete": "oversize_review_not_complete",
    "XMP-GPSVehicleRouteAvoidOversizeReviewNotStarted": "oversize_review_not_started",
    "XMP-GPSVehicleRouteAvoidOversizeReviewNotFinished": "oversize_review_not_finished",
    "XMP-GPSVehicleRouteAvoidOversizeReviewNotCompleted": "oversize_review_not_completed",
}
