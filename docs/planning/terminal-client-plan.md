# Terminal Chat Client Plan

## Technology Choice: Textual

### Why Textual?

1. **Built for Async** - Perfect for handling MCP notifications while maintaining UI responsiveness
2. **Modern Python** - Full type hints, async/await support
3. **Rich Features** - Scrollable areas, input widgets, styled text out of the box
4. **Active Development** - Well-maintained by the Rich team
5. **CSS-like Styling** - Familiar styling system
6. **Event-Driven** - Natural fit for chat notifications

### Alternatives Considered

- **Rich** - Great for output formatting but not full TUI apps
- **Blessed** - Powerful but more complex, less modern
- **Urwid** - Mature but dated API design
- **Prompt Toolkit** - Good for input but not full UI

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                Terminal Chat Client              │
├─────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────┐   │
│  │          Textual UI Layer               │   │
│  │  - ChatDisplay widget                   │   │
│  │  - InputBox widget                      │   │
│  │  - StatusBar widget                     │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │         ChatClient Class                │   │
│  │  - FastMCP Client wrapper               │   │
│  │  - Message queue                        │   │
│  │  - Connection state                     │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │      NotificationHandler                │   │
│  │  - on_notification router               │   │
│  │  - UI update callbacks                  │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## UI Layout

```
┌──────────────────────────────────────────────────┐
│ MCP Chat - Connected to: http://localhost:8000   │
├──────────────────────────────────────────────────┤
│                                                  │
│  [System] Welcome to MCP Chat!                   │
│  [System] Type /help for commands                │
│                                                  │
│  [You] Hello!                                    │
│  [Alice] Hi there!                               │
│  [You] How are you?                              │
│  [Alice] I'm doing great, thanks!                │
│                                                  │
│                                                  │
│                                                  │
│                                                  │
├──────────────────────────────────────────────────┤
│ Status: In chat with Alice (Room: abc-123)      │
├──────────────────────────────────────────────────┤
│ > Type your message...                           │
└──────────────────────────────────────────────────┘
```

## Core Components

### 1. Main Application Class
```python
class ChatApp(App):
    """Main Textual application."""
    - Manages UI lifecycle
    - Coordinates between UI and client
    - Handles user commands
```

### 2. Chat Client
```python
class MCPChatClient:
    """Wrapper around FastMCP client."""
    - Connects to MCP server
    - Calls tools (enter_queue, send_message, leave_chat)
    - Manages connection state
```

### 3. Notification Handler
```python
class ChatNotificationHandler(MessageHandler):
    """Handles MCP notifications."""
    - Routes notifications to UI updates
    - Handles: chatroom.found, message.received, partner.disconnected
```

### 4. UI Widgets

#### ChatDisplay
- Scrollable message history
- Colored message formatting
- System message support

#### InputBox
- Message input with history
- Command support (/help, /leave, /quit)
- Enter to send

#### StatusBar
- Connection status
- Current room/partner info
- Queue position when waiting

## Features

### Phase 1: Core Chat
- [x] Connect to MCP server
- [x] Enter queue command
- [x] Display queue status
- [x] Show match notification
- [x] Send/receive messages
- [x] Leave chat
- [x] Basic error handling

### Phase 2: Enhanced UX
- [ ] Message timestamps
- [ ] Typing indicators
- [ ] Connection retry
- [ ] Message history
- [ ] Sound notifications
- [ ] Multiple color themes

### Phase 3: Advanced
- [ ] File sharing
- [ ] Emoji support
- [ ] Chat history save/load
- [ ] Multiple server support

## Commands

- `/enter [name]` - Enter queue with optional display name
- `/leave` - Leave current chat
- `/quit` or `/exit` - Exit the application
- `/help` - Show available commands
- `/status` - Show current status

## Error Handling

1. **Connection Errors**
   - Display clear error message
   - Offer retry option
   - Maintain UI responsiveness

2. **MCP Errors**
   - Show tool error responses
   - Guide user to correct action

3. **Notification Errors**
   - Log but don't crash
   - Show warning in status bar

## Dependencies

```toml
[dependency-groups]
client = [
    "textual>=0.47.0",
    "fastmcp[client]>=2.0.0",
    "httpx>=0.25.0",
]
```

## File Structure

```
mcp_chat/
├── client/
│   ├── __init__.py
│   ├── app.py          # Main Textual app
│   ├── client.py       # MCP client wrapper
│   ├── widgets.py      # Custom UI widgets
│   ├── handlers.py     # Notification handlers
│   └── styles.css      # Textual CSS styles
└── __main__.py         # Entry point for client
```

## Next Steps

1. Add Textual to dependencies
2. Create basic app skeleton
3. Implement MCP client wrapper
4. Build UI widgets
5. Connect notification handlers
6. Add command processing
7. Test with server

## Testing Strategy

1. **Unit Tests**
   - Test client methods
   - Test notification parsing
   - Test command parsing

2. **Integration Tests**
   - Test with real server
   - Test notification flow
   - Test error scenarios

3. **Manual Testing**
   - Full chat flow
   - Edge cases
   - UI responsiveness