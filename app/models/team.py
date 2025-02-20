from sqlalchemy import String, JSON, Integer, ForeignKey
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import db
from typing import List, Dict
from app.models.server import Server 

class Team(db.Model):
    __tablename__ = 'team'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(225))
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('team.id', ondelete='SET NULL'), nullable=True, default=None)
    servers: Mapped[List[int]] = mapped_column(JSON)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = relationship("User", back_populates="team")

    parent = relationship(
        "Team", 
        remote_side=[id],            
        backref="children",        
        foreign_keys=[parent_id]    
    )
    def toDict(self):
        server_ids = self.servers or []
        server_objects = []
        if server_ids:
            server_objects = Server.query.filter(Server.id.in_(server_ids)).all()
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'parent_name': self.parent.name if self.parent_id else None,
            'servers': self.servers,
            'server_name': [sv.name for sv in server_objects],
            'createdAt': str(self.createdAt),
            'updatedAt': str(self.updatedAt)
        }