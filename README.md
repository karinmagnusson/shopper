# Pinterest Fashion Finder

A full-stack MVP web application that connects your Pinterest boards to real shoppable fashion products.

## Overview

Pinterest Fashion Finder analyzes your Pinterest fashion boards and surfaces shoppable product recommendations that match your personal style. Connect your Pinterest account, select your favorite boards, and discover where to buy similar items across major retailers.

## Features

- **Pinterest OAuth** — Secure sign-in with your Pinterest account
- **Board & Pin Analysis** — Automatic style extraction from your boards
- **AI-Powered Recommendations** — Match pins to real products via image similarity
- **Multi-Retailer Search** — Results from ASOS, Amazon, Zara, and more
- **Advanced Filtering** — Filter by price, color, category, and brand
- **GDPR Compliant** — Full data deletion support from the settings page

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI (Python 3.12) |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Auth | NextAuth.js + Pinterest OAuth |
| Infra | Docker Compose |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Pinterest Developer account (for OAuth credentials)

### 1. Clone & configure

```bash
git clone https://github.com/karinmagnusson/shopper.git
cd shopper
cp .env.example .env
# Edit .env with your Pinterest API keys and other secrets
```

### 2. Start all services

```bash
docker-compose up --build
```

The app will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Local frontend development (without Docker)

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See `.env.example` for all required variables. Key variables:

| Variable | Description |
|---|---|
| `PINTEREST_CLIENT_ID` | Pinterest OAuth app client ID |
| `PINTEREST_CLIENT_SECRET` | Pinterest OAuth app client secret |
| `NEXTAUTH_SECRET` | Random secret for NextAuth.js session encryption |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |

## Project Structure

```
shopper/
├── frontend/               # Next.js 14 application
│   ├── src/
│   │   ├── app/            # App Router pages
│   │   ├── components/     # Reusable UI components
│   │   ├── lib/            # API client, auth config
│   │   └── types/          # TypeScript interfaces
│   └── package.json
├── backend/                # FastAPI application (coming soon)
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Reference

The backend exposes a REST API documented at `/docs` (Swagger UI) when running locally.

## Privacy & GDPR

Users can delete their account and all associated data at any time from **Settings → Data Management**. No Pinterest data is stored beyond what is needed to generate recommendations.

## License

MIT
