from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    raw_password: Mapped[str] = mapped_column(String(255), default='')
    role: Mapped[str] = mapped_column(String(50), default='user')

    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'raw_password': self.raw_password,
            'role': self.role
            # 'created_at': str(self.created_at),
            # 'updated_at': str(self.updated_at)
        }