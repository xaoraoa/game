#!/bin/bash

# Render Build Script for Irys Reflex Backend
# Handles both Python and Node.js dependencies

set -e  # Exit on any error

echo "🚀 Starting Render build process for Irys Reflex Backend..."

# Navigate to backend directory
cd backend

echo "📦 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "🟢 Node.js dependency installation..."
# Check if Node.js is available
if command -v node &> /dev/null; then
    echo "✅ Node.js version: $(node --version)"
    echo "✅ npm version: $(npm --version)"
else
    echo "❌ Node.js not found! This will cause module import errors."
    exit 1
fi

# Install Node.js dependencies
echo "📦 Installing Node.js packages..."
npm install

echo "🔍 Verifying critical dependencies..."
# Verify critical Node.js packages are installed
if [ -d "node_modules/@irys/upload" ]; then
    echo "✅ @irys/upload package installed successfully"
else
    echo "❌ @irys/upload package not found!"
    exit 1
fi

if [ -d "node_modules/@irys/upload-ethereum" ]; then
    echo "✅ @irys/upload-ethereum package installed successfully"
else
    echo "❌ @irys/upload-ethereum package not found!"
    exit 1
fi

echo "🎯 Dependency verification completed successfully!"

# Test Node.js script can load modules
echo "🧪 Testing Node.js module imports..."
node -e "
try {
    const { Uploader } = require('@irys/upload');
    const { Ethereum } = require('@irys/upload-ethereum');
    console.log('✅ All critical Node.js modules can be imported successfully');
} catch (error) {
    console.error('❌ Module import test failed:', error.message);
    process.exit(1);
}
"

echo "🎉 Render build completed successfully!"
echo "📋 Build Summary:"
echo "   - Python dependencies: ✅ Installed"
echo "   - Node.js dependencies: ✅ Installed" 
echo "   - Module imports: ✅ Verified"
echo "   - Ready for deployment: ✅ Yes"