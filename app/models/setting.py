from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db
from datetime import datetime

class Setting(db.Model):
    __tablename__ = 'settings'

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(255), unique=True)
    value: Mapped[str] = mapped_column(String(1000))
    group: Mapped[str] = mapped_column(String(255))
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def toDict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'group': self.group,
            'createdAt': str(self.createdAt),
            'updatedAt': str(self.updatedAt)
        }
