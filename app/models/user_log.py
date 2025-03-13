from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.db import db
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class UserLog(db.Model):
    __tablename__ = 'user_log'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    ip: Mapped[str] = mapped_column(String(45), nullable=False)
    name_account: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    detail: Mapped[str] = Column(Text)
    time_active: Mapped[datetime] = Column(DateTime, default=func.now(), index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'name_account': self.name_account,
            'detail': self.detail,
            'time_active': self.time_active,
        }