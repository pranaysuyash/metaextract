# Test Files Documentation - Phone Photo Sarah

**Created:** 2026-01-02
**Persona:** Phone Photo Sarah (Free Tier User)
**Purpose:** Baseline testing and V2 development

---

## Test File Collection

### File 1: `IMG_20251225_164634.jpg`
**Source:** User's phone camera
**Size:** 2.8 MB
**Type:** JPEG (3072 x 4096 pixels)

**Known Metadata:**
```json
{
  "file_name": "IMG_20251225_164634.jpg",
  "file_size": "2.8 MB",
  "resolution": "3072 x 4096",
  "megapixels": "12.6 MP",
  "aspect_ratio": "3:4 (portrait)",
  "color_space": "Uncalibrated",
  "iso": 640,
  "exposure_program": "Program AE",
  "max_aperture": "1.6",
  "exposure_mode": "Auto",
  "offset_time": "+05:30",
  "gps": "Likely present (need to verify)",
  "device": "Phone camera (need to identify make/model)"
}
```

**Expected Sarah's Questions:**
1. "When was this photo taken?" → Look for DateTimeOriginal
2. "Where was I when I took this?" → Check GPS coordinates
3. "What phone took this?" → Find Make/Model info
4. "Is this photo original?" → Check for editing signs

**Test Value:** High - This is exactly what Sarah would upload

---

### File 2: `gps-map-photo.jpg`
**Original Name:** `20251225_44810PMByGPSMapCamera_A27, Santhosapuram, Kudremukh Colony, Koramangala_Bengaluru_Karnataka_India_12_923974_77_6254197J4VWJFG+H5GMT_+05_30.jpg`
**Source:** User's phone camera (GPS app capture)
**Size:** 9.2 MB
**Type:** JPEG

**Known Metadata (from filename):**
```json
{
  "file_name": "gps-map-photo.jpg",
  "original_name": "20251225_44810PMByGPSMapCamera...",
  "file_size": "9.2 MB",
  "date_taken": "December 25, 2025 at 4:48:10 PM",
  "location": {
    "formatted": "A27, Santhosapuram, Kudremukh Colony, Koramangala, Bengaluru, Karnataka, India",
    "coordinates": {
      "latitude": 12.923974,
      "longitude": 77.6254197,
      "plus_code": "J4VWJFG+H5GMT+05:30"
    },
    "timezone": "+05:30"
  },
  "source_app": "GPS Map Camera"
}
```

**Expected Sarah's Questions:**
1. "When was this photo taken?" → December 25, 2025 at 4:48 PM
2. "Where was I when I took this?" → Bengaluru, India (very specific location!)
3. "What's this location?" → This is a GPS map screenshot
4. "Can I see this on a map?" → Yes, coordinates are precise

**Test Value:** **Very High** - Perfect GPS data for testing location features

---

## Baseline Testing Plan

### Test Session 1: Current UI (V1) Performance

**Date:** 2026-01-02
**Tester:** You (acting as Sarah)
**UI Version:** Current (V1)

#### Task 1: "When was this photo taken?"
**File:** `IMG_20251225_164634.jpg`

**Expected Current UI Experience:**
- ❌ Have to scan through 200+ technical fields
- ❌ DateTimeOriginal buried in EXIF section
- ❌ Format confusing: "2023:06:15 14:34:22"
- ❌ No prominent "when taken" display

**Measurements:**
- Time to complete: __________ seconds
- Clicks/scrolls required: __________
- Confusion level: ___/10
- Success on first try: Yes/No

#### Task 2: "Where was I when I took this?"
**File:** `gps-map-photo.jpg`

**Expected Current UI Experience:**
- ❌ GPS shown as coordinates: "12.923974, 77.6254197"
- ❌ No address or location context
- ❌ Coordinates are meaningless to normal users
- ❌ Might show "Google Maps" link but unclear

**Measurements:**
- Time to complete: __________ seconds
- User confusion: ___/10
- Did they understand the location? Yes/No
- Success on first try: Yes/No

#### Task 3: "What phone took this?"
**File:** `IMG_20251225_164634.jpg`

**Expected Current UI Experience:**
- ❌ Make/Model scattered across technical fields
- ❌ Buried in EXIF data
- ❌ No simple "iPhone 13 Pro" type display
- ❌ Technical camera details mixed in

**Measurements:**
- Time to complete: __________ seconds
- Confusion level: ___/10
- Success on first try: Yes/No

#### Task 4: "Is this photo authentic?"
**File:** Both files

**Expected Current UI Experience:**
- ❌ No clear authenticity assessment
- ❌ No confidence score
- ❌ Technical hash info but no plain English answer
- ❌ User has to interpret technical data

**Measurements:**
- Time to complete: __________ seconds
- Confidence in answer: ___/10
- Did they get an answer? Yes/No

---

## Additional Test Files to Collect

### Still Needed for Sarah:
1. **Android phone photo** - Different metadata structure than iPhone
2. **Screenshot** - No GPS, different metadata characteristics
3. **Instagram/WhatsApp download** - Stripped metadata
4. **Edited photo** - Software signatures present

### Still Needed for Peter (Photographer):
1. **RAW file** (.CR2, .NEF, .ARW)
2. **Professional JPEG** with IPTC/XMP data
3. **Edited photo** with software signatures

### Still Needed for Mike (Investigator):
1. **Video file** with telemetry
2. **Manipulated image** for testing detection
3. **Social media download** (heavily stripped metadata)

---

## Testing Environment Setup

### Browser Testing Checklist:
- [ ] Chrome (desktop)
- [ ] Safari (desktop)
- [ ] Firefox (desktop)
- [ ] Mobile Safari (iPhone)
- [ ] Mobile Chrome (Android)

### Screen Recording Setup:
```bash
# For macOS built-in screen recording
# Use QuickTime Player or CMD+SHIFT+5

# For more detailed analysis:
# Consider using browser extensions that track:
# - Mouse movements
# - Click patterns
# - Time spent on sections
# - Scroll behavior
```

---

## Success Criteria for V2

### For Phone Photo Sarah:

**Task 1: "When was this photo taken?"**
- Target: <5 seconds to find answer
- Target: 100% success rate
- Target: Format: "June 15, 2023 at 2:34 PM"

**Task 2: "Where was I when I took this?"**
- Target: <10 seconds to find answer
- Target: Show address + map
- Target: "Bengaluru, India" not "12.923974, 77.6254197"

**Task 3: "What phone took this?"**
- Target: <5 seconds to find answer
- Target: Format: "iPhone 13 Pro" or similar
- Target: Prominent display near top of page

**Task 4: "Is this photo authentic?"**
- Target: Clear yes/no with confidence level
- Target: <10 seconds to find answer
- Target: Format: "File appears authentic (95% confidence)"

---

## Next Steps

1. **Run Baseline Tests** - Test current UI with these files
2. **Document Current Performance** - Record all measurements
3. **Build V2 Key Findings Component** - Based on test results
4. **Test V2 vs V1** - Side-by-side comparison
5. **Document Improvements** - Quantify all gains

---

**Status:** ✅ Test files collected and documented
**Ready for:** Baseline testing with current UI
**Priority:** HIGH - Sprint 1, Week 1