"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-10-14

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("role", sa.Enum("user", "admin", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("telegram_chat_id", sa.String(), nullable=True),
        sa.Column("telegram_enabled", sa.Boolean(), nullable=False),
        sa.Column("email_enabled", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # Create portfolios table
    op.create_table(
        "portfolios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("is_default", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create positions table
    op.create_table(
        "positions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("portfolio_id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("average_price", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["portfolio_id"],
            ["portfolios.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_positions_symbol"), "positions", ["symbol"], unique=False)

    # Create transactions table
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("position_id", sa.Integer(), nullable=False),
        sa.Column(
            "transaction_type",
            sa.Enum("buy", "sell", name="transactiontype"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("fee", sa.Float(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["position_id"],
            ["positions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create alerts table
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column(
            "alert_type",
            sa.Enum(
                "price_above",
                "price_below",
                "price_change",
                "ai_signal",
                "technical_pattern",
                "volume_spike",
                name="alerttype",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("active", "triggered", "expired", "disabled", name="alertstatus"),
            nullable=False,
        ),
        sa.Column("threshold_value", sa.Float(), nullable=True),
        sa.Column(
            "condition_params", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("channels", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column("custom_message", sa.String(), nullable=True),
        sa.Column("trigger_count", sa.Integer(), nullable=False),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alerts_symbol"), "alerts", ["symbol"], unique=False)

    # Create alert_history table
    op.create_table(
        "alert_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column("triggered_value", sa.Float(), nullable=True),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column(
            "channels_sent", postgresql.JSON(astext_type=sa.Text()), nullable=False
        ),
        sa.Column(
            "delivery_status", postgresql.JSON(astext_type=sa.Text()), nullable=False
        ),
        sa.Column(
            "triggered_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["alert_id"],
            ["alerts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create model_metrics table
    op.create_table(
        "model_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("model_version", sa.String(), nullable=False),
        sa.Column("model_name", sa.String(), nullable=False),
        sa.Column("epoch", sa.Integer(), nullable=False),
        sa.Column("mse", sa.Float(), nullable=False),
        sa.Column("mae", sa.Float(), nullable=False),
        sa.Column("r2_score", sa.Float(), nullable=False),
        sa.Column("learning_rate", sa.Float(), nullable=False),
        sa.Column("gradient_norm", sa.Float(), nullable=True),
        sa.Column("training_samples", sa.Integer(), nullable=False),
        sa.Column("validation_samples", sa.Integer(), nullable=True),
        sa.Column("training_duration_seconds", sa.Float(), nullable=True),
        sa.Column(
            "additional_metrics", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("is_production", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_model_metrics_model_version"),
        "model_metrics",
        ["model_version"],
        unique=False,
    )

    # Create prediction_logs table
    op.create_table(
        "prediction_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("model_version", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("bullish_probability", sa.Float(), nullable=False),
        sa.Column("bearish_probability", sa.Float(), nullable=False),
        sa.Column("neutral_probability", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("prediction", sa.String(), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column(
            "input_features", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("actual_outcome", sa.String(), nullable=True),
        sa.Column("outcome_recorded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "predicted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_prediction_logs_model_version"),
        "prediction_logs",
        ["model_version"],
        unique=False,
    )
    op.create_index(
        op.f("ix_prediction_logs_symbol"), "prediction_logs", ["symbol"], unique=False
    )

    # Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "action",
            sa.Enum(
                "login",
                "logout",
                "register",
                "password_change",
                "profile_update",
                "portfolio_create",
                "portfolio_update",
                "portfolio_delete",
                "position_add",
                "position_update",
                "position_delete",
                "alert_create",
                "alert_update",
                "alert_delete",
                "settings_update",
                name="auditaction",
            ),
            nullable=False,
        ),
        sa.Column("resource_type", sa.String(), nullable=True),
        sa.Column("resource_id", sa.String(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("old_values", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("new_values", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("metadata", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index(op.f("ix_prediction_logs_symbol"), table_name="prediction_logs")
    op.drop_index(
        op.f("ix_prediction_logs_model_version"), table_name="prediction_logs"
    )
    op.drop_table("prediction_logs")
    op.drop_index(op.f("ix_model_metrics_model_version"), table_name="model_metrics")
    op.drop_table("model_metrics")
    op.drop_table("alert_history")
    op.drop_index(op.f("ix_alerts_symbol"), table_name="alerts")
    op.drop_table("alerts")
    op.drop_table("transactions")
    op.drop_index(op.f("ix_positions_symbol"), table_name="positions")
    op.drop_table("positions")
    op.drop_table("portfolios")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
