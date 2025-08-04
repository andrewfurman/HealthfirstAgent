# Cloud Deployment Notes

## Azure Web App Deployment

### Prerequisites
- Azure CLI installed ✅
- Azure subscription access

### Login to Azure using Device Code
To authenticate with Azure using device code (convenient for remote/headless deployment):

```bash
az login --use-device-code
```

This will:
1. Display a device code and URL
2. Open your browser to https://microsoft.com/devicelogin
3. Enter the device code shown in terminal
4. Complete authentication in browser
5. Return authenticated session to CLI

### Deployment Commands

#### 1. Create Resource Group
```bash
az group create --name healthfirst-agent-rg --location "East US"
```

#### 2. Create App Service Plan
```bash
az appservice plan create --name healthfirst-agent-plan --resource-group healthfirst-agent-rg --sku B1 --is-linux
```

#### 3. Create Web App
```bash
az webapp create --resource-group healthfirst-agent-rg --plan healthfirst-agent-plan --name healthfirst-agent-app --runtime "PYTHON:3.11" --startup-file "main.py"
```

#### 4. Configure App Settings
```bash
# Set environment variables
az webapp config appsettings set --resource-group healthfirst-agent-rg --name healthfirst-agent-app --settings \
    OPENAI_API_KEY="your-openai-api-key" \
    DATABASE_URL="your-postgresql-connection-string" \
    FLASK_ENV="production" \
    PORT="8080"
```

#### 5. Deploy from Git
```bash
# Configure deployment from local git
az webapp deployment source config-local-git --name healthfirst-agent-app --resource-group healthfirst-agent-rg

# Add Azure remote and push
git remote add azure <deployment-url-from-previous-command>
git push azure main
```

### Database Setup
For production deployment, you'll need:

1. **Azure Database for PostgreSQL**:
```bash
az postgres server create --resource-group healthfirst-agent-rg --name healthfirst-db --location "East US" --admin-user dbadmin --admin-password <secure-password> --sku-name GP_Gen5_2
```

2. **Create Database**:
```bash
az postgres db create --resource-group healthfirst-agent-rg --server-name healthfirst-db --name healthfirstdb
```

3. **Configure Firewall** (allow Azure services):
```bash
az postgres server firewall-rule create --resource-group healthfirst-agent-rg --server healthfirst-db --name AllowAzureServices --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
```

### Environment Variables Required
- `OPENAI_API_KEY`: Your OpenAI API key for Realtime API access
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: Set to "production"
- `PORT`: Set to "8080" (Azure default)
- `SECRET_KEY`: Flask secret key for sessions

### Post-Deployment Steps
1. Run database migrations via Azure CLI or SSH
2. Upload plan data and documents
3. Test voice chat functionality
4. Configure custom domain (optional)
5. Set up SSL certificate
6. Configure monitoring and logging

### Scaling Considerations
- Use higher SKU plans (S or P tier) for production load
- Consider Azure Application Insights for monitoring
- Set up auto-scaling rules based on CPU/memory usage
- Use Azure CDN for static assets if needed

### Security Notes
- Store sensitive keys in Azure Key Vault
- Use managed identity for database connections
- Configure network security groups
- Enable HTTPS redirect
- Set up Web Application Firewall (WAF) if needed