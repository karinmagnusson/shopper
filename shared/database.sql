-- Complete PostgreSQL schema – shared reference copy
-- See backend/migrations/init.sql for the canonical runnable version.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pinterest_id            VARCHAR(255) NOT NULL UNIQUE,
    email                   VARCHAR(255),
    access_token_encrypted  VARCHAR(2048) NOT NULL,
    refresh_token_encrypted VARCHAR(2048),
    style_preferences       JSONB DEFAULT '{}',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_sync               TIMESTAMPTZ,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pinterest_boards (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pinterest_board_id  VARCHAR(255) NOT NULL UNIQUE,
    name                VARCHAR(512) NOT NULL,
    description         TEXT,
    cover_image_url     VARCHAR(2048),
    pin_count           INTEGER NOT NULL DEFAULT 0,
    last_synced         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pinterest_pins (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    board_id            UUID NOT NULL REFERENCES pinterest_boards(id) ON DELETE CASCADE,
    pinterest_pin_id    VARCHAR(255) NOT NULL UNIQUE,
    image_url           VARCHAR(2048),
    description         TEXT,
    link                VARCHAR(2048),
    analyzed_at         TIMESTAMPTZ,
    analysis_data       JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    retailer_id     VARCHAR(512) NOT NULL,
    retailer_name   VARCHAR(255) NOT NULL,
    title           VARCHAR(1024) NOT NULL,
    price           DECIMAL(10, 2),
    currency        VARCHAR(10) NOT NULL DEFAULT 'USD',
    image_url       VARCHAR(2048),
    product_url     VARCHAR(2048) NOT NULL,
    affiliate_url   VARCHAR(2048),
    category        VARCHAR(255),
    brand           VARCHAR(255),
    description     TEXT,
    colors          TEXT[],
    sizes           TEXT[],
    embedding       FLOAT[],
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_updated    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_interactions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id          UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    interaction_type    VARCHAR(50) NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
