from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    nameAccount: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[str] = mapped_column(String(255))
    team_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('team.id'))
    rawPassword: Mapped[str] = mapped_column(String(255), default='')
    isAdmin: Mapped[bool] = mapped_column(Boolean, default=False) 
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    status: Mapped[bool] = mapped_column(Boolean, default=True)  # True for active, False for deactive
    attackCount: Mapped[int] = mapped_column(Integer, default=0)

    team = db.relationship("Team", back_populates="users")
    permissions = db.relationship(
        "Permission",
        secondary='user_permissions',
        primaryjoin='User.id == UserPermission.userId',
        secondaryjoin='Permission.id == UserPermission.permissionId',
        lazy='dynamic'
    )

    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def deactivate(self):
        self.status = False
        db.session.commit()

    def increment_attack_count(self):
        self.attackCount += 1
        if self.attackCount >= 3:
            self.deactivate()
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'nameAccount': self.nameAccount,
            'avatar': self.avatar,
            'isAdmin': self.isAdmin,
            'rawPassword': self.rawPassword,
            'permissions': [permission.to_dict() for permission in self.permissions],
            'status': self.status,
            'team_id': self.team_id,
            'team_name': self.team.name if self.team else None,
            'attackCount': self.attackCount,
            'createdAt': str(self.createdAt),
            'updatedAt': str(self.updatedAt)
        }