# 🚀 Deploying CIHIP to Render.com (Step-by-Step Guide)

Deploy the Centralized Indian Healthcare Information Portal (CIHIP) to [Render.com](https://render.com) on their free 24/7 web service tier in under 3 minutes.

---

## Step 1: Push Your Code to GitHub

If you haven't pushed this local Git repository to GitHub yet:

1. Create a new repository on [GitHub](https://github.com/new) (e.g., `cihip-portal`).
2. Run the following commands in your terminal:
   ```bash
   git remote add origin https://github.com/<YOUR-GITHUB-USERNAME>/cihip-portal.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 2: Deploy on Render

### Option A: 1-Click Render Blueprint (Fastest)

1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** in the top navigation and select **Blueprint**.
3. Connect your GitHub repository (`cihip-portal`).
4. Render will automatically detect [`render.yaml`](./render.yaml) and configure:
   - **Service Name**: `cihip-national-exchange`
   - **Runtime**: `Python 3.12`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
   - **Plan**: `Free`
5. Click **Apply**. Render will build and deploy the web service with automatic SSL (`https://...onrender.com`).

---

### Option B: Manual Web Service Setup

If you prefer setting it up manually:

1. Go to [Render Dashboard](https://dashboard.render.com) &rarr; **New +** &rarr; **Web Service**.
2. Select **Build and deploy from a Git repository**.
3. Select your `cihip-portal` repository.
4. Fill in the following settings:
   - **Name**: `cihip-national-portal`
   - **Region**: `Singapore (Southeast Asia)` or `Frankfurt` (closest to India)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
   - **Instance Type**: `Free`
5. (Optional) In **Environment Variables**, add:
   - `CIHIP_HOST` = `0.0.0.0`
   - `PYTHON_VERSION` = `3.12.4`
6. Click **Create Web Service**.

---

## Step 3: Verify Your Deployment

Once Render finishes the build (usually takes ~1 minute), you will receive a public URL:
```
https://<your-service-name>.onrender.com
```

### Check Available Endpoints:
- **Public Portal**: `https://<your-service-name>.onrender.com/`
- **Interactive FHIR R4 Explorer**: `https://<your-service-name>.onrender.com/api/docs`
- **Patient Portal**: `https://<your-service-name>.onrender.com/patient`
- **Doctor Consultation**: `https://<your-service-name>.onrender.com/doctor`
- **Lab Worklist**: `https://<your-service-name>.onrender.com/lab`
- **Hospital Administration**: `https://<your-service-name>.onrender.com/hospital`
- **Epidemiological Research**: `https://<your-service-name>.onrender.com/research`
- **Zero-Trust Audit Ledger**: `https://<your-service-name>.onrender.com/admin/security`
- **Live Healthcheck**: `https://<your-service-name>.onrender.com/api/v1/audit/verify`

---

## 🔒 Production Features Included Out of the Box:
- **Automatic HTTPS / TLS 1.3**: Provided by Render.
- **Zero-Trust Audit Ledger**: Every visit and action is recorded in the SHA-256 tamper-evident blockchain chain.
- **Pre-seeded Registries**: Indian hospitals (AIIMS, CMC, Apollo, TMH), accredited NABL labs, NMC doctors, and ABHA patients are initialized automatically on first startup.
