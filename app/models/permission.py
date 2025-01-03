from enum import Enum
from datetime import datetime
from sqlalchemy import String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column
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

    def __repr__(self) -> str:
        return f"Permission(id={self.id}, name={self.name}, method={self.method}, module={self.module})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'apiPath': self.apiPath,
            'method': self.method,
            'module': self.module,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }