# Azure Deployment Guide for JURY-AI

This guide details the step-by-step process to deploy your **JURY-AI** platform live on Microsoft Azure using your free credits.

---

## Part 1: Deploying the FastAPI Backend (Azure App Service)

Azure App Service will host your Python FastAPI server. It detects Python applications automatically if there is a `requirements.txt` file (which we have added) and a startup entry point.

### Step 1: Install Azure CLI
If you do not have Azure CLI installed on your machine:
* Download and run the installer from: [Install Azure CLI on Windows](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows)

### Step 2: Login to Azure
Open your terminal in the directory `c:\Users\HP\OneDrive\Desktop\one page resume\JURY-AI` and run:
```bash
az login
```
*This will open your browser to log in with your Azure credentials (the one with the ₹18,800 credit).*

### Step 3: Create and Deploy the Web App
Run the following single command to build the app service resource and deploy your code:
```bash
az webapp up --name jury-ai-backend --resource-group JuryAI-RG --plan JuryAI-Plan --sku B1 --runtime "PYTHON:3.10"
```
*   `--name jury-ai-backend`: This will be your backend URL (e.g. `https://jury-ai-backend.azurewebsites.net`). Feel free to change the name if this one is taken.
*   `--sku B1`: The Basic B1 tier is perfect for utilizing your free credits.
*   `--runtime "PYTHON:3.10"`: Configures Python version 3.10.

### Step 4: Configure App Settings on Azure
FastAPI requires environment variables (like your Gemini API Key). Configure them via Azure CLI:
```bash
az webapp config appsettings set --name jury-ai-backend --resource-group JuryAI-RG --settings GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_KEY"
```

---

## Part 2: Deploying the Next.js Frontend (Azure Static Web Apps)

Azure Static Web Apps is a **free hosting service** for static frontend frameworks (like React/Next.js).

### Step 1: Push JURY-AI to your GitHub
Since we modified the backend dependency files, commit and push them to your GitHub:
```bash
git add backend/requirements.txt
git commit -m "Add backend dependencies for Azure deployment"
git push origin main
```

### Step 2: Create a Static Web App in the Azure Portal
1. Go to the [Azure Portal](https://portal.azure.com/).
2. Search for **Static Web Apps** and click **Create**.
3. Under Deployment Details, choose **GitHub** and authorize Azure to access your account.
4. Select your Organization, Repository (`JURY-AI`), and Branch (`main`).
5. Under Build Details, select the preset: **Next.js**.
6. Set the **App location** to: `/frontend`.
7. Leave **Api location** and **Output location** empty.
8. Click **Review + Create**. 

*Azure will automatically create a GitHub Action file in your repository that will build and host your Next.js app live.*

---

## Part 3: Pointing Frontend to Backend URL

Once your backend is live (e.g. `https://jury-ai-backend.azurewebsites.net`), update your Next.js API configuration or environment variable (like `NEXT_PUBLIC_API_URL` or configuration code) to point to your Azure backend instead of `http://localhost:8000`.
