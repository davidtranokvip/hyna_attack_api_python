from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from app.db import db

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'

    id: Mapped[int] = mapped_column(primary_key=True)
    roleId: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=False)
    permissionId: Mapped[int] = mapped_column(ForeignKey('permissions.id'), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
