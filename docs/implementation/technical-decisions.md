# Technical Decisions

## MCP Communication Pattern

### Decision: Use Notifications instead of LLM Sampling

**Context**: Initially considered using MCP's LLM sampling feature for real-time communication between chat clients.

**Research Findings**:
- LLM sampling is designed for requesting AI-generated responses, not general messaging
- It follows a request-response pattern where the server asks for LLM completion
- The client is expected to process messages through an LLM and return generated text

**Decision**: Use MCP's notification system for all real-time updates

**Rationale**:
1. **Notifications are one-way messages** - perfect for server-to-client updates
2. **No response required** - ideal for chat messages and status updates  
3. **SSE transport support** - Server-Sent Events enable true real-time push
4. **Direct message relay** - can send exact user messages without LLM processing

### Implementation Pattern

```python
# Correct: Using notifications for real-time updates
async def notify_client(connection_id: str, method: str, params: dict):
    await server.send_notification(
        connection_id,
        {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
    )

# When chat room is found
await notify_client(user.connection_id, "chatroom.found", {
    "room_id": room.room_id,
    "partner": partner.display_name
})

# When message is received
await notify_client(recipient.connection_id, "message.received", {
    "room_id": room.room_id,
    "message": message_text,
    "timestamp": datetime.now().isoformat()
})
```

## Transport Choice

### Decision: Streamable HTTP with SSE

**Options Considered**:
1. STDIO - Standard input/output
2. HTTP - Basic request/response
3. Streamable HTTP - HTTP with Server-Sent Events

**Decision**: Streamable HTTP

**Rationale**:
- SSE enables server-push notifications
- Maintains persistent connections
- Works well with web-based MCP clients
- Supports multiple concurrent connections

## State Management

### Decision: In-Memory Storage for MVP

**Decision**: Use Python dictionaries for queue and room storage

**Rationale**:
- Simplest implementation for prototype
- No external dependencies
- Fast lookups and updates
- Adequate for testing and development

**Future Considerations**:
- Redis for distributed state
- PostgreSQL for chat history
- Message queue for scalability

## Matching Algorithm

### Decision: Simple FIFO Queue

**Decision**: First-come, first-served matching

**Implementation**:
```python
waiting_queue: deque[User] = deque()

# When user joins
waiting_queue.append(user)

# Check for match
if len(waiting_queue) >= 2:
    user1 = waiting_queue.popleft()
    user2 = waiting_queue.popleft()
    create_chat_room(user1, user2)
```

**Rationale**:
- Simplest possible implementation
- No matching logic needed for MVP
- Easy to test and debug
- Can add interest matching later

## Error Handling

### Decision: Graceful Degradation

**Patterns**:
1. **Disconnection**: Remove from queue/room, notify partner
2. **Invalid room**: Return error via tool response
3. **Network issues**: Rely on SSE reconnection

**Example**:
```python
@mcp.tool
async def send_message(room_id: str, message: str) -> dict:
    room = rooms.get(room_id)
    if not room:
        return {"error": "Room not found"}
    
    if not room.active:
        return {"error": "Chat has ended"}
    
    # Send message...
    return {"success": True}
```