from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db
from datetime import datetime
from app.models.attack_log import AttackLog

class AttackServerLog(db.Model):
    __tablename__ = 'attack_server_logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    attackLogId: Mapped[int] = mapped_column(Integer, db.ForeignKey('attack_logs.id'))
    serverHostname: Mapped[str] = mapped_column(String(255))
    output: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='running')
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    attackLog: Mapped[AttackLog] = db.relationship('AttackLog', foreign_keys=[attackLogId])

    def toDict(self):
        return {
            'id': self.id,
            'attackLogId': self.attackLogId,
            'serverHostname': self.serverHostname,
            'output': self.output,
            'status': self.status,
            'createdAt': str(self.createdAt),
            'updatedAt': str(self.updatedAt)
        }
