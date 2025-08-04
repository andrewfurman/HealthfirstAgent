# Azure Deployment Guide
## Healthfirst Agent Application - Complete Developer Setup

> **Quick Start**: This guide provides everything needed for a developer to deploy and manage the Healthfirst Agent application on Azure from the CLI.

## Prerequisites

### Required Tools
```bash
# Install Azure CLI (macOS)
brew install azure-cli

# Install Azure CLI (Windows)
winget install -e --id Microsoft.AzureCLI

# Install Azure CLI (Linux)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Authentication Setup
```bash
# Login to Azure with device code (easiest for new developers)
az login --use-device-code

# Verify login
az account show
```

## Application Details
- **App Name**: healthfirstagent
- **Resource Group**: furman_resource_group
- **App Service Plan**: furman-rxclaims-plan
- **Location**: East US 2
- **Runtime**: Python 3.11 on Linux
- **URL**: https://healthfirstagent.azurewebsites.net

### Deployment Configuration

#### Git Deployment
- **Git Remote URL**: https://furman@healthfirstagent.scm.azurewebsites.net/healthfirstagent.git
- **Deployment Method**: Local Git
- **Branch**: main

#### Environment Variables
Currently deployed environment variables:
- `DATABASE_URL`: PostgreSQL connection string (Neon database)
- `OPENAI_API_KEY`: OpenAI API key for Realtime API access
- `PORT`: 8080 (Azure default)
- `FLASK_ENV`: production
- `WEBSITES_PORT`: 8000 (CRITICAL: Must match Gunicorn port)
- `SCM_DO_BUILD_DURING_DEPLOYMENT`: true
- `ORYX_PYTHON_PACKAGE_MANAGER`: poetry

**IMPORTANT**: Azure runs Gunicorn on port 8000 by default. The `WEBSITES_PORT` must be set to 8000 to match.

### Resource Identifiers

#### Subscription & Resources
- **Subscription ID**: 6d963098-3d75-43e7-bb2f-3831c31df754
- **Resource ID**: `/subscriptions/6d963098-3d75-43e7-bb2f-3831c31df754/resourceGroups/furman_resource_group/providers/Microsoft.Web/sites/healthfirstagent`
- **App Service Plan ID**: `/subscriptions/6d963098-3d75-43e7-bb2f-3831c31df754/resourceGroups/furman_resource_group/providers/Microsoft.Web/serverfarms/furman-rxclaims-plan`

#### Networking
- **Inbound IP**: 20.119.136.17
- **Outbound IPs**: 20.80.215.86,20.80.215.137,20.80.215.174,20.80.215.189,20.80.215.235,20.85.96.34,20.80.209.20,20.80.209.139,20.80.210.253,20.80.211.142,20.80.211.150,20.80.212.54,20.119.136.17
- **FTP Hostname**: ftps://waws-prod-bn1-239.ftp.azurewebsites.windows.net/site/wwwroot

## Complete Deployment Workflow

### Step 1: Environment Setup
```bash
# 1. Ensure you have the correct Azure subscription
az account set --subscription 6d963098-3d75-43e7-bb2f-3831c31df754

# 2. Verify resource group access
az group show --name furman_resource_group

# 3. Check app service exists
az webapp show --resource-group furman_resource_group --name healthfirstagent --query "state"
```

### Step 2: Configure Local Environment
```bash
# 1. Clone the repository (if not already done)
git clone <repository-url>
cd HealthfirstAgent

# 2. Set up Azure git remote (one-time setup)
git remote remove azure 2>/dev/null || true
git remote add azure https://furman@healthfirstagent.scm.azurewebsites.net/healthfirstagent.git

# 3. Verify remote is added
git remote -v
```

### Step 3: Deploy Environment Variables
```bash
# Deploy all required environment variables at once
az webapp config appsettings set --resource-group furman_resource_group --name healthfirstagent --settings \
    DATABASE_URL="postgresql://neondb_owner:npg_Qucx6nvo0wHj@ep-orange-voice-a5tglure.us-east-2.aws.neon.tech/neondb?sslmode=require" \
    OPENAI_API_KEY="your-openai-api-key-here" \
    PORT="8080" \
    FLASK_ENV="production" \
    WEBSITES_PORT="8000" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    ORYX_PYTHON_PACKAGE_MANAGER="poetry"

# Set custom startup command (critical for proper deployment)
az webapp config set --resource-group furman_resource_group --name healthfirstagent \
    --startup-file "gunicorn --bind 0.0.0.0:8000 main:app"

# Verify environment variables are set
az webapp config appsettings list --resource-group furman_resource_group --name healthfirstagent --output table
```

### Step 4: Deploy Application Code
```bash
# 1. Ensure all changes are committed
git add .
git commit -m "Deploy to Azure: $(date)"

# 2. Deploy to Azure (this takes 5-10 minutes)
git push azure main

# 3. Monitor deployment progress
az webapp log tail --resource-group furman_resource_group --name healthfirstagent
```

### Step 5: Verify Deployment
```bash
# 1. Check app status
az webapp show --resource-group furman_resource_group --name healthfirstagent --query "state"

# 2. Test the application
curl -I https://healthfirstagent.azurewebsites.net

# 3. View recent logs
az webapp log tail --resource-group furman_resource_group --name healthfirstagent --since 1h
```

## Quick Commands Reference

### Deployment Commands
```bash
# Quick redeploy (assumes git remote already configured)
git add . && git commit -m "Update $(date)" && git push azure main

# Force rebuild and deploy
az webapp restart --resource-group furman_resource_group --name healthfirstagent
git push azure main --force

# Deploy specific branch
git push azure feature-branch:main
```

### Environment Management
```bash
# View all current settings
az webapp config appsettings list --resource-group furman_resource_group --name healthfirstagent --output table

# Update single environment variable
az webapp config appsettings set --resource-group furman_resource_group --name healthfirstagent --settings "OPENAI_API_KEY=new-key-value"

# Remove environment variable
az webapp config appsettings delete --resource-group furman_resource_group --name healthfirstagent --setting-names "VARIABLE_NAME"
```

### Monitoring & Debugging
```bash
# Real-time log streaming
az webapp log tail --resource-group furman_resource_group --name healthfirstagent

# Download all logs
az webapp log download --resource-group furman_resource_group --name healthfirstagent --log-file logs.zip

# Check app metrics
az monitor metrics list --resource "/subscriptions/6d963098-3d75-43e7-bb2f-3831c31df754/resourceGroups/furman_resource_group/providers/Microsoft.Web/sites/healthfirstagent" --metric "Requests"

# Restart application
az webapp restart --resource-group furman_resource_group --name healthfirstagent
```

## Environment Variables Required

### Critical Variables (Must be set)
```bash
DATABASE_URL="postgresql://neondb_owner:npg_Qucx6nvo0wHj@ep-orange-voice-a5tglure.us-east-2.aws.neon.tech/neondb?sslmode=require"
OPENAI_API_KEY="sk-proj-..." # Your OpenAI API key
```

### Azure Configuration Variables (Pre-configured)
```bash
PORT="8080"                              # Azure default port (not used by our app)
FLASK_ENV="production"                   # Production environment
WEBSITES_PORT="8000"                     # CRITICAL: Must match Gunicorn port (8000)
SCM_DO_BUILD_DURING_DEPLOYMENT="true"   # Enable build during deployment
ORYX_PYTHON_PACKAGE_MANAGER="poetry"    # Use Poetry for dependencies
```

**Note**: The startup command is configured to: `gunicorn --bind 0.0.0.0:8000 main:app`

## One-Command Deployment Script

Create a deployment script for maximum ease:

```bash
#!/bin/bash
# deploy.sh - One-command deployment script

set -e  # Exit on any error

echo "🚀 Starting Azure deployment..."

# Check Azure login
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure. Please run: az login --use-device-code"
    exit 1
fi

# Set correct subscription
az account set --subscription 6d963098-3d75-43e7-bb2f-3831c31df754

# Add git remote if not exists
git remote remove azure 2>/dev/null || true
git remote add azure https://furman@healthfirstagent.scm.azurewebsites.net/healthfirstagent.git

# Commit and deploy
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" || true
echo "📦 Pushing to Azure..."
git push azure main

echo "✅ Deployment initiated! Check status at: https://healthfirstagent.azurewebsites.net"
echo "📊 Monitor logs with: az webapp log tail --resource-group furman_resource_group --name healthfirstagent"
```

**Usage:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### Current Deployment Status

**Application URL**: https://healthfirstagent.azurewebsites.net

#### Last Deployment Information
- **Status**: In Progress (Git push initiated)
- **Method**: Git push to Azure remote
- **Waiting on**: Azure build and deployment process to complete
- **Expected completion**: 5-10 minutes

#### Monitoring Deployment
```bash
# Check deployment logs
az webapp log tail --resource-group furman_resource_group --name healthfirstagent

# Or view logs in Azure Portal
# https://portal.azure.com -> App Services -> healthfirstagent -> Log stream
```

### Troubleshooting

#### Common Issues
1. **HTTP 503 Service Unavailable**: 
   - Check that `WEBSITES_PORT=8000` is set (must match Gunicorn port)
   - Verify startup command is set to `gunicorn --bind 0.0.0.0:8000 main:app`
   - Check logs for startup probe failures
2. **Build failures**: Check that all dependencies are in pyproject.toml
3. **Runtime errors**: Verify environment variables are set correctly
4. **Database connection**: Ensure DATABASE_URL is accessible from Azure
5. **API limits**: Monitor OpenAI API usage and rate limits

#### Log Access
- **Azure Portal**: https://portal.azure.com -> App Services -> healthfirstagent -> Logs
- **CLI**: `az webapp log tail --resource-group furman_resource_group --name healthfirstagent`
- **Download logs**: `az webapp log download --resource-group furman_resource_group --name healthfirstagent`

### Security Notes
- Application uses HTTPS (healthfirstagent.azurewebsites.net)
- Environment variables stored securely in Azure App Settings
- Database connection uses SSL/TLS encryption
- OpenAI API key secured in Azure configuration

### Scaling Information
- **Current Plan**: Basic (B1)
- **Auto-scaling**: Not enabled
- **Manual scaling**: Available through Azure Portal or CLI
- **Upgrade path**: Standard or Premium plans for production workloads