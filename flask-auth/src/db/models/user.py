import uuid

from db import alchemy
from flask_bcrypt import check_password_hash, generate_password_hash
from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    String,
    func,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship


class User(alchemy.Model):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="Идентификатор пользователя",
    )
    created = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        comment="Время создания записи",
    )
    modified = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=True,
        comment="Время изменения записи",
    )
    login = Column(
        String(256),
        unique=True,
        nullable=False,
        index=True,
        comment="Логин пользователя",
    )
    email = Column(String(320), nullable=False, comment="Адрес электронной почты пользователя")
    password_hash = Column(String(128), nullable=False, comment="Хэш пароля пользователя")
    is_active = Column(
        Boolean, nullable=False, default=True, comment="Признак активного пользователя"
    )
    is_verified = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Признак верифицированного пользователя",
    )
    is_admin = Column(Boolean, nullable=False, comment="Признак администратора")
    roles = relationship("Role", secondary="user_role", back_populates="users")

    def __repr__(self):
        return f"<User: {self.login}>"

    @property
    def password(self):
        raise AttributeError("Пароль не является читаемым атрибутом")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password).decode("utf8")

    def verify_password(self, password=None):
        if not password:
            return False
        return check_password_hash(self.password_hash, password)

    def get_roles(self):
        return [role.name for role in self.roles]

    def to_dict(self):
        return dict(
            id=self.id,
            created=self.created,
            modified=self.modified,
            login=self.login,
            email=self.email,
            is_active=self.is_active,
            is_verified=self.is_verified,
            is_admin=self.is_admin,
            roles=self.get_roles(),
        )


class UserActionsHistory(alchemy.Model):
    __tablename__ = "user_actions_history"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Идентификатор записи",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False,
        comment="Идентификатор пользователя",
    )
    action = Column(
        String(255),
        nullable=False,
        comment="Действие пользователя",
    )
    ip = Column(
        String(45),
        nullable=False,
        comment="IP пользователя",
    )
    device_info = Column(
        String(255),
        primary_key=False,
        comment="Информация о устройстве",
    )
    created = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        comment="Время создания записи",
    )

    def __repr__(self):
        return f"<UserActionsHistory: (User: {self.user_id}, {self.action}, {self.created}>"

    def to_dict(self):
        return dict(
            id=self.id,
            user_id=self.user_id,
            action=self.action,
            ip=self.ip,
            device_info=self.device_info,
            created=self.created,
        )


class Role(alchemy.Model):
    __tablename__ = "roles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="Идентификатор роли",
    )
    name = Column(String(72), unique=True, nullable=False, comment="Название роли")
    description = Column(String(255), nullable=False, comment="Описание роли")
    users = relationship("User", secondary="user_role", back_populates="roles")

    def __repr__(self):
        return f"<Role: {self.name}>"


class UserRole(alchemy.Model):
    __tablename__ = "user_role"
    __table_args__ = (UniqueConstraint("user_id", "role_id"),)

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="Идентификатор связи пользователя с его ролью",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(User.id, ondelete="CASCADE"),
        comment="Идентификатор пользователя",
    )
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey(Role.id, ondelete="CASCADE"),
        comment="Идентификатор роли",
    )
