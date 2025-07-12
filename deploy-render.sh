#!/bin/bash

# Render Deployment Helper Script for Irys Reflex
# This script helps deploy the Irys Reflex app to Render.com

set -e

echo "🚀 Irys Reflex - Render Deployment Helper"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if render CLI is installed
if ! command -v render &> /dev/null; then
    echo -e "${YELLOW}⚠️  Render CLI not found. Installing...${NC}"
    echo "Please choose your installation method:"
    echo "1. macOS (using Homebrew): brew install render-cli"
    echo "2. npm: npm install -g @render/cli"
    echo "3. Direct download: https://render.com/docs/cli"
    echo ""
    read -p "Install now? (y/N): " install_cli
    if [[ $install_cli =~ ^[Yy]$ ]]; then
        if command -v brew &> /dev/null; then
            brew install render-cli
        elif command -v npm &> /dev/null; then
            npm install -g @render/cli
        else
            echo -e "${RED}❌ Please install Render CLI manually from https://render.com/docs/cli${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Render CLI is required for deployment${NC}"
        exit 1
    fi
fi

# Check if user is logged in
echo -e "${BLUE}🔐 Checking Render CLI authentication...${NC}"
if ! render auth whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Render CLI${NC}"
    echo "Please log in to your Render account:"
    render auth login
fi

# Validate render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo -e "${RED}❌ render.yaml not found in current directory${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo -e "${GREEN}✅ Render CLI is ready${NC}"

# Environment setup check
echo -e "${BLUE}🔧 Environment Setup Checklist${NC}"
echo "==============================="

echo "Please ensure you have the following ready:"
echo ""
echo "📋 MongoDB Atlas:"
echo "   • Free cluster created at https://cloud.mongodb.com"
echo "   • Database user created"
echo "   • IP whitelist configured (0.0.0.0/0 for all)"
echo "   • Connection string ready"
echo ""
echo "🔑 Irys Configuration:"
echo "   • Private key for Arbitrum Sepolia testnet"
echo "   • Testnet ETH in your wallet"
echo ""

read -p "✅ Do you have all the above ready? (y/N): " env_ready
if [[ ! $env_ready =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  Please complete the environment setup first${NC}"
    echo "Refer to .env.render for detailed instructions"
    exit 1
fi

# Deploy services
echo -e "${BLUE}🚀 Deploying to Render...${NC}"
echo "========================="

echo -e "${YELLOW}📤 Creating services from render.yaml...${NC}"
render services create --apply render.yaml

echo ""
echo -e "${GREEN}🎉 Deployment initiated successfully!${NC}"
echo "======================================"

echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "1. Go to https://dashboard.render.com"
echo "2. Configure environment variables for both services:"
echo ""
echo -e "${YELLOW}   Frontend (irys-reflex-frontend):${NC}"
echo "   • REACT_APP_PRIVATE_KEY=your_private_key_here"
echo ""
echo -e "${YELLOW}   Backend (irys-reflex-backend):${NC}"
echo "   • MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/..."
echo ""
echo "3. Wait for builds to complete (5-10 minutes)"
echo "4. Access your app at:"
echo "   • Frontend: https://irys-reflex-frontend.onrender.com"
echo "   • Backend API: https://irys-reflex-backend.onrender.com/api/health"
echo ""
echo -e "${GREEN}🔗 Useful Links:${NC}"
echo "• Render Dashboard: https://dashboard.render.com"
echo "• Environment Variables Guide: .env.render"
echo "• MongoDB Atlas: https://cloud.mongodb.com"
echo ""
echo -e "${GREEN}✨ Happy deploying!${NC}"