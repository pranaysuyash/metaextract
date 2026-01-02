# Image Field Audit (Source of Truth)
This report enumerates image-related fields as implemented in code. It lists field names and their data sources by module.

## Pipeline Note
Primary production extraction uses `server/extractor/metadata_engine.py` (exiftool + Pillow + supporting modules). The plugin modules in `server/extractor/modules/` exist but are not the default path for the comprehensive engine.

## exif
Source file: `server/extractor/modules/exif.py`
Note: `ULTRA_*` and `MEGA_*` dictionaries are used for field count only; they are not currently extracted at runtime.

### EXIF_TAGS
- `aperture_value` <- `ApertureValue`
- `artist` <- `Artist`
- `bits_per_sample` <- `BitsPerSample`
- `body_serial_number` <- `BodySerialNumber`
- `brightness_value` <- `BrightnessValue`
- `camera_make` <- `Make`
- `camera_model` <- `Model`
- `camera_owner_name` <- `CameraOwnerName`
- `camera_serial_number` <- `CameraSerialNumber`
- `color_space` <- `ColorSpace`
- `compression` <- `Compression`
- `contrast` <- `Contrast`
- `copyright` <- `Copyright`
- `date_time` <- `DateTime`
- `date_time_digitized` <- `DateTimeDigitized`
- `date_time_original` <- `DateTimeOriginal`
- `description` <- `ImageDescription`
- `digital_zoom` <- `DigitalZoomRatio`
- `exposure_bias` <- `ExposureBiasValue`
- `exposure_index` <- `ExposureIndex`
- `exposure_mode` <- `ExposureMode`
- `exposure_program` <- `ExposureProgram`
- `exposure_time` <- `ExposureTime`
- `exposure_value` <- `ExposureValue`
- `f_number` <- `FNumber`
- `flash` <- `Flash`
- `flash_energy` <- `FlashEnergy`
- `flash_exposure_comp` <- `FlashExposureComp`
- `flash_metering` <- `FlashMetering`
- `flash_sync_speed` <- `FlashSyncSpeed`
- `focal_length` <- `FocalLength`
- `focal_length_35mm` <- `FocalLengthIn35mmFilm`
- `focal_plane_resolution_unit` <- `FocalPlaneResolutionUnit`
- `focal_plane_x_resolution` <- `FocalPlaneXResolution`
- `focal_plane_y_resolution` <- `FocalPlaneYResolution`
- `gain_control` <- `GainControl`
- `gps_altitude` <- `GPSAltitude`
- `gps_altitude_ref` <- `GPSAltitudeRef`
- `gps_area_information` <- `GPSAreaInformation`
- `gps_date_stamp` <- `GPSDateStamp`
- `gps_dest_bearing` <- `GPSDestBearing`
- `gps_dest_bearing_ref` <- `GPSDestBearingRef`
- `gps_dest_distance` <- `GPSDestDistance`
- `gps_dest_distance_ref` <- `GPSDestDistanceRef`
- `gps_dest_latitude_ref` <- `GPSDestLatitudeRef`
- `gps_dest_longitude_ref` <- `GPSDestLongitudeRef`
- `gps_differential` <- `GPSDifferential`
- `gps_dop` <- `GPSDOP`
- `gps_h_positioning_error` <- `GPSHPositioningError`
- `gps_image_direction` <- `GPSImgDirection`
- `gps_img_direction_ref` <- `GPSImgDirectionRef`
- `gps_latitude` <- `GPSLatitude`
- `gps_latitude_ref` <- `GPSLatitudeRef`
- `gps_longitude` <- `GPSLongitude`
- `gps_longitude_ref` <- `GPSLongitudeRef`
- `gps_map_datum` <- `GPSMapDatum`
- `gps_measure_mode` <- `GPSMeasureMode`
- `gps_processing_method` <- `GPSProcessingMethod`
- `gps_satellites` <- `GPSSatellites`
- `gps_speed` <- `GPSSpeed`
- `gps_speed_ref` <- `GPSSpeedRef`
- `gps_status` <- `GPSStatus`
- `gps_timestamp` <- `GPSTimeStamp`
- `gps_track` <- `GPSTrack`
- `gps_track_ref` <- `GPSTrackRef`
- `gps_version_id` <- `GPSVersionID`
- `image_height` <- `ImageHeight`
- `image_number` <- `ImageNumber`
- `image_width` <- `ImageWidth`
- `interoperability_index` <- `InteroperabilityIndex`
- `interoperability_version` <- `InteroperabilityVersion`
- `iso_speed_ratings` <- `ISOSpeedRatings`
- `lens_info` <- `LensInfo`
- `lens_make` <- `LensMake`
- `lens_model` <- `LensModel`
- `lens_serial_number` <- `LensSerialNumber`
- `lens_specification` <- `LensSpecification`
- `light_source` <- `LightSource`
- `max_aperture` <- `MaxApertureValue`
- `metering_mode` <- `MeteringMode`
- `number_of_strips` <- `NumberOfStrips`
- `orientation` <- `Orientation`
- `photometric_interpretation` <- `PhotometricInterpretation`
- `pixel_height` <- `PixelYDimension`
- `pixel_width` <- `PixelXDimension`
- `planar_configuration` <- `PlanarConfiguration`
- `primary_chromaticities` <- `PrimaryChromaticities`
- `processing_software` <- `ProcessingSoftware`
- `quality` <- `Quality`
- `reference_black_white` <- `ReferenceBlackWhite`
- `related_image_file_format` <- `RelatedImageFileFormat`
- `related_image_length` <- `RelatedImageLength`
- `related_image_width` <- `RelatedImageWidth`
- `resolution_unit` <- `ResolutionUnit`
- `row_samples_per_strip` <- `RowSamplesPerStrip`
- `samples_per_pixel` <- `SamplesPerPixel`
- `saturation` <- `Saturation`
- `scene_type` <- `SceneCaptureType`
- `self_timer_mode` <- `SelfTimerMode`
- `sensing_method` <- `SensingMethod`
- `sharpness` <- `Sharpness`
- `shutter_counter` <- `ShutterCounter`
- `shutter_speed_value` <- `ShutterSpeedValue`
- `software` <- `Software`
- `strip_byte_counts` <- `StripByteCounts`
- `strip_offsets` <- `StripOffsets`
- `subject_distance` <- `SubjectDistance`
- `subject_distance_range` <- `SubjectDistanceRange`
- `thumbnail_byte_count` <- `ThumbnailByteCount`
- `thumbnail_compression` <- `ThumbnailCompression`
- `thumbnail_height` <- `ThumbnailImageHeight`
- `thumbnail_offset` <- `ThumbnailOffset`
- `thumbnail_orientation` <- `ThumbnailOrientation`
- `thumbnail_resolution_unit` <- `ThumbnailResolutionUnit`
- `thumbnail_width` <- `ThumbnailImageWidth`
- `thumbnail_x_resolution` <- `ThumbnailXResolution`
- `thumbnail_y_resolution` <- `ThumbnailYResolution`
- `white_balance` <- `WhiteBalance`
- `white_point` <- `WhitePoint`
- `x_position` <- `XPosition`
- `x_resolution` <- `XResolution`
- `y_position` <- `YPosition`
- `y_resolution` <- `YResolution`
- `ycbcr_coefficients` <- `YCbCrCoefficients`
- `ycbcr_positioning` <- `YCbCrPositioning`
- `ycbcr_sub_sampling` <- `YCbCrSubSampling`

### MEGA_EXPANSION_FIELDS
- `360_panorama_capture` <- `panorama_mode`
- `3d_image_layers` <- `z_stack_depth`
- `above_ground_level_meters` <- `flight_altitude`
- `action_capture_settings` <- `sports_mode`
- `advanced_timelapse_drone` <- `hyperlapse`
- `ai_upscaling_method` <- `super_resolution`
- `ambisonic_audio_format` <- `spatial_audio`
- `animated_image_capture` <- `live_photos`
- `augmented_reality_stickers` <- `ar_emoji`
- `autopano_video_stitch` <- `stitching_software`
- `brightfield_fluorescence_confocal` <- `microscope_type`
- `camera_rotation_angle` <- `gimbal_roll`
- `camera_synchronization_ms` <- `time_sync`
- `camera_tilt_angle` <- `gimbal_pitch`
- `chemical_dye_used` <- `staining_method`
- `chest_abdomen_extremity` <- `body_part`
- `cinematic_color_science` <- `color_grading`
- `circular_flight_pattern` <- `orbit_mode`
- `close_up_focusing` <- `macro_mode`
- `collision_detection_system` <- `obstacle_avoidance`
- `color_optimization_food` <- `food_mode`
- `depth_effect_portrait` <- `portrait_mode`
- `dji_mavic_phantom_autel` <- `drone_model`
- `document_scanning` <- `documents_mode`
- `drone_velocity_kmh` <- `flight_speed`
- `equirectangular_cubemap` <- `projection_format`
- `exposure_dose_mgy` <- `radiation_dose`
- `face_enhancement_level` <- `beauty_mode`
- `fixation_sectioning` <- `sample_preparation`
- `front_camera_optimization` <- `selfie_mode`
- `hdr_compression_method` <- `tone_mapping`
- `hero_insta360_kandao` <- `camera_rig_type`
- `high_dynamic_range_plus` <- `hdr_plus`
- `high_fps_recording` <- `slow_motion`
- `image_restoration_method` <- `deconvolution`
- `initial_view_angle` <- `view_orientation`
- `low_light_enhancement` <- `night_mode`
- `manual_autonomous_waypoint` <- `drone_operation_mode`
- `manual_controls_enabled` <- `pro_mode`
- `microscopy_time_lapse` <- `time_lapse_interval`
- `multi_exposure_combination` <- `image_fusion`
- `multichannel_colors` <- `fluorescence_channels`
- `noise_reduction_frames` <- `multi_frame_noise`
- `objective_magnification` <- `microscope_mag`
- `pa_ap_lat_medial_oblique` <- `xray_technique`
- `plenoptic_camera_data` <- `light_field_capture`
- `posterior_anterior_lateral` <- `view_projection`
- `realtime_360_stream` <- `live_streaming`
- `rth_functionality` <- `return_to_home`
- `subject_detection_mask` <- `semantic_segmentation`
- `subject_tracking` <- `follow_mode`
- `supine_prone_lateral` <- `patient_position`
- `surface_tracking_mode` <- `terrain_follow`
- `synthetic_depth_blur` <- `computational_bokeh`
- `timelapse_recording` <- `time_lapse`
- `video_cinematic_effects` <- `cinematic_mode`
- `virtual_ready_ready` <- `vr_compatible`
- `window_level_width` <- `contrast_enhancement`
- `zoom_enlargement` <- `magnification_factor`

### ULTRA_EXIF_FIELDS
- `ae_af_lock_status` <- `exposure_lock`
- `af_motor_type_usm_swm` <- `autofocus_motor`
- `autofocus_manual_manual_focus` <- `focus_mode`
- `autofocus_point_selection` <- `focus_points`
- `beauty_filter_strength` <- `skin_softening`
- `canon_picture_style` <- `picture_style`
- `coating_element_count` <- `lens_optical_attributes`
- `compass_heading_direction` <- `gps_direction`
- `coordinate_reference_system` <- `map_datum`
- `distance_to_subject_meters` <- `focus_distance`
- `elevation_above_sea_level` <- `gps_altitude`
- `exposure_bracketing_count` <- `multiple_exposure`
- `exposure_compensation_steps` <- `exposure_bracketing`
- `exposure_metering_pattern` <- `metering_mode`
- `eye_blink_detected` <- `blink_detection`
- `face_coordinates_in_frame` <- `face_locations`
- `geographic_coordinate_latitude` <- `gps_latitude`
- `geographic_coordinate_longitude` <- `gps_longitude`
- `gps_datetime_fix` <- `gps_timestamp`
- `hdr_effect_intensity` <- `hdr_strength`
- `high_dynamic_range_capture` <- `hdr_mode`
- `high_iso_noise_reduction` <- `high_iso_nr`
- `horizontal_dilution_of_precision` <- `gps_precision`
- `identified_persons_names` <- `face_recognition`
- `if_internal_focusing` <- `internal_focus`
- `lens_firmware_version` <- `lens_firmware`
- `lens_manufacturer_serial` <- `lens_serial_number`
- `long_exposure_noise_reduction` <- `long_exposure_nr`
- `nikon_active_dlighting` <- `active_dlighting`
- `number_of_faces_identified` <- `faces_detected`
- `number_of_satellites_tracked` <- `gps_satellites`
- `optical_stabilization_mode` <- `image_stabilization`
- `self_timer_seconds` <- `timer_duration`
- `smile_confidence_level` <- `smile_detection`
- `srgb_adobe_rgb_prophoto` <- `color_space`
- `time_lapse_interval` <- `interval_shooting`
- `vr_vibration_reduction` <- `vibration_reduction`
- `wb_color_compensation` <- `white_balance_shift`


## iptc_xmp
Source file: `server/extractor/modules/iptc_xmp.py`
Note: `ULTRA_*` and `MEGA_*` dictionaries are used for field count only; they are not currently extracted at runtime.

### IPTC_CORE_FIELDS
- `city` <- `Iptc.Application2.City`
- `copyright_notice` <- `Iptc.Application2.Copyright`
- `country` <- `Iptc.Application2.CountryName`
- `country_code` <- `Iptc.Application2.CountryCode`
- `creator` <- `Iptc.Application2.Byline`
- `creator_title` <- `Iptc.Application2.BylineTitle`
- `credit` <- `Iptc.Application2.Credit`
- `date_created` <- `Iptc.Application2.DateCreated`
- `description` <- `Iptc.Application2.Caption`
- `headline` <- `Iptc.Application2.Headline`
- `instructions` <- `Iptc.Application2.SpecialInstructions`
- `intellectual_genre` <- `Iptc.Application2.ObjectType`
- `keywords` <- `Iptc.Application2.Keywords`
- `location` <- `Iptc.Application2.SubLocation`
- `source` <- `Iptc.Application2.Source`
- `state_province` <- `Iptc.Application2.ProvinceState`
- `subject_codes` <- `Iptc.Application2.SubjectCode`
- `transmission_reference` <- `Iptc.Application2.TransmissionReference`

### IPTC_CREATOR_CONTACT_INFO
- `creator_contact` <- `Iptc.Application2.Contact`
- `email_1` <- `Iptc.Application2.Email1`
- `email_2` <- `Iptc.Application2.Email2`
- `phone_1` <- `Iptc.Application2.Phone1`
- `phone_2` <- `Iptc.Application2.Phone2`
- `web_url` <- `Iptc.Application2.WebURL`

### IPTC_EXTENSION_FIELDS
- `copyright_notice` <- `Iptc.Application2.CopyrightNotice`
- `digital_source_type` <- `Iptc.Application2.DigitalSourceType`
- `event` <- `Iptc.Application2.Event`
- `image_type` <- `Iptc.Application2.ImageType`
- `location_created` <- `Iptc.Application2.LocationCreated`
- `location_shown` <- `Iptc.Application2.LocationShown`
- `max_available_height` <- `Iptc.Application2.MaxAvailHeight`
- `max_available_width` <- `Iptc.Application2.MaxAvailWidth`
- `model_release_status` <- `Iptc.Application2.ModelReleaseStatus`
- `organizations` <- `Iptc.Application2.OrganisationInImageName`
- `persons_shown` <- `Iptc.Application2.PersonInImage`
- `property_release_status` <- `Iptc.Application2.PropertyReleaseStatus`
- `scene_codes` <- `Iptc.Application2.Scene`
- `subject_reference` <- `Iptc.Application2.SubjectReference`
- `urgency` <- `Iptc.Application2.Urgency`
- `usage_terms` <- `Iptc.Application2.UsageTerms`
- `web_statement` <- `Iptc.Application2.WebStatement`

### IPTC_LICENSOR
- `licensor` <- `Iptc.Application2.Licensor`
- `licensor_address` <- `Iptc.Application2.LicensorAddress`
- `licensor_city` <- `Iptc.Application2.LicensorCity`
- `licensor_country` <- `Iptc.Application2.LicensorCountry`
- `licensor_email` <- `Iptc.Application2.LicensorEmail`
- `licensor_name` <- `Iptc.Application2.LicensorName`
- `licensor_phone_1` <- `Iptc.Application2.LicensorTelephone1`
- `licensor_phone_2` <- `Iptc.Application2.LicensorTelephone2`
- `licensor_postal_code` <- `Iptc.Application2.LicensorPostalCode`
- `licensor_state` <- `Iptc.Application2.LicensorState`
- `licensor_url` <- `Iptc.Application2.LicensorURL`

### MEGA_IPTC_XMP_FIELDS
- `asset_management` <- `manager_variant`
- `content_identifier` <- `document_id`
- `content_quality_score` <- `xmp_rating`
- `copyright_status` <- `marking_status`
- `creation_software` <- `xmp_creator_tool`
- `creation_timestamp` <- `xmp_create_date`
- `creator_contact` <- `provider_identification`
- `digital_capture_type` <- `digital_source_type`
- `editorial_content_label` <- `xmp_label`
- `editorial_keywords` <- `xmp_labels`
- `instance_identifier` <- `instance_id`
- `intended_use` <- `manage_to`
- `license_link` <- `license_url`
- `license_terms` <- `rights_usage_terms`
- `media_format` <- `xmp_format`
- `metadata_timestamp` <- `xmp_metadata_date`
- `modification_timestamp` <- `xmp_modify_date`
- `online_rights` <- `web_statement`
- `online_rights_statement` <- `web_statement_rights`
- `project_identifier` <- `job_reference`
- `provider_info` <- `service_identification`
- `rendition_type` <- `rendition_class`
- `rights_contact` <- `copyright_owner_url`
- `rights_holder_name` <- `copyright_owner`
- `rights_identifier` <- `copyright_owner_id`
- `scene_recognition` <- `scene_type`
- `source_reference` <- `rendition_of`
- `target_usage` <- `manager_to`
- `unique_content_id` <- `xmp_identifier`
- `usage_guidelines` <- `instructions`
- `usage_instructions` <- `usagetext`
- `usage_permissions` <- `license_right`

### ULTRA_IPTC_XMP_FIELDS
- `client_project_identifier` <- `job_reference`
- `content_creator_contact` <- `provider_identification`
- `copyrighted_public_domain` <- `copyright_status`
- `digital_image_capture_type` <- `digital_source_type`
- `editorial_label_tags` <- `xmp_labels`
- `editorial_rating_score` <- `xmp_rating`
- `hierarchical_keyword_structure` <- `xmp_nested_keywords`
- `legal_copyright_statement` <- `copyright_notice`
- `license_information_link` <- `license_url`
- `media_format_classification` <- `xmp_format`
- `online_rights_statement` <- `web_statement`
- `scene_recognition_category` <- `scene_type`
- `service_provider_info` <- `service_identification`
- `software_created_with` <- `xmp_creator_tool`
- `unique_content_identifier` <- `xmp_identifier`
- `usage_instructions_notes` <- `instructions`
- `usage_license_terms` <- `rights_usage_terms`
- `xmp_content_label` <- `xmp_label`
- `xmp_creation_timestamp` <- `xmp_create_date`
- `xmp_last_modified` <- `xmp_modify_date`
- `xmp_metadata_timestamp` <- `xmp_metadata_date`

### XMP_ADOBE_STOCK
- `stock_asset_id` <- `Xmp.adobe stock.AssetId`
- `stock_creation_date` <- `Xmp.adobe stock.CreationDate`
- `stock_modification_date` <- `Xmp.adobe stock.ModificationDate`
- `stock_preview_url` <- `Xmp.adobe stock.PreviewUrl`
- `stock_url` <- `Xmp.adobe stock.Url`

### XMP_CREATOR_CONTACT
- `contact_address` <- `Xmp.creatorContactInfo.CiAdrExtadr`
- `contact_city` <- `Xmp.creatorContactInfo.CiAdrCity`
- `contact_country` <- `Xmp.creatorContactInfo.CiAdrCtry`
- `contact_email` <- `Xmp.creatorContactInfo.CiEmailWork`
- `contact_phone` <- `Xmp.creatorContactInfo.CiTelWork`
- `contact_postal_code` <- `Xmp.creatorContactInfo.CiAdrPcode`
- `contact_region` <- `Xmp.creatorContactInfo.CiAdrRegion`
- `contact_url` <- `Xmp.creatorContactInfo.CiUrlWork`

### XMP_DC_PREFS_FIELDS
- `edit_history` <- `Xmp.dcprefs.History`
- `rating` <- `Xmp.dcprefs.Rating`
- `web_statement` <- `Xmp.dcprefs.WebStatement`

### XMP_DUBLIN_CORE_FIELDS
- `abstract` <- `Xmp.dc.abstract`
- `audience` <- `Xmp.dc.audience`
- `contributor` <- `Xmp.dc.contributor`
- `coverage` <- `Xmp.dc.coverage`
- `creator` <- `Xmp.dc.creator`
- `date` <- `Xmp.dc.date`
- `description` <- `Xmp.dc.description`
- `extent` <- `Xmp.dc.extent`
- `format` <- `Xmp.dc.format`
- `identifier` <- `Xmp.dc.identifier`
- `language` <- `Xmp.dc.language`
- `medium` <- `Xmp.dc.medium`
- `provenance` <- `Xmp.dc.provenance`
- `publisher` <- `Xmp.dc.publisher`
- `relation` <- `Xmp.dc.relation`
- `rights` <- `Xmp.dc.rights`
- `rights_holder` <- `Xmp.dc.rightsHolder`
- `source` <- `Xmp.dc.source`
- `subject` <- `Xmp.dc.subject`
- `table_of_contents` <- `Xmp.dc.tableOfContents`
- `title` <- `Xmp.dc.title`
- `type` <- `Xmp.dc.type`

### XMP_PHOTOSHOP_FIELDS
- `animated` <- `Xmp.photoshop.Animated`
- `authors_position` <- `Xmp.photoshop.AuthorsPosition`
- `caption_writer` <- `Xmp.photoshop.CaptionWriter`
- `category` <- `Xmp.photoshop.Category`
- `city` <- `Xmp.photoshop.City`
- `color_mode` <- `Xmp.photoshop.ColorMode`
- `country` <- `Xmp.photoshop.Country`
- `credit` <- `Xmp.photoshop.Credit`
- `date_created` <- `Xmp.photoshop.DateCreated`
- `headline` <- `Xmp.photoshop.Headline`
- `icc_profile` <- `Xmp.photoshop.ICCProfile`
- `instructions` <- `Xmp.photoshop.Instructions`
- `photoshop_version` <- `Xmp.photoshop.Version`
- `source` <- `Xmp.photoshop.Source`
- `state` <- `Xmp.photoshop.State`
- `supplemental_categories` <- `Xmp.photoshop.SupplementalCategories`
- `timing` <- `Xmp.photoshop.Timing`
- `transmission_reference` <- `Xmp.photoshop.TransmissionReference`
- `urgency` <- `Xmp.photoshop.Urgency`

### XMP_RIGHTS_MANAGEMENT
- `rights_adobe` <- `Xmp.xmpRights.Adobe`
- `rights_certificate` <- `Xmp.xmpRights.Certificate`
- `rights_marked` <- `Xmp.xmpRights.Marked`
- `rights_usage_terms` <- `Xmp.xmpRights.UsageTerms`
- `rights_web_statement` <- `Xmp.xmpRights.WebStatement`


## mobile_metadata
Source file: `server/extractor/modules/mobile_metadata.py`
### ANDROID_TAGS
- `android_capture_fps` <- `Android_CaptureFPS`
- `android_depth_far` <- `Android_DepthFar`
- `android_depth_format` <- `Android_DepthFormat`
- `android_depth_mime_type` <- `Android_DepthMimeType`
- `android_depth_near` <- `Android_DepthNear`
- `android_hdr_mode` <- `Android_HDR_Mode`
- `android_manufacturer` <- `Android_Manufacturer`
- `android_model` <- `Android_Model`
- `android_motion_photo` <- `Android_MotionPhoto`
- `android_motion_photo_timestamp` <- `Android_MotionPhotoPresentationTimestampUs`
- `android_motion_photo_version` <- `Android_MotionPhotoVersion`
- `android_night_sight` <- `Android_NightSight`
- `android_photo_booth_setting` <- `Android_PhotoBoothSetting`
- `android_portrait_blur_strength` <- `Android_PortraitBlurStrength`
- `android_portrait_mode` <- `Android_PortraitMode`
- `android_top_shot` <- `Android_TopShot`
- `google_depth_map` <- `Google_DepthMap`
- `google_device_name` <- `Google_DeviceName`
- `google_image_metadata` <- `Google_Image`

### APPLE_MAKERNOTE_TAGS
- `apple_acceleration_vector` <- `Apple_Acceleration_Vector`
- `apple_af_confidence` <- `Apple_AFConfidence`
- `apple_burst_uuid` <- `Apple_BurstUUID`
- `apple_camera_orientation` <- `Apple_CameraOrientation`
- `apple_cinematic_video_enabled` <- `Apple_CinematicVideoEnabled`
- `apple_color_matrix` <- `Apple_ColorMatrix`
- `apple_content_identifier` <- `Apple_ContentIdentifier`
- `apple_depth_data` <- `Apple_DepthData`
- `apple_detected_faces` <- `Apple_DetectedFaces`
- `apple_focus_distance_range` <- `Apple_FocusDistanceRange`
- `apple_front_facing_camera` <- `Apple_FrontFacingCamera`
- `apple_gps_horizontal_error` <- `Apple_GPSHPositioningError`
- `apple_hdr_image_type` <- `Apple_HDR_ImageType`
- `apple_image_capture_type` <- `Apple_ImageCaptureType`
- `apple_image_unique_id` <- `Apple_ImageUniqueID`
- `apple_live_photo` <- `Apple_LivePhoto`
- `apple_live_photo_video_index` <- `Apple_LivePhotoVideoIndex`
- `apple_maker_data` <- `Apple_MakerApple`
- `apple_media_group_uuid` <- `Apple_MediaGroupUUID`
- `apple_photo_identifier` <- `Apple_PhotoIdentifier`
- `apple_portrait_effect_strength` <- `Apple_PortraitEffectStrength`
- `apple_portrait_lighting_effect_strength` <- `Apple_PortraitLightingEffectStrength`
- `apple_pro_raw` <- `Apple_ProRAW`
- `apple_region_info` <- `Apple_RegionInfo`
- `apple_runtime_epoch` <- `Apple_RunTime_Epoch`
- `apple_runtime_flags` <- `Apple_RunTime_Flags`
- `apple_runtime_scale` <- `Apple_RunTime_Scale`
- `apple_runtime_value` <- `Apple_RunTime_Value`
- `apple_scene_flags` <- `Apple_SceneFlags`
- `apple_semantic_style` <- `Apple_SemanticStyle`
- `apple_semantic_style_preset` <- `Apple_SemanticStylePreset`
- `apple_semantic_style_rendering_version` <- `Apple_SemanticStyleRenderingVersion`
- `apple_smart_hdr` <- `Apple_SmartHDR`
- `apple_temporal_scalability_enabled` <- `Apple_TemporalScalabilityEnabled`
- `apple_video_metadata` <- `Apple_VideoMetadata`

### GCAMERA_XMP_TAGS
- `android_capture_mode` <- `CaptureMode`
- `android_hdr_plus_enabled` <- `HdrPlusEnabled`
- `android_micro_video` <- `MicroVideo`
- `android_micro_video_duration` <- `MicroVideoPresentationDurationUs`
- `android_micro_video_offset` <- `MicroVideoOffset`
- `android_micro_video_timestamp` <- `MicroVideoPresentationTimestampUs`
- `android_micro_video_version` <- `MicroVideoVersion`
- `android_motion_photo` <- `MotionPhoto`
- `android_motion_photo_timestamp` <- `MotionPhotoPresentationTimestampUs`
- `android_motion_photo_version` <- `MotionPhotoVersion`
- `android_night_sight` <- `NightSight`
- `android_portrait_blur_strength` <- `PortraitBlurStrength`
- `android_portrait_mode` <- `PortraitMode`
- `android_top_shot` <- `TopShot`

### GDEPTH_XMP_TAGS
- `android_depth_confidence` <- `Confidence`
- `android_depth_data` <- `Data`
- `android_depth_far` <- `Far`
- `android_depth_format` <- `Format`
- `android_depth_mime_type` <- `Mime`
- `android_depth_near` <- `Near`

### GIMAGE_XMP_TAGS
- `android_image_data` <- `Data`
- `android_image_mime_type` <- `Mime`

### GPANO_XMP_TAGS
- `android_panorama_cropped_height` <- `CroppedAreaImageHeightPixels`
- `android_panorama_cropped_left` <- `CroppedAreaLeftPixels`
- `android_panorama_cropped_top` <- `CroppedAreaTopPixels`
- `android_panorama_cropped_width` <- `CroppedAreaImageWidthPixels`
- `android_panorama_full_height` <- `FullPanoHeightPixels`
- `android_panorama_full_width` <- `FullPanoWidthPixels`
- `android_panorama_heading` <- `InitialViewHeadingDegrees`
- `android_panorama_pitch` <- `InitialViewPitchDegrees`
- `android_panorama_projection_type` <- `ProjectionType`
- `android_panorama_roll` <- `InitialViewRollDegrees`
- `android_panorama_viewer` <- `UsePanoramaViewer`

### HUAWEI_TAGS
- `huawei_ae_mode` <- `Huawei_AE_Mode`
- `huawei_af_area_mode` <- `Huawei_AF_Area_Mode`
- `huawei_af_mode` <- `Huawei_AFMode`
- `huawei_anti_banding` <- `Huawei_AntiBanding`
- `huawei_color_correction_mode` <- `Huawei_ColorCorrectionMode`
- `huawei_engineer_mode` <- `Huawei_EngineerMode`
- `huawei_exposure_time` <- `Huawei_ExposureTime`
- `huawei_f_number` <- `Huawei_FNumber`
- `huawei_face_detect_mode` <- `Huawei_FaceDetectMode`
- `huawei_flash_mode` <- `Huawei_FlashMode`
- `huawei_focus_mode` <- `Huawei_FocusMode`
- `huawei_image_type` <- `Huawei_ImageType`
- `huawei_iso` <- `Huawei_ISO`
- `huawei_lens_type` <- `Huawei_LensType`
- `huawei_noise_reduction_mode` <- `Huawei_NoiseReductionMode`
- `huawei_picture_size` <- `Huawei_PictureSize`
- `huawei_rec_mode` <- `Huawei_RecMode`
- `huawei_wb_mode` <- `Huawei_WB_Mode`

### SAMSUNG_TAGS
- `samsung_custom_rendered` <- `Samsung_CustomRendered`
- `samsung_device_name` <- `Samsung_DeviceName`
- `samsung_exposure_program` <- `Samsung_ExposureProgram`
- `samsung_exposure_time` <- `Samsung_ExposureTime`
- `samsung_f_number` <- `Samsung_FNumber`
- `samsung_flash` <- `Samsung_Flash`
- `samsung_focal_length` <- `Samsung_FocalLength`
- `samsung_gps_latitude` <- `Samsung_GPSLatitude`
- `samsung_gps_longitude` <- `Samsung_GPSLongitude`
- `samsung_height` <- `Samsung_Height`
- `samsung_image_type` <- `Samsung_ImageType`
- `samsung_iso_speed_ratings` <- `Samsung_ISOSpeedRatings`
- `samsung_orientation` <- `Samsung_Orientation`
- `samsung_processing` <- `Samsung_Processing`
- `samsung_white_balance` <- `Samsung_WhiteBalance`
- `samsung_width` <- `Samsung_Width`

### XIAOMI_TAGS
- `xiaomi_contrast` <- `Xiaomi_Contrast`
- `xiaomi_exposure_bias` <- `Xiaomi_ExposureBias`
- `xiaomi_exposure_time` <- `Xiaomi_ExposureTime`
- `xiaomi_f_number` <- `Xiaomi_FNumber`
- `xiaomi_flash_mode` <- `Xiaomi_FlashMode`
- `xiaomi_focal_length` <- `Xiaomi_FocalLength`
- `xiaomi_image_type` <- `Xiaomi_ImageType`
- `xiaomi_iso` <- `Xiaomi_ISO`
- `xiaomi_metering_mode` <- `Xiaomi_MeteringMode`
- `xiaomi_saturation` <- `Xiaomi_Saturation`
- `xiaomi_sharpness` <- `Xiaomi_Sharpness`
- `xiaomi_subject_distance` <- `Xiaomi_SubjectDistance`
- `xiaomi_white_balance` <- `Xiaomi_WhiteBalance`


## metadata_engine.image
Source file: `server/extractor/metadata_engine.py` (function `extract_image_properties`)
Fields returned by `extract_image_properties`:
- `width`
- `height`
- `format`
- `mode`
- `dpi`
- `bits_per_pixel`
- `color_palette`
- `animation`
- `frames`
- `icc_profile`
- `is_animated`
- `n_frames`
- `has_icc_profile`
- `has_transparency`
- `icc_profile_details`
- `color_accuracy`

## metadata_engine.filesystem
Source file: `server/extractor/metadata_engine.py` (function `extract_filesystem_metadata`)
Fields returned by `extract_filesystem_metadata`:
- `size_bytes`
- `size_human`
- `created`
- `modified`
- `accessed`
- `changed`
- `permissions_octal`
- `permissions_human`
- `owner`
- `owner_uid`
- `group`
- `group_gid`
- `inode`
- `device`
- `hard_links`
- `file_type`
- `is_hidden`

## metadata_engine.hashes
Source file: `server/extractor/metadata_engine.py` (function `extract_file_hashes`) and `server/extractor/modules/hashes.py`
Fields returned by `extract_file_hashes`:
- `md5`
- `sha256`
- `sha1`
- `crc32`

## metadata_engine.exiftool_categories
Source file: `server/extractor/metadata_engine.py` (function `categorize_exiftool_output`)
Notes: exiftool tag keys are dynamic at runtime. Category buckets include: `exif`, `gps`, `composite`, `exif_ifd`, `iptc`, `xmp`, `xmp_namespaces`, `image_container`, `icc_profile`, `interoperability`, `thumbnail_metadata`, `makernote`.


## modules.images (plugin)
Source file: `server/extractor/modules/images.py`
Fields returned by `extract_image_properties` (plugin path):
- `format`
- `mode`
- `width`
- `height`
- `has_transparency`
- `is_animated`
- `n_frames`
- `dpi_x`
- `dpi_y`
- `has_icc_profile`
- `icc_profile_size`
- `aspect_ratio`
- `aspect_ratio_string`
- `megapixels`
- `bits_per_pixel`
- `exif_orientation`

Fields returned by `extract_thumbnail_properties` (plugin path):
- `has_embedded`
- `width`
- `height`
- `format`
- `max_size`

## modules.perceptual_hashes (plugin)
Source file: `server/extractor/modules/perceptual_hashes.py`
Fields returned by `extract_perceptual_hashes` (plugin path):
- `perceptual_hashes` (object) with keys:
  - `phash`
  - `phash_hex`
  - `phash_b64`
  - `dhash`
  - `dhash_hex`
  - `ahash`
  - `ahash_hex`
  - `whash`
  - `whash_hex`
  - `blockhash`
  - `blockhash_hex`
  - `phash_bits`
  - `dhash_bits`
  - `ahash_bits`
  - `whash_bits`
  - `blockhash_bits`
- `hash_comparison` (object)
- `fields_extracted`


## modules.colors (plugin)
Source file: `server/extractor/modules/colors.py`
Fields returned by `extract_color_palette` (plugin path):
- `dominant_colors[]: {hex, rgb, percentage}`
- `color_count`
- `extraction_method`
- `image_size: {width, height}`

Fields returned by `extract_color_histograms` (plugin path):
- `histogram_rgb: {red, green, blue}`
- `histogram_luminance`
- `clipping: {red_highlights_pct, green_highlights_pct, blue_highlights_pct, red_shadows_pct, green_shadows_pct, blue_shadows_pct}`
- `tone_distribution: {shadows_pct, midtones_pct, highlights_pct}`
- `image_dimensions: {width, height}`

Fields returned by `calculate_color_temperature` (plugin path):
- `average_rgb`
- `temperature`
- `color_balance`
- `saturation_pct`

## modules.quality (plugin)
Source file: `server/extractor/modules/quality.py`
Fields returned by `extract_quality_metrics` (plugin path):
- `sharpness_score`
- `is_blurry`
- `blur_type`
- `noise_level`
- `noise_assessment`
- `mean_brightness`
- `brightness_assessment`
- `contrast`
- `contrast_assessment`
- `dynamic_range`
- `exposure`
- `histogram_analysis: {shadows_pct, highlights_pct}`
- `image_dimensions: {width, height}`

Fields returned by `detect_blur` (plugin path):
- `is_blurry`
- `sharpness_score`
- `threshold`
- `blur_type`

