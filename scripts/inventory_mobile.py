#!/usr/bin/env python3
"""Mobile Format Metadata Fields Inventory

This script documents metadata fields available in mobile application formats
including IPA (iOS), APK/AAB (Android), and other mobile app formats.

Reference:
- Apple PKZIP/APFS documentation
- Google Play AAB specification
- Android APK format
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


MOBILE_INVENTORY = {
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "source": "Apple IPA, Android APK/AAB, Mobile App Standards",
    "description": "Mobile application metadata fields for iOS and Android",
    "categories": {
        "ios_ipa": {
            "description": "iOS IPA (App Store) metadata fields",
            "fields": [
                "CFBundleName", "CFBundleDisplayName", "CFBundleIdentifier",
                "CFBundleVersion", "CFBundleShortVersionString", "CFBundlePackageType",
                "CFBundleExecutable", "CFBundleSignature", "LSRequiresIPhoneOS",
                "UILaunchStoryboardName", "UIMainStoryboardFile", "UIRequiredDeviceCapabilities",
                "UISupportedInterfaceOrientations", "UISupportedInterfaceOrientations~ipad",
                "UIApplicationSupportsIndirectInputEvents", "UIStatusBarStyle",
                "UIStatusBarHidden", "UIViewControllerBasedStatusBarAppearance",
                "UILaunchImage", "UILaunchImageMinimumOSVersion", "UILaunchImageFile",
                "UIPrerenderedIcon", "CFBundleIconFiles", "CFBundleIcons",
                "CFBundlePrimaryIcon", "CFBundleIcons~ipad", "CFBundleDocumentTypes",
                "UIFileSharingEnabled", "UISupportsDocumentBrowser", "LSSupportsOpeningDocumentsInPlace",
                "ITSAppUsesNonExemptEncryption", "ITSEncryptionExportComplianceCode",
                "NSAppTransportSecurity", "NSAllowsArbitraryLoads", "NSAllowsArbitraryLoadsInWebContent",
                "NSAllowsLocalNetworking", "NSTemporaryDirectoryUsageDescription",
                "NSPhotoLibraryUsageDescription", "NSPhotoLibraryAddUsageDescription",
                "NSCameraUsageDescription", "NSMicrophoneUsageDescription",
                "NSContactsUsageDescription", "NSCalendarUsageDescription",
                "NSRemindersUsageDescription", "NSLocationWhenInUseUsageDescription",
                "NSLocationAlwaysUsageDescription", "NSLocationAlwaysAndWhenInUseUsageDescription",
                "NSBackgroundModes", "UIBackgroundModes", "BGTaskSchedulerPermittedIdentifiers",
                "UIBackgroundSession", "UIBackgroundModes", "UIApplicationSupportsSnapshots",
                "NSUserActivityTypes", "NSUserTrackingUsageDescription",
                "NSFaceIDUsageDescription", "NSHealthShareUsageDescription",
                "NSHealthUpdateUsageDescription", "NSMotionUsageDescription",
                "NSSiriUsageDescription", "NSHomeKitUsageDescription",
                "NSBluetoothAlwaysUsageDescription", "NSBluetoothPeripheralUsageDescription",
                "NSAppleMusicUsageDescription", "NSNetworkUsageDescription",
                "NSLocalNetworkUsageDescription", "NSMulticastUsageDescription",
                "BGTaskSchedulerPermittedIdentifiers", "UIBackgroundModes",
                "com.apple.developer.healthkit", "com.apple.developer.healthkit.access",
                "com.apple.developer.healthkit.background-delivery",
                "com.apple.developer.pass-type-identifiers", "com.apple.developer.in-app-payments",
                "com.apple.developer.associated-domains", "application-identifier",
                "com.apple.developer.team-identifier", "aps-environment",
                "beta-reports-active", "build-version", "bundle-version",
                "bundle-identifier", "bundle-name", "com.apple.security.application-groups",
                "com.apple.developer.ubiquity-kvstore-identifier",
                "com.apple.developer.siri", "com.apple.developer.restricted-button",
                "com.apple.developer.system-capabilities", "com.apple.developer.networking.vpn",
                "com.apple.developer.networking.multicast", "com.apple.developer.networking.wifi-info",
                "com.apple.developer.nfc.readersession.formats",
                "NFCReaderUsageDescription", "com.apple.developer.nfc.tag-reading",
                "ISEnableOrder", "ISStartOrder", "ISUpdateOrder", "ISInstallOrder",
                "CFBundleDevelopmentRegion", "CFBundleInfoDictionaryVersion",
                "CFBundlePackageType", "CFBundleShortVersionString", "CFBundleVersion",
                "CFAppleScriptEnabled", "NSHumanReadableCopyright", "NSMainNibFile",
                "NSPrincipalClass", "UIRequiresFullScreen", "UIRequiresPersistentWiFi",
                "UIStatusBarStyle", "UILaunchOrientation", "UIMinimumIntersectingEdgeInsets",
            ],
            "count": 102,
            "reference": "Apple iOS Info.plist Keys"
        },
        "android_apk": {
            "description": "Android APK manifest and metadata",
            "fields": [
                "package", "versionCode", "versionName", "versionMajor",
                "compileSdkVersion", "compileSdkVersionCodename", "minSdkVersion",
                "targetSdkVersion", "maxSdkVersion", "previewSdkVersion",
                "installLocation", "storageUuid", "isFeatureSplit",
                "baseApkDataDir", "baseApkManifestLocation", "coreLibrary",
                "requiredSplit", "requiredUnclaimedSplit", "splitName",
                "splitId", "splitRoot", "isSplitRequired", "minExtensionVersion",
                "enforcePackageIntegrity", "enforceMinSdkVersion", "hashCode",
                "signatureSchemaVersion", "apkSigningVersion", "mSignatureVersion",
                "minAppVersionCode", "minAppVersionName", "appMetadata",
                "sharedUserId", "sharedUserLabel", "process", "taskAffinity",
                "launchMode", "theme", "screenOrientation", "configChanges",
                "windowSoftInputMode", "uiOptions", "label", "icon", "logo",
                "allowBackup", "backupAgent", "fullBackupContent", "fullBackupOnly",
                "dataExtractionRules", "hardwareAccelerated", "largeHeap",
                "multiprocess", "debuggable", "debuggableText", "factoryTest",
                "resizeable", "anyDensity", "normalScreens", "smallScreens",
                "largeScreens", "xlargeScreens", "required", "supportsRtl",
                "maxAspectRatio", "minAspectRatio", "resizeableActivity",
                "lockedActivityOrientation", "immersive", "allowEmbedded",
                "autoRemoveFromRecents", "showForAllUsers", "installLocation",
                "hidden", "excludeFromRecents", "excludedFromRecents",
                "singleUser", "persistent", "clearTaskOnLaunch", "alwaysRetainTaskState",
                "finishOnTaskLaunch", "skipCurrentTask", "noHistory",
                "windowFullscreen", "titleVisible", "titleNotIncluded",
                "action", "category", "data", "scheme", "host", "port", "path",
                "pathPrefix", "pathPattern", "pathAdvancedPattern", "mimeTypePattern",
                "ssp", "sspPrefix", "sspPattern", "schemeSpecificPart", "actionView",
                "actionEdit", "actionSend", "actionViewEdit", "actionSendMultiple",
                "actionMain", "actionViewActivity", "actionDefault",
                "actionDefault", "component", "intentFilter", "priority",
                "autoVerify", "exported", "permission", "mimeGroup",
                "categoryDefault", "categoryBrowser", "categoryLauncher",
                "categoryHome", "categoryPreferences", "categoryALternative",
                "categorySelection", "categorySecondarysharedUserId",
                "grantUriPermissions", "permissionUriPattern", "exportedUriPattern",
                "readPermission", "writePermission", "readPermission", "writePermission",
                "forwardLockPermissions", "invalidatePermissions", "visibleToInstantApps",
                "turnOnScreen", "keepScreenOn", "usesCleartextTraffic",
                "usesLibssl", "usesCdd", "usesSdkVersion", "usesFeature",
                "usesGlEsVersion", "usesConfiguration", "usesPermission",
                "usesPermissionSdk23", "usesExternalStorage", "signature",
                "protectionLevel", "basePermission", "permissionGroup",
                "permGroupDef", "signatureOrSystem", "privileged", "signature",
                "normal", "dangerous", "internal", "appop", "instant", "runtime",
                "pre23", "installer", "verifier", "preinstalled", "setup",
                "instantapp", "vendorPrivileged", "OEM", "VENDOR_PRIVILEGED",
                "text", "style", "color", "integer", "bool", "dimen", "array",
                "string-array", "int-array", "typed-array", "plurals",
                "localized", "quantity", "other", "zero", "one", "two",
                "few", "many", "format", "encoding", "collation", "caseOrder",
            ],
            "count": 138,
            "reference": "AndroidManifest.xml / AAPT"
        },
        "google_play_aab": {
            "description": "Google Play App Bundle (AAB) metadata",
            "fields": [
                "base", "split", "config", "language", "density", "abi",
                "screenDensity", "screenLayout", "smallestScreenSize", "version",
                "baseCode", "splitCode", "moduleType", "moduleVersion", "bundleVersion",
                "assetVersion", "targetSandboxVersion", "targetSandboxUpdate",
                "bundled", "uncompressed", "compressed", "directory", "metadata",
                "signature", "encryption", "compression", "optimization",
                "resourceConfig", "abiConfig", "languageConfig", "screenConfig",
                "densityConfig", "featureConfig", "onDemand", "instant",
                "delivery", "installTime", "fastFollow", "PreL", "L",
                "PreL", "M", "N", "O", "P", "Q", "R", "S", "T", "baseConfig",
                "deviceTier", "deviceGroup", "screenWidth", "screenHeight",
                "glExtension", "featureGroup", "feature", "requiredFeature",
                "usesFeature", "optionalFeature", "fallbackFor", "replaceOf",
                "assetModule", "resourceModule", "nativeModule", "dexModule",
                "unknownModule", "repackaged", "standalone", "merged",
                "dedupe", "mergeReport", "moduleGraph", "rootModule", "dependency",
                "depModule", "depConfig", "provided", "annotationProcessor",
                "kapt", "kcp", "ksp", "annotationProcessorPath", "annotationProcessorClass",
                "kaptIncremental", "kaptCorrectErrorTypes", "resourceShrinker",
                "minifyEnabled", "shrinkResources", "proguardFiles", "consumerProguardRules",
                "proguardFile", "proguardRules", "multiDexEnabled", "multiDexKeepFile",
                "multiDexKeepProguard", "debugSigning", "releaseSigning",
                "signingConfig", "keyAlias", "keyPassword", "storeFile",
                "storePassword", "v1SigningEnabled", "v2SigningEnabled",
                "v3SigningEnabled", "v4SigningEnabled", "v1Scheme", "v2Scheme",
                "v3Scheme", "v4Scheme", "apkSigner", "apksigner", "signingKeyVersion",
                "keyAlgorithm", "keySize", "validity", "subject", "issuer",
                "serialNumber", "thumbprint", "sha256", "sha1", "md5",
                "certificateChain", "timestamp", "verified", "validation",
                "certificates", "lineage", "rotation", "apkSignatureBlock",
                "signingBlock", "signingBlockOffset", "signingBlockSize",
                "signer", "proofOfOrigin", "proofOfOriginLayer", "proofOfSigner",
                "appMetadata", "packageName", "versionCode", "versionName",
                "minSdkVersion", "targetSdkVersion", "extractNativeLibs",
                "isCoreApp", "useEmbeddedDex", "useEmbeddedNativeLibs",
                "useAppLibs", "allowBackup", "hasDirectBootAware", "defaultToDeviceProtectedStorage",
                "directBootAware", "requestLegacyExternalStorage", "category",
                "defaultCategory", "role", "defaultRole", "appRoles",
                "appRoleManager", "roleManager", "roles", "roleHolder",
            ],
            "count": 132,
            "reference": "Google Play App Bundle"
        },
        "android_permissions": {
            "description": "Android permission definitions and attributes",
            "fields": [
                "android.permission.READ_CALENDAR", "android.permission.WRITE_CALENDAR",
                "android.permission.CAMERA", "android.permission.READ_CONTACTS",
                "android.permission.WRITE_CONTACTS", "android.permission.GET_ACCOUNTS",
                "android.permission.ACCESS_FINE_LOCATION", "android.permission.ACCESS_COARSE_LOCATION",
                "android.permission.ACCESS_BACKGROUND_LOCATION", "android.permission.RECORD_AUDIO",
                "android.permission.READ_PHONE_STATE", "android.permission.READ_PHONE_NUMBERS",
                "android.permission.CALL_PHONE", "android.permission.ANSWER_PHONE_CALLS",
                "android.permission.READ_CALL_LOG", "android.permission.WRITE_CALL_LOG",
                "android.permission.ADD_VOICEMAIL", "android.permission.USE_SIP",
                "android.permission.PROCESS_OUTGOING_CALLS", "android.permission.BODY_SENSORS",
                "android.permission.ACTIVITY_RECOGNITION", "android.permission.SEND_SMS",
                "android.permission.RECEIVE_SMS", "android.permission.READ_SMS",
                "android.permission.RECEIVE_WAP_PUSH", "android.permission.RECEIVE_MMS",
                "android.permission.READ_EXTERNAL_STORAGE", "android.permission.WRITE_EXTERNAL_STORAGE",
                "android.permission.READ_MEDIA_IMAGES", "android.permission.READ_MEDIA_VIDEO",
                "android.permission.READ_MEDIA_AUDIO", "android.permission.POST_NOTIFICATIONS",
                "android.permission.USE_BIOMETRIC", "android.permission.USE_FINGERPRINT",
                "android.permission.REQUEST_INSTALL_PACKAGES", "android.permission.REQUEST_DELETE_PACKAGES",
                "android.permission.BIND_ACCESSIBILITY_SERVICE", "android.permission.BIND_AUTOFILL_SERVICE",
                "android.permission.BIND_CARRIER_MESSAGING_SERVICE", "android.permission.BIND_CARRIER_SERVICES",
                "android.permission.BIND_CHOOSER_TARGET_SERVICE", "android.permission.BIND_CONDITION_PROVIDER_SERVICE",
                "android.permission.BIND_CONTROLS", "android.permission.BIND_DEVICE_ADMIN",
                "android.permission.BIND_DREAM_SERVICE", "android.permission.BIND_INCALL_SERVICE",
                "android.permission.BIND_INPUT_METHOD", "android.permission.BIND_MIDI_DEVICE_SERVICE",
                "android.permission.BIND_NFC_SERVICE", "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE",
                "android.permission.BIND_PRINT_SERVICE", "android.permission.BIND_QUICK_SETTINGS_TILE",
                "android.permission.BIND_REMOTEVIEWS", "android.permission.BIND_SCREENING_SERVICE",
                "android.permission.BIND_TELECOM_CONNECTION_SERVICE", "android.permission.BIND_TEXT_SERVICE",
                "android.permission.BIND_TV_INPUT", "android.permission.BIND_VOICE_INTERACTION_SERVICE",
                "android.permission.BIND_VPN_SERVICE", "android.permission.BIND_VR_LISTENER_SERVICE",
                "android.permission.BIND_WINDOW_MANAGER", "android.permission.CAMERA",
                "android.permission.INTERNET", "android.permission.ACCESS_NETWORK_STATE",
                "android.permission.ACCESS_WIFI_STATE", "android.permission.CHANGE_WIFI_STATE",
                "android.permission.CHANGE_WIFI_MULTICAST_STATE", "android.permission.BLUETOOTH",
                "android.permission.BLUETOOTH_ADMIN", "android.permission.BLUETOOTH_CONNECT",
                "android.permission.BLUETOOTH_SCAN", "android.permission.BLUETOOTH_ADVERTISE",
                "android.permission.NEARBY_WIFI_DEVICES", "android.permission.CHANGE_NETWORK_STATE",
                "android.permission.WAKE_LOCK", "android.permission.RECEIVE_BOOT_COMPLETED",
                "android.permission.WRITE_SETTINGS", "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS",
                "android.permission.VIBRATE", "android.permission.REORDER_TASKS",
                "android.permission.START_FOREGROUND_SERVICE", "android.permission.START_BACKGROUND_SERVICE",
                "android.permission.CALL_COMPANION_APP", "android.permission.CAMERA",
                "android.permission.RECORD_AUDIO", "android.permission.READ_MEDIA_IMAGES",
                "android.permission.READ_MEDIA_VIDEO", "android.permission.READ_MEDIA_AUDIO",
                "android.permission.POST_NOTIFICATIONS", "android.permission.NEARBY_WIFI_DEVICES",
                "android.permission.USE_BIOMETRIC", "android.permission.USE_FINGERPRINT",
                "android.permission.USE_OTP_CREDENTIALS", "android.permission.USE_BIOMETRIC_PRIVILEGED",
                "android.permission.MANAGE_USB", "android.permission.HIGH_SAMPLING_RATE_SENSORS",
                "android.permission.UWB_RANGING", "android.permission.FOREGROUND_SERVICE_CAMERA",
                "android.permission.FOREGROUND_SERVICE_MICROPHONE", "android.permission.FOREGROUND_SERVICE_LOCATION",
                "android.permission.FOREGROUND_SERVICE_CONNECTED_DEVICE",
                "android.permission.FOREGROUND_SERVICE_DATA_SYNC", "android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK",
                "android.permission.FOREGROUND_SERVICE_PHONE_CALL", "android.permission.FOREGROUND_SERVICE_REMOTE_MESSAGING",
                "android.permission.FOREGROUND_SERVICE_HEALTH", "android.permission.FOREGROUND_SERVICE_SYSTEM_EXHIBITED",
                "android.permission.FOREGROUND_SERVICE_SPECIAL_USE",
            ],
            "count": 95,
            "reference": "Android Permission Constants"
        },
        "ios_capabilities": {
            "description": "iOS App Capabilities and Entitlements",
            "fields": [
                "com.apple.developer.associated-domains", "com.apple.developer.automatic-asset-codes.v2",
                "com.apple.developer.coreservices.flash", "com.apple.developer.deviceinformation.read",
                "com.apple.developer.family-controls", "com.apple.developer.healthkit",
                "com.apple.developer.healthkit.access", "com.apple.developer.healthkit.background-delivery",
                "com.apple.developer.healthkit.rehabilitate-exercise", "com.apple.developer.healthkit.smarting",
                "com.apple.developer.homekit", "com.apple.developer.in-app-payments",
                "com.apple.developer.iCloud", "com.apple.developer.icloud-container-identifiers",
                "com.apple.developer.icloud-services", "com.apple.developer.icloud-container-application-identifiers",
                "com.apple.developer.icloud-quota", "com.apple.developer.icloud-additional-services",
                "com.apple.developer.networking.Multicast", "com.apple.developer.networking.VPN",
                "com.apple.developer.networking.wifi-info", "com.apple.developer.pass-type-identifiers",
                "com.apple.developer.push-notification", "com.apple.developer.siri",
                "com.apple.developer.usernotifications.time-sensitive",
                "com.apple.developer.usernotifications.filtering",
                "com.apple.developer.usernotifications.reactive",
                "com.apple.developer.videotoolbox.allow-encoder", "com.apple.developer.videotoolbox.allow-decoder",
                "com.apple.developer.avfoundation.multitask-camera-access",
                "com.apple.developer.nfc.tag-reading", "com.apple.developer.nfc.readersession.formats",
                "com.apple.developer.nfc.encryption-status", "com.apple.developer.nfc.definitions",
                "com.apple.security.application-groups", "com.apple.developer.associated-domains",
                "com.apple.developer.ubiquity-kvstore-identifier", "com.apple.developer.sbbt",
                "com.apple.developer.applesignin", "com.apple.developer.tvos.supported",
                "com.apple.developer.wallet", "com.apple.developer.pass-type-identifiers",
                "com.apple.developer.in-app-payments", "com.apple.developer.Maps",
                "com.apple.developer.maps", "com.apple.developer.location.lpa",
                "com.apple.developer.location.distancefilter", "com.apple.developer.location.core-location",
                "com.apple.developer.location.always.foreground", "com.apple.developer.location.always",
                "com.apple.developer.location.alwaysandwheninuse", "com.apple.developer.location.wheninuse",
                "com.apple.developer.bluetooth.access", "com.apple.developer.bluetooth.le",
                "com.apple.developer.bluetooth.central", "com.apple.developer.bluetooth.peripheral",
                "com.apple.developer.bluetooth.public", "com.apple.developer.keychain.groups",
                "com.apple.developer.keychain-services", "com.apple.developer.keychain-share-access",
                "com.apple.developer.networking.HotspotConfiguration", "com.apple.developer.networking.Multicast",
                "com.apple.developer.networking.vpn.api", "com.apple.developer.SafariExtension",
                "com.apple.developer.SafariExtensionContentBlocker", "com.apple.developer.SafariWebExtension",
                "com.apple.developer.fileprovider", "com.apple.developer.appgroups",
                "com.apple.developer.carplayAudio", "com.apple.developer.carplayCommunication",
                "com.apple.developer.contacts.notes", "com.apple.developer.contacts.vcard-photos",
                "com.apple.developer.associated-appclip-app-groups", "com.apple.developer.appclip-parent",
                "com.apple.developer.syssec.entitlements", "com.apple.developer.certificates",
                "com.apple.developer.code-signing-style", "com.apple.developer.code-signing-identity",
                "com.apple.developer.code-signing-requirement", "com.apple.developer.code-signing-entitlements",
                "com.apple.developer.provisioning-profile-api", "com.apple.developer.authentication.method.device",
                "com.apple.developer.authentication.method.derived-identity",
                "com.apple.developer.authentication.method.fido", "com.apple.developer.fido.key",
            ],
            "count": 82,
            "reference": "iOS Capability Keys"
        },
        "mobile_app_metadata": {
            "description": "Mobile app store and general metadata",
            "fields": [
                "app_name", "app_id", "bundle_id", "package_name", "version",
                "version_name", "version_code", "build_number", "build_id",
                "release_type", "release_version", "min_os_version", "target_os_version",
                "sdk_version", "compile_version", "description", "short_description",
                "full_description", "keywords", "release_notes", "changelog",
                "privacy_policy", "support_url", "marketing_url", "website_url",
                "icon", "screenshot", "preview", "video", "category", "subcategory",
                "genre", "content_rating", "age_rating", "price", "currency",
                "in_app_purchases", "subscription", "free", "paid", "downloads",
                "rating", "reviews", "average_rating", "total_ratings", "total_reviews",
                "installs", "last_updated", "published_date", "created_date",
                "size", "download_size", "install_size", "file_size", "compressed_size",
                "developer", "publisher", "author", "company", "organization",
                "seller", "provider", "copyright", "trademark", "license",
                "terms_of_service", "disclaimer", "attribution", "credits",
                "acknowledgments", "permissions", "features", "requirements",
                "dependencies", "libraries", "frameworks", "sdks", "api_level",
                "cpu_architecture", "abi", "armv7", "arm64", "x86", "x86_64",
                "mips", "screens", "resolution", "orientation", "dpi", "density",
                "language", "supported_languages", "locale", "region", "country",
                "store", "app_store", "play_store", "渠道", "distribution",
                "channel", "campaign", "referral", "source", "medium", "content",
                "term", "click_id", "impression_id", "install_attribution",
                "deep_link", "universal_link", "app_link", "intent_url",
                "deeplink", "deeplinking", "deferred_deeplink", "attribution_window",
                "fingerprint", "device_fingerprint", "click_fingerprint",
                "install_fingerprint", "cohort", "cohort_analysis", "retention",
                "lifetime_value", "churn", "engagement", "active_users", "dau",
                "mau", "wau", "stickiness", "session", "session_count",
                "session_duration", "time_in_app", "screen_views", "events",
                "conversion", "conversion_rate", "attribution_conversion",
                "reattribution", "postback", "tracking_url", "click_url",
                "impression_url", "attribution_url", "skan", "skadn", "skad",
                "StoreKit", "SKAdNetwork", "SKAdNetworkItem", "SKAdNetworkID",
                "conversion_value", "coarse_conversion_value", "locked",
                "postback_type", "postback_signature",
            ],
            "count": 112,
            "reference": "Mobile App Store Standards"
        }
    },
    "totals": {
        "categories": 6,
        "total_fields": 761
    }
}


def main():
    output_dir = Path("dist/mobile_inventory")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "mobile_inventory.json"
    output_file.write_text(json.dumps(MOBILE_INVENTORY, indent=2, sort_keys=True), encoding="utf-8")
    
    summary = {
        "generated_at": MOBILE_INVENTORY["generated_at"],
        "source": MOBILE_INVENTORY["source"],
        "categories": MOBILE_INVENTORY["totals"]["categories"],
        "total_fields": MOBILE_INVENTORY["totals"]["total_fields"],
        "field_counts_by_category": {}
    }
    
    for cat, data in MOBILE_INVENTORY["categories"].items():
        summary["field_counts_by_category"][cat] = {
            "description": data["description"],
            "count": data["count"],
            "reference": data.get("reference", "N/A")
        }
    
    summary_file = output_dir / "mobile_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    
    print("=" * 70)
    print("MOBILE FORMAT METADATA FIELD INVENTORY")
    print("=" * 70)
    print()
    print(f"Generated: {MOBILE_INVENTORY['generated_at']}")
    print(f"Categories: {MOBILE_INVENTORY['totals']['categories']}")
    print(f"Total Fields: {MOBILE_INVENTORY['totals']['total_fields']:,}")
    print()
    print("FIELD COUNTS BY CATEGORY:")
    print("-" * 50)
    for cat, data in sorted(MOBILE_INVENTORY["categories"].items(), key=lambda x: x[1]["count"], reverse=True):
        ref = data.get("reference", "")[:35]
        print(f"  {cat:35s}: {data['count']:>3}  [{ref}]")
    print()
    print(f"Wrote: {output_file}")
    print(f"Wrote: {summary_file}")


if __name__ == "__main__":
    main()
