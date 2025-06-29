"""In-memory storage managers for chat rooms."""

from typing import Dict, Optional
import asyncio

from mcp_chat.models import User, ChatRoom


class RoomManager:
    """Manages active chat rooms."""

    def __init__(self) -> None:
        self._rooms: Dict[str, ChatRoom] = {}
        self._user_to_room: Dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def create_room(self, user1: User, user2: User) -> ChatRoom:
        """Create a new chat room for two users."""
        async with self._lock:
            room = ChatRoom(user1=user1, user2=user2)
            self._rooms[room.room_id] = room
            self._user_to_room[user1.user_id] = room.room_id
            self._user_to_room[user2.user_id] = room.room_id
            return room

    async def get_room(self, room_id: str) -> Optional[ChatRoom]:
        """Get a room by ID."""
        async with self._lock:
            return self._rooms.get(room_id)

    async def get_user_room(self, user_id: str) -> Optional[ChatRoom]:
        """Get the room a user is currently in."""
        async with self._lock:
            room_id = self._user_to_room.get(user_id)
            if room_id:
                return self._rooms.get(room_id)
            return None

    async def close_room(self, room_id: str) -> Optional[ChatRoom]:
        """Close a room and remove users from it."""
        async with self._lock:
            room = self._rooms.get(room_id)
            if room:
                room.active = False
                # Remove users from mapping
                self._user_to_room.pop(room.user1.user_id, None)
                self._user_to_room.pop(room.user2.user_id, None)
                # Keep room in history for now (could implement cleanup later)
            return room

    async def remove_user(self, user_id: str) -> Optional[ChatRoom]:
        """Remove a user from their room and close it."""
        room = await self.get_user_room(user_id)
        if room:
            await self.close_room(room.room_id)
        return room

    async def get_active_room_count(self) -> int:
        """Get the number of active rooms."""
        async with self._lock:
            return sum(1 for room in self._rooms.values() if room.active)
