#!/bin/bash
# deploy.sh - One-command deployment script for Healthfirst Agent

set -e  # Exit on any error

echo "🚀 Starting Azure deployment for Healthfirst Agent..."

# Check Azure login
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure. Please run: az login --use-device-code"
    exit 1
fi

# Set correct subscription
echo "📋 Setting Azure subscription..."
az account set --subscription 6d963098-3d75-43e7-bb2f-3831c31df754

# Verify resource group access
echo "🔍 Verifying resource group access..."
if ! az group show --name furman_resource_group &> /dev/null; then
    echo "❌ Cannot access resource group 'furman_resource_group'. Please check permissions."
    exit 1
fi

# Check app service exists
echo "🔍 Checking app service status..."
APP_STATE=$(az webapp show --resource-group furman_resource_group --name healthfirstagent --query "state" -o tsv)
echo "📱 App current state: $APP_STATE"

# Add git remote if not exists
echo "🔗 Configuring git remote..."
git remote remove azure 2>/dev/null || true
git remote add azure https://furman@healthfirstagent.scm.azurewebsites.net/healthfirstagent.git

# Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    echo "📝 Found uncommitted changes, committing..."
    git add .
    git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" || true
fi

# Deploy to Azure
echo "📦 Pushing to Azure (this may take 5-10 minutes)..."
git push azure main

echo ""
echo "✅ Deployment initiated successfully!"
echo "🌐 Application URL: https://healthfirstagent.azurewebsites.net"
echo "📊 Monitor deployment logs with:"
echo "   az webapp log tail --resource-group furman_resource_group --name healthfirstagent"
echo ""
echo "🔍 Check deployment status:"
echo "   az webapp show --resource-group furman_resource_group --name healthfirstagent --query 'state'"
echo ""
echo "⏱️  Deployment typically takes 5-10 minutes to complete."