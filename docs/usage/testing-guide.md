# Testing the MCP Chat Server

## Method 1: Using FastMCP Dev Client (Recommended)

FastMCP provides a built-in development client that's perfect for testing:

```bash
# Start the server in one terminal
uv run python -m mcp_chat.server

# In another terminal, connect as a client
uv run fastmcp dev http://localhost:8000
```

Once connected, you can call tools interactively:

```
# Enter the queue
> call enter_queue {"display_name": "Alice"}

# After being matched, send a message
> call send_message {"room_id": "abc-123", "message": "Hello!"}

# Leave the chat
> call leave_chat {"room_id": "abc-123"}
```

## Method 2: Using curl for Direct HTTP Testing

Since FastMCP uses HTTP transport, you can test with curl:

```bash
# List available tools
curl http://localhost:8000/mcp/v1/tools/list

# Call enter_queue
curl -X POST http://localhost:8000/mcp/v1/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "enter_queue",
    "params": {"display_name": "Alice"}
  }'

# Call send_message
curl -X POST http://localhost:8000/mcp/v1/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "send_message",
    "params": {
      "room_id": "YOUR_ROOM_ID",
      "message": "Hello there!"
    }
  }'
```

## Method 3: Create a Test Client Script

Create a simple Python test client:

```python
# test_client.py
import asyncio
from fastmcp.client import FastMCPClient

async def test_chat():
    # Connect to the server
    client = FastMCPClient(transport="http://localhost:8000")
    await client.connect()
    
    # Enter queue
    result = await client.call_tool(
        "enter_queue", 
        {"display_name": "TestUser"}
    )
    print(f"Queue result: {result}")
    
    # If matched, the result will contain room_id
    if result.get("status") == "matched":
        room_id = result["room_id"]
        
        # Send a message
        msg_result = await client.call_tool(
            "send_message",
            {"room_id": room_id, "message": "Hello from test client!"}
        )
        print(f"Message sent: {msg_result}")
        
        # Leave chat
        leave_result = await client.call_tool(
            "leave_chat",
            {"room_id": room_id}
        )
        print(f"Left chat: {leave_result}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_chat())
```

## Method 4: Multi-Client Testing Script

To test matching between users, you need multiple clients:

```python
# test_multiple_clients.py
import asyncio
from fastmcp.client import FastMCPClient

async def simulate_user(name: str):
    client = FastMCPClient(transport="http://localhost:8000")
    await client.connect()
    
    print(f"{name}: Entering queue...")
    result = await client.call_tool(
        "enter_queue",
        {"display_name": name}
    )
    print(f"{name}: {result}")
    
    # Keep the client alive to receive notifications
    if result.get("status") == "matched":
        room_id = result["room_id"]
        print(f"{name}: Matched! Room ID: {room_id}")
        
        # Send a greeting
        await client.call_tool(
            "send_message",
            {"room_id": room_id, "message": f"Hello from {name}!"}
        )
        
        # Wait a bit for messages
        await asyncio.sleep(5)
        
        # Leave
        await client.call_tool("leave_chat", {"room_id": room_id})
    
    await client.close()

async def main():
    # Start two users concurrently
    await asyncio.gather(
        simulate_user("Alice"),
        simulate_user("Bob")
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## Method 5: Using MCP Inspector (if available)

Some MCP implementations provide inspector tools:

```bash
# If you have mcp-inspector installed
mcp-inspector connect http://localhost:8000
```

## Testing Scenarios

### Scenario 1: Basic Matching
1. Start User A - enters queue (should see "waiting")
2. Start User B - enters queue (both should be matched)
3. Exchange messages
4. One user leaves

### Scenario 2: Queue Management
1. User A enters queue
2. User A tries to enter queue again (should see "already_waiting")
3. User B enters and matches
4. User A tries to enter queue while in chat (should see "already_in_chat")

### Scenario 3: Error Handling
1. Try to send message without being in a room
2. Try to send message with invalid room_id
3. Try to leave a room you're not in

## Monitoring

While testing, watch the server logs to see:
- User connections
- Queue operations
- Matching events
- Message routing
- Disconnections

The server logs all major operations, which helps debug the flow.

## Known Limitations for Testing

1. **Connection ID Issue**: Currently, all users have the same connection ID ("unknown"), so true multi-user testing won't work properly yet.
2. **No Real SSE**: Notifications are only logged, not actually sent to clients.
3. **No Persistence**: Server restart loses all state.

For proper testing, you'll need to implement proper connection tracking first.