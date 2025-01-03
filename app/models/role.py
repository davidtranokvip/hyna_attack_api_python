from datetime import datetime
from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import db
from app.models.permission import Permission
from app.models.role_permission import RolePermission

class Role(db.Model):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255))
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    permissions: Mapped[List[Permission]] = relationship(
        "Permission",
        secondary=RolePermission.__tablename__
    )

    def __repr__(self) -> str:
        return f"Role(id={self.id}, name={self.name})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': [permission.to_dict() for permission in self.permissions],
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }