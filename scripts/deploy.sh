#!/bin/bash

# MetaExtract Deployment Script
# Automates the setup and deployment process

set -e  # Exit on any error

echo "🚀 MetaExtract Deployment Script"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported OS
check_os() {
    print_status "Checking operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Linux detected"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "macOS detected"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check for required system dependencies
check_system_deps() {
    print_status "Checking system dependencies..."
    
    # Check for Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 20+ first."
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version $NODE_VERSION is too old. Please install Node.js 18+ or 20+."
        exit 1
    fi
    print_success "Node.js $(node --version) found"
    
    # Check for Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    print_success "Python $PYTHON_VERSION found"
    
    # Check for pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip first."
        exit 1
    fi
    print_success "pip3 found"
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    if [[ "$OS" == "macos" ]]; then
        # Check for Homebrew
        if ! command -v brew &> /dev/null; then
            print_warning "Homebrew not found. Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        # Install FFmpeg
        if ! command -v ffmpeg &> /dev/null; then
            print_status "Installing FFmpeg..."
            brew install ffmpeg
        fi
        
        # Install ExifTool (recommended)
        if ! command -v exiftool &> /dev/null; then
            print_status "Installing ExifTool..."
            brew install exiftool
        fi
        
        # Install Redis (optional)
        if ! command -v redis-server &> /dev/null; then
            print_status "Installing Redis..."
            brew install redis
        fi
        
        # Install libmagic
        if ! brew list libmagic &> /dev/null; then
            print_status "Installing libmagic..."
            brew install libmagic
        fi
        
    elif [[ "$OS" == "linux" ]]; then
        # Update package list
        print_status "Updating package list..."
        sudo apt update
        
        # Install FFmpeg
        if ! command -v ffmpeg &> /dev/null; then
            print_status "Installing FFmpeg..."
            sudo apt install -y ffmpeg
        fi
        
        # Install ExifTool (recommended)
        if ! command -v exiftool &> /dev/null; then
            print_status "Installing ExifTool..."
            sudo apt install -y libimage-exiftool-perl
        fi
        
        # Install Redis (optional)
        if ! command -v redis-server &> /dev/null; then
            print_status "Installing Redis..."
            sudo apt install -y redis-server
        fi
        
        # Install libmagic
        print_status "Installing libmagic..."
        sudo apt install -y libmagic1 libmagic-dev
    fi
    
    print_success "System dependencies installed"
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Python dependencies installed"
}

# Install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js dependencies..."
    
    npm install
    
    print_success "Node.js dependencies installed"
}

# Setup environment variables
setup_env() {
    print_status "Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from .env.example"
            print_warning "Please edit .env file with your configuration"
        else
            print_warning "No .env.example file found. Creating basic .env file..."
            cat > .env << EOF
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/metaextract

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Performance settings
MAX_CONCURRENT_EXTRACTIONS=10
CACHE_TTL_HOURS=24
MAX_FILE_SIZE_MB=1000

# DodoPayments (for production)
DODO_PAYMENTS_API_KEY=your_api_key
DODO_WEBHOOK_SECRET=your_webhook_secret
DODO_ENV=test

# Node environment
NODE_ENV=development
PORT=3000
EOF
            print_success "Created basic .env file"
        fi
    else
        print_success ".env file already exists"
    fi
}

# Build the application
build_app() {
    print_status "Building application..."
    
    npm run build
    
    print_success "Application built successfully"
}

# Start services
start_services() {
    print_status "Starting services..."
    
    # Start Redis if available
    if command -v redis-server &> /dev/null; then
        if ! pgrep -x "redis-server" > /dev/null; then
            print_status "Starting Redis server..."
            if [[ "$OS" == "macos" ]]; then
                brew services start redis
            elif [[ "$OS" == "linux" ]]; then
                sudo systemctl start redis-server
            fi
        fi
        print_success "Redis server is running"
    else
        print_warning "Redis not available - caching will be disabled"
    fi
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    if [ -f "drizzle.config.ts" ]; then
        npm run db:push
        print_success "Database migrations completed"
    else
        print_warning "No database configuration found - skipping migrations"
    fi
}

# Test the installation
test_installation() {
    print_status "Testing installation..."
    
    # Test Python metadata engine
    if [ -f "server/extractor/metadata_engine_enhanced.py" ]; then
        print_status "Testing Python metadata engine..."
        source venv/bin/activate
        python3 server/extractor/metadata_engine_enhanced.py --help > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            print_success "Python metadata engine is working"
        else
            print_warning "Python metadata engine test failed"
        fi
    fi
    
    # Test Node.js build
    if [ -f "dist/index.cjs" ]; then
        print_success "Node.js build is ready"
    else
        print_warning "Node.js build not found - run 'npm run build' manually"
    fi
}

# Main deployment function
main() {
    echo
    print_status "Starting MetaExtract deployment..."
    echo
    
    check_os
    check_system_deps
    
    # Ask user what to install
    echo
    echo "What would you like to do?"
    echo "1) Full installation (recommended for new setups)"
    echo "2) Install system dependencies only"
    echo "3) Install application dependencies only"
    echo "4) Build and start services"
    echo "5) Test installation"
    echo
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            install_system_deps
            install_python_deps
            install_node_deps
            setup_env
            build_app
            run_migrations
            start_services
            test_installation
            ;;
        2)
            install_system_deps
            ;;
        3)
            install_python_deps
            install_node_deps
            setup_env
            ;;
        4)
            build_app
            run_migrations
            start_services
            ;;
        5)
            test_installation
            ;;
        *)
            print_error "Invalid choice. Exiting."
            exit 1
            ;;
    esac
    
    echo
    print_success "Deployment completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Set up your database (PostgreSQL recommended)"
    echo "3. Configure DodoPayments for production"
    echo "4. Run 'npm run dev' to start development server"
    echo "5. Run 'npm start' to start production server"
    echo
    echo "For more information, see README.md and IMPLEMENTATION_PROGRESS.md"
    echo
}

# Run main function
main "$@"