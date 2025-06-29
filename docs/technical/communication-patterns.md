# FastMCP Communication Patterns Guide

## Overview

FastMCP provides several distinct communication patterns between servers and clients. Each serves a specific purpose and should be used in appropriate scenarios.

## 1. Logging - Server Diagnostics & Monitoring

### What is it?
A unidirectional channel for servers to send log messages to clients.

### Direction
Server → Client (one-way)

### When to use it?
- **Debugging**: Track what your server is doing internally
- **Error reporting**: Notify clients about server-side errors
- **Audit trails**: Record important server actions
- **Operational monitoring**: Track server health and performance

### Example usage:
```python
# Server side
from fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
async def process_data(data: str):
    # Log different severity levels
    await mcp.log.debug(f"Starting to process: {data}")
    await mcp.log.info("Data validation passed")
    
    if len(data) > 1000:
        await mcp.log.warning("Large data size may slow processing")
    
    try:
        result = await heavy_processing(data)
        await mcp.log.info("Processing completed successfully")
        return result
    except Exception as e:
        await mcp.log.error(f"Processing failed: {e}")
        raise
```

### Client side handling:
```python
# Client receives logs passively
async def handle_log(level: str, message: str, logger: str):
    print(f"[{level}] {logger}: {message}")

client = MCPClient()
client.log_handler = handle_log
```

## 2. Progress - Long Operation Feedback

### What is it?
A mechanism for servers to report progress on long-running operations.

### Direction
Server → Client (one-way)

### When to use it?
- **File operations**: Upload/download progress
- **Batch processing**: Show items processed vs total
- **Long computations**: Indicate completion percentage
- **Multi-step workflows**: Show current step

### Example usage:
```python
# Server side
@mcp.tool()
async def batch_process_files(file_ids: list[str]):
    total = len(file_ids)
    
    for i, file_id in enumerate(file_ids):
        # Report progress
        await mcp.progress(
            current=i + 1,
            total=total,
            message=f"Processing file {file_id}"
        )
        
        await process_single_file(file_id)
    
    return {"processed": total}
```

### Client side handling:
```python
async def handle_progress(current: int, total: int, message: str):
    percentage = (current / total * 100) if total else 0
    print(f"Progress: {percentage:.1f}% - {message}")

client.progress_handler = handle_progress
```

## 3. Sampling - LLM Integration

### What is it?
A request-response pattern where servers can ask clients for LLM completions.

### Direction
Server → Client → Server (bidirectional)

### When to use it?
- **AI-enhanced tools**: Server needs LLM capabilities
- **Text generation**: Server orchestrates complex generation
- **Analysis with AI**: Server needs AI to process data
- **Multi-step reasoning**: Server coordinates multiple LLM calls

### Example usage:
```python
# Server side
@mcp.tool()
async def summarize_with_context(text: str, context: str):
    # Ask client's LLM to generate a summary
    summary = await mcp.sample(
        messages=[
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": f"Summarize this text: {text}"}
        ],
        temperature=0.7,
        max_tokens=200
    )
    
    # Process the LLM response
    return {"summary": summary}
```

### Client side handling:
```python
async def handle_sampling(messages, params, context):
    # Use your LLM integration (OpenAI, Anthropic, etc.)
    response = await llm.complete(
        messages=messages,
        temperature=params.temperature,
        max_tokens=params.max_tokens
    )
    return response.text

client.sampling_handler = handle_sampling
```

## 4. Messages/Notifications - Protocol-Level Communication

### What is it?
Low-level handler for all MCP protocol messages and custom notifications.

### Direction
Primarily Server → Client (notifications), some bidirectional

### When to use it?
- **Custom notifications**: Implement your own notification types
- **State change monitoring**: React to server capability changes
- **Protocol debugging**: Monitor all communications
- **Advanced integrations**: Custom protocol extensions

### Example usage:
```python
# Server side - Custom notifications
async def notify_clients(method: str, params: dict):
    # Send custom notification to all connected clients
    await mcp.send_notification({
        "jsonrpc": "2.0",
        "method": method,
        "params": params
    })

# Example: Custom chat notification
await notify_clients("chat.message_received", {
    "room_id": "room123",
    "message": "Hello!",
    "timestamp": datetime.now().isoformat()
})
```

### Client side handling:
```python
async def handle_message(message: dict):
    if message.get("method") == "chat.message_received":
        params = message.get("params", {})
        print(f"New message in {params['room_id']}: {params['message']}")

client.message_handler = handle_message
```

## Comparison Chart

| Pattern | Use Case | Response? | Best For |
|---------|----------|-----------|----------|
| **Logging** | Server diagnostics | No | Debugging, monitoring, errors |
| **Progress** | Operation status | No | Progress bars, status updates |
| **Sampling** | LLM requests | Yes | AI features, text generation |
| **Messages** | Custom protocols | Sometimes | Chat, real-time updates, state changes |

## For Your Chat Server

Based on your use case, here's what you need:

1. **Messages/Notifications** ✅ - For real-time chat messages
   ```python
   # Send chat messages between users
   await notify_client("message.received", {
       "room_id": room_id,
       "message": text,
       "from": sender_id
   })
   ```

2. **Logging** ✅ - For debugging and monitoring
   ```python
   await mcp.log.info(f"User {user_id} joined queue")
   await mcp.log.info(f"Matched users in room {room_id}")
   ```

3. **Progress** ❌ - Not needed (no long operations)

4. **Sampling** ❌ - Not needed (no AI features in basic chat)

## Key Principles

1. **Use the right tool**: Each pattern has a specific purpose
2. **Don't overload**: Don't use sampling for simple notifications
3. **Keep it simple**: Start with tools and notifications, add others as needed
4. **Think about direction**: Some are one-way, only sampling is bidirectional
5. **Consider the client**: What capabilities does your client need to support?