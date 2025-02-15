from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db

class UserPermission(db.Model):
    __tablename__ = 'user_permissions'

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    permissionId: Mapped[int] = mapped_column(ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.userId,
            'permissionId': self.permissionId,
            'createdAt': str(self.createdAt),
            'updatedAt': str(self.updatedAt)
        }