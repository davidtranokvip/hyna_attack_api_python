from sqlalchemy import String, Integer
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import db
  
class Server(db.Model):
    __tablename__ = 'server'

    id: Mapped[int] = mapped_column(primary_key=True)
    ip: Mapped[str] = mapped_column(String(45), nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100))
    thread: Mapped[int] = mapped_column(Integer)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="server")

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'ip': self.ip,
            'thread': self.thread,
            'password': self.password,
            'name': self.name,
            'createdAt': str(self.createdAt),
            'updatedAt': str(self.updatedAt)
        }
    