-- ============================================================
-- 001_initial_schema.sql  –  Pinterest Fashion Finder
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Users ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pinterest_id     VARCHAR UNIQUE,
    email            VARCHAR,
    access_token     VARCHAR,
    refresh_token    VARCHAR,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_sync        TIMESTAMPTZ,
    style_preferences JSONB
);
CREATE INDEX IF NOT EXISTS idx_users_pinterest_id ON users (pinterest_id);

-- ── Pinterest boards ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pinterest_boards (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pinterest_board_id   VARCHAR NOT NULL,
    name                 VARCHAR NOT NULL,
    description          TEXT,
    cover_image_url      VARCHAR,
    pin_count            INTEGER DEFAULT 0,
    last_synced          TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_boards_user_id ON pinterest_boards (user_id);
CREATE INDEX IF NOT EXISTS idx_boards_pinterest_id ON pinterest_boards (pinterest_board_id);

-- ── Pinterest pins ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pinterest_pins (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    board_id         UUID NOT NULL REFERENCES pinterest_boards(id) ON DELETE CASCADE,
    pinterest_pin_id VARCHAR UNIQUE NOT NULL,
    image_url        VARCHAR,
    description      TEXT,
    link             VARCHAR,
    analyzed_at      TIMESTAMPTZ,
    analysis_data    JSONB
);
CREATE INDEX IF NOT EXISTS idx_pins_board_id ON pinterest_pins (board_id);
CREATE INDEX IF NOT EXISTS idx_pins_pinterest_id ON pinterest_pins (pinterest_pin_id);

-- ── Products ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_id   VARCHAR,
    retailer_name VARCHAR,
    title         VARCHAR NOT NULL,
    price         NUMERIC(10,2),
    image_url     VARCHAR,
    product_url   VARCHAR,
    affiliate_url VARCHAR,
    category      VARCHAR,
    brand         VARCHAR,
    colors        VARCHAR[],
    sizes         VARCHAR[],
    style_tags    VARCHAR[],
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_updated  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_products_category ON products (category);
CREATE INDEX IF NOT EXISTS idx_products_brand    ON products (brand);

-- ── User interactions ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_interactions (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id       UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    interaction_type VARCHAR NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_interactions_user    ON user_interactions (user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_product ON user_interactions (product_id);
