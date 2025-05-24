#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section headers
print_section() {
    echo -e "\n${GREEN}=== $1 ===${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root or with sudo"
    exit 1
fi

# Check if running on WSL
if ! grep -q WSL /proc/version; then
    echo "This script is intended to run on WSL2"
    exit 1
fi

print_section "MySQL Installation and Configuration for WSL2"

# Get user inputs
read -p "Enter MySQL root password: " -s MYSQL_ROOT_PASSWORD
echo
read -p "Enter new MySQL username: " MYSQL_USER
read -p "Enter password for $MYSQL_USER: " -s MYSQL_USER_PASSWORD
echo
read -p "Allow remote access from any host? (y/n, default: n): " ALLOW_REMOTE_ACCESS

# Set default values
ALLOW_REMOTE_ACCESS=${ALLOW_REMOTE_ACCESS:-n}
BIND_ADDRESS="127.0.0.1"

if [[ "$ALLOW_REMOTE_ACCESS" =~ ^[Yy]$ ]]; then
    BIND_ADDRESS="0.0.0.0"
    echo -e "${YELLOW}Warning: Allowing remote access from any host${NC}"
fi

print_section "Updating package lists"
apt-get update

# Install MySQL Server non-interactively
export DEBIAN_FRONTEND=noninteractive
if ! command_exists mysql; then
    print_section "Installing MySQL Server"
    apt-get install -y mysql-server
fi

# Start MySQL service
print_section "Starting MySQL Service"
systemctl start mysql
systemctl enable mysql

# Secure MySQL installation
echo -e "\n${YELLOW}Securing MySQL installation...${NC}"
mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}'; FLUSH PRIVILEGES;"

# Create mysql_secure_installation.sql file
cat > /tmp/mysql_secure_installation.sql << EOF
-- Remove anonymous users
DELETE FROM mysql.user WHERE User='';
-- Disallow root login remotely
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
-- Remove test database
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%';
-- Reload privilege tables
FLUSH PRIVILEGES;
EOF

# Execute secure installation
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" < /tmp/mysql_secure_installation.sql
rm /tmp/mysql_secure_installation.sql

# Configure MySQL for remote access
print_section "Configuring MySQL for remote access"

# Create MySQL configuration file
cat > /etc/mysql/conf.d/mysql_wsl2.cnf << EOF
[mysqld]
bind-address = ${BIND_ADDRESS}
skip-name-resolve
EOF

# Create user and grant privileges
print_section "Creating MySQL user and granting privileges"
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<EOF
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_USER_PASSWORD}';
GRANT ALL PRIVILEGES ON *.* TO '${MYSQL_USER}'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

# Restart MySQL to apply changes
print_section "Restarting MySQL service"
systemctl restart mysql

# Get WSL2 IP address
WSL_IP=$(hostname -I | awk '{print $1}')

print_section "MySQL Setup Complete!"
echo "MySQL has been successfully configured with the following settings:"
echo -e "${YELLOW}Root password:${NC} [as provided]"
echo -e "${YELLOW}New user:${NC} ${MYSQL_USER}"
echo -e "${YELLOW}User password:${NC} [as provided]"
echo -e "${YELLOW}Bind address:${NC} ${BIND_ADDRESS}"
echo -e "${YELLOW}WSL2 IP address:${NC} ${WSL_IP}"

echo -e "\n${GREEN}To connect from Windows:${NC}"
echo "1. Install MySQL Workbench or MySQL Shell"
echo "2. Use the following connection details:"
echo "   - Host: ${WSL_IP} or localhost"
echo "   - Port: 3306"
echo "   - Username: ${MYSQL_USER}"
echo "   - Password: [your provided password]"

echo -e "\n${YELLOW}Note:${NC} If you can't connect, check Windows Firewall settings to allow port 3306."
