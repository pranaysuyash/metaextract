# Images MVP: Detailed User Flow Scenarios & Outcomes

**Date**: January 5, 2026  
**Purpose**: Map every user journey and identify friction/failure points  

---

## 1. IDEAL PATH: Desktop User, Large File, Successful Conversion

### User Profile
- Device: MacBook Pro (1440p screen)
- File: 75MB JPG from professional camera (EXIF-heavy)
- Goal: Extract and analyze camera metadata
- Outcome: Converts to paid plan

### Timeline & Checkpoints

```
T=0:00    Landing Page
          ├─ View: Hero section, CTA buttons
          ├─ Status: ✅ LOADS FAST
          ├─ Check: Does user understand value prop?
          └─ Decision: Click "Analyze My Image"

T=0:05    Upload Page
          ├─ View: Upload zone, file picker
          ├─ Status: ✅ CLEAR INSTRUCTIONS
          ├─ Check: Is upload zone visible & clickable?
          └─ Decision: Click upload zone, select file

T=0:20    File Selected
          ├─ Status: 📤 75MB JPG, 3.5 seconds to upload
          ├─ Feedback: Progress bar visible?
          └─ Risk: ❌ NO PROGRESS BAR MENTIONED
              If missing: User thinks it's frozen

T=0:25    Upload Complete, Processing Starts
          ├─ Status: 🔄 Server extracting metadata
          ├─ Expected Duration: 5-10 seconds
          ├─ User Sees: Progress indicator (0-100%)
          └─ Risk: 🔴 WEBSOCKET BROKEN
              If broken: User sees 0% the entire time
              Consequence: User thinks it failed after 30 seconds

T=0:35    Processing Complete
          ├─ Status: ✅ EXTRACTION DONE
          ├─ Feedback: Smooth transition to results
          └─ Check: Does results page render correctly?

T=0:40    Results Page Loads
          ├─ View: 7,000+ metadata fields displayed
          ├─ Status: ✅ DESKTOP LAYOUT LOOKS GOOD
          ├─ Check: Fields organized by category?
          ├─ Check: Search function visible?
          └─ Risk: 🟡 OVERWHELMED BY DATA
              If no guidance: User scrolls aimlessly

T=0:50    User Explores Results
          ├─ Action: Searches for "camera"
          ├─ Results: 47 fields shown for camera info
          ├─ Status: ✅ USEFUL RESULTS
          └─ Emotion: "This is powerful!"

T=1:00    Export Options
          ├─ Action: Clicks "Download JSON"
          ├─ Status: ✅ FILE DOWNLOADS
          └─ Next Step: Opens in text editor, satisfied

T=1:05    Returns to Results
          ├─ Action: Sees paywall for "Summary Export"
          ├─ Message: "Upgrade for CSV & PDF export"
          ├─ Status: ✅ PAYWALL VISIBLE & CLEAR
          └─ Decision: "Maybe, let me think about it"

T=1:10    Conversion Moment
          ├─ Action: Tries to access "Professional Tier"
          ├─ Sees: $9.99/month, 500 extractions
          ├─ Status: ✅ PRICING CLEAR & REASONABLE
          ├─ Friction: ❓ Payment form on desktop?
          └─ Decision: "Let's try it"

T=1:20    Payment Complete
          ├─ Action: Enters card, completes purchase
          ├─ Status: ✅ CONFIRMATION EMAIL SENT
          ├─ Check: Can user download additional formats now?
          └─ Result: 💰 CONVERSION SUCCESS

T=1:25    End State
          ├─ User Satisfaction: ⭐⭐⭐⭐⭐
          ├─ Time Invested: 1:25 min
          ├─ Revenue: $9.99
          └─ Lifetime Value: $50+ (if retention)
```

### Critical Checkpoints
1. **[T=0:20]** Upload progress visible during transfer?
2. **[T=0:25]** Processing progress visible (WebSocket)?
3. **[T=0:35]** Results load without errors?
4. **[T=0:40]** Layout readable on desktop?
5. **[T=1:05]** Paywall triggers correctly?
6. **[T=1:10]** Payment form loads & is usable?

---

## 2. WORST CASE: Mobile User, Large File, Complete Failure

### User Profile
- Device: iPhone 12 (390px screen width)
- File: 60MB JPG from phone camera
- Goal: Extract metadata on the go
- Outcome: Complete abandonment

### Timeline & Checkpoints

```
T=0:00    Landing Page (Mobile)
          ├─ View: Page zoomed out to fit screen
          ├─ Status: 🔴 TEXT TOO SMALL
          ├─ Check: Can user see CTA buttons?
          └─ Risk: ⚠️ USER CONFUSION
              First impression: "Is this site broken?"

T=0:10    Click "Analyze" Button
          ├─ View: Routed to upload page
          ├─ Status: 🔴 UPLOAD ZONE TOO SMALL
          ├─ Problem: Zone is maybe 200x200px
          └─ User Reaction: "How do I click this?"

T=0:20    Tries to Tap Upload Zone
          ├─ Attempt 1: Misses, taps address bar
          ├─ Attempt 2: Phone keyboard appears
          ├─ Attempt 3: Finally clicks upload zone
          ├─ Status: 🔴 POOR TOUCH TARGET (recommend 44x44px min)
          └─ Frustration: 😠 Already annoyed

T=0:30    File Picker Opens
          ├─ View: Native iOS file picker
          ├─ Status: ✅ WORKS FINE (native)
          ├─ Action: Navigates to photos, selects 60MB JPG
          └─ Check: "Upload this photo?" confirmation?

T=0:45    Upload Starts
          ├─ Status: 📤 60MB over 4G LTE (~10s upload time)
          ├─ Visible Feedback: ???
          └─ Risk: 🔴 NO PROGRESS VISIBLE
              User can't see upload is happening

T=1:00    Upload Complete (Hopefully)
          ├─ Status: 🔄 Processing starts
          ├─ User Sees: ??? (unclear UI)
          └─ Risk: 🔴 WEBSOCKET BROKEN ON MOBILE
              Progress shows 0% for entire duration

T=1:30    Still Waiting...
          ├─ Time Elapsed: 30 seconds
          ├─ Progress Indicator: 0% still showing
          ├─ User Thinks: "This is broken"
          └─ Action: Refreshes page

T=1:35    Page Refresh
          ├─ Result: 🔴 DUPLICATE EXTRACTION STARTED
          ├─ User Charged: 2x credits (or $2 if paid)
          ├─ Backend State: Processing still happening
          └─ Consequence: User sees 2 results, but charged twice

T=2:00    Results Finally Load
          ├─ View: Mobile layout (or no layout)
          ├─ Status: 🔴 HORIZONTAL SCROLLING REQUIRED
          ├─ Fields: Truncated, hard to read on small screen
          ├─ Action: User scrolls horizontally
          └─ Frustration: 😤 "This is terrible"

T=2:10    Tries to Export
          ├─ Button: Visible but too small to tap reliably
          ├─ Action: Taps multiple times (misses)
          ├─ Status: 🔴 POOR UX CONTINUES
          └─ Emotion: "I'm done"

T=2:15    Abandons
          ├─ Action: User closes browser
          ├─ Revenue: -$0 (possibly -$2 for duplicate charge)
          ├─ Support Ticket: "I was charged twice!"
          └─ Likelihood Tells Friends: "Don't use, broken app"

T=2:20    End State
          ├─ User Satisfaction: ⭐☆☆☆☆
          ├─ Time Invested: 2:20 min (wasted)
          ├─ Revenue: -$2 (refund needed)
          ├─ Churn: 100% (will never return)
          └─ Damage: Negative review, word-of-mouth
```

### Critical Failure Points
1. **[T=0:00]** Page layout not responsive
2. **[T=0:10]** Upload zone not visible/usable on mobile
3. **[T=0:20]** Touch targets too small
4. **[T=0:45]** Upload progress not shown
5. **[T=1:00]** Processing progress not shown (WebSocket)
6. **[T=1:35]** Duplicate extraction from refresh
7. **[T=2:00]** Results page layout broken
8. **[T=2:10]** Export buttons hard to interact with

### Why This User Bounces
- Mobile represents 60% of potential users
- If this experience is what they see, 0% conversion from mobile
- Cost to acquire mobile user: same as desktop
- Lifetime value: $0
- Every mobile acquisition is unprofitable

---

## 3. PROBLEMATIC PATH: Desktop, Small File, Conversion Blocker

### User Profile
- Device: Windows laptop
- File: 5MB JPG from budget phone
- Goal: Free analysis, no purchase plan
- Outcome: Gets free results but doesn't convert

### Timeline & Checkpoints

```
T=0:00    Landing → Upload
          ├─ Status: ✅ FAST, CLEAR
          └─ Decision: Click upload

T=0:10    Upload & Process
          ├─ Status: ✅ COMPLETES IN 3 SECONDS
          ├─ Progress: Shows 100% immediately
          └─ Check: Does WebSocket work for quick uploads?

T=0:15    Results Load
          ├─ View: 7,000 fields displayed
          ├─ Problem: 🟡 NO GUIDANCE GIVEN
          ├─ User Thinks: "This is too much information"
          └─ Action: Scrolls aimlessly

T=0:30    Tries to Understand Results
          ├─ Question: "What am I looking at?"
          ├─ Issue: 🟡 NO TOOLTIPS OR LABELS
          ├─ No Help: "What does 'ColorSpace XYZ' mean?"
          └─ Frustration: 😐 Feeling lost

T=0:45    Looks for Export
          ├─ Action: Clicks "Download Summary"
          ├─ Paywall Appears: "Upgrade for Summary Export"
          ├─ Message: "Professional plan for CSV & PDF"
          ├─ Price: $9.99/month
          └─ Reaction: 🟡 "That's expensive for this"

T=1:00    Decision Point
          ├─ Free Option: JSON export (default)
          ├─ User Thinks: "I can't read JSON easily"
          ├─ Blocked: Can't access CSV/Summary
          └─ Decision: "Not worth it"

T=1:05    Leaves
          ├─ Action: Closes page without upgrading
          ├─ Revenue: $0
          ├─ Data: User never returns to check free tier limits
          └─ Reason: Didn't understand value of paid features

T=1:10    End State
          ├─ User Satisfaction: ⭐⭐☆☆☆
          ├─ Conversion: ❌ NO
          ├─ Reason: Unclear value proposition for upgrade
          └─ Churn Likelihood: High
```

### Why This Fails
- No clear "start here" guidance for 7,000 fields
- Free tier limitations not explained
- Value prop of paid tier unclear
- User doesn't know what they're missing
- Friction in conversion path
- Better approach: Show free tier limits BEFORE extraction, educate user, then paywall

---

## 4. PROBLEMATIC PATH: Free User, Hit Limit, No Clear Path

### User Profile
- Device: Desktop
- File: 3rd image analysis (free tier limit = 2)
- Goal: Continue using free
- Outcome: Confusion, support ticket

### Timeline & Checkpoints

```
T=0:00-5:00    First 2 extractions
                ├─ Status: ✅ WORKS
                └─ User Thinks: "Great, this is free!"

T=5:10         Third Upload
                ├─ Action: Uploads 3rd image
                ├─ Backend: Checks credit balance
                ├─ Result: ❌ "Free tier limit reached"
                └─ Response: Error message appears

T=5:15         Error Message
                ├─ Message: "Your free quota is exhausted"
                ├─ Problem: 🟡 UNCLEAR NEXT STEPS
                ├─ Questions: "How many was I supposed to get?"
                ├─ Questions: "What now?"
                └─ Action: ??? (confusing)

T=5:20         User Reaction
                ├─ Confusion: "I didn't know there was a limit"
                ├─ Frustration: "I already used my free tier?"
                ├─ Support Ticket: "Why am I limited?"
                └─ Emotion: 😤 Annoyed at surprise

T=5:30         User Scrolls for Help
                ├─ Looks For: Information about upgrade
                ├─ Finds: Paywall modal
                ├─ Modal: "Upgrade to Professional"
                ├─ Cost: $9.99/month
                └─ Decision: "No, I'll find something else"

T=5:40         End State
                ├─ Conversion: ❌ NO
                ├─ Support Ticket: YES
                ├─ Churn: ✅ YES
                └─ Reason: Surprise limit, unclear value
```

### Why This Fails
- Free tier limit not communicated upfront
- Error message doesn't explain options
- No guidance on how to upgrade
- User feels tricked (limited without warning)
- Creates support burden

---

## 5. PAYMENT FRICTION: Desktop User, Payment Fails

### User Profile
- Device: Desktop
- Converted: Clicked upgrade button
- Card: Visa, but maybe fraudulent flag
- Goal: Buy professional plan
- Outcome: Payment fails, user leaves

### Timeline & Checkpoints

```
T=0:00    Paywall Clicked
          ├─ Action: "Upgrade Now" button clicked
          ├─ Modal: Payment form appears
          └─ Fields: Name, email, card details

T=0:05    Payment Form Loads
          ├─ Status: ✅ FORM VISIBLE
          ├─ Check: ❓ Is form optimized for desktop?
          └─ Check: ❓ Is security info shown (SSL, privacy)?

T=0:30    Enters Card Details
          ├─ Card: Visa ending in 4242 (Stripe test card)
          ├─ Expiry: 12/25
          ├─ CVC: 123
          └─ Name: John Doe

T=0:35    Clicks "Complete Purchase"
          ├─ Action: Form submitted to Stripe
          ├─ Status: 🔄 Processing...
          └─ Check: Is there a loading indicator?

T=0:40    Payment Processing
          ├─ Backend: Calls Stripe API
          ├─ Result: ❌ CARD DECLINED (fraudulent flag)
          ├─ Stripe Response: Error code `card_declined`
          └─ Check: ❓ Is error user-friendly?

T=0:45    Error Displayed
          ├─ Message: "Card was declined by bank"
          ├─ Problem: 🟡 NO GUIDANCE
          ├─ User Thinks: "My card doesn't work?"
          ├─ Information: No retry option explained
          └─ Frustration: 😠 "This is broken"

T=0:50    User Action
          ├─ Option 1: Tries different card → fails again
          ├─ Option 2: Closes payment modal
          ├─ Option 3: Contacts support
          └─ Likely: Gives up

T=1:00    End State
          ├─ Conversion: ❌ FAILED
          ├─ User Frustration: HIGH
          ├─ Reason: Unclear error, no alternatives
          └─ Support Burden: YES
```

### Why This Fails
- Error message doesn't explain what to do
- No mention of contacting bank
- No alternative payment methods
- No "retry" guidance
- Creates support tickets

---

## 6. DATA LOSS SCENARIO: Network Interruption

### User Profile
- Device: Mobile on WiFi
- File: 100MB video file (unusual, likely unsupported)
- Connection: WiFi drops mid-upload
- Goal: Extract metadata
- Outcome: Lost data, unclear state

### Timeline & Checkpoints

```
T=0:00    Selects 100MB File
          ├─ Status: 📤 Upload starts (over WiFi)
          ├─ Progress: Visible at 25%
          └─ Check: ❓ Is upload resumable?

T=0:15    WiFi Drops (Network Interruption)
          ├─ Status: ❌ CONNECTION LOST
          ├─ Upload: Stops at 45% (~45MB uploaded)
          ├─ Backend: Received partial data
          └─ Check: ❓ Is there cleanup on server?

T=0:16    User Notices
          ├─ Display: Upload progress frozen at 45%
          ├─ Network: Switched to 4G
          └─ Decision: "Should I retry?"

T=0:20    User Retries Upload
          ├─ Action: Clicks upload again
          ├─ Result: ❌ DUPLICATE UPLOAD (not resumed)
          ├─ Server: Now has 2 partial files
          └─ Check: ❓ Is partial file cleaned up?

T=0:35    First Upload Times Out
          ├─ Status: 🔴 404 ERROR
          ├─ Message: "File not found"
          ├─ Reason: Upload session expired
          └─ User Thinks: "What happened?"

T=0:40    Second Upload Completes
          ├─ Status: ✅ UPLOAD DONE
          ├─ File: 100MB (different format, unsupported)
          ├─ Error: "Unsupported file type: .mov"
          └─ User Frustrated: "But I uploaded an image!"

T=0:50    End State
          ├─ Extraction: ❌ FAILED
          ├─ Credit Usage: ❓ Unclear (partial attempts?)
          ├─ User Clarity: 🔴 NONE
          └─ Support Burden: YES (user confused)
```

### Why This Fails
- No resumable uploads
- No clear session management
- File type validation happens too late
- Duplicate attempt handling unclear
- Partial files not cleaned up

---

## 7. BEST CASE CONVERSION: Desktop User, Seamless Flow

### User Profile
- Device: Desktop (1440p)
- File: 200MB RAW camera file
- Tech Level: Power user (photographer)
- Goal: Extract & analyze raw metadata
- Outcome: Converts, becomes repeat customer

### Timeline & Checkpoints

```
T=0:00    Landing Page
          ├─ Clear value prop
          ├─ ✅ Immediately understands "extract metadata"
          └─ Decision: "This is what I need"

T=0:05    Clicks CTA
          ├─ Action: "Analyze Your Image"
          ├─ Navigation: Smooth, fast
          └─ Status: ✅ Clear next step

T=0:10    Upload Page
          ├─ View: Clean, obvious upload zone
          ├─ Instructions: "Supports JPG, PNG, RAW, TIFF..." (shows formats)
          ├─ Status: ✅ USER KNOWS FILE WILL WORK
          └─ Confidence: High

T=0:15    Selects 200MB RAW File
          ├─ Status: 📤 Upload starts (~30s for large file)
          ├─ Feedback: ✅ UPLOAD PROGRESS VISIBLE
          └─ Display: "Uploading... 45% complete"

T=0:50    Upload Complete
          ├─ Status: 🔄 Processing starts
          ├─ Feedback: ✅ WEBSOCKET CONNECTED
          ├─ Message: "Analyzing image... 20%"
          └─ User Knows: Processing happening, eta shown

T=1:00    Processing Complete
          ├─ Message: ✅ "Analysis complete - 2,847 fields extracted"
          ├─ Transition: Smooth to results page
          └─ Load Time: <1 second

T=1:05    Results Display
          ├─ View: Well-organized by category (Camera, Lens, Location, etc.)
          ├─ Guidance: ✅ "Most Important" section highlighted
          ├─ Search: ✅ Easily find "Shutter Speed", "ISO", etc.
          └─ Status: ✅ USER KNOWS EXACTLY WHAT THEY'RE LOOKING AT

T=1:20    Explores Results
          ├─ View: Camera settings (ISO 400, F/2.8, 1/500s)
          ├─ View: Lens info (Canon 24-70mm)
          ├─ View: GPS coordinates (San Francisco)
          ├─ Satisfaction: ⭐⭐⭐⭐⭐ "Perfect!"
          └─ Value: "This is exactly what I needed"

T=1:30    Tries Free Export (JSON)
          ├─ Action: Click "Download JSON"
          ├─ Status: ✅ FILE DOWNLOADS
          ├─ Format: Readable in text editor
          └─ Thought: "But I need CSV for spreadsheet..."

T=1:40    Sees Paywall
          ├─ Suggestion: "Want CSV, PDF, or Summary? Upgrade for $9.99/month"
          ├─ Message: ✅ CLEAR VALUE PROP
          ├─ Features: "500 extractions/month, priority support"
          ├─ Check: Makes sense, fair price
          └─ Decision: "Let me try it"

T=1:50    Payment
          ├─ Form: ✅ LOADS INSTANTLY
          ├─ Security: ✅ Shows SSL padlock
          ├─ Submit: ✅ FAST PROCESSING
          ├─ Confirmation: ✅ EMAIL RECEIVED
          └─ Relief: "Done, it worked!"

T=2:00    Post-Purchase
          ├─ Access: ✅ Can now download CSV
          ├─ Excel: ✅ Opens perfectly in spreadsheet
          ├─ Satisfaction: ⭐⭐⭐⭐⭐ "Exactly what I needed!"
          └─ Thought: "Worth every penny"

T=2:10    End State
          ├─ Conversion: ✅ YES
          ├─ Revenue: $9.99 + $2.99 (CSV export) = $12.98
          ├─ Lifetime Value: $100+ (recurring monthly)
          ├─ Satisfaction: Very High
          ├─ Likelihood to Recommend: 90%+
          └─ Repeat Usage: Likely
```

### Why This Succeeds
- Clear value prop from start
- File format support clear upfront
- Progress feedback at every step
- Results well-organized with guidance
- Paywall clear with compelling value prop
- Payment fast and reliable
- Post-purchase delivers on promise

---

## 8. EDGE CASE: Uploading Unsupported Format

### User Profile
- Device: Desktop
- File: 500KB SVG (vector graphic)
- Goal: Extract metadata from logo
- Outcome: Clear error handling

### Ideal Scenario
```
T=0:00    Upload Page
          ├─ Supported Formats Listed: JPG, PNG, HEIC, WEBP, TIFF, BMP, GIF, RAW...
          ├─ SVG: ❌ NOT LISTED
          └─ User Knows: "SVG not supported"

T=0:10    User Selects SVG Anyway
          ├─ File Picker: Filters to images only?
          ├─ Status: ❓ Does it block SVG?
          └─ If Blocked: User sees greyed-out file

T=0:15    If SVG Slips Through
          ├─ Error: "SVG format not supported"
          ├─ Message: ✅ CLEAR & ACTIONABLE
          ├─ Suggestion: ✅ "Try JPG, PNG, or other formats"
          └─ Refund: ✅ "No credits charged"

T=0:20    User Tries PNG Version
          ├─ Upload: ✅ WORKS
          ├─ Results: ✅ DISPLAYED
          └─ Success: Recovered from error
```

### Bad Scenario
```
T=0:00    Upload Page
          ├─ Supported Formats: Not listed
          └─ User Guesses: "Probably works"

T=0:10    Uploads SVG
          ├─ Status: 🔄 Processing...
          └─ Progress: Shows 100%

T=0:20    Error Occurs
          ├─ Server: Python extractor crashes on SVG
          ├─ Error: ❌ "Internal Server Error"
          ├─ User Thinks: "The site is broken!"
          └─ Credit Charged: ✅ YES (even though failed)

T=0:25    Support Ticket
          ├─ User: "Why did I get charged for an error?"
          ├─ Your Response: Manual investigation
          └─ Cost: Manual refund + support time
```

---

## Summary: Journey Comparison

| Scenario | Success | Time | Satisfaction | Reason |
|----------|---------|------|--------------|--------|
| **Ideal (1)** | ✅ Yes | 1:25 | ⭐⭐⭐⭐⭐ | Clear, smooth, rewarding |
| **Mobile Worst (2)** | ❌ No | 2:20 | ⭐☆☆☆☆ | Broken UX, duplicate charge |
| **Free Confused (3)** | ❌ No | 1:10 | ⭐⭐☆☆☆ | No guidance, slow paywall |
| **Hit Limit (4)** | ❌ No | 0:40 | ⭐⭐☆☆☆ | Surprise limit, support ticket |
| **Payment Fails (5)** | ❌ No | 0:45 | ⭐☆☆☆☆ | Unclear error, lost customer |
| **Network Fail (6)** | ❌ No | 1:00 | ⭐☆☆☆☆ | Data loss, support ticket |
| **Power User (7)** | ✅ Yes | 2:10 | ⭐⭐⭐⭐⭐ | Exactly what they need |
| **Wrong Format (8)** | ⚠️ Partial | 0:20 | ⭐⭐⭐☆☆ | Error handled well |

---

## Key Insights

### What Determines Success
1. **Clear Communication**: User knows what will happen
2. **Smooth Progress**: Real-time feedback at each step
3. **Error Handling**: Failures explained, not surprising
4. **Mobile Optimization**: Works on all devices
5. **Intuitive UX**: User doesn't need tutorial
6. **Visible Value**: Why they should upgrade, clear benefits
7. **Reliable Payment**: Payment works reliably, errors clear

### What Causes Failure
1. **Mobile Broken**: 60% of users excluded
2. **WebSocket Down**: Real-time feedback missing
3. **Surprise Limits**: Free tier not explained upfront
4. **Overwhelming UX**: 7,000 fields with no guidance
5. **Vague Errors**: "Something went wrong" with no action
6. **Duplicate Charges**: Retries cause double charges
7. **Unclear Value**: Don't understand why they should upgrade

### Financial Impact by Scenario
| Scenario | Revenue | Support Cost | Net |
|----------|---------|--------------|-----|
| Ideal | $12.98 | $0.25 | +$12.73 |
| Mobile Worst | -$2.00 | $5.00 | -$7.00 |
| Confused | $0 | $2.00 | -$2.00 |
| Hit Limit | $0 | $3.00 | -$3.00 |
| Payment Fails | $0 | $1.00 | -$1.00 |

---

**End of User Flow Scenarios**

Use these journeys to guide UX decisions, error handling, and feature prioritization. Every negative scenario should be explicitly addressed before launch.
