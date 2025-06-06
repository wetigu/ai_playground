#!/bin/bash

# GitHub Secrets Setup Script for Frontend CI/CD
# This script uses GitHub CLI (gh) to configure all required secrets

set -e  # Exit on any error

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

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed!"
    print_status "Install it with: sudo apt install gh"
    print_status "Or visit: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    print_error "You are not authenticated with GitHub CLI!"
    print_status "Run: gh auth login"
    exit 1
fi

print_status "🚀 Setting up GitHub Secrets for Frontend CI/CD Pipeline"
echo

# Function to set secret with confirmation
set_secret() {
    local secret_name=$1
    local description=$2
    local example=$3
    
    echo -e "${YELLOW}📝 Setting: ${secret_name}${NC}"
    echo "Description: $description"
    echo "Example: $example"
    echo
    
    # Check if secret already exists
    if gh secret list | grep -q "^${secret_name}"; then
        print_warning "Secret '${secret_name}' already exists!"
        read -p "Do you want to update it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Skipping ${secret_name}"
            echo
            return
        fi
    fi
    
    # Prompt for secret value
    echo "Please enter the value for ${secret_name}:"
    if [[ $secret_name == *"SSH_KEY"* ]]; then
        echo "💡 Tip: Paste the entire private key including -----BEGIN OPENSSH PRIVATE KEY----- and -----END OPENSSH PRIVATE KEY-----"
        echo "📄 You can read the key from file with: cat ~/.ssh/id_ed25519"
        echo
    fi
    
    read -s -p "Value: " secret_value
    echo
    
    if [[ -z "$secret_value" ]]; then
        print_warning "Empty value provided. Skipping ${secret_name}"
        echo
        return
    fi
    
    # Set the secret
    echo "$secret_value" | gh secret set "$secret_name"
    
    if [ $? -eq 0 ]; then
        print_success "✅ Successfully set ${secret_name}"
    else
        print_error "❌ Failed to set ${secret_name}"
    fi
    echo
}

# Configuration prompts
echo "🔧 We'll now configure secrets for three environments:"
echo "   • 🧪 STAGING (for testing)"
echo "   • 🚀 PRODUCTION (for live site)"  
echo "   • 🛠️  DEVELOPMENT (for dev work)"
echo
echo "💡 If you don't have all environments ready, you can skip some and add them later."
echo

read -p "Do you want to continue? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    print_status "Setup cancelled by user"
    exit 0
fi

echo
print_status "🧪 === STAGING ENVIRONMENT SECRETS ==="
echo

# Staging Environment
set_secret "STAGING_SSH_KEY" \
    "Private SSH key for accessing staging server" \
    "Contents of ~/.ssh/id_ed25519 file"

set_secret "STAGING_HOST" \
    "Hostname or IP address of staging server" \
    "staging.yoursite.com or 192.168.1.100"

set_secret "STAGING_USER" \
    "Username for SSH access to staging server" \
    "deploy"

set_secret "STAGING_PATH" \
    "Full path where files should be deployed on staging server" \
    "/var/www/staging"

echo
print_status "🚀 === PRODUCTION ENVIRONMENT SECRETS ==="
echo

# Production Environment
set_secret "PRODUCTION_SSH_KEY" \
    "Private SSH key for accessing production server" \
    "Contents of ~/.ssh/id_ed25519 file"

set_secret "PRODUCTION_HOST" \
    "Hostname or IP address of production server" \
    "yoursite.com or 192.168.1.101"

set_secret "PRODUCTION_USER" \
    "Username for SSH access to production server" \
    "deploy"

set_secret "PRODUCTION_PATH" \
    "Full path where files should be deployed on production server" \
    "/var/www/html"

echo
print_status "🛠️ === DEVELOPMENT ENVIRONMENT SECRETS ==="
echo

# Development Environment
set_secret "DEV_SSH_KEY" \
    "Private SSH key for accessing development server" \
    "Contents of ~/.ssh/id_ed25519 file"

set_secret "DEV_HOST" \
    "Hostname or IP address of development server" \
    "dev.yoursite.com or 192.168.1.102"

set_secret "DEV_USER" \
    "Username for SSH access to development server" \
    "deploy"

set_secret "DEV_PATH" \
    "Full path where files should be deployed on development server" \
    "/var/www/dev"

echo
print_success "🎉 GitHub Secrets setup completed!"
echo
print_status "📋 Summary of what was configured:"
gh secret list | grep -E "(STAGING|PRODUCTION|DEV)_" | while read line; do
    echo "   ✅ $line"
done

echo
print_status "🧪 To test your setup:"
echo "   1. Go to your GitHub repository"
echo "   2. Click Actions → Frontend CI/CD → Run workflow"
echo "   3. Choose environment: staging"
echo "   4. Click 'Run workflow'"
echo
print_status "📚 For server setup instructions, see: frontend_deploy_wiki.md" 