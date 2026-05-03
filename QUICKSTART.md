# Quick Start Guide 🚀

## Step 1: Get API Credentials

### Pinterest Developer Setup (5 minutes)

1. **Go to**: https://developers.pinterest.com/apps/
2. **Click**: "Create app" or "Connect app"
3. **Fill in**:
   - App name: `Pinterest Style Matcher` (or your choice)
   - Description: `Personal shopping recommendation app`
   - Redirect URI: `http://localhost:8000/auth/pinterest/callback`
4. **Save** and copy:
   - ✅ App ID → Save for `.env`
   - ✅ App Secret → Save for `.env`

### Amazon Product Advertising API Setup (15-30 minutes)

1. **Join Amazon Associates**: https://affiliate-program.amazon.com/
   - Create account and complete application
   - Wait for approval (usually instant for existing Amazon accounts)

2. **Get Product Advertising API Access**:
   - Once approved, go to: https://affiliate-program.amazon.com/home/account/tag/manage
   - Note your **Associate Tag** (e.g., `yourtag-20`)
   
3. **Get API Keys**: 
   - Go to: https://webservices.amazon.com/paapi5/documentation/register-for-pa-api.html
   - Request access and get:
     - ✅ Access Key
     - ✅ Secret Key

## Step 2: Configure Your App

Open `/workspaces/shopper/.env` and update these values:

```bash
# Replace these with YOUR credentials:
PINTEREST_APP_ID=1234567890
PINTEREST_APP_SECRET=abc123def456...
AMAZON_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
AMAZON_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AMAZON_ASSOCIATE_TAG=yourtag-20

# Generate a secure secret key:
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_urlsafe(32))">
```

## Step 3: Start the Server

```bash
# Option 1: Use the convenient script
./run_server.sh

# Option 2: Manual start
export PYTHONPATH=/workspaces/shopper
python -m backend.main
```

Server will be available at:
- 🌐 http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

## Step 4: Test Authentication

1. **Visit**: http://localhost:8000/auth/pinterest/login
2. **You'll be redirected** to Pinterest to authorize
3. **Click "Allow"** to grant permissions
4. **You'll be redirected back** with an access token

## Step 5: Explore the API

Open the interactive API documentation:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

Try these endpoints:
- `GET /` - Health check
- `GET /health` - Detailed health info
- `GET /auth/pinterest/login` - Start OAuth flow

## Troubleshooting

### "No module named 'backend'"
**Fix**: Make sure to set PYTHONPATH:
```bash
export PYTHONPATH=/workspaces/shopper
```

### "ValidationError: PINTEREST_APP_ID"
**Fix**: Your `.env` file is missing credentials. Copy from `.env.example` and fill in real values.

### Pinterest redirect doesn't work
**Fix**: Make sure your redirect URI in Pinterest app settings exactly matches:
```
http://localhost:8000/auth/pinterest/callback
```

### Port 8000 already in use
**Fix**: Kill the existing process:
```bash
lsof -ti:8000 | xargs kill -9
```

## Next Steps

Once authentication works:
1. ✅ Phase 1 complete!
2. 🔜 Start Phase 2: Fetch and display Pinterest pins
3. 🔜 Add shopping product recommendations

## Need Help?

- Pinterest API Docs: https://developers.pinterest.com/docs/getting-started/introduction/
- Amazon API Docs: https://webservices.amazon.com/paapi5/documentation/
- FastAPI Docs: https://fastapi.tiangolo.com/
