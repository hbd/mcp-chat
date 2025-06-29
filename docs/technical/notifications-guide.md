# MCP Notifications Guide for Chat Server

## Understanding MCP Notifications vs LLM Sampling

### Why Not LLM Sampling?

After researching the FastMCP documentation, we discovered that **LLM sampling is not suitable** for our chat application because:

1. **Purpose Mismatch**: LLM sampling is designed for requesting AI-generated completions, not for relaying messages
2. **Processing Overhead**: Clients would need to process every message through an LLM
3. **Response Requirement**: Sampling expects a generated response, not simple message display

### The Right Approach: MCP Notifications

MCP notifications are perfect for chat because they:
- Are one-way messages (server → client)
- Require no response from the client
- Support real-time push via SSE transport
- Can carry arbitrary payloads (chat messages, status updates)

## Implementing Notifications in FastMCP

### Server-Side Setup

```python
from fastmcp import FastMCP

# Enable SSE transport for push notifications
mcp = FastMCP(
    name="mcp-chat",
    transport="streamable_http"
)

# Store client connections
connections: dict[str, Connection] = {}
```

### Sending Notifications

```python
async def send_notification(user_id: str, method: str, params: dict):
    """Send a notification to a specific client."""
    connection = connections.get(user_id)
    if connection:
        await connection.send_notification({
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        })
```

### Notification Types for Chat

#### 1. Chat Room Found
```python
await send_notification(user_id, "chatroom.found", {
    "room_id": "room_123",
    "partner": {
        "display_name": "Anonymous User"
    }
})
```

#### 2. Message Received
```python
await send_notification(user_id, "message.received", {
    "room_id": "room_123",
    "message": "Hello there!",
    "timestamp": "2024-01-01T12:00:00Z"
})
```

#### 3. Partner Disconnected
```python
await send_notification(user_id, "partner.disconnected", {
    "room_id": "room_123",
    "reason": "left"
})
```

## Client-Side Handling

Clients need to register handlers for our custom notifications:

```python
# Example client code (not part of server)
@client.notification_handler("chatroom.found")
async def handle_chatroom_found(params):
    print(f"Matched! Room ID: {params['room_id']}")

@client.notification_handler("message.received")  
async def handle_message(params):
    print(f"New message: {params['message']}")
```

## Transport Configuration

### Streamable HTTP with SSE

```python
# Server configuration
mcp = FastMCP(
    name="mcp-chat",
    transport="streamable_http",
    transport_options={
        "endpoint": "/mcp",
        "sse_endpoint": "/mcp/sse"  # SSE endpoint for notifications
    }
)
```

### Connection Lifecycle

1. **Client connects** to SSE endpoint
2. **Server stores** connection reference
3. **Server pushes** notifications as events occur
4. **Client reconnects** automatically if connection drops

## Best Practices

1. **Namespace Methods**: Use dot notation (e.g., `chatroom.found`, `message.received`)
2. **Include Metadata**: Always include room_id, timestamps, user info
3. **Handle Disconnections**: Clean up state when clients disconnect
4. **Validate State**: Check if user is in room before sending messages
5. **Error Notifications**: Send error notifications for failed operations

## Example Flow Implementation

```python
@mcp.tool
async def enter_queue(context: Context) -> dict:
    user_id = context.connection_id
    
    # Add to queue
    waiting_queue.append(user_id)
    
    # Check for match
    if len(waiting_queue) >= 2:
        user1_id = waiting_queue.pop(0)
        user2_id = waiting_queue.pop(0)
        
        # Create room
        room_id = str(uuid.uuid4())
        rooms[room_id] = ChatRoom(user1_id, user2_id)
        
        # Notify both users
        await send_notification(user1_id, "chatroom.found", {
            "room_id": room_id,
            "partner": {"id": user2_id}
        })
        
        await send_notification(user2_id, "chatroom.found", {
            "room_id": room_id,
            "partner": {"id": user1_id}
        })
        
        return {"status": "matched", "room_id": room_id}
    
    return {"status": "waiting", "position": len(waiting_queue)}
```

## Testing Notifications

1. Use FastMCP's test client to verify notifications
2. Log all sent notifications during development
3. Test connection drops and reconnection
4. Verify notification order and timing