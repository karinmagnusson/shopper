"""Initial schema – all tables and indexes.

Revision ID: 001
Revises: –
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all application tables."""

    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("pinterest_id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("last_sync", sa.DateTime(), nullable=True),
        sa.Column("style_preferences", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_users_pinterest_id", "users", ["pinterest_id"], unique=True)

    # ------------------------------------------------------------------
    # pinterest_boards
    # ------------------------------------------------------------------
    op.create_table(
        "pinterest_boards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("pinterest_board_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cover_image_url", sa.String(), nullable=True),
        sa.Column("pin_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("follower_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("synced_at", sa.DateTime(), nullable=True),
        sa.Column("board_metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
    )
    op.create_index("ix_pinterest_boards_user_id", "pinterest_boards", ["user_id"])
    op.create_index("ix_pinterest_boards_pinterest_board_id", "pinterest_boards", ["pinterest_board_id"], unique=True)

    # ------------------------------------------------------------------
    # pinterest_pins
    # ------------------------------------------------------------------
    op.create_table(
        "pinterest_pins",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "board_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pinterest_boards.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("pinterest_pin_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("link", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("saved_at", sa.DateTime(), nullable=True),
        sa.Column("analysis_data", postgresql.JSONB(), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_pinterest_pins_board_id", "pinterest_pins", ["board_id"])
    op.create_index("ix_pinterest_pins_pinterest_pin_id", "pinterest_pins", ["pinterest_pin_id"], unique=True)

    # ------------------------------------------------------------------
    # products
    # ------------------------------------------------------------------
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("asin", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("brand", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("affiliate_url", sa.String(), nullable=False),
        sa.Column("colors", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("sizes", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("style_tags", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_products_asin", "products", ["asin"], unique=True)
    op.create_index("ix_products_brand", "products", ["brand"])
    op.create_index("ix_products_category", "products", ["category"])
    op.create_index("ix_products_category_brand", "products", ["category", "brand"])
    op.create_index("ix_products_price", "products", ["price"])

    # ------------------------------------------------------------------
    # user_interactions
    # ------------------------------------------------------------------
    op.create_table(
        "user_interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("interaction_type", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("session_id", sa.String(), nullable=True),
        sa.Column("referrer_pin_id", sa.String(), nullable=True),
    )
    op.create_index("ix_user_interactions_user_id", "user_interactions", ["user_id"])
    op.create_index("ix_user_interactions_product_id", "user_interactions", ["product_id"])

    # ------------------------------------------------------------------
    # product_recommendations
    # ------------------------------------------------------------------
    op.create_table(
        "product_recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("source_pin_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_product_recommendations_user_id", "product_recommendations", ["user_id"])
    op.create_index("ix_product_recommendations_product_id", "product_recommendations", ["product_id"])


def downgrade() -> None:
    """Drop all application tables in reverse dependency order."""
    op.drop_table("product_recommendations")
    op.drop_table("user_interactions")
    op.drop_table("products")
    op.drop_table("pinterest_pins")
    op.drop_table("pinterest_boards")
    op.drop_table("users")
