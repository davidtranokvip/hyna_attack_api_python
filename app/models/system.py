from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db
from datetime import datetime
from app.models.user import User

class System(db.Model):
    __tablename__ = 'systems'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    createdBy: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'))
    updatedBy: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'))
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    createdByUser: Mapped[User] = db.relationship('User', foreign_keys=[createdBy])
    updatedByUser: Mapped[User] = db.relationship('User', foreign_keys=[updatedBy])

    def toDict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'createdBy': {
                'id': self.createdByUser.id,
                'email': self.createdByUser.email
            },
            'updatedBy': {
                'id': self.updatedByUser.id,
                'email': self.updatedByUser.email
            },
            'createdAt': str(self.createdAt),
            'updatedAt': str(self.updatedAt)
        }
