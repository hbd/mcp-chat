"""In-memory storage managers for queue and chat rooms."""

from collections import deque
from typing import Dict, Optional, Tuple, Deque
import asyncio

from mcp_chat.models import User, ChatRoom


class QueueManager:
    """Manages the queue of users waiting to be matched."""

    def __init__(self) -> None:
        self._queue: Deque[User] = deque()
        self._lock = asyncio.Lock()

    async def add_user(self, user: User) -> int:
        """Add a user to the queue and return their position."""
        async with self._lock:
            self._queue.append(user)
            return len(self._queue)

    async def remove_user(self, user_id: str) -> bool:
        """Remove a user from the queue. Returns True if removed."""
        async with self._lock:
            initial_len = len(self._queue)
            self._queue = deque(u for u in self._queue if u.user_id != user_id)
            return len(self._queue) < initial_len

    async def pop_pair(self) -> Optional[Tuple[User, User]]:
        """Pop two users from the queue if available."""
        async with self._lock:
            if len(self._queue) >= 2:
                user1 = self._queue.popleft()
                user2 = self._queue.popleft()
                return (user1, user2)
            return None

    async def get_position(self, user_id: str) -> Optional[int]:
        """Get a user's position in the queue (1-indexed)."""
        async with self._lock:
            for i, user in enumerate(self._queue):
                if user.user_id == user_id:
                    return i + 1
            return None

    async def get_queue_length(self) -> int:
        """Get the current queue length."""
        async with self._lock:
            return len(self._queue)


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
