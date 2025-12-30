#!/usr/bin/env python3
"""Web Standards metadata field inventory.

This script generates an inventory of web standard metadata fields:

- Open Graph Protocol (og:* tags)
- Twitter Cards (twitter:* tags)
- Schema.org structured data
- Web App Manifest fields
- PWA (Progressive Web App) fields
- Security headers
- Microdata/RDFa fields
"""

import json
from pathlib import Path
from typing import Dict, List


# Open Graph Protocol fields (og:*)
OPEN_GRAPH_FIELDS = [
    # Basic metadata
    "og:title", "og:type", "og:image", "og:url", "og:description",
    "og:site_name", "og:locale", "og:locale:alternate", "og:video",
    "og:audio", "og:determiner", "og:updated_time", "og:video:tag",
    "og:video:url", "og:video:secure_url", "og:video:type",
    "og:video:width", "og:video:height", "og:video:tag",
    "og:image:url", "og:image:secure_url", "og:image:type",
    "og:image:width", "og:image:height", "og:image:alt",
    "og:audio:url", "og:audio:secure_url", "og:audio:type",
    "og:book:author", "og:book:isbn", "og:book:release_date",
    "og:book:tag", "og:profile:first_name", "og:profile:last_name",
    "og:profile:username", "og:profile:gender", "og:article:published_time",
    "og:article:modified_time", "og:article:author",
    "og:article:section", "og:article:tag", "og:article:expiration_time",
    "og:video:actor", "og:video:actor:role", "og:video:director",
    "og:video:writer", "og:video:duration", "og:video:release_date",
    "og:video:tag", "og:video:series", "og:restaurant:contact_info",
    "og:restaurant:menu_url", "og:restaurant:price_range",
    "og:product:price:amount", "og:product:price:currency",
    "og:product:availability", "og:product:brand", "og:product:ean",
    "og:product:isbn", "og:product:upc", "og:product:mfr_part_no",
    "og:product:size", "og:product:color", "og:product:material",
    "og:product:weight",
]

# Twitter Card fields (twitter:*)
TWITTER_CARDS_FIELDS = [
    # Card types
    "twitter:card", "twitter:site", "twitter:site:id",
    "twitter:creator", "twitter:creator:id", "twitter:title",
    "twitter:description", "twitter:image", "twitter:image:alt",
    "twitter:image:width", "twitter:image:height", "twitter:image0",
    "twitter:image1", "twitter:image2", "twitter:image3",
    "twitter:player", "twitter:player:width", "twitter:player:height",
    "twitter:player:stream", "twitter:player:stream:content_type",
    "twitter:app:name:iphone", "twitter:app:id:iphone",
    "twitter:app:url:iphone", "twitter:app:name:ipad",
    "twitter:app:id:ipad", "twitter:app:url:ipad", "twitter:app:name:googleplay",
    "twitter:app:id:googleplay", "twitter:app:url:googleplay",
    "twitter:label1", "twitter:data1", "twitter:label2", "twitter:data2",
    "twitter:label3", "twitter:data3", "twitter:label4", "twitter:data4",
    "twitter:gallery:image0", "twitter:gallery:image1", "twitter:gallery:image2",
    "twitter:gallery:image3", "twitter:platform", "twitter:platform:id",
    "twitter:platform:display_name", "twitter:player:loop",
    "twitter:player:autoplay", "twitter:player:hide_controls",
]

# Schema.org fields (structured data types and properties)
SCHEMA_ORG_FIELDS = [
    # Types
    "Thing", "Person", "Organization", "LocalBusiness", "Restaurant",
    "Product", "Offer", "PriceSpecification", "AggregateOffer",
    "Event", "PostalAddress", "GeoCoordinates", "Place", "Venue",
    "CreativeWork", "Article", "BlogPosting", "NewsArticle",
    "TechArticle", "Review", "Rating", "AggregateRating",
    "ImageObject", "VideoObject", "AudioObject", "MediaObject",
    "Book", "Movie", "TVEpisode", "TVSeason", "TVSeries",
    "MusicRecording", "MusicAlbum", "MusicGroup", "MusicPlaylist",
    "Playlist", "Episode", "Season", "Series", "Course",
    "JobPosting", "EmploymentType", "OccupationalCategory",
    "EducationEvent", "BusinessEvent", "Festival", "SportsEvent",
    "TheaterEvent", "VisualArtwork", "Painting", "Sculpture", "Photograph",
    "SoftwareApplication", "MobileApplication", "WebApplication",
    "VideoGame", "VideoGameClip", "VideoGameSeries", "VideoGameMultiplayer",
    "Recipe", "NutritionInformation", "HowTo", "HowToStep", "HowToDirection",
    "FAQPage", "QAPage", "CheckoutPage", "LodgingBusiness", "Hotel", "Motel",
    "BedAndBreakfast", "Hostel", "Resort", "TouristAttraction", "LandmarksOrHistoricalBuildings",
    "Museum", "Gallery", "Theater", "MovieTheater", "NightClub", "BarOrPub", "Bakery",
    "CafeOrCoffeeShop", "FastFoodRestaurant", "IceCreamShop", "Distillery",
    "Corporation", "EducationalOrganization", "CollegeOrUniversity", "School",
    "GovernmentOrganization", "NGO", "PerformingGroup", "MusicGroup", "DanceGroup",
    "SportsTeam", "SportsOrganization", "SportsActivityLocation", "Gymnasium", "HealthClub",
    "Store", "ElectronicsStore", "DepartmentStore", "ClothingStore", "ShoeStore",
    "HardwareStore", "HomeAndConstructionBusiness", "RealEstateAgent", "AutoDealer",
    "Vehicle", "Car", "Motorcycle", "Truck", "Bus", "Boat", "Aircraft", "MotorizedBicycle",
    "Physician", "Hospital", "MedicalClinic", "Pharmacy", "Dentist", "VeterinaryCare",
    "HealthAndBeautyBusiness", "BeautySalon", "HairSalon", "NailSalon", "TattooParlor",
    "FinancialService", "BankOrCreditUnion", "InsuranceAgency", "AccountingService",
    "LegalService", "Attorney", "Notary", "GovernmentOffice", "PostOffice",
    "TireShop", "Airport", "TrainStation", "BusStation", "SubwayStation", "TransitStation",
    "TravelAgency", "Hotel", "Motel", "BedAndBreakfast", "VacationRental",
    "ApartmentComplex", "SingleFamilyResidence", "House", "GatedResidenceCommunity",

    # Common properties
    "additionalType", "alternateName", "description", "image", "name",
    "sameAs", "url", "identifier", "mainEntityOfPage", "potentialAction",
    "about", "audience", "author", "contentRating", "dateCreated",
    "dateModified", "datePublished", "editor", "encoding", "hasPart",
    "isPartOf", "keywords", "license", "publisher", "recordedAt",
    "releasedEvent", "spatialCoverage", "temporalCoverage", "typicalAgeRange",
    "version", "genre", "contentUrl", "embedUrl", "uploadDate",
    "duration", "bitrate", "playerType", "productionCompany",
    "purchaseUrl", "reviewAspect", "aggregateRating", "reviewRating",
    "starRating", "ratingValue", "bestRating", "worstRating",
    "ratingCount", "reviewCount", "address", "addressLocality",
    "addressRegion", "postalCode", "streetAddress", "addressCountry",
    "geo", "latitude", "longitude", "telephone", "faxNumber",
    "openingHours", "openingHoursSpecification", "priceRange",
    "paymentAccepted", "currency", "price", "highPrice", "lowPrice",
    "availability", "itemCondition", "sku", "gtin", "gtin8", "gtin12",
    "gtin13", "gtin14", "mpn", "brand", "manufacturer", "model",
    "color", "weight", "height", "width", "depth", "size",
    "material", "pattern", "award", "category", "subCategory",
    "targetProduct", "educationalAlignment", "educationalUse",
    "skillLevel", "timeRequired", "typicalCreditsPerHour",

    # Person properties
    "givenName", "familyName", "additionalName", "honorificPrefix",
    "honorificSuffix", "jobTitle", "worksFor", "birthDate", "deathDate",
    "birthPlace", "deathPlace", "nationality", "alumniOf",
    "employee", "memberOf", "award", "knows", "knowsAbout",
    "speaks", "address", "colleague", "contactPoint", "email",
    "telephone", "faxNumber", "relatedTo", "spouse", "sibling",
]

# Web App Manifest fields (PWA)
WEB_APP_MANIFEST_FIELDS = [
    "manifest", "short_name", "name", "icons", "icon", "src", "type",
    "sizes", "purpose", "maskable", "any", "start_url", "display",
    "orientation", "background_color", "theme_color", "categories",
    "lang", "dir", "short_name", "description", "icons", "screenshots",
    "shortcuts", "name", "short_name", "description", "url", "icons",
    "related_applications", "prefer_related_applications", "scope",
    "serviceworker", "src", "scope", "update_via_cache", "prefer_related_applications",
    "display_override", "orientation", "categories", "dir", "lang",
    "description", "icons", "screenshots", "shortcuts", "start_url",
    "theme_color", "background_color", "shortcuts", "related_applications",
    "display", "orientation", "scope", "serviceworker", "workbox",
    "injectManifest", "sw", "fallback", "publicPath", "modifyUrlPrefix",
    "exclude", "globPatterns", "globDirectory", "swDest", "swSrc",
]

# PWA (Progressive Web App) fields
PWA_FIELDS = [
    # Service Worker
    "service-worker", "serviceWorker", "sw.js", "sw.js.map",
    "fetch", "cache", "install", "activate", "push", "sync",
    "notification", "background-sync", "periodic-background-sync",
    "pushManager", "subscription", "getSubscription", "subscribe",
    "requestPermission", "showNotification", "getNotifications",

    # Cache API
    "caches", "cacheName", "cacheKeys", "cacheMatch", "cacheAdd",
    "cachePut", "cacheDelete", "cacheKeys", "cacheMatchAll",

    # IndexedDB
    "indexedDB", "IDBOpenDBRequest", "IDBRequest", "IDBTransaction",
    "IDBObjectStore", "IDBIndex", "IDBCursor", "IDBKeyRange",

    # Web App Install
    "beforeinstallprompt", "preventDefault", "userChoice",
    "installPrompt", "platform", "isIgnored", "isFallback",
    "didDefault", "dismiss", "outcome", "addToHomescreen",
    "isInstallable", "InstallPromptEvent", "appinstalled",

    # Background
    "background-fetch", "background-sync", "push", "periodic-sync",
    "periodic-background-sync", "BackgroundFetchManager",
    "BackgroundFetchRegistration", "BackgroundFetchResult",

    # Payments
    "PaymentRequest", "PaymentMethod", "PaymentResponse",
    "PaymentAddress", "PaymentDetails", "PaymentItem",
    "PaymentShippingOption", "merchantValidation",
]

# Security headers (already partially covered in HTTP, but adding specific security fields)
SECURITY_FIELDS = [
    # CSP directives
    "default-src", "script-src", "style-src", "img-src", "connect-src",
    "media-src", "object-src", "frame-src", "child-src", "worker-src",
    "font-src", "manifest-src", "prefetch-src", "form-action",
    "frame-ancestors", "base-uri", "plugin-types", "sandbox",
    "report-uri", "report-to", "require-trusted-types-for",
    "trusted-types", "upgrade-insecure-requests", "block-all-mixed-content",

    # Feature Policy / Permissions Policy
    "geolocation", "microphone", "camera", "payment", "vr",
    "accelerometer", "gyroscope", "magnetometer", "usb", "hid",
    "clipboard-read", "clipboard-write", "display-capture",
    "fullscreen", "payment", "document-domain", "encrypted-media",
    "autoplay", "camera", "microphone", "usb", "bluetooth",
    "background-sync", "ambient-light-sensor", "background-fetch",

    # Subresource Integrity
    "integrity", "crossorigin", "anonymous", "use-credentials",

    # Content options
    "crossorigin", "crossorigin", "referrerpolicy", "referrer",
    "nomodule", "defer", "async", "lazyload", "preload",
    "prefetch", "prerender", "modulepreload", "module",
]

# Generate complete inventory
def generate_inventory(output_dir: Path) -> None:
    """Generate web standards metadata field inventory."""

    output_dir.mkdir(parents=True, exist_ok=True)

    inventory = {
        "generated_at": "",
        "source": "Web Standards Specifications (Open Graph, Twitter Cards, Schema.org, W3C)",
        "categories": {},
    }

    from datetime import datetime, timezone
    inventory["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Open Graph
    inventory["categories"]["Open_Graph"] = {
        "description": "Open Graph Protocol metadata fields",
        "fields": sorted(OPEN_GRAPH_FIELDS),
        "count": len(OPEN_GRAPH_FIELDS),
    }

    # Twitter Cards
    inventory["categories"]["Twitter_Cards"] = {
        "description": "Twitter Card metadata fields",
        "fields": sorted(TWITTER_CARDS_FIELDS),
        "count": len(TWITTER_CARDS_FIELDS),
    }

    # Schema.org
    inventory["categories"]["Schema_org"] = {
        "description": "Schema.org structured data types and properties",
        "fields": sorted(SCHEMA_ORG_FIELDS),
        "count": len(SCHEMA_ORG_FIELDS),
    }

    # Web App Manifest
    inventory["categories"]["Web_App_Manifest"] = {
        "description": "Web App Manifest (PWA) fields",
        "fields": sorted(WEB_APP_MANIFEST_FIELDS),
        "count": len(WEB_APP_MANIFEST_FIELDS),
    }

    # PWA
    inventory["categories"]["PWA_Progressive"] = {
        "description": "Progressive Web App fields",
        "fields": sorted(PWA_FIELDS),
        "count": len(PWA_FIELDS),
    }

    # Security
    inventory["categories"]["Security_Headers"] = {
        "description": "Security header fields",
        "fields": sorted(SECURITY_FIELDS),
        "count": len(SECURITY_FIELDS),
    }

    # Calculate totals
    all_fields = (
        OPEN_GRAPH_FIELDS + TWITTER_CARDS_FIELDS + SCHEMA_ORG_FIELDS +
        WEB_APP_MANIFEST_FIELDS + PWA_FIELDS + SECURITY_FIELDS
    )
    unique_fields = len(set(all_fields))

    inventory["totals"] = {
        "total_fields": len(all_fields),
        "unique_fields": unique_fields,
        "categories": len(inventory["categories"]),
    }

    # Write JSON
    output_path = output_dir / "web_standards_inventory.json"
    output_path.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote: {output_path}")

    # Print summary
    print()
    print("=" * 60)
    print("WEB STANDARDS INVENTORY SUMMARY")
    print("=" * 60)
    print()
    print(f"Total fields: {len(all_fields):,}")
    print(f"Unique fields: {unique_fields:,}")
    print(f"Categories: {len(inventory['categories'])}")
    print()

    for cat_name, cat_data in inventory["categories"].items():
        print(f"  {cat_name}: {cat_data['count']:,} fields")

    print()
    print("=" * 60)
    print("TOTAL WEB STANDARDS FIELDS: {:,}".format(len(all_fields)))
    print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate web standards metadata field inventory",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("dist/web_standards_inventory"),
        help="Output directory (default: dist/web_standards_inventory)",
    )
    args = parser.parse_args()

    generate_inventory(args.out_dir)


if __name__ == "__main__":
    main()
