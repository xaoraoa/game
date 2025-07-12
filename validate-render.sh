#!/bin/bash

# Render Deployment Validation Script
# Checks if the project is ready for Render deployment

set -e

echo "🔍 Render Deployment Validation"
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

errors=0
warnings=0

# Check if render.yaml exists
echo -e "${BLUE}📋 Checking configuration files...${NC}"
if [ -f "render.yaml" ]; then
    echo -e "${GREEN}✅ render.yaml found${NC}"
else
    echo -e "${RED}❌ render.yaml not found${NC}"
    errors=$((errors + 1))
fi

# Check frontend package.json
if [ -f "frontend/package.json" ]; then
    echo -e "${GREEN}✅ frontend/package.json found${NC}"
    
    # Check for required dependencies
    if grep -q "@irys/sdk" frontend/package.json; then
        echo -e "${GREEN}✅ Irys SDK dependency found${NC}"
    else
        echo -e "${RED}❌ Irys SDK dependency missing${NC}"
        errors=$((errors + 1))
    fi
    
    # Check build script
    if grep -q '"build"' frontend/package.json; then
        echo -e "${GREEN}✅ Build script found in package.json${NC}"
    else
        echo -e "${RED}❌ Build script missing in package.json${NC}"
        errors=$((errors + 1))
    fi
else
    echo -e "${RED}❌ frontend/package.json not found${NC}"
    errors=$((errors + 1))
fi

# Check backend requirements.txt
if [ -f "backend/requirements.txt" ]; then
    echo -e "${GREEN}✅ backend/requirements.txt found${NC}"
    
    # Check for required dependencies
    if grep -q "fastapi" backend/requirements.txt; then
        echo -e "${GREEN}✅ FastAPI dependency found${NC}"
    else
        echo -e "${RED}❌ FastAPI dependency missing${NC}"
        errors=$((errors + 1))
    fi
    
    if grep -q "mangum" backend/requirements.txt; then
        echo -e "${GREEN}✅ Mangum dependency found${NC}"
    else
        echo -e "${RED}❌ Mangum dependency missing${NC}"
        errors=$((errors + 1))
    fi
else
    echo -e "${RED}❌ backend/requirements.txt not found${NC}"
    errors=$((errors + 1))
fi

# Check backend entry point
if [ -f "backend/index.py" ]; then
    echo -e "${GREEN}✅ backend/index.py found${NC}"
    
    if grep -q "handler = Mangum" backend/index.py; then
        echo -e "${GREEN}✅ Mangum handler found${NC}"
    else
        echo -e "${RED}❌ Mangum handler not found in index.py${NC}"
        errors=$((errors + 1))
    fi
else
    echo -e "${RED}❌ backend/index.py not found${NC}"
    errors=$((errors + 1))
fi

# Check for _redirects file
if [ -f "frontend/public/_redirects" ]; then
    echo -e "${GREEN}✅ _redirects file found${NC}"
else
    echo -e "${YELLOW}⚠️  _redirects file not found (recommended for SPA routing)${NC}"
    warnings=$((warnings + 1))
fi

# Check environment files
echo -e "${BLUE}🔧 Checking environment configuration...${NC}"

if [ -f ".env.render" ]; then
    echo -e "${GREEN}✅ .env.render template found${NC}"
else
    echo -e "${YELLOW}⚠️  .env.render template missing${NC}"
    warnings=$((warnings + 1))
fi

# Check for health endpoint in backend
if grep -q "/api/health" backend/server.py; then
    echo -e "${GREEN}✅ Health check endpoint found${NC}"
else
    echo -e "${RED}❌ Health check endpoint missing${NC}"
    errors=$((errors + 1))
fi

# Check deployment script
if [ -f "deploy-render.sh" ]; then
    if [ -x "deploy-render.sh" ]; then
        echo -e "${GREEN}✅ Deployment script found and executable${NC}"
    else
        echo -e "${YELLOW}⚠️  Deployment script found but not executable${NC}"
        echo "   Run: chmod +x deploy-render.sh"
        warnings=$((warnings + 1))
    fi
else
    echo -e "${YELLOW}⚠️  Deployment script not found${NC}"
    warnings=$((warnings + 1))
fi

# Project structure validation
echo -e "${BLUE}📁 Validating project structure...${NC}"

required_dirs=("frontend" "backend" "frontend/src" "frontend/public")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅ Directory $dir exists${NC}"
    else
        echo -e "${RED}❌ Directory $dir missing${NC}"
        errors=$((errors + 1))
    fi
done

# Summary
echo ""
echo "📊 Validation Summary"
echo "===================="

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical checks passed!${NC}"
    if [ $warnings -eq 0 ]; then
        echo -e "${GREEN}✨ Project is ready for Render deployment${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Push your code to GitHub"
        echo "2. Run ./deploy-render.sh"
        echo "3. Configure environment variables in Render Dashboard"
    else
        echo -e "${YELLOW}⚠️  $warnings warning(s) found - consider addressing them${NC}"
        echo -e "${GREEN}✅ Project can be deployed to Render${NC}"
    fi
else
    echo -e "${RED}❌ $errors critical error(s) found${NC}"
    echo -e "${RED}🚨 Please fix errors before deploying${NC}"
    exit 1
fi

if [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $warnings warning(s) found${NC}"
fi

echo ""
echo -e "${BLUE}🔗 Useful resources:${NC}"
echo "• Render Documentation: https://render.com/docs"
echo "• MongoDB Atlas: https://cloud.mongodb.com"
echo "• Environment Setup: .env.render"