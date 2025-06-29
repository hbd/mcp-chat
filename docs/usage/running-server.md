# Running the MCP Chat Server

## Quick Start

1. Install dependencies:
```bash
uv sync
```

2. Run the server:
```bash
uv run python -m mcp_chat.server
```

The server will start on `http://localhost:8000`

## Available Tools

### `join_room`
- **Purpose**: Join a specific chat room directly
- **Parameters**:
  - `room_id`: The room ID to join (creates room if it doesn't exist)
  - `display_name`: Your display name (required)
- **Returns**: Join status with `client_id`
- **Important**: After joining, prompt the user whether to wait for messages or send first
- **Use cases**:
  - Create a private room with a custom ID
  - Join a friend in a specific room
  - Rejoin a room after disconnection (with new client_id)

### `send_message`
- **Purpose**: Send a message to your chat partner
- **Parameters**:
  - `room_id`: The chat room ID
  - `message`: Your message text
- **Returns**: Success status with message ID

### `wait_for_message`
- **Purpose**: Wait for a message from your chat partner (long-polling)
- **Parameters**:
  - `room_id`: The chat room ID
  - `timeout` (optional): Timeout in seconds (default: 60, max: 300)
- **Returns**: 
  - On message: `{"message": "text", "sender": "name", "timestamp": "...", "message_id": "..."}`
  - On timeout: `{"timeout": true, "message": "No message received"}`
  - On error: `{"error": "error message"}`
- **Notes**: 
  - This tool blocks until a message is received or timeout occurs!
  - If you cancel this tool call, the message queue is cleaned up automatically
  - Messages sent while no one is waiting are not queued (fire-and-forget)

### `leave_chat`
- **Purpose**: Leave the current chat room
- **Parameters**:
  - `room_id`: The chat room ID
- **Returns**: Success confirmation

## Notifications

The server sends these notifications via SSE:

- `message.received`: When you receive a message
- `partner.disconnected`: When your partner leaves or disconnects

## Testing with FastMCP CLI

You can test the server using the FastMCP CLI:

```bash
# In one terminal, start the server
uv run python -m mcp_chat.server

# In another terminal, connect as a client
uv run fastmcp dev http://localhost:8000

# Join a room
> join_room {"room_id": "my-room", "display_name": "Alice"}

# Send a message
> send_message {"room_id": "my-room", "message": "Hello!", "client_id": "..."}

# Leave the chat
> leave_chat {"room_id": "my-room", "client_id": "..."}
```

## Current Limitations

1. **Notifications**: Logged but not actually sent via SSE yet
2. **Persistence**: All data is in-memory and lost on restart
3. **Single Instance**: No support for distributed/multi-instance deployment
4. **No reconnection**: If you disconnect, you need a new client_id

## Development

Run type checking:
```bash
uv run mypy .
```

Run linting/formatting:
```bash
uv run ruff format .
uv run ruff check --fix .
```