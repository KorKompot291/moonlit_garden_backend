"""add_habit_frequency

Revision ID: 45dafc4cc32c
Revises: 04029018e368
Create Date: 2025-12-06 19:46:28.354975

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45dafc4cc32c'
down_revision: Union[str, None] = '04029018e368'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # 1) Создаём enum-тип в Postgres (если ещё нет)
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'habit_frequency_type_enum'
          ) THEN
            CREATE TYPE habit_frequency_type_enum AS ENUM (
              'daily',
              'weekly',
              'custom_days',
              'custom_weeks'
            );
          END IF;
        END$$;
        """
    )

    # 2) Добавляем колонки в таблицу habit
    op.add_column(
        "habit",
        sa.Column(
            "frequency_type",
            sa.Enum(
                "daily",
                "weekly",
                "custom_days",
                "custom_weeks",
                name="habit_frequency_type_enum",
            ),
            nullable=False,
            server_default="daily",  # для уже существующих строк
        ),
    )
    op.add_column(
        "habit",
        sa.Column(
            "frequency_value",
            sa.Integer(),
            nullable=False,
            server_default="1",  # для уже существующих строк
        ),
    )

    # 3) Убираем server_default, чтобы в будущем не прилипало
    op.alter_column("habit", "frequency_type", server_default=None)
    op.alter_column("habit", "frequency_value", server_default=None)


def downgrade() -> None:
    # Откат: сначала колонки, потом тип
    op.drop_column("habit", "frequency_value")
    op.drop_column("habit", "frequency_type")

    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'habit_frequency_type_enum'
          ) THEN
            DROP TYPE habit_frequency_type_enum;
          END IF;
        END$$;
        """
    )

    # ### end Alembic commands ###
