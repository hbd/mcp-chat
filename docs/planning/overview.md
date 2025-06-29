# MCP Chat Server - Project Overview

## What We're Building

A simple "chat roulette" style MCP server that:
- Randomly connects users for 1-on-1 text chat
- Uses MCP tools for user actions (join queue, send message, leave)
- Uses MCP notifications for real-time updates (match found, new message)
- Runs on Streamable HTTP transport with SSE for push notifications

## Key Design Decisions

1. **No LLM Sampling** - Use notifications for real-time messaging
2. **Random Matching** - Simple FIFO queue, no interest matching yet
3. **In-Memory Storage** - No database for MVP
4. **Python + FastMCP** - Using uv, mypy, and ruff for development

## Core User Flow

```
1. User calls enter_queue tool
2. Server adds user to waiting queue
3. When 2 users are waiting, server matches them
4. Server sends chatroom.found notification to both users
5. Users exchange messages using send_message tool
6. Server relays messages via message.received notifications
7. Either user can call leave_chat to end conversation
```

## Project Structure

```
mcp-chat/
├── docs/                    # Planning documents
├── mcp_chat/               # Main package
│   ├── server.py          # FastMCP server implementation
│   └── models.py          # Data structures
├── tests/                  # Test files  
├── pyproject.toml         # Project config & dependencies
├── CLAUDE.md              # AI assistant guidelines
└── README.md              # Project documentation
```

## Next Steps

1. Initialize project with `uv init`
2. Add FastMCP dependency
3. Implement basic server with queue and matching
4. Add message exchange
5. Test with MCP client

## Resources

- [Implementation Plan](./implementation-plan.md) - Detailed architecture
- [MVP Plan](./mvp-plan.md) - Simplified first version
- [Technical Decisions](./technical-decisions.md) - Key choices explained