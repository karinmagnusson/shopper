# Shopper – Pinterest Fashion Finder

> Connect your Pinterest boards and discover shoppable fashion products that match your personal style, powered by AI image analysis.

## Features

- **Pinterest OAuth** — Secure login with `boards:read` and `pins:read` scopes
- **AI Style Analysis** — Extracts colors, clothing types, and aesthetic from saved pins (Google Vision API or built-in mock)
- **Personalized Recommendations** — Weighted scoring: style (40%) · color (30%) · clothing type (20%) · brand (10%)
- **Affiliate Tracking** — Click-through to Amazon Associates and other retailer partners
- **Filtering** — Price range, category, color, brand, style
- **GDPR-friendly** — Minimal data collection; users can delete their data any time

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, React Query, Framer Motion |
| Backend | FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, Redis |
| AI/ML | Google Vision API (mock fallback included) |
| Auth | Pinterest OAuth 2.0, JWT (python-jose 3.4) |
| Infrastructure | Docker Compose, Vercel-ready frontend, Railway-ready backend |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.11+

### 1. Clone and configure

```bash
git clone https://github.com/karinmagnusson/shopper
cd shopper

# Backend env
cp backend/.env.example backend/.env
# Edit backend/.env with your Pinterest App ID/Secret, etc.

# Frontend env
cp frontend/.env.local.example frontend/.env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Start with Docker Compose

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

### 3. Manual setup (without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

---

## Pinterest API Setup

1. Create a developer app at https://developers.pinterest.com
2. Set the OAuth redirect URI to `http://localhost:3000/auth/callback` (dev) or your production URL
3. Copy **App ID** and **App Secret** into `backend/.env`
4. Request scopes: `boards:read`, `pins:read`, `user_accounts:read`

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|---|---|
| `PINTEREST_APP_ID` | Pinterest OAuth App ID |
| `PINTEREST_APP_SECRET` | Pinterest OAuth App Secret |
| `PINTEREST_REDIRECT_URI` | OAuth redirect URI (must match Pinterest app settings) |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `SECRET_KEY` | JWT signing key (min 32 chars) |
| `GOOGLE_VISION_API_KEY` | Google Vision API key (optional – mock is used if absent) |
| `AMAZON_ASSOCIATE_TAG` | Amazon Associates tag (optional) |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Base URL of the backend API |

---

## Database

Migrations are in `database/migrations/`. The Docker Compose setup runs `001_initial_schema.sql` automatically on first start.

To seed sample products:
```bash
psql $DATABASE_URL -f database/seeds/sample_products.sql
```

---

## Project Structure

```
/
├── backend/
│   ├── app/
│   │   ├── api/v1/       # auth, boards, products endpoints
│   │   ├── core/         # config, database, security, cache
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Pinterest API, image analysis, product matching, affiliate
│   │   └── utils/        # rate limiter
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── app/          # Next.js app router pages
│       ├── components/   # Reusable UI and product components
│       └── lib/          # API client, auth helpers, utils
├── database/
│   ├── migrations/       # SQL migration files
│   └── seeds/            # Sample data
└── docker-compose.yml
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/auth/pinterest/login` | Redirect to Pinterest OAuth |
| `GET` | `/api/v1/auth/pinterest/callback` | OAuth callback handler |
| `GET` | `/api/v1/auth/me` | Get current user |
| `GET` | `/api/v1/boards` | List synced boards |
| `POST` | `/api/v1/boards/sync` | Sync boards from Pinterest |
| `GET` | `/api/v1/boards/{id}/pins` | List pins for a board |
| `POST` | `/api/v1/boards/{id}/sync-pins` | Sync + analyze pins |
| `GET` | `/api/v1/products` | Get recommendations (with filters) |
| `POST` | `/api/v1/products/{id}/interact` | Record view/click/save |
| `GET` | `/api/v1/products/{id}/affiliate-link` | Get affiliate URL |

Full interactive docs at `/docs` when the backend is running.

---

## Privacy & Compliance

- Only public Pinterest data is accessed via official API
- OAuth tokens are stored encrypted at rest
- GDPR: users can request full data deletion
- Affiliate relationships are disclosed per FTC guidelines
- No Pinterest images are stored long-term; only metadata

---

## License

MIT
