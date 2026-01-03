#!/bin/bash

echo "Testing simple upload for persona interpretation..."
echo ""

# Copy file to temp location with no spaces
cp "/Users/pranay/Downloads/WhatsApp Image 2026-01-02 at 13.45.25.jpeg" /tmp/test_image.jpg

echo "Sending extraction request..."
curl -s -X POST \
  -F "file=@/tmp/test_image.jpg" \
  -F "trial_email=test@example.com" \
  http://localhost:5000/api/images_mvp/extract > /tmp/response.json

echo "Checking response..."
if jq -e '.persona_interpretation' /tmp/response.json > /dev/null 2>&1; then
    echo "✅ Persona interpretation found!"
    echo "When taken source: $(jq -r '.persona_interpretation.plain_english_answers.when_taken.source' /tmp/response.json)"
    echo "When taken answer: $(jq -r '.persona_interpretation.plain_english_answers.when_taken.answer' /tmp/response.json)"
else
    echo "❌ No persona interpretation found"
    echo "Available keys: $(jq -r 'keys' /tmp/response.json)"
fi

# Cleanup
rm /tmp/test_image.jpg