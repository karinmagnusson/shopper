# Pinterest Style Matcher 🛍️

Connect your Pinterest pins with shopping recommendations powered by visual AI.

## What It Does

1. **Connect Pinterest** - OAuth authentication with your Pinterest account
2. **View Your Pins** - Browse all your saved pins in one place  
3. **Shop Similar Styles** - AI-powered visual similarity finds matching products
4. **Discover Products** - Get recommendations from Amazon and other retailers

## Tech Stack

- **Backend**: FastAPI (Python 3.12+)
- **Database**: SQLAlchemy with SQLite (dev) / PostgreSQL (prod)
- **AI/ML**: CLIP model for visual similarity matching
- **APIs**: Pinterest API v5, Amazon Product Advertising API

## Quick Start

### 1. Prerequisites

- Python 3.12+
- Pinterest Developer Account ([Get credentials](https://developers.pinterest.com/apps/))
- Amazon Product Advertising API access ([Sign up](https://affiliate-program.amazon.com/))

### 2. Clone & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API credentials
# PINTEREST_APP_ID, PINTEREST_APP_SECRET, AMAZON_ACCESS_KEY, etc.
```

### 3. Configure API Credentials

**Pinterest Setup:**
1. Go to [developers.pinterest.com](https://developers.pinterest.com/apps/)
2. Create new app
3. Set redirect URI: `http://localhost:8000/auth/pinterest/callback`
4. Copy App ID and App Secret to `.env`

**Amazon Setup:**
1. Join [Amazon Associates Program](https://affiliate-program.amazon.com/)
2. Apply for Product Advertising API access
3. Get Access Key, Secret Key, and Associate Tag
4. Add to `.env`

**Generate Secret Key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Run the Backend

```bash
# Initialize database
python -c "from backend.models.database import init_db; init_db()"

# Start FastAPI server
python backend/main.py
```

Server runs at: **http://localhost:8000**

API docs at: **http://localhost:8000/docs**

### 5. Test Authentication

Visit: `http://localhost:8000/auth/pinterest/login`

This redirects to Pinterest for OAuth authorization.

## Project Structure

```
shopper/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── routers/
│   │   └── auth.py          # Pinterest OAuth endpoints
│   ├── models/
│   │   └── database.py      # SQLAlchemy models (User, Pin, Product)
│   └── services/
│       └── pinterest_client.py  # Pinterest API wrapper
├── requirements.txt         # Python dependencies
├── .env                     # Your API credentials (not committed)
└── .env.example            # Template for required variables
```

## Development Status

✅ Phase 1: Foundation & Authentication
- [x] Project structure
- [x] FastAPI backend setup
- [x] Pinterest OAuth flow
- [x] Database models
- [ ] JWT token verification
- [ ] User session management

⏳ Phase 2: Pinterest Integration (Next)
- [ ] Fetch user's pins
- [ ] Store pins in database
- [ ] API endpoints for pins
- [ ] Frontend pin gallery

🔜 Phase 3: Shopping Integration
🔜 Phase 4: Visual Similarity Engine  
🔜 Phase 5: Frontend Experience
🔜 Phase 6: Deployment

## API Endpoints

### Authentication
- `GET /auth/pinterest/login` - Initiate Pinterest OAuth
- `GET /auth/pinterest/callback` - OAuth callback handler
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout user

### Health
- `GET /` - API status
- `GET /health` - Health check

## Next Steps

1. **Add your API credentials** to `.env`
2. **Run the server** and test authentication
3. **Verify** you can log in with Pinterest
4. Ready for Phase 2: Pinterest data fetching!

## Contributing

This is a personal project. Feel free to fork and adapt!

## License

MIT
