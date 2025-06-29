# MCP Chat

A fun experiment using MCP (Model Context Protocol) servers as chat clients! This project demonstrates how MCP's tool-calling interface can be repurposed for real-time human-to-human chat.

![MCP Chat Demo](static/demo.gif)

## What is this?

MCP Chat is a proof-of-concept that turns MCP clients into chat applications. Instead of AI assistants calling tools, humans use the same interface to send messages to each other. It's like building a chat app where the "API" is designed for robots, but humans are using it instead!

## Key Features

- **Random matching**: Enter a queue and get matched with another user (like Omegle/ChatRoulette)
- **Private rooms**: Create or join specific rooms for direct conversations
- **Long-polling**: Real-time message delivery without WebSocket support
- **Multiple clients**: Connect from different MCP clients simultaneously
- **Simple & fun**: No authentication, no persistence, just ephemeral chats

## How It Works

The server exposes MCP tools that clients can call:

1. **`enter_queue`** - Join the matchmaking queue
2. **`join_room`** - Join a specific room by ID
3. **`send_message`** - Send a message to your chat partner
4. **`wait_for_message`** - Wait for incoming messages (long-polling)
5. **`leave_chat`** - Leave the current conversation

The magic is that `wait_for_message` blocks until a message arrives, enabling real-time chat through the MCP protocol!

## Quick Start

```bash
# Install dependencies
uv sync

# Run the server
uv run python -m mcp_chat.server

# In another terminal, connect with any MCP client
uv run fastmcp dev http://localhost:8000

# Start chatting!
call enter_queue {"display_name": "Alice"}
```

## The Fun Part

This project explores an unconventional use of MCP:
- MCP is designed for AI assistants to use tools
- But what if humans used those same tools directly?
- The result: a chat system with a very unique "API"!

It's like using a robot's control panel to have a human conversation. Quirky? Yes. Fun? Absolutely!

## Technical Details

- **Language**: Python 3.11+
- **Framework**: FastMCP
- **Storage**: In-memory (ephemeral)
- **Transport**: HTTP with SSE
- **Concurrency**: asyncio with message queues

## Limitations

- Messages are fire-and-forget (only delivered if someone is waiting)
- No persistence - everything is lost on server restart
- No authentication or user accounts
- Single server instance only

## Try It Out!

The best way to understand this project is to try it:
1. Run the server
2. Open two MCP clients
3. Have a conversation with yourself (or a friend)!

## Contributing

This is a fun weekend project! Feel free to:
- Report bugs
- Suggest features
- Share your chat experiences
- Build your own MCP experiments

## License

MIT - Do whatever you want with this!