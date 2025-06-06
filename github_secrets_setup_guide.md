# 🔑 GitHub Secrets Setup Guide

This guide shows you how to configure the required secrets for your CI/CD pipeline.

## 📋 Required Secrets

Your workflow needs these 12 secrets across 3 environments:

| Environment | Required Secrets |
|-------------|------------------|
| **🧪 Staging** | `STAGING_SSH_KEY`, `STAGING_HOST`, `STAGING_USER`, `STAGING_PATH` |
| **🚀 Production** | `PRODUCTION_SSH_KEY`, `PRODUCTION_HOST`, `PRODUCTION_USER`, `PRODUCTION_PATH` |
| **🛠️ Development** | `DEV_SSH_KEY`, `DEV_HOST`, `DEV_USER`, `DEV_PATH` |

## 🚀 Method 1: Automated Setup (Recommended)

### Prerequisites:
```bash
# 1. Install GitHub CLI
sudo apt update
sudo apt install gh

# 2. Authenticate with GitHub
gh auth login
# Follow the prompts to authenticate
```

### Run the Setup Script:
```bash
# Make sure you're in your project directory
cd /path/to/your/project

# Run the automated setup script
./setup_github_secrets.sh
```

The script will:
- ✅ Check if you're authenticated with GitHub
- ✅ Guide you through each secret configuration
- ✅ Show examples for each value
- ✅ Handle existing secrets (ask before overwriting)
- ✅ Provide helpful tips for SSH keys

## 🖱️ Method 2: Manual Setup (GitHub Web Interface)

1. **Go to your GitHub repository**
2. **Click Settings → Secrets and variables → Actions**
3. **Click "New repository secret"**
4. **Add each secret one by one:**

### Staging Environment:
```
Secret Name: STAGING_SSH_KEY
Value: [Paste your private SSH key from ~/.ssh/id_ed25519]

Secret Name: STAGING_HOST  
Value: staging.yoursite.com (or IP like 192.168.1.100)

Secret Name: STAGING_USER
Value: deploy

Secret Name: STAGING_PATH
Value: /var/www/staging
```

### Production Environment:
```
Secret Name: PRODUCTION_SSH_KEY
Value: [Paste your private SSH key from ~/.ssh/id_ed25519]

Secret Name: PRODUCTION_HOST
Value: yoursite.com (or IP like 192.168.1.101)

Secret Name: PRODUCTION_USER  
Value: deploy

Secret Name: PRODUCTION_PATH
Value: /var/www/html
```

### Development Environment:
```
Secret Name: DEV_SSH_KEY
Value: [Paste your private SSH key from ~/.ssh/id_ed25519]

Secret Name: DEV_HOST
Value: dev.yoursite.com (or IP like 192.168.1.102)

Secret Name: DEV_USER
Value: deploy

Secret Name: DEV_PATH
Value: /var/www/dev
```

## 🔑 Getting SSH Keys

If you don't have SSH keys yet, generate them on each server:

```bash
# On each server (staging, production, development):
sudo su - deploy
ssh-keygen -t ed25519 -C "github-actions-$(hostname)" -f ~/.ssh/id_ed25519 -N ""

# Display the private key (copy this to GitHub secrets):
cat ~/.ssh/id_ed25519

# Add public key to authorized_keys:
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## ✅ Verify Setup

### Using GitHub CLI:
```bash
# List all secrets to verify they're set
gh secret list

# Should show something like:
# STAGING_SSH_KEY     Updated 2024-01-01
# STAGING_HOST        Updated 2024-01-01
# STAGING_USER        Updated 2024-01-01
# ... etc
```

### Using GitHub Web Interface:
Go to **Settings → Secrets and variables → Actions** and verify all 12 secrets are listed.

## 🧪 Test Your Setup

1. **Go to your GitHub repository**
2. **Click Actions → Frontend CI/CD → Run workflow**
3. **Choose:**
   - Environment: `staging`
   - Branch: `dev`
   - Skip tests: `true` (for faster testing)
4. **Click "Run workflow"**
5. **Watch the deployment logs**

Expected success output:
```
🚀 Deploying to STAGING environment
Target: deploy@staging.yoursite.com:/var/www/staging
sending incremental file list
✅ Successfully deployed to STAGING!
🌐 Visit: https://staging.yoursite.com
```

## 🛠️ Common Issues

### SSH Key Format Error:
Make sure to include the full key including headers:
```
-----BEGIN OPENSSH PRIVATE KEY-----
[key content]
-----END OPENSSH PRIVATE KEY-----
```

### Permission Denied:
- Ensure the deploy user exists on your server
- Verify SSH key permissions (600 for private key)
- Check that the public key is in `~/.ssh/authorized_keys`

### Host Key Verification Failed:
The workflow automatically handles this, but if you see this error:
```bash
# On your server, check SSH service is running:
sudo systemctl status ssh
```

## 📚 Related Files

- `frontend_deploy_wiki.md` - Complete server setup guide
- `.github/workflows/frontend-ci.yml` - The workflow that uses these secrets
- `setup_github_secrets.sh` - Automated script for setting secrets 