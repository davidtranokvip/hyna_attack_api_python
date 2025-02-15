from enum import Enum
from datetime import datetime
from sqlalchemy import String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db
from typing import List

class MethodEnum(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

class Permission(db.Model):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    route: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[MethodEnum] = mapped_column(SQLAlchemyEnum(MethodEnum), nullable=False)
    module: Mapped[str] = mapped_column(String(255), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"Permission(id={self.id}, name={self.name}, method={self.method}, module={self.module})"
    user = db.relationship(
        "User",
        secondary='user_permissions',
        primaryjoin='Permission.id == UserPermission.permissionId',
        secondaryjoin='User.id == UserPermission.userId',
        lazy='dynamic'
    )
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'route': self.route,
            'method': self.method,
            'module': self.module,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }