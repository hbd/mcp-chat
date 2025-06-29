# Quick Testing Guide

## The Fastest Way: Using FastMCP CLI

1. **Start the server** (Terminal 1):
```bash
uv run python -m mcp_chat.server
```

2. **Connect with FastMCP dev client** (Terminal 2):
```bash
uv run fastmcp dev http://localhost:8000
```

3. **In the FastMCP dev client, type these commands**:

```
# See available tools
tools

# Enter the queue
call enter_queue {"display_name": "Alice"}

# You'll see something like:
# {"status": "waiting", "position": 1, "queue_length": 1, "client_id": "abc-123-..."}
```

4. **To test matching, open another terminal** (Terminal 3):
```bash
uv run fastmcp dev http://localhost:8000
```

Then enter:
```
call enter_queue {"display_name": "Bob"}
```

Both clients should now show they're matched!

5. **Exchange messages using the new long-polling approach**:

In Alice's terminal (use the client_id from enter_queue):
```
# Send a message (replace CLIENT_ID with your actual client_id)
call send_message {"room_id": "THE_ROOM_ID", "message": "Hello Bob!", "client_id": "YOUR_CLIENT_ID"}

# Wait for Bob's response (this will block!)
call wait_for_message {"room_id": "THE_ROOM_ID", "client_id": "YOUR_CLIENT_ID"}
```

In Bob's terminal (use Bob's client_id):
```
# Wait for Alice's message (do this first to catch her message)
call wait_for_message {"room_id": "THE_ROOM_ID", "client_id": "YOUR_CLIENT_ID"}
# You'll see: {"message": "Hello Bob!", "sender": "Alice", ...}

# Send a response
call send_message {"room_id": "THE_ROOM_ID", "message": "Hi Alice!", "client_id": "YOUR_CLIENT_ID"}
```

The `wait_for_message` tool blocks until a message arrives, making real-time chat possible!

6. **Leave the chat**:
```
call leave_chat {"room_id": "THE_ROOM_ID", "client_id": "YOUR_CLIENT_ID"}
```

## Important: Client ID System

**NEW**: Each client now gets a unique `client_id` when calling `enter_queue` or `join_room`. You must use this ID in all subsequent calls:

1. Call `enter_queue` or `join_room` and save the `client_id` from the response
2. Use that `client_id` in `send_message`, `wait_for_message`, and `leave_chat`
3. Each client (Claude Code, FastMCP dev, etc.) will get a different ID

This fixes the issue where all clients were seen as the same user!

## Private Rooms with join_room

You can create or join specific rooms:

```bash
# Alice creates a private room
call join_room {"room_id": "alice-bob-chat", "display_name": "Alice"}
# Returns: {"status": "room_created", "client_id": "abc-123-...", ...}

# Alice chooses to wait for Bob to join and message first
call wait_for_message {"room_id": "alice-bob-chat", "client_id": "abc-123-..."}

# Bob joins the same room
call join_room {"room_id": "alice-bob-chat", "display_name": "Bob"}
# Returns: {"status": "joined", "client_id": "xyz-789-...", ...}

# Bob sees Alice is already in the room and chooses to send a greeting
call send_message {"room_id": "alice-bob-chat", "message": "Hi Alice!", "client_id": "xyz-789-..."}

# Bob then waits for Alice's response
call wait_for_message {"room_id": "alice-bob-chat", "client_id": "xyz-789-..."}

# The conversation continues with each person alternating between sending and waiting
```

## Alternative: Test with our Python script

```bash
# Make sure server is running, then:
uv run python test_simple.py
```

This will test all the endpoints and show you exactly what's available.

## What to Look For

1. **Server logs** - Watch the terminal running the server. You'll see:
   - User connections with unique IDs
   - Queue entries
   - Matches being made
   - Messages being delivered to queues

2. **Client responses** - Each tool call returns JSON with:
   - Status information
   - Error messages if something went wrong
   - Room IDs when matched
   - **client_id** for tracking your session