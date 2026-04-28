# Shopper – Pinterest Fashion Finder

A Pinterest-based fashion recommendation website that helps users discover shoppable clothes and accessories inspired by their Pinterest boards.

## Features

- **Pinterest OAuth**: Secure login via Pinterest API v5 with PKCE
- **Board Import**: Analyze your Pinterest fashion boards and pins
- **AI Image Analysis**: Detect colours, clothing types, and styles using Google Vision API
- **Product Recommendations**: Find matching shoppable products with cosine-similarity matching
- **Affiliate Links**: Earn commissions via Amazon Associates and other retailers
- **Filters**: Filter by price, category, colour, and brand
- **Responsive UI**: Works on desktop and mobile

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11+ |
| Database | PostgreSQL 15+ |
| Cache | Redis |
| Image AI | Google Cloud Vision API |
| Products | Amazon Associates API |
| Auth | Pinterest OAuth 2.0 (PKCE), JWT |

## Project Structure

```
shopper/
├── frontend/          # Next.js 14 + TypeScript
│   ├── src/
│   │   ├── app/       # Pages (landing, boards, recommendations, auth callback)
│   │   ├── components # UI components
│   │   ├── lib/       # API client, Pinterest helpers, utilities
│   │   └── types/     # TypeScript interfaces
│   └── package.json
├── backend/           # FastAPI + Python
│   ├── app/
│   │   ├── api/       # Routes (auth, boards, products, users)
│   │   ├── core/      # Config, database, security
│   │   ├── models/    # SQLAlchemy models
│   │   ├── services/  # Pinterest API, image analysis, product matching
│   │   └── utils/     # Rate limiter, cache
│   ├── migrations/    # SQL schema
│   └── requirements.txt
└── shared/
    ├── database.sql   # Complete PostgreSQL schema
    └── types/         # Shared TypeScript types
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### 1. Database

```bash
createdb shopper
psql shopper < backend/migrations/init.sql
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # Fill in your credentials
uvicorn app.main:app --reload
```

Backend runs at **http://localhost:8000** · API docs at **http://localhost:8000/docs**

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local      # Fill in your credentials
npm run dev
```

Frontend runs at **http://localhost:3000**

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async URL, e.g. `postgresql+asyncpg://user:pass@localhost/shopper` |
| `REDIS_URL` | Redis URL, e.g. `redis://localhost:6379` |
| `PINTEREST_CLIENT_ID` | Pinterest app client ID |
| `PINTEREST_CLIENT_SECRET` | Pinterest app client secret |
| `PINTEREST_REDIRECT_URI` | OAuth callback, e.g. `http://localhost:8000/auth/callback` |
| `GOOGLE_VISION_API_KEY` | Google Cloud Vision API key |
| `AMAZON_ACCESS_KEY` | Amazon Product Advertising API access key |
| `AMAZON_SECRET_KEY` | Amazon Product Advertising API secret key |
| `AMAZON_ASSOCIATE_TAG` | Amazon Associates tracking tag |
| `JWT_SECRET_KEY` | Secret for JWT signing (generate with `openssl rand -hex 32`) |
| `TOKEN_ENCRYPTION_KEY` | Fernet key for encrypting Pinterest tokens (generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`) |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend URL, e.g. `http://localhost:8000` |
| `NEXT_PUBLIC_PINTEREST_CLIENT_ID` | Pinterest app client ID (same as backend) |

## Getting Pinterest API Access

1. Go to [Pinterest Developers](https://developers.pinterest.com/)
2. Create a new app
3. Add the OAuth redirect URI: `http://localhost:8000/auth/callback`
4. Request the scopes: `boards:read`, `pins:read`
5. Copy the Client ID and Client Secret into your `.env` file

## Deployment

### Vercel (Frontend)
```bash
cd frontend
npx vercel --prod
```

### Railway (Backend + Database)
```bash
# Connect your repo to Railway, add environment variables, deploy
```

## Architecture Notes

- Pinterest OAuth uses **PKCE** (Proof Key for Code Exchange) for security
- Pinterest access tokens are **Fernet-encrypted** before storage
- API calls to Pinterest respect the **1,000 requests/hour** rate limit using a Redis token-bucket algorithm
- Product matching uses **cosine similarity** on feature vectors (colour 30%, style 40%, type 20%, brand 10%)
- Image analysis results are cached in Redis to avoid redundant API calls

## License

MIT
