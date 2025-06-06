#!/bin/bash

# GitHub Actions Local Runner (act) Installation Script for Ubuntu
# This script installs Docker (if needed) and act tool for local GitHub Actions testing

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if user is in docker group
user_in_docker_group() {
    groups $USER | grep -q docker
}

# Function to install Docker
install_docker() {
    print_status "Installing Docker..."
    
    # Update package index
    sudo apt update
    
    # Install required packages
    sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update package index again
    sudo apt update
    
    # Install Docker
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Start and enable Docker service
    sudo systemctl start docker
    sudo systemctl enable docker
    
    print_success "Docker installed successfully!"
}

# Function to setup Docker for current user
setup_docker_user() {
    print_status "Setting up Docker for current user..."
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    print_warning "User added to docker group. You may need to log out and back in for changes to take effect."
    print_warning "Alternatively, run 'newgrp docker' to apply group changes in current session."
}

# Function to install act
install_act() {
    print_status "Installing act..."
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Download and install act
    curl -L https://github.com/nektos/act/releases/latest/download/act_Linux_x86_64.tar.gz | tar -xz
    
    # Move to /usr/local/bin
    sudo mv act /usr/local/bin/
    sudo chmod +x /usr/local/bin/act
    
    # Clean up
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
    
    print_success "act installed successfully!"
}

# Function to create act configuration
create_act_config() {
    print_status "Creating act configuration..."
    
    # Create config directory
    mkdir -p ~/.config/act
    
    # Create actrc file with optimized settings
    cat > ~/.config/act/actrc << 'EOF'
-P ubuntu-latest=catthehacker/ubuntu:act-latest
-P ubuntu-22.04=catthehacker/ubuntu:act-22.04
-P ubuntu-20.04=catthehacker/ubuntu:act-20.04
-P ubuntu-18.04=catthehacker/ubuntu:act-18.04
--container-daemon-socket /var/run/docker.sock
EOF
    
    print_success "act configuration created at ~/.config/act/actrc"
}

# Function to test installation
test_installation() {
    print_status "Testing installation..."
    
    # Test Docker
    if command_exists docker; then
        print_success "Docker is available"
        if docker ps >/dev/null 2>&1; then
            print_success "Docker daemon is running and accessible"
        else
            print_warning "Docker daemon is running but may require 'sudo' or group membership"
        fi
    else
        print_error "Docker is not available"
        return 1
    fi
    
    # Test act
    if command_exists act; then
        ACT_VERSION=$(act --version 2>/dev/null || echo "unknown")
        print_success "act is installed: $ACT_VERSION"
    else
        print_error "act is not available"
        return 1
    fi
    
    print_success "Installation test completed!"
}

# Function to display usage instructions
show_usage_instructions() {
    print_status "Usage Instructions:"
    echo ""
    echo "Basic commands:"
    echo "  act                    # Run all workflows"
    echo "  act -l                 # List available workflows"
    echo "  act push               # Run workflows triggered by push event"
    echo "  act pull_request       # Run workflows triggered by PR event"
    echo "  act -j job_name        # Run specific job"
    echo "  act --dryrun           # Show what would be executed without running"
    echo "  act -v                 # Verbose output"
    echo ""
    echo "Example workflow testing:"
    echo "  cd /path/to/your/repo"
    echo "  act -l                 # List workflows in current repo"
    echo "  act                    # Run all workflows"
    echo ""
    echo "For more information: https://github.com/nektos/act"
}

# Main installation function
main() {
    echo "================================================="
    echo "GitHub Actions Local Runner (act) Installer"
    echo "================================================="
    echo ""
    
    # Check if running on Ubuntu
    if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
        print_warning "This script is designed for Ubuntu. It may work on other Debian-based systems."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check for sudo privileges
    if ! sudo -n true 2>/dev/null; then
        print_status "This script requires sudo privileges for installation."
        sudo -v
    fi
    
    # Install Docker if not present
    if ! command_exists docker; then
        print_status "Docker not found. Installing Docker..."
        install_docker
    else
        print_success "Docker is already installed"
    fi
    
    # Setup Docker user permissions if needed
    if ! user_in_docker_group; then
        setup_docker_user
        NEED_RELOGIN=true
    else
        print_success "User is already in docker group"
    fi
    
    # Install act if not present
    if ! command_exists act; then
        install_act
    else
        print_success "act is already installed"
        ACT_VERSION=$(act --version 2>/dev/null || echo "unknown")
        print_status "Current version: $ACT_VERSION"
        
        read -p "Reinstall act? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_act
        fi
    fi
    
    # Create configuration
    if [ ! -f ~/.config/act/actrc ]; then
        create_act_config
    else
        print_success "act configuration already exists"
        read -p "Recreate configuration? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_act_config
        fi
    fi
    
    # Test installation
    test_installation
    
    echo ""
    echo "================================================="
    print_success "Installation completed successfully!"
    echo "================================================="
    
    if [ "$NEED_RELOGIN" = true ]; then
        echo ""
        print_warning "IMPORTANT: You need to log out and back in (or run 'newgrp docker')"
        print_warning "for Docker group changes to take effect."
    fi
    
    echo ""
    show_usage_instructions
}

# Run main function
main "$@" 