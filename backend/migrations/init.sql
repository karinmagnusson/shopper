-- PostgreSQL schema for Shopper – Pinterest Fashion Finder
-- Run with: psql -d shopper -f init.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------------------------------------------------------------
-- users
-- ---------------------------------------------------------------
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

CREATE INDEX IF NOT EXISTS idx_users_pinterest_id ON users(pinterest_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ---------------------------------------------------------------
-- pinterest_boards
-- ---------------------------------------------------------------
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

CREATE INDEX IF NOT EXISTS idx_boards_user_id ON pinterest_boards(user_id);
CREATE INDEX IF NOT EXISTS idx_boards_pinterest_id ON pinterest_boards(pinterest_board_id);

-- ---------------------------------------------------------------
-- pinterest_pins
-- ---------------------------------------------------------------
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

CREATE INDEX IF NOT EXISTS idx_pins_board_id ON pinterest_pins(board_id);
CREATE INDEX IF NOT EXISTS idx_pins_pinterest_id ON pinterest_pins(pinterest_pin_id);
CREATE INDEX IF NOT EXISTS idx_pins_analyzed_at ON pinterest_pins(analyzed_at);

-- ---------------------------------------------------------------
-- products
-- ---------------------------------------------------------------
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

CREATE INDEX IF NOT EXISTS idx_products_retailer ON products(retailer_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_colors ON products USING GIN(colors);

-- ---------------------------------------------------------------
-- user_interactions
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_interactions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id          UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    interaction_type    VARCHAR(50) NOT NULL,   -- 'click', 'save', 'purchase'
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_product_id ON user_interactions(product_id);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON user_interactions(interaction_type);

-- ---------------------------------------------------------------
-- updated_at trigger (applied to users and products)
-- ---------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE FUNCTION set_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_products_last_updated
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION set_last_updated();
