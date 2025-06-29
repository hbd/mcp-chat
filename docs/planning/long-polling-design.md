# Long-Polling Design for MCP Chat

## Concept

Instead of using notifications (which require special client support), we use a blocking tool call that waits for incoming messages. This makes our chat server compatible with ANY MCP client.

## How It Works

```
User A                          Server                          User B
  |                               |                               |
  |-- send_message("Hello") ----->|                               |
  |<-- "Message sent" ------------|                               |
  |                               |                               |
  |-- wait_for_message() -------->|                               |
  |   (blocks waiting...)         |<----- send_message("Hi!") ---|
  |<-- {"message": "Hi!"} --------|                               |
  |                               |                               |
  |-- send_message("How are?") -->|                               |
  |<-- "Message sent" ------------|                               |
  |                               |<----- wait_for_message() ----|
  |-- wait_for_message() -------->|       (blocks waiting...)     |
  |   (blocks waiting...)         |                               |
```

## New Tool Design

### `wait_for_message`
- **Purpose**: Block until a message is received in the current chat room
- **Parameters**: 
  - `room_id`: The chat room to listen in
  - `timeout`: Optional timeout in seconds (default: 60)
- **Returns**: 
  - On success: `{"message": "text", "sender": "display_name", "timestamp": "..."}`
  - On timeout: `{"timeout": true, "message": "No message received"}`
  - On error: `{"error": "Not in room"}` or `{"error": "Partner disconnected"}`

## Implementation Approach

```python
@mcp.tool()
async def wait_for_message(room_id: str, timeout: int = 60) -> Dict[str, Any]:
    """Wait for a message in the chat room (long-polling)."""
    # Get user and validate room
    user = connections.get(connection_id)
    room = await room_manager.get_room(room_id)
    
    # Create a message queue for this user
    message_queue = asyncio.Queue()
    
    # Register the queue to receive messages
    if room_id not in message_queues:
        message_queues[room_id] = {}
    message_queues[room_id][user.user_id] = message_queue
    
    try:
        # Wait for a message with timeout
        message = await asyncio.wait_for(
            message_queue.get(),
            timeout=timeout
        )
        return {
            "message": message["content"],
            "sender": message["sender_name"],
            "timestamp": message["timestamp"]
        }
    except asyncio.TimeoutError:
        return {"timeout": True, "message": "No message received"}
    finally:
        # Clean up queue registration
        if room_id in message_queues:
            message_queues[room_id].pop(user.user_id, None)
```

## Modified `send_message` Tool

```python
@mcp.tool()
async def send_message(room_id: str, message: str) -> Dict[str, Any]:
    """Send a message and notify waiting recipients."""
    # ... validation ...
    
    # Create message object
    msg = {
        "content": message,
        "sender_name": user.name,
        "sender_id": user.user_id,
        "timestamp": datetime.now().isoformat()
    }
    
    # Deliver to all waiting recipients in the room
    if room_id in message_queues:
        for recipient_id, queue in message_queues[room_id].items():
            if recipient_id != user.user_id:  # Don't send to self
                await queue.put(msg)
    
    return {"success": True, "sent_at": msg["timestamp"]}
```

## Client Usage (Works with ANY MCP Client!)

### Using FastMCP Dev Client
```bash
# Terminal 1 - Alice
> call enter_queue {"display_name": "Alice"}
# Get room_id when matched

> call send_message {"room_id": "abc-123", "message": "Hello Bob!"}
> call wait_for_message {"room_id": "abc-123"}
# Blocks until Bob responds...
# {"message": "Hi Alice!", "sender": "Bob", "timestamp": "..."}

> call send_message {"room_id": "abc-123", "message": "How are you?"}
> call wait_for_message {"room_id": "abc-123"}
# Continues conversation...
```

### Using Standard HTTP/curl
```bash
# Send message
curl -X POST http://localhost:8000/mcp/v1/tools/call \
  -d '{"method": "send_message", "params": {"room_id": "abc", "message": "Hello!"}}'

# Wait for response (this blocks!)
curl -X POST http://localhost:8000/mcp/v1/tools/call \
  -d '{"method": "wait_for_message", "params": {"room_id": "abc"}}'
```

## Advantages

1. **Universal Compatibility**: Works with ANY MCP client
2. **Simple Implementation**: No complex notification system needed
3. **Natural Flow**: Mimics request-response pattern
4. **No Special Client**: Can even use curl!
5. **Timeout Control**: Clients can specify how long to wait

## Considerations

1. **Blocking Calls**: Client is blocked while waiting (but that's the point!)
2. **Connection Management**: Need to handle dropped connections gracefully
3. **Multiple Messages**: Might need a `get_messages` tool for history
4. **Timeout Handling**: Clients need to retry after timeout

## Enhanced Tool Set

1. `enter_queue` - Join queue
2. `send_message` - Send a message
3. `wait_for_message` - Wait for incoming message (blocking)
4. `get_messages` - Get recent message history (non-blocking)
5. `leave_chat` - Leave the chat

## Migration Path

1. Keep existing notification system (for future use)
2. Add message queue management
3. Implement `wait_for_message` tool
4. Update `send_message` to deliver to queues
5. Test with various clients

This approach is much simpler and more compatible than building a custom client!