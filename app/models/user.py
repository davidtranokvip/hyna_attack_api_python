from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.models.role import Role

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    rawPassword: Mapped[str] = mapped_column(String(255), default='')
    roleId: Mapped[int] = mapped_column(Integer, db.ForeignKey('roles.id'))
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    role: Mapped[Role] = db.relationship('Role', backref='users')

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
            'role': {
                'id': self.role.id,
                'name': self.role.name
            },
            'createdAt': str(self.createdAt),
            'updatedAt': str(self.updatedAt)
        }