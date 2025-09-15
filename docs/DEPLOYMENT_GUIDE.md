# DCRI MCP Tools - Azure Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the DCRI MCP Tools server to Azure App Service with Key Vault integration.

## Prerequisites

- Azure subscription with appropriate permissions
- Azure CLI installed and configured
- Docker installed (optional, for container deployment)
- Python 3.11+ for local testing

## Deployment Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Azure App     │    │   Azure Key      │    │   Azure         │
│   Service       │    │   Vault          │    │   Monitor       │
│                 │◄──►│                  │    │                 │
│ - Flask App     │    │ - Secrets        │    │ - Logging       │
│ - Auto-scaling  │    │ - Certificates   │    │ - Metrics       │
│ - Load Balancer │    │ - Access Policies│    │ - Alerting      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Step 1: Create Azure Resources

### 1.1 Resource Group
```bash
# Create resource group
az group create --name rg-dcri-mcp-tools --location eastus
```

### 1.2 Key Vault
```bash
# Create Key Vault
az keyvault create \
  --name kv-dcri-mcp-tools-001 \
  --resource-group rg-dcri-mcp-tools \
  --location eastus \
  --sku standard
```

### 1.3 App Service Plan
```bash
# Create App Service Plan
az appservice plan create \
  --name plan-dcri-mcp-tools \
  --resource-group rg-dcri-mcp-tools \
  --location eastus \
  --sku B1 \
  --is-linux
```

### 1.4 Web App
```bash
# Create Web App
az webapp create \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --plan plan-dcri-mcp-tools \
  --runtime "PYTHON:3.11"
```

## Step 2: Configure Key Vault

### 2.1 Add Secrets
```bash
# Add application secrets
az keyvault secret set \
  --vault-name kv-dcri-mcp-tools-001 \
  --name "FLASK-SECRET-KEY" \
  --value "your-secret-key-here"

az keyvault secret set \
  --vault-name kv-dcri-mcp-tools-001 \
  --name "AZURE-CLIENT-ID" \
  --value "your-client-id"

az keyvault secret set \
  --vault-name kv-dcri-mcp-tools-001 \
  --name "AZURE-CLIENT-SECRET" \
  --value "your-client-secret"

az keyvault secret set \
  --vault-name kv-dcri-mcp-tools-001 \
  --name "AZURE-TENANT-ID" \
  --value "your-tenant-id"
```

### 2.2 Configure Access Policy
```bash
# Get Web App's managed identity
WEBAPP_PRINCIPAL_ID=$(az webapp identity assign \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --query principalId -o tsv)

# Set Key Vault access policy
az keyvault set-policy \
  --name kv-dcri-mcp-tools-001 \
  --object-id $WEBAPP_PRINCIPAL_ID \
  --secret-permissions get list
```

## Step 3: Configure App Service

### 3.1 Set Environment Variables
```bash
# Set Key Vault URI
az webapp config appsettings set \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --settings KEY_VAULT_URI="https://kv-dcri-mcp-tools-001.vault.azure.net/"

# Set Python version and startup command
az webapp config set \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --startup-file "gunicorn --bind 0.0.0.0:8000 server:app"
```

### 3.2 Configure Logging
```bash
# Enable application logs
az webapp log config \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --application-logging filesystem \
  --detailed-error-messages true \
  --failed-request-tracing true \
  --web-server-logging filesystem
```

## Step 4: Deploy Application

### 4.1 ZIP Deployment
```bash
# Create deployment package
zip -r deployment.zip . -x "*.git*" "*__pycache__*" "*.pyc" "venv/*" ".env*"

# Deploy to Azure
az webapp deploy \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --src-path deployment.zip \
  --type zip
```

### 4.2 Alternative: Git Deployment
```bash
# Configure Git deployment
az webapp deployment source config \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --repo-url https://github.com/your-org/dcri-mcp-tools.git \
  --branch main \
  --manual-integration
```

## Step 5: Post-Deployment Configuration

### 5.1 Custom Domain (Optional)
```bash
# Add custom domain
az webapp config hostname add \
  --webapp-name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --hostname mcp-tools.dcri.duke.edu
```

### 5.2 SSL Certificate
```bash
# Create managed SSL certificate
az webapp config ssl create \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --hostname mcp-tools.dcri.duke.edu
```

### 5.3 Scaling Configuration
```bash
# Configure auto-scaling
az monitor autoscale create \
  --resource-group rg-dcri-mcp-tools \
  --resource /subscriptions/{subscription-id}/resourceGroups/rg-dcri-mcp-tools/providers/Microsoft.Web/serverfarms/plan-dcri-mcp-tools \
  --name autoscale-dcri-mcp-tools \
  --min-count 1 \
  --max-count 5 \
  --count 2

# Add CPU scaling rule
az monitor autoscale rule create \
  --resource-group rg-dcri-mcp-tools \
  --autoscale-name autoscale-dcri-mcp-tools \
  --scale-out 2 \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale-in 1 \
  --condition "Percentage CPU < 30 avg 5m"
```

## Step 6: Validation Testing

### 6.1 Health Check
```bash
# Test health endpoint
curl https://app-dcri-mcp-tools-prod.azurewebsites.net/health
```

### 6.2 Tool Execution Test
```bash
# Test sample tool
curl -X POST https://app-dcri-mcp-tools-prod.azurewebsites.net/run_tool/test_echo \
  -H "Content-Type: application/json" \
  -d '{"text": "production test"}'
```

### 6.3 Load Testing
```bash
# Install Apache Bench (if not available)
sudo apt-get install apache2-utils

# Run load test
ab -n 100 -c 10 https://app-dcri-mcp-tools-prod.azurewebsites.net/health
```

## Step 7: Monitoring and Alerting

### 7.1 Application Insights
```bash
# Create Application Insights
az monitor app-insights component create \
  --app dcri-mcp-tools-insights \
  --location eastus \
  --resource-group rg-dcri-mcp-tools

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app dcri-mcp-tools-insights \
  --resource-group rg-dcri-mcp-tools \
  --query instrumentationKey -o tsv)

# Configure App Service
az webapp config appsettings set \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

### 7.2 Alerts
```bash
# Create alert for high CPU usage
az monitor metrics alert create \
  --name "High CPU Usage" \
  --resource-group rg-dcri-mcp-tools \
  --scopes /subscriptions/{subscription-id}/resourceGroups/rg-dcri-mcp-tools/providers/Microsoft.Web/sites/app-dcri-mcp-tools-prod \
  --condition "avg Percentage CPU > 80" \
  --description "Alert when CPU usage exceeds 80%"

# Create alert for high response time
az monitor metrics alert create \
  --name "High Response Time" \
  --resource-group rg-dcri-mcp-tools \
  --scopes /subscriptions/{subscription-id}/resourceGroups/rg-dcri-mcp-tools/providers/Microsoft.Web/sites/app-dcri-mcp-tools-prod \
  --condition "avg Response Time > 5" \
  --description "Alert when response time exceeds 5 seconds"
```

## Step 8: Security Hardening

### 8.1 Network Security
```bash
# Configure IP restrictions (adjust IP ranges as needed)
az webapp config access-restriction add \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --rule-name "Duke University" \
  --action Allow \
  --ip-address 152.3.0.0/16 \
  --priority 100
```

### 8.2 Authentication (Optional)
```bash
# Configure Azure AD authentication
az webapp auth update \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --enabled true \
  --action LoginWithAzureActiveDirectory \
  --aad-client-id your-aad-app-id \
  --aad-client-secret your-aad-client-secret \
  --aad-token-issuer-url https://sts.windows.net/your-tenant-id/
```

## Step 9: Backup and Recovery

### 9.1 Backup Configuration
```bash
# Create storage account for backups
az storage account create \
  --name stdcrimcptoolsbackup \
  --resource-group rg-dcri-mcp-tools \
  --location eastus \
  --sku Standard_LRS

# Configure automated backups
az webapp config backup create \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --storage-account-url "https://stdcrimcptoolsbackup.blob.core.windows.net/backups" \
  --frequency 1d \
  --retain-one true
```

## Step 10: Maintenance

### 10.1 Regular Updates
```bash
# Update application
az webapp deploy \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --src-path updated-deployment.zip \
  --type zip

# Restart application
az webapp restart \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools
```

### 10.2 Log Analysis
```bash
# View recent logs
az webapp log tail \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools

# Download logs
az webapp log download \
  --name app-dcri-mcp-tools-prod \
  --resource-group rg-dcri-mcp-tools \
  --log-file logs.zip
```

## Troubleshooting

### Common Issues

1. **Key Vault Access Denied**
   - Verify managed identity is enabled
   - Check Key Vault access policies
   - Ensure correct vault URI in app settings

2. **Application Won't Start**
   - Check startup command configuration
   - Verify Python version compatibility
   - Review application logs

3. **High Memory Usage**
   - Monitor tool execution patterns
   - Consider upgrading App Service plan
   - Implement request queuing

### Performance Optimization

1. **Enable Application Insights** for detailed performance monitoring
2. **Configure CDN** for static content delivery
3. **Implement caching** for frequently accessed data
4. **Use connection pooling** for database connections

## Security Best Practices

1. **Regular Security Updates**
   - Keep Python dependencies updated
   - Monitor security advisories
   - Implement vulnerability scanning

2. **Access Control**
   - Use least privilege principle
   - Implement role-based access control
   - Regular access reviews

3. **Data Protection**
   - Encrypt data in transit and at rest
   - Implement data retention policies
   - Regular security audits

This deployment guide ensures a secure, scalable, and maintainable deployment of the DCRI MCP Tools platform on Azure.