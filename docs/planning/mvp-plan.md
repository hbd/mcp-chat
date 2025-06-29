# MVP Implementation Plan - Random Chat Server

## Simplified Scope

For the initial version, we'll build a basic chat roulette style MCP server that:
1. Connects users randomly (no interest matching yet)
2. Allows text message exchange
3. Handles basic disconnections

## Core Features

### Tools

1. **`enter_queue`**
   - Adds user to waiting queue
   - Automatically matches when 2 users are waiting
   - Returns status (waiting/matched)

2. **`send_message`**
   - Sends text to chat partner
   - Requires active room_id

3. **`leave_chat`**
   - Exits current chat
   - Returns user to main state

### Notifications (Server → Client)

1. **`chatroom.found`**
   - Sent when match is made
   - Includes room_id for sending messages

2. **`message.received`**
   - Relays messages from chat partner
   
3. **`partner.disconnected`**
   - Notifies when partner leaves

## Simple Implementation Flow

```python
# 1. User enters queue
await client.call_tool("enter_queue")
# Response: {"status": "waiting", "position": 1}

# 2. When matched, receive notification
# Notification: {"method": "chatroom.found", "params": {"room_id": "abc123"}}

# 3. Exchange messages
await client.call_tool("send_message", {"room_id": "abc123", "message": "Hello!"})
# Partner receives: {"method": "message.received", "params": {"message": "Hello!"}}

# 4. Leave chat
await client.call_tool("leave_chat", {"room_id": "abc123"})
```

## Minimal File Structure

```
mcp-chat/
├── mcp_chat/
│   ├── __init__.py
│   ├── server.py        # Main server with all logic
│   └── models.py        # Simple dataclasses
├── pyproject.toml
└── tests/
    └── test_server.py
```

## Key Implementation Notes

1. **Transport**: Use SSE-enabled HTTP transport for real-time notifications
2. **Storage**: Simple in-memory dictionaries for queue and rooms
3. **Matching**: Basic FIFO - first two users in queue get matched
4. **IDs**: Use UUID4 for room_ids and auto-generated user_ids

## Development Steps

1. **Setup** (30 min)
   - Initialize project with uv
   - Add FastMCP dependency
   - Create basic file structure

2. **Core Server** (1 hour)
   - Create FastMCP server instance
   - Set up SSE transport
   - Add basic models (User, ChatRoom)

3. **Queue System** (1 hour)
   - Implement enter_queue tool
   - Add matching logic
   - Send chatroom.found notifications

4. **Messaging** (1 hour)
   - Implement send_message tool
   - Add message relay via notifications
   - Handle leave_chat

5. **Testing** (30 min)
   - Basic integration test
   - Manual testing with MCP client

Total estimated time: ~4 hours for basic working prototype