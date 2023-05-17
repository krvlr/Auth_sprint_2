"""Create user roles table

Revision ID: 7c21289c77c4
Revises: 6d79bc22005b
Create Date: 2023-05-13 14:45:29.359868

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c21289c77c4"
down_revision = "6d79bc22005b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "roles",
        sa.Column("id", sa.UUID(), nullable=False, comment="Идентификатор роли"),
        sa.Column("name", sa.String(length=72), nullable=False, comment="Название роли"),
        sa.Column("description", sa.String(length=255), nullable=False, comment="Описание роли"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roles")),
        sa.UniqueConstraint("id", name=op.f("uq_roles_id")),
        sa.UniqueConstraint("name", name=op.f("uq_roles_name")),
    )
    op.create_table(
        "user_role",
        sa.Column(
            "id", sa.UUID(), nullable=False, comment="Идентификатор связи пользователя с его ролью"
        ),
        sa.Column("user_id", sa.UUID(), nullable=True, comment="Идентификатор пользователя"),
        sa.Column("role_id", sa.UUID(), nullable=True, comment="Идентификатор роли"),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.id"], name=op.f("fk_user_role_role_id_roles"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_user_role_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_role")),
        sa.UniqueConstraint("id", name=op.f("uq_user_role_id")),
        sa.UniqueConstraint("user_id", "role_id", name=op.f("uq_user_role_user_id")),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_role")
    op.drop_table("roles")
    # ### end Alembic commands ###
