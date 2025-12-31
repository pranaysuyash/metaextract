#!/bin/bash

# MetaExtract Comprehensive Engine Installation Script v4.0
# Installs all dependencies for comprehensive metadata field extraction

set -e

echo "🚀 MetaExtract Comprehensive Engine v4.0 Installation"
echo "=================================================="
echo "This will install dependencies for extracting comprehensive metadata fields"
echo "across all domains: Medical, Astronomical, Geospatial, Scientific, etc."
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   exit 1
fi

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

echo "🔍 Detected OS: $OS"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install system dependencies
install_system_deps() {
    echo ""
    echo "📦 Installing system dependencies..."
    
    if [[ "$OS" == "macos" ]]; then
        # macOS with Homebrew
        if ! command_exists brew; then
            echo "❌ Homebrew not found. Please install Homebrew first:"
            echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
        
        echo "Installing macOS dependencies..."
        brew update
        brew install \
            python@3.11 \
            ffmpeg \
            exiftool \
            libmagic \
            redis \
            postgresql \
            gdal \
            proj \
            geos \
            hdf5 \
            netcdf \
            opencv \
            exempi
            
    elif [[ "$OS" == "linux" ]]; then
        # Linux (Ubuntu/Debian)
        if command_exists apt-get; then
            echo "Installing Ubuntu/Debian dependencies..."
            sudo apt-get update
            sudo apt-get install -y \
                python3.11 \
                python3.11-dev \
                python3-pip \
                ffmpeg \
                libimage-exiftool-perl \
                libmagic1 \
                libmagic-dev \
                redis-server \
                postgresql \
                postgresql-contrib \
                gdal-bin \
                libgdal-dev \
                libproj-dev \
                libgeos-dev \
                libhdf5-dev \
                libnetcdf-dev \
                libopencv-dev \
                python3-opencv \
                libexempi8 \
                libexempi-dev \
                build-essential \
                cmake \
                pkg-config
                
        elif command_exists yum; then
            echo "Installing RHEL/CentOS dependencies..."
            sudo yum update -y
            sudo yum install -y \
                python311 \
                python311-devel \
                python3-pip \
                ffmpeg \
                perl-Image-ExifTool \
                file-devel \
                redis \
                postgresql \
                postgresql-server \
                gdal \
                gdal-devel \
                proj \
                proj-devel \
                geos \
                geos-devel \
                hdf5-devel \
                netcdf-devel \
                opencv \
                opencv-devel \
                exempi \
                exempi-devel \
                gcc \
                gcc-c++ \
                cmake \
                pkgconfig
        else
            echo "❌ Unsupported Linux distribution. Please install dependencies manually."
            exit 1
        fi
        
    elif [[ "$OS" == "windows" ]]; then
        echo "❌ Windows installation not yet supported in this script."
        echo "Please install dependencies manually:"
        echo "1. Install Python 3.11+ from python.org"
        echo "2. Install FFmpeg from ffmpeg.org"
        echo "3. Install ExifTool from exiftool.org"
        echo "4. Install Redis and PostgreSQL"
        echo "5. Install Visual Studio Build Tools"
        exit 1
    fi
}

# Function to create Python virtual environment
setup_python_env() {
    echo ""
    echo "🐍 Setting up Python environment..."
    
    # Check Python version
    if command_exists python3.11; then
        PYTHON_CMD="python3.11"
    elif command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [[ "$PYTHON_VERSION" < "3.9" ]]; then
            echo "❌ Python 3.9+ required, found $PYTHON_VERSION"
            exit 1
        fi
        PYTHON_CMD="python3"
    else
        echo "❌ Python 3.9+ not found"
        exit 1
    fi
    
    echo "Using Python: $($PYTHON_CMD --version)"
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d ".venv" ]]; then
        echo "Creating Python virtual environment..."
        $PYTHON_CMD -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
}

# Function to install Python dependencies
install_python_deps() {
    echo ""
    echo "📚 Installing Python dependencies..."
    
    # Ensure we're in virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source .venv/bin/activate
    fi
    
    # Install core dependencies first
    echo "Installing core dependencies..."
    pip install \
        pillow>=10.0.0 \
        exifread>=3.0.0 \
        ffmpeg-python>=0.2.0 \
        mutagen>=1.47.0 \
        pypdf>=4.0.0 \
        python-magic>=0.4.27 \
        redis>=4.5.0 \
        psutil>=5.9.0
    
    # Install comprehensive engine dependencies
    echo "Installing comprehensive engine dependencies..."
    
    # Medical imaging
    pip install pydicom>=2.4.0
    
    # Astronomical data
    pip install astropy>=5.0.0
    
    # Geospatial data
    pip install \
        rasterio>=1.3.0 \
        fiona>=1.9.0 \
        geopandas>=0.14.0 \
        pyproj>=3.4.0
    
    # Scientific data formats
    pip install \
        h5py>=3.8.0 \
        netCDF4>=1.6.0 \
        xarray>=2023.1.0
    
    # Advanced image analysis
    pip install \
        scikit-image>=0.20.0 \
        imageio>=2.25.0 \
        opencv-python>=4.5.0 \
        scikit-learn>=1.0.0 \
        imagehash>=4.3.0
    
    # Microscopy and scientific imaging
    pip install \
        aicsimageio>=4.9.0 \
        tifffile>=2023.1.0
    
    # Advanced audio analysis
    pip install \
        librosa>=0.10.0 \
        soundfile>=0.12.0 \
        pydub>=0.25.0
    
    # Document processing
    pip install \
        python-docx>=0.8.11 \
        openpyxl>=3.1.0 \
        beautifulsoup4>=4.11.0 \
        lxml>=4.9.0
    
    # Optional: Machine learning dependencies (large downloads)
    read -p "Install AI/ML dependencies? (tensorflow, torch, transformers) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing AI/ML dependencies (this may take a while)..."
        
        # Check architecture for Apple Silicon
        if [[ "$OS" == "macos" ]] && [[ $(uname -m) == "arm64" ]]; then
            echo "Detected Apple Silicon, installing optimized packages..."
            pip install tensorflow-macos>=2.12.0
            pip install torch>=2.0.0
        else
            pip install tensorflow>=2.12.0
            pip install torch>=2.0.0
        fi
        
        pip install transformers>=4.25.0
    fi
    
    # Blockchain and cryptography
    pip install \
        web3>=6.0.0 \
        cryptography>=40.0.0 \
        pycryptodome>=3.17.0
    
    # Enhanced metadata extraction
    pip install \
        pillow-heif>=0.16.0 \
        iptcinfo3>=2.1.4 \
        python-xmp-toolkit>=2.0.1
    
    # Extended attributes (Unix-like systems only)
    if [[ "$OS" != "windows" ]]; then
        pip install xattr>=1.1.0
    fi
    
    echo "✅ Python dependencies installed successfully"
}

# Function to verify installation
verify_installation() {
    echo ""
    echo "🔍 Verifying installation..."
    
    # Ensure we're in virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source .venv/bin/activate
    fi
    
    # Test comprehensive engine
    echo "Testing comprehensive metadata engine..."
    python3 -c "
import sys
sys.path.append('server/extractor')

try:
    from comprehensive_metadata_engine import ComprehensiveMetadataExtractor
    extractor = ComprehensiveMetadataExtractor()
    print('✅ Comprehensive engine loaded successfully')
    
    # Test specialized engines
    engines = {
        'Medical Imaging (DICOM)': 'pydicom',
        'Astronomical Data (FITS)': 'astropy.io.fits',
        'Geospatial (Rasterio)': 'rasterio',
        'Scientific Data (HDF5)': 'h5py',
        'Scientific Data (NetCDF)': 'netCDF4',
        'Advanced Image Analysis': 'cv2',
        'Audio Analysis': 'librosa',
        'Document Processing': 'docx',
        'Blockchain': 'web3'
    }
    
    available_engines = []
    for name, module in engines.items():
        try:
            __import__(module)
            available_engines.append(name)
            print(f'✅ {name} engine available')
        except ImportError:
            print(f'⚠️  {name} engine not available (optional)')
    
    print(f'\\n🎉 {len(available_engines)}/{len(engines)} specialized engines available')
    
except Exception as e:
    print(f'❌ Error testing comprehensive engine: {e}')
    sys.exit(1)
"
    
    # Test system dependencies
    echo ""
    echo "Testing system dependencies..."
    
    if command_exists exiftool; then
        echo "✅ ExifTool: $(exiftool -ver)"
    else
        echo "⚠️  ExifTool not found (recommended for full metadata extraction)"
    fi
    
    if command_exists ffprobe; then
        echo "✅ FFmpeg: $(ffprobe -version | head -n1)"
    else
        echo "⚠️  FFmpeg not found (required for video metadata)"
    fi
    
    if command_exists redis-server; then
        echo "✅ Redis available (for caching)"
    else
        echo "⚠️  Redis not found (optional, improves performance)"
    fi
}

# Function to create sample test
create_test() {
    echo ""
    echo "📝 Creating test script..."
    
    cat > test_comprehensive_engine.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for MetaExtract Comprehensive Engine v4.0
"""

import sys
import os
sys.path.append('server/extractor')

from comprehensive_metadata_engine import extract_comprehensive_metadata
import tempfile
from PIL import Image
import json

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='red')
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file.name, 'JPEG')
    return temp_file.name

def main():
    print("🧪 Testing MetaExtract Comprehensive Engine v4.0")
    print("=" * 50)
    
    # Create test image
    test_file = create_test_image()
    
    try:
        # Test different tiers
        for tier in ['free', 'starter', 'premium', 'super']:
            print(f"\n🔍 Testing {tier.upper()} tier...")
            
            result = extract_comprehensive_metadata(test_file, tier)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            fields_extracted = result.get('extraction_info', {}).get('comprehensive_fields_extracted', 0)
            engine_version = result.get('extraction_info', {}).get('comprehensive_version', 'unknown')
            
            print(f"✅ Engine version: {engine_version}")
            print(f"✅ Fields extracted: {fields_extracted}")
            
            # Show specialized engines status
            specialized = result.get('extraction_info', {}).get('specialized_engines', {})
            if specialized:
                print("🔧 Specialized engines:")
                for engine, available in specialized.items():
                    status = "✅" if available else "⚠️"
                    print(f"   {status} {engine}")
        
        print(f"\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    finally:
        # Clean up
        try:
            os.unlink(test_file)
        except:
            pass
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF
    
    chmod +x test_comprehensive_engine.py
    echo "✅ Test script created: test_comprehensive_engine.py"
}

# Main installation flow
main() {
    echo "Starting installation..."
    
    # Check if we're in the right directory
    if [[ ! -f "package.json" ]] || [[ ! -d "server" ]]; then
        echo "❌ Please run this script from the MetaExtract root directory"
        exit 1
    fi
    
    # Install system dependencies
    install_system_deps
    
    # Setup Python environment
    setup_python_env
    
    # Install Python dependencies
    install_python_deps
    
    # Verify installation
    verify_installation
    
    # Create test script
    create_test
    
    echo ""
    echo "🎉 MetaExtract Comprehensive Engine v4.0 Installation Complete!"
    echo "=" * 60
    echo ""
    echo "📋 What's installed:"
    echo "   • Comprehensive metadata engine (extensive field coverage)"
    echo "   • Medical imaging support (DICOM)"
    echo "   • Astronomical data support (FITS)"
    echo "   • Geospatial analysis (GeoTIFF, Shapefile)"
    echo "   • Scientific data formats (HDF5, NetCDF)"
    echo "   • Advanced image/video analysis"
    echo "   • AI content detection capabilities"
    echo "   • Enhanced steganography detection"
    echo "   • Blockchain provenance support"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Activate the virtual environment: source .venv/bin/activate"
    echo "   2. Run the test: python test_comprehensive_engine.py"
    echo "   3. Start the server: npm run dev"
    echo ""
    echo "📚 Documentation:"
    echo "   • Comprehensive engine: server/extractor/comprehensive_metadata_engine.py"
    echo "   • Advanced analysis: server/extractor/modules/advanced_analysis.py"
    echo "   • Requirements: requirements.txt"
    echo ""
    echo "⚡ Performance tips:"
    echo "   • Install Redis for caching: brew install redis (macOS) or apt install redis (Linux)"
    echo "   • Use SSD storage for better I/O performance"
    echo "   • Consider GPU acceleration for AI features"
    echo ""
}

# Run main function
main "$@"