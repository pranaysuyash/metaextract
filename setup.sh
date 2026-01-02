#!/bin/bash

# MetaExtract Environment Setup Script

set -e  # Exit on any error

echo "MetaExtract Environment Setup Script"
echo "====================================="

# Function to check if a command exists
command_exists() {
    command -v "$@" > /dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 20+."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+."
    exit 1
fi

if ! command_exists pip3; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

if ! command_exists ffmpeg; then
    echo "⚠️  FFmpeg is not installed. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install ffmpeg
        else
            echo "❌ Homebrew is required to install FFmpeg on macOS. Please install Homebrew first."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt update
        sudo apt install -y ffmpeg
    else
        echo "❌ Could not install FFmpeg automatically. Please install it manually."
        exit 1
    fi
else
    echo "✅ FFmpeg is installed"
fi

if ! command_exists exiftool; then
    echo "⚠️  ExifTool is not installed. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install exiftool
        else
            echo "❌ Homebrew is required to install ExifTool on macOS. Please install Homebrew first."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt update
        sudo apt install -y libimage-exiftool-perl
    else
        echo "❌ Could not install ExifTool automatically. Please install it manually."
        exit 1
    fi
else
    echo "✅ ExifTool is installed"
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'.' -f1 | sed 's/v//')
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "❌ Node.js version is too old. Please upgrade to Node.js 20+."
    exit 1
else
    echo "✅ Node.js version: $(node --version)"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1)
if [ "$PYTHON_VERSION" -lt 3 ]; then
    echo "❌ Python version is too old. Please upgrade to Python 3.11+."
    exit 1
else
    PYTHON_MINOR=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f2)
    if [ "$PYTHON_MINOR" -lt 11 ]; then
        echo "⚠️  Python version is older than 3.11. Consider upgrading to Python 3.11+ for best compatibility."
    else
        echo "✅ Python version: $(python3 --version)"
    fi
fi

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm ci

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p uploads temp logs

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your configuration values."
fi

# Run database migrations
echo "Running database migrations..."
npm run db:push

# Build the application
echo "Building the application..."
npm run build

echo ""
echo "🎉 MetaExtract environment setup completed!"
echo ""
echo "To start the application, run:"
echo "  npm run dev"
echo ""
echo "For production deployment, see the deployment documentation."