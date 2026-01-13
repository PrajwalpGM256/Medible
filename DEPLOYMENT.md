# Medible Deployment Guide

Deploy Medible with **Railway** (backend + PostgreSQL) and **Vercel** (frontend).

---

## 🚀 Backend Deployment (Railway)

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub

### Step 2: Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Select your Medible repository
4. Railway will auto-detect the backend folder

### Step 3: Configure Backend Service
1. Click on the deployed service
2. Go to **Settings** → **Root Directory** → Set to `backend`
3. Railway should auto-detect the `Procfile`

### Step 4: Add PostgreSQL Database
1. Click **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway automatically sets `DATABASE_URL`

### Step 5: Set Environment Variables
Go to your backend service → **Variables** tab and add:

| Variable | Value |
|----------|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `CORS_ORIGINS` | `https://your-app.vercel.app` (update after deploying frontend) |
| `USDA_API_KEY` | Your USDA API key (optional) |

### Step 6: Deploy
Railway deploys automatically on push. Your backend URL will be like:
```
https://medible-backend-production.up.railway.app
```

### Step 7: Initialize Database
In Railway, go to your service → **Settings** → **Deploy** → Open the **Shell** and run:
```bash
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
```

Or seed with demo data:
```bash
python seed_data.py
```

---

## 🌐 Frontend Deployment (Vercel)

### Step 1: Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub

### Step 2: Import Project
1. Click **"Add New Project"**
2. Import your Medible repository
3. Set **Root Directory** to `frontend`

### Step 3: Configure Build Settings
Vercel should auto-detect Vite. Verify:
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### Step 4: Set Environment Variables
Add this environment variable:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://your-backend.railway.app/api/v1` |

Replace with your actual Railway backend URL from Step 6 above.

### Step 5: Deploy
Click **"Deploy"**. Your frontend URL will be like:
```
https://medible.vercel.app
```

---

## 🔗 Connect Frontend to Backend

After both are deployed:

1. **Update Railway CORS**: 
   - Go to Railway → Backend service → Variables
   - Set `CORS_ORIGINS` to your Vercel URL (e.g., `https://medible.vercel.app`)
   - Redeploy

2. **Verify Connection**:
   - Visit your Vercel URL
   - Try registering/logging in
   - Check browser console for any CORS errors

---

## 🔧 Troubleshooting

### CORS Errors
- Make sure `CORS_ORIGINS` in Railway includes your Vercel URL
- Include the full URL with `https://`

### Database Errors  
- Ensure PostgreSQL is connected in Railway
- Check `DATABASE_URL` is set automatically
- Run `db.create_all()` in Railway shell

### API Connection Failed
- Verify `VITE_API_URL` in Vercel matches your Railway URL
- Include `/api/v1` at the end
- Check Railway logs for errors

---

## 📋 Environment Variables Summary

### Backend (Railway)
```
FLASK_ENV=production
SECRET_KEY=<your-secret-key>
CORS_ORIGINS=https://your-app.vercel.app
DATABASE_URL=<auto-set by Railway>
USDA_API_KEY=<optional>
```

### Frontend (Vercel)
```
VITE_API_URL=https://your-backend.railway.app/api/v1
```

---

## 🎉 Done!

Your Medible app should now be live at:
- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-backend.railway.app/api/v1`
- **Health Check**: `https://your-backend.railway.app/api/v1/health`
