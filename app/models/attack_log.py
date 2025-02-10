from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db
from datetime import datetime
from app.models.user import User

class AttackLog(db.Model):
    __tablename__ = 'attack_logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'))
    domainName: Mapped[str] = mapped_column(String(255))
    time: Mapped[int] = mapped_column(Integer)
    concurrent: Mapped[int] = mapped_column(Integer)
    request: Mapped[int] = mapped_column(Integer)
    command: Mapped[str] = mapped_column(Text)
    output: Mapped[str] = mapped_column(Text, nullable=True)
    headers: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='running')
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped[User] = db.relationship('User', foreign_keys=[userId])

    def toDict(self):
        return {
            'id': self.id,
            'userId': self.userId,
            'domainName': self.domainName,
            'time': self.time,
            'concurrent': self.concurrent,
            'request': self.request,
            'command': self.command,
            'output': self.output,
            'headers': self.headers,
            'status': self.status,
            'user': {
                'id': self.user.id,
                'email': self.user.email
            },
            'createdAt': str(self.createdAt),
            'updatedAt': str(self.updatedAt)
        }
