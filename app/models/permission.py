from enum import Enum
from typing import List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from app.db import db

class ModuleEnum(str, Enum):
    USER = "USER"
    POST = "POST"
    ROLE = "ROLE"
    PERMISSION = "PERMISSION"

class MethodEnum(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

class Permission(db.Model):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    apiPath: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[MethodEnum] = mapped_column(SQLAlchemyEnum(MethodEnum), nullable=False)
    module: Mapped[ModuleEnum] = mapped_column(SQLAlchemyEnum(ModuleEnum), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="role_permission",
        back_populates="permissions"
    )

    def __repr__(self) -> str:
        return f"Permission(id={self.id}, name={self.name}, method={self.method}, module={self.module})"
