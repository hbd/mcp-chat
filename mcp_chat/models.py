"""Data models for MCP Chat server."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class User:
    """Represents a connected user."""

    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    display_name: Optional[str] = None
    connection_id: str = ""  # SSE connection identifier
    joined_at: datetime = field(default_factory=datetime.now)

    @property
    def name(self) -> str:
        """Get display name or anonymous identifier."""
        return self.display_name or f"Anonymous-{self.user_id[:8]}"


@dataclass
class ChatRoom:
    """Represents an active chat room between two users."""

    room_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user1: User = field(default_factory=User)
    user2: User = field(default_factory=User)
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True

    def get_partner(self, user_id: str) -> Optional[User]:
        """Get the chat partner for a given user ID."""
        if self.user1.user_id == user_id:
            return self.user2
        elif self.user2.user_id == user_id:
            return self.user1
        return None

    def has_user(self, user_id: str) -> bool:
        """Check if a user is in this room."""
        return user_id in (self.user1.user_id, self.user2.user_id)


@dataclass
class Message:
    """Represents a chat message."""

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    room_id: str = ""
    sender_id: str = ""
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
