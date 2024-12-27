from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    rawPassword: Mapped[str] = mapped_column(String(255), default='')
    role: Mapped[str] = mapped_column(String(50), default='user')
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'rawPassword': self.rawPassword,
            'role': self.role,
            'createdAt': str(self.createdAt),
            'updatedAt': str(self.updatedAt)
        }