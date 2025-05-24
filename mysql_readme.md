# MySQL on WSL2 with Windows Access

This guide explains how to install MySQL on WSL2 (Ubuntu) and access it from Windows.

## Table of Contents
- [Installation on WSL2](#installation-on-wsl2)
- [Securing MySQL](#securing-mysql)
- [Starting MySQL Service](#starting-mysql-service)
- [Configuring Remote Access](#configuring-remote-access)
- [Creating a MySQL User](#creating-a-mysql-user)
- [Accessing from Windows](#accessing-from-windows)
- [Troubleshooting](#troubleshooting)

## Installation on WSL2

1. Open your WSL2 terminal (Ubuntu)
2. Update package lists:
   ```bash
   sudo apt update
   ```
3. Install MySQL Server:
   ```bash
   sudo apt install mysql-server
   ```
4. Set a root password when prompted.

## Securing MySQL

Run the security script:
```bash
sudo mysql_secure_installation
```

Follow the prompts to set security options. It's recommended to:
- Set a strong root password if not already set
- Remove anonymous users
- Disallow root login remotely
- Remove test database and access to it
- Reload privilege tables

## Starting MySQL Service

```bash
sudo service mysql start
sudo systemctl enable mysql
```

## Configuring Remote Access

1. Edit the MySQL configuration file:
   ```bash
   sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
   ```

2. Find the `bind-address` line and change it to:
   ```
   bind-address = 0.0.0.0
   ```

3. Save and exit (Ctrl+O, Enter, Ctrl+X)

4. Restart MySQL:
   ```bash
   sudo service mysql restart
   ```

## Creating a MySQL User

1. Log in to MySQL:
   ```bash
   sudo mysql -u root -p
   ```

2. Create a new user and grant privileges:
   ```sql
   CREATE USER 'username'@'%' IDENTIFIED BY 'your_strong_password';
   GRANT ALL PRIVILEGES ON *.* TO 'username'@'%' WITH GRANT OPTION;
   FLUSH PRIVILEGES;
   EXIT;
   ```

## Accessing from Windows

### Option 1: Using MySQL Workbench (Recommended)

1. Download and install [MySQL Workbench](https://dev.mysql.com/downloads/workbench/) on Windows
2. Open MySQL Workbench
3. Click the "+" icon next to "MySQL Connections"
4. Enter connection details:
   - Connection Name: WSL MySQL
   - Hostname: `localhost` (or your WSL2 IP)
   - Port: 3306
   - Username: The username you created
   - Password: The password you set

### Option 2: Using Command Line

1. Download and install [MySQL Shell](https://dev.mysql.com/downloads/shell/) on Windows
2. Open Command Prompt or PowerShell and connect:
   ```bash
   mysql -h localhost -P 3306 -u username -p
   ```

## Windows Firewall Configuration (If Needed)

If you have connection issues, allow the MySQL port through Windows Firewall:
1. Open Windows Defender Firewall with Advanced Security
2. Go to Inbound Rules > New Rule
3. Select Port > TCP > Specific local ports: 3306
4. Allow the connection
5. Name it "MySQL WSL Access"

## Troubleshooting

- **Connection refused**: 
  - Verify MySQL is running in WSL: `sudo service mysql status`
  - Check bind-address in config file is set to `0.0.0.0`
  
- **Access denied**: 
  - Double-check username and password
  - Verify user has proper privileges
  
- **Can't connect to MySQL server**:
  - Ensure MySQL service is running: `sudo service mysql status`
  - Check if port 3306 is listening: `sudo netstat -tulpn | grep 3306`

- **Firewall issues**:
  - Temporarily disable Windows Firewall to test if it's causing connection problems
  - Ensure WSL2 has proper network access in Windows Defender Firewall
