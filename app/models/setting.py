from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db
from datetime import datetime
from typing import List, Dict

class Setting(db.Model):
    __tablename__ = 'settings'

    id: Mapped[int] = mapped_column(primary_key=True)
    group: Mapped[str] = mapped_column(String(255))
    value: Mapped[List[Dict[str, str]]] = mapped_column(JSON)
    type: Mapped[str] = mapped_column(String(255))  
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def toDict(self):
        return {
            'id': self.id,
            'type': self.type,
            'value': self.value,
            'group': self.group,
            'createdAt': str(self.createdAt),
            'updatedAt': str(self.updatedAt)
        }
