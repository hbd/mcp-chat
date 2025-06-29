# MCP Chat Server Implementation Plan

## Overview

A simple MCP server that connects users randomly for pen-pal style chat conversations. The initial version will focus on basic functionality: queue management, random pairing, and message relay between connected users.

## Architecture

### Core Components

1. **Queue Manager**
   - Maintains a queue of users waiting to be matched
   - Handles user entry/exit from queue
   - Performs random pairing when 2+ users are waiting

2. **Chat Room Manager**
   - Creates and manages active chat rooms
   - Assigns unique room IDs
   - Handles message relay between participants
   - Manages room lifecycle (creation, active, closed)

3. **MCP Server**
   - Exposes tools for user interaction
   - Sends notifications for real-time updates
   - Uses SSE transport for persistent connections

### Communication Flow

```
User A                     Server                      User B
  |                          |                           |
  |-- enter_queue() -------->|                           |
  |                          |<--------- enter_queue() --|
  |                          |                           |
  |                    [Match Found]                     |
  |                          |                           |
  |<-- notification:         |         notification: --->|
  |    chatroom.found        |        chatroom.found    |
  |                          |                           |
  |-- send_message() ------->|                           |
  |                          |-------> notification: --->|
  |                          |        message.received   |
  |                          |                           |
  |<-- notification:         |<-------- send_message() --|
  |    message.received      |                           |
```

## Implementation Details

### 1. MCP Tools

#### `enter_queue`
- **Purpose**: Add user to matching queue
- **Parameters**: 
  - `user_id`: String (optional, auto-generated if not provided)
  - `display_name`: String (optional)
- **Returns**: Queue position and estimated wait time

#### `send_message`
- **Purpose**: Send message to chat partner
- **Parameters**:
  - `room_id`: String
  - `message`: String
- **Returns**: Success confirmation

#### `leave_chat`
- **Purpose**: Exit current chat room
- **Parameters**:
  - `room_id`: String
- **Returns**: Success confirmation

### 2. MCP Notifications

#### `chatroom.found`
- **Sent when**: Two users are matched
- **Payload**:
  ```json
  {
    "room_id": "room_123",
    "partner": {
      "user_id": "user_456",
      "display_name": "Anonymous"
    }
  }
  ```

#### `message.received`
- **Sent when**: Partner sends a message
- **Payload**:
  ```json
  {
    "room_id": "room_123",
    "message": "Hello!",
    "timestamp": "2024-01-01T12:00:00Z"
  }
  ```

#### `partner.disconnected`
- **Sent when**: Chat partner leaves or disconnects
- **Payload**:
  ```json
  {
    "room_id": "room_123",
    "reason": "left" | "timeout"
  }
  ```

### 3. Data Models

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    user_id: str
    display_name: Optional[str]
    joined_at: datetime
    connection_id: str  # For SSE transport

@dataclass
class ChatRoom:
    room_id: str
    participants: tuple[User, User]
    created_at: datetime
    active: bool = True

@dataclass
class Message:
    room_id: str
    sender_id: str
    content: str
    timestamp: datetime
```

## Transport Configuration

Use **Streamable HTTP with SSE** for real-time server-to-client communication:

```python
from fastmcp import FastMCP

mcp = FastMCP(
    name="mcp-chat",
    transport="streamable_http"  # Enables SSE for notifications
)
```

## Development Phases

### Phase 1: Basic Queue and Matching (MVP)
- [ ] Set up FastMCP server with SSE transport
- [ ] Implement queue manager with basic FIFO matching
- [ ] Create `enter_queue` tool
- [ ] Send `chatroom.found` notifications
- [ ] Basic in-memory storage

### Phase 2: Message Exchange
- [ ] Implement chat room manager
- [ ] Create `send_message` tool
- [ ] Send `message.received` notifications
- [ ] Add `leave_chat` tool
- [ ] Handle disconnections

### Phase 3: Enhancements (Future)
- [ ] Add interest-based matching
- [ ] Persist chat history
- [ ] Add typing indicators
- [ ] Implement reconnection logic
- [ ] Add moderation features

## Technical Considerations

1. **State Management**: Use in-memory storage initially (dictionaries)
2. **Concurrency**: Use asyncio for handling multiple connections
3. **Error Handling**: Graceful handling of disconnections and timeouts
4. **Testing**: Unit tests for queue and room managers, integration tests for full flow

## File Structure

```
mcp-chat/
├── mcp_chat/
│   ├── __init__.py
│   ├── server.py           # Main FastMCP server
│   ├── models.py           # Data models
│   ├── queue_manager.py    # Queue management logic
│   ├── room_manager.py     # Chat room management
│   └── tools/
│       ├── __init__.py
│       ├── queue.py        # Queue-related tools
│       └── chat.py         # Chat-related tools
├── tests/
│   ├── test_queue.py
│   ├── test_room.py
│   └── test_server.py
└── pyproject.toml
```

## Next Steps

1. Set up project structure and dependencies
2. Implement basic FastMCP server with SSE transport
3. Create queue manager with enter_queue tool
4. Test basic matching functionality
5. Add message exchange capabilities