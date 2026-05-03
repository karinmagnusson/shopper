# Railway Deployment Instructions

## Prerequisites
1. Create a Railway account at https://railway.app
2. Have your Pinterest API credentials ready

## Deployment Steps

### 1. Deploy Backend

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select this repository: `karinmagnusson/shopper`
4. Select branch: `railway-deployment`
5. Railway will auto-detect the Python app and deploy it

### 2. Configure Backend Environment Variables

In Railway backend service settings, add these variables:

```
# Pinterest API
PINTEREST_APP_ID=1567249
PINTEREST_APP_SECRET=your_secret_here
PINTEREST_REDIRECT_URI=https://your-frontend.up.railway.app/auth/callback

# Security (generate a new secret key!)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Database
DATABASE_URL=sqlite:///./shopper.db

# App Settings
APP_ENV=production
LOG_LEVEL=INFO

# CORS - Add your frontend URL
CORS_ORIGINS=["https://your-frontend.up.railway.app"]
```

Get your backend URL from Railway (e.g., `https://shopper-backend.up.railway.app`)

### 3. Deploy Frontend

1. In Railway, click "New" → "GitHub Repo" again
2. Select the same repository but configure it for frontend:
3. Set **Root Directory**: `frontend`
4. Set **Build Command**: `npm run build`
5. Set **Start Command**: `npm start`

### 4. Configure Frontend Environment Variables

In Railway frontend service settings:

```
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

### 5. Update Pinterest Redirect URI

Update your Pinterest App settings at https://developers.pinterest.com/apps/ with the new callback URL:
```
https://your-frontend.up.railway.app/auth/callback
```

## Your URLs

After deployment, you'll have:
- **Frontend**: `https://shopper-production-XXXX.up.railway.app`
- **Backend API**: `https://shopper-production-YYYY.up.railway.app`

## Alternative: CLI Deployment

Install Railway CLI:
```bash
npm install -g @railway/cli
railway login
railway link
railway up
```

## Troubleshooting

- **CORS errors**: Make sure CORS_ORIGINS includes your frontend URL
- **API not connecting**: Check NEXT_PUBLIC_API_URL is set correctly
- **Database errors**: SQLite file is stored with the service (ephemeral storage)

For persistent database, consider:
- Railway PostgreSQL plugin
- External database service
