from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

# --- Modelos de Base de Datos ---

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    
    # Relación para facilitar consultas (opcional pero útil)
    messages: List["Message"] = Relationship(back_populates="user")

class Room(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    
    messages: List["Message"] = Relationship(back_populates="room")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Claves foráneas
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    
    # Relaciones
    user: Optional[User] = Relationship(back_populates="messages")
    room: Optional[Room] = Relationship(back_populates="messages")

    def to_dict(self):
        """Helper para convertir el mensaje a diccionario para enviar por WebSocket."""
        return {
            "user": self.user.username if self.user else "Unknown",
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
