from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    nameTeam: Mapped[str] = mapped_column(String(255))
    nameAccount: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[str] = mapped_column(String(255))
    rawPassword: Mapped[str] = mapped_column(String(255), default='')
    isAdmin: Mapped[bool] = mapped_column(Boolean, default=False) 
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

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

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'nameTeam': self.nameTeam,
            'nameAccount': self.nameAccount,
            'avatar': self.avatar,
            'isAdmin': self.isAdmin,
            'rawPassword': self.rawPassword,
            'permissions': [permission.to_dict() for permission in self.permissions],
            'createdAt': str(self.createdAt),
            'updatedAt': str(self.updatedAt)
        }