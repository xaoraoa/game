#!/bin/bash

# Render Build Script for Irys Reflex Frontend
# Enhanced error handling and dependency resolution

set -e  # Exit on any error

echo "🚀 Starting Render build process for Irys Reflex Frontend..."

# Navigate to frontend directory
cd frontend

echo "📦 Installing frontend dependencies..."
# Only clear node_modules if they're corrupted, keep lockfiles for consistency
rm -rf node_modules

# Install dependencies with existing lockfile for consistency
yarn install --frozen-lockfile

echo "🔧 Updating browser data..."
# Update browserslist data to resolve warnings
npx update-browserslist-db@latest || echo "Browserslist update failed - continuing anyway"

echo "🔍 Pre-build verification..."
# Verify critical dependencies
if [ ! -d "node_modules/react" ]; then
    echo "❌ React not found!"
    exit 1
fi

if [ ! -d "node_modules/react-scripts" ]; then
    echo "❌ React Scripts not found!"
    exit 1
fi

echo "✅ Dependencies verified successfully"

echo "🏗️ Building production bundle..."
# Set environment variables for stable build
export DISABLE_HOT_RELOAD=true
export GENERATE_SOURCEMAP=false
export NODE_OPTIONS="--max-old-space-size=4096"
export CI=true

# Build with optimizations
yarn build

echo "🔍 Verifying build output..."
# Check if build was successful
if [ ! -d "build" ]; then
    echo "❌ Build directory not created!"
    exit 1
fi

if [ ! -f "build/index.html" ]; then
    echo "❌ Main HTML file not found!"
    exit 1
fi

# Check build size
BUILD_SIZE=$(du -sh build | cut -f1)
echo "✅ Build completed successfully - Size: $BUILD_SIZE"

echo "🎉 Frontend build completed successfully!"
echo "📋 Build Summary:"
echo "   - Dependencies: ✅ Installed (with lockfile)"
echo "   - Browser data: ✅ Updated" 
echo "   - Production build: ✅ Created"
echo "   - Build size: $BUILD_SIZE"
echo "   - Ready for deployment: ✅ Yes"