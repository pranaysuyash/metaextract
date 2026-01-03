#!/bin/bash

echo "Testing Persona Interpretation with Improved EXIF Date Access"
echo "=============================================================="
echo ""

# Check if server is running
if ! curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "❌ Server is not running. Please start the server first."
    exit 1
fi

echo "✅ Server is running"
echo ""

# Create a test image with proper EXIF data if we don't have one
# For now, let's test with an existing sample

TEST_IMAGE="/Users/pranay/Downloads/WhatsApp Image 2026-01-02 at 13.45.25.jpeg"

if [ ! -f "$TEST_IMAGE" ]; then
    echo "❌ Test image not found at $TEST_IMAGE"
    echo "Please provide a photo with EXIF data for testing"
    exit 1
fi

echo "📸 Testing with image: $TEST_IMAGE"
echo ""

# Test the extraction endpoint
echo "Sending extraction request..."
RESPONSE=$(curl -s -X POST \
  -F "file=@$TEST_IMAGE" \
  -F "trial_email=test@example.com" \
  http://localhost:5000/api/images_mvp/extract)

echo "✅ Extraction complete"
echo ""

# Extract persona interpretation
echo "📋 Persona Interpretation Results:"
echo "=================================="
echo ""

# Check if we have persona_interpretation in the response
if echo "$RESPONSE" | jq -e '.persona_interpretation' > /dev/null 2>&1; then
    echo "✅ Persona interpretation found in response"
    echo ""

    # Extract the when_taken answer
    WHEN_TAKEN=$(echo "$RESPONSE" | jq -r '.persona_interpretation.plain_english_answers.when_taken')

    echo "📅 When was this photo taken?"
    echo "Answer: $(echo "$WHEN_TAKEN" | jq -r '.answer')"
    echo "Details: $(echo "$WHEN_TAKEN" | jq -r '.details')"
    echo "Source: $(echo "$WHEN_TAKEN" | jq -r '.source')"
    echo "Confidence: $(echo "$WHEN_TAKEN" | jq -r '.confidence')"
    echo ""

    # Extract device info
    DEVICE=$(echo "$RESPONSE" | jq -r '.persona_interpretation.plain_english_answers.device')
    echo "📱 What device took this?"
    echo "Answer: $(echo "$DEVICE" | jq -r '.answer')"
    echo "Device Type: $(echo "$DEVICE" | jq -r '.device_type')"
    echo "Confidence: $(echo "$DEVICE" | jq -r '.confidence')"
    echo ""

    # Extract location info
    LOCATION=$(echo "$RESPONSE" | jq -r '.persona_interpretation.plain_english_answers.location')
    echo "📍 Where was this taken?"
    echo "Answer: $(echo "$LOCATION" | jq -r '.answer')"
    echo "Has Location: $(echo "$LOCATION" | jq -r '.has_location')"
    echo ""

    # Extract authenticity
    AUTHENTICITY=$(echo "$RESPONSE" | jq -r '.persona_interpretation.plain_english_answers.authenticity')
    echo "✨ Is this photo authentic?"
    echo "Assessment: $(echo "$AUTHENTICITY" | jq -r '.assessment')"
    echo "Score: $(echo "$AUTHENTICITY" | jq -r '.score')"
    echo "Confidence: $(echo "$AUTHENTICITY" | jq -r '.confidence')"
    echo ""

    # Show key findings
    echo "🔍 Key Findings:"
    echo "$RESPONSE" | jq -r '.persona_interpretation.key_findings[]' | sed 's/^/  - /'

    # Check if we're using EXIF dates or filesystem dates
    DATE_SOURCE=$(echo "$WHEN_TAKEN" | jq -r '.source')
    if [ "$DATE_SOURCE" = "photo_metadata" ]; then
        echo ""
        echo "✅ SUCCESS: Using EXIF/photo metadata dates (not filesystem dates)"
    elif [ "$DATE_SOURCE" = "filesystem" ]; then
        echo ""
        echo "⚠️  WARNING: Still using filesystem dates - EXIF date access issue persists"
    else
        echo ""
        echo "❓ UNKNOWN: Date source is '$DATE_SOURCE'"
    fi

else
    echo "❌ No persona interpretation found in response"
    echo ""
    echo "Response structure:"
    echo "$RESPONSE" | jq 'keys' 2>/dev/null || echo "Invalid JSON response"
fi

echo ""
echo "============================================================"
echo "Testing complete"