#!/bin/bash
# Setup script for burned metadata extraction

echo "================================================"
echo "MetaExtract - Burned Metadata Setup"
echo "================================================"
echo ""

# Check if Tesseract is installed
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract OCR is already installed"
    tesseract --version | head -n 1
else
    echo "✗ Tesseract OCR not found"
    echo ""
    echo "Installing Tesseract OCR..."
    
    # Detect OS and install
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install tesseract
        else
            echo "Error: Homebrew not found. Please install from https://brew.sh"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y tesseract-ocr
        elif command -v yum &> /dev/null; then
            sudo yum install -y tesseract
        else
            echo "Error: Package manager not found. Please install tesseract manually."
            exit 1
        fi
    else
        echo "Error: Unsupported OS. Please install Tesseract manually."
        echo "Visit: https://github.com/tesseract-ocr/tesseract"
        exit 1
    fi
fi

echo ""
echo "================================================"
echo "Testing Installation"
echo "================================================"
echo ""

# Test Python modules
cd "$(dirname "$0")"
python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from extractor.modules.ocr_burned_metadata import extract_burned_metadata
    from extractor.modules.metadata_comparator import compare_metadata
    print('✓ Python modules imported successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✓ All dependencies installed"
    echo ""
    echo "================================================"
    echo "Setup Complete!"
    echo "================================================"
    echo ""
    echo "Test the feature:"
    echo "  python test_burned_metadata.py <image_file>"
    echo ""
    echo "Example:"
    echo "  python test_burned_metadata.py ~/Pictures/gps_map_photo.jpg"
    echo ""
else
    echo "✗ Setup failed"
    exit 1
fi
