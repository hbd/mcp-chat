"""MCP Chat Server implementation."""

from typing import Dict, Any, Optional
import asyncio
import logging
import uuid
from datetime import datetime

from fastmcp import FastMCP

from mcp_chat.models import User, Message
from mcp_chat.managers import QueueManager, RoomManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server with SSE transport
mcp: Any = FastMCP(name="mcp-chat", version="0.1.0")

# Initialize managers
queue_manager = QueueManager()
room_manager = RoomManager()

# Store active connections (connection_id -> User)
connections: Dict[str, User] = {}

# Message queues for long-polling (room_id -> {user_id -> Queue})
message_queues: Dict[str, Dict[str, asyncio.Queue[Dict[str, Any]]]] = {}


@mcp.tool()
async def enter_queue(display_name: Optional[str] = None) -> Dict[str, Any]:
    """Enter the queue to be matched with another user.
    
    Each call creates a new session with a unique client_id. Use the returned
    client_id for all subsequent calls (send_message, wait_for_message, leave_chat).

    Args:
        display_name: Optional display name for the user

    Returns:
        Status information about queue position or match (includes generated client_id)
    """
    # Generate a unique client_id for this user
    connection_id = str(uuid.uuid4())

    # Create new user (always new since each enter_queue generates a new session)
    user = User(display_name=display_name, connection_id=connection_id)
    connections[connection_id] = user

    # Add to queue
    position = await queue_manager.add_user(user)

    # Log for debugging
    logger.info(f"User {user.name} entered queue at position {position}")

    # Try to match users
    pair = await queue_manager.pop_pair()
    if pair:
        user1, user2 = pair

        # Create room
        room = await room_manager.create_room(user1, user2)

        # Log match
        logger.info(f"Matched {user1.name} with {user2.name} in room {room.room_id}")

        # Send notifications to both users
        await send_notification(
            user1.connection_id,
            "chatroom.found",
            {
                "room_id": room.room_id,
                "partner": {"user_id": user2.user_id, "display_name": user2.name},
            },
        )

        await send_notification(
            user2.connection_id,
            "chatroom.found",
            {
                "room_id": room.room_id,
                "partner": {"user_id": user1.user_id, "display_name": user1.name},
            },
        )

        # Return success for the current user
        partner = user2 if user.user_id == user1.user_id else user1
        return {
            "status": "matched",
            "room_id": room.room_id,
            "partner": {"user_id": partner.user_id, "display_name": partner.name},
            "client_id": connection_id
        }

    # Still waiting
    return {
        "status": "waiting",
        "position": await queue_manager.get_position(user.user_id) or 1,
        "queue_length": await queue_manager.get_queue_length(),
        "client_id": connection_id
    }


@mcp.tool()
async def join_room(room_id: str, display_name: str) -> Dict[str, Any]:
    """Join a specific chat room directly.
    
    Creates a new session with a unique client_id and adds the user to the specified room.
    Useful for rejoining a room or creating private rooms.
    
    IMPORTANT: After joining a room, prompt the user to choose whether they want to:
    - Wait for messages (call wait_for_message) - if they expect to receive first
    - Send a message (call send_message) - if they want to initiate conversation
    
    This gives users control over the conversation flow rather than automatically blocking.
    
    Args:
        room_id: The ID of the room to join
        display_name: Display name for the user (required)
        
    Returns:
        Success status with client_id or error information
    """
    # Generate a unique client_id for this user
    connection_id = str(uuid.uuid4())
    
    # Create new user
    user = User(display_name=display_name, connection_id=connection_id)
    connections[connection_id] = user
    
    # Check if room exists
    room = await room_manager.get_room(room_id)
    if not room:
        # Create a new room with just this user
        room = await room_manager.create_room(user, user)  # Temporarily both users
        room.room_id = room_id  # Override the generated ID
        # Update the room in manager
        room_manager._rooms[room_id] = room
        room_manager._user_to_room[user.user_id] = room_id
        
        logger.info(f"Created new room {room_id} for {user.name}")
        
        return {
            "status": "room_created",
            "room_id": room_id,
            "client_id": connection_id,
            "message": "New room created, waiting for another user to join"
        }
    
    # Check if room is active
    if not room.active:
        return {
            "status": "error",
            "error": "Room is no longer active",
            "client_id": connection_id
        }
    
    # Check if room has space (max 2 users)
    current_users = []
    active_user_ids = {u.user_id for u in connections.values()}
    if room.user1 and room.user1.user_id in active_user_ids:
        current_users.append(room.user1)
    if room.user2 and room.user2.user_id != room.user1.user_id and room.user2.user_id in active_user_ids:
        current_users.append(room.user2)
    
    if len(current_users) >= 2:
        return {
            "status": "error", 
            "error": "Room is full",
            "client_id": connection_id
        }
    
    # Add user to room
    if len(current_users) == 0:
        # First user in existing room
        room.user1 = user
    else:
        # Second user joining
        room.user2 = user
        # Notify the first user
        partner = room.user1
        if partner and partner.user_id in connections:
            # Send notification about new user joining
            if room_id in message_queues and partner.user_id in message_queues[room_id]:
                join_msg = {
                    "content": f"[System] {user.name} has joined the chat.",
                    "sender_name": "System",
                    "sender_id": "system",
                    "timestamp": datetime.now().isoformat(),
                    "message_id": str(uuid.uuid4()),
                    "system": True
                }
                try:
                    message_queues[room_id][partner.user_id].put_nowait(join_msg)
                except (asyncio.QueueFull, RuntimeError) as e:
                    # Queue might be full or closed
                    logger.debug(f"Could not send join notification: {e}")
    
    # Update user-to-room mapping
    room_manager._user_to_room[user.user_id] = room_id
    
    logger.info(f"User {user.name} joined room {room_id}")
    
    # Get partner info if exists
    partner = room.get_partner(user.user_id)
    
    return {
        "status": "joined",
        "room_id": room_id,
        "client_id": connection_id,
        "partner": {"display_name": partner.name} if partner else None,
        "message": "Successfully joined room" + (f" with {partner.name}" if partner else ", waiting for partner")
    }


@mcp.tool()
async def send_message(room_id: str, message: str, client_id: str) -> Dict[str, Any]:
    """Send a message to your chat partner.
    
    IMPORTANT: After sending a message, you should immediately call wait_for_message
    to receive the response. This enables real-time conversation flow.
    
    Typical usage:
    1. Call send_message to send your message
    2. Call wait_for_message to wait for the response
    3. Repeat

    Args:
        room_id: The ID of the chat room
        message: The message to send
        client_id: Your client identifier (from enter_queue or join_room)

    Returns:
        Success status or error information
    """
    # Use the provided client_id
    connection_id = client_id

    # Get user
    user = connections.get(connection_id)
    if not user:
        logger.error(f"User not found for client_id: {client_id}")
        logger.debug(f"Active connections: {list(connections.keys())}")
        return {"success": False, "error": f"User not found. Invalid client_id: {client_id}"}

    # Get room
    room = await room_manager.get_room(room_id)
    if not room:
        return {"success": False, "error": "Room not found"}

    if not room.active:
        return {"success": False, "error": "Chat has ended"}

    # Verify user is in the room
    if not room.has_user(user.user_id):
        return {"success": False, "error": "You are not in this room"}

    # Get partner
    partner = room.get_partner(user.user_id)
    if not partner:
        return {"success": False, "error": "Partner not found"}

    # Create message
    msg = Message(room_id=room_id, sender_id=user.user_id, content=message)

    # Log message
    logger.info(f"Message from {user.name} to {partner.name}: {message[:50]}...")

    # Create message data
    message_data = {
        "content": message,
        "sender_name": user.name,
        "sender_id": user.user_id,
        "timestamp": msg.timestamp.isoformat(),
        "message_id": msg.message_id,
    }

    # Deliver to waiting recipients via message queues
    if room_id in message_queues:
        # Create a copy of items to avoid modification during iteration
        recipients = list(message_queues[room_id].items())
        for recipient_id, queue in recipients:
            if recipient_id != user.user_id:  # Don't send to self
                try:
                    # Put message in queue (non-blocking)
                    queue.put_nowait(message_data)
                    logger.info(
                        f"Delivered message to waiting queue for {recipient_id}"
                    )
                except asyncio.QueueFull:
                    logger.warning(f"Queue full for recipient {recipient_id}")
                except Exception as e:
                    # Handle case where queue was closed/cancelled
                    logger.warning(f"Failed to deliver to {recipient_id}: {e}")
                    # Clean up the dead queue
                    if room_id in message_queues and recipient_id in message_queues[room_id]:
                        del message_queues[room_id][recipient_id]
                        if not message_queues[room_id]:
                            del message_queues[room_id]

    # Still send notification for future notification support
    await send_notification(
        partner.connection_id,
        "message.received",
        {
            "room_id": room_id,
            "message": message,
            "sender": {"user_id": user.user_id, "display_name": user.name},
            "timestamp": msg.timestamp.isoformat(),
        },
    )

    return {
        "success": True,
        "message_id": msg.message_id,
        "timestamp": msg.timestamp.isoformat(),
    }


@mcp.tool()
async def leave_chat(room_id: str, client_id: str) -> Dict[str, Any]:
    """Leave the current chat room.

    Args:
        room_id: The ID of the chat room to leave
        client_id: Your client identifier (from enter_queue)

    Returns:
        Success status
    """
    # Use the provided client_id
    connection_id = client_id

    # Get user
    user = connections.get(connection_id)
    if not user:
        return {"success": False, "error": "User not found"}

    # Get room
    room = await room_manager.get_room(room_id)
    if not room:
        return {"success": False, "error": "Room not found"}

    # Verify user is in the room
    if not room.has_user(user.user_id):
        return {"success": False, "error": "You are not in this room"}

    # Get partner before closing room
    partner = room.get_partner(user.user_id)

    # Close the room
    await room_manager.close_room(room_id)

    # Log
    logger.info(f"User {user.name} left room {room_id}")

    # Notify partner if they exist
    if partner:
        # Send disconnection message to waiting queue
        if room_id in message_queues and partner.user_id in message_queues[room_id]:
            disconnect_msg = {
                "content": "[System] Your chat partner has left the conversation.",
                "sender_name": "System",
                "sender_id": "system",
                "timestamp": datetime.now().isoformat(),
                "message_id": str(uuid.uuid4()),
                "system": True,
                "disconnect": True,
            }
            try:
                message_queues[room_id][partner.user_id].put_nowait(disconnect_msg)
            except (asyncio.QueueFull, RuntimeError) as e:
                # Queue might be full or closed
                logger.debug(f"Could not send disconnect notification: {e}")

        # Also send regular notification
        await send_notification(
            partner.connection_id,
            "partner.disconnected",
            {"room_id": room_id, "reason": "left"},
        )

    return {"success": True, "message": "Successfully left the chat"}


@mcp.tool()
async def wait_for_message(room_id: str, client_id: str, timeout: int = 60) -> Dict[str, Any]:
    """Wait for a message in the chat room (long-polling).

    This tool blocks until a message is received or the timeout is reached.
    Use this after sending a message to wait for a response, or call it first
    to wait for an incoming message.
    
    Conversation flow:
    - If you sent the last message: wait_for_message to get response
    - If you're waiting for first contact: wait_for_message before sending
    - After receiving a message: send_message to respond, then wait_for_message again

    Args:
        room_id: The ID of the chat room to listen in
        client_id: Your client identifier (from enter_queue or join_room)
        timeout: Timeout in seconds (default: 60, max: 300)

    Returns:
        On message: {"message": "text", "sender": "name", "timestamp": "...", "message_id": "..."}
        On timeout: {"timeout": true, "message": "No message received"}
        On error: {"error": "error message"}
    """
    # Use the provided client_id
    connection_id = client_id

    # Validate timeout
    timeout = min(timeout, 300)  # Max 5 minutes
    timeout = max(timeout, 1)  # Min 1 second

    # Get user
    user = connections.get(connection_id)
    if not user:
        logger.error(f"User not found for client_id: {client_id}")
        logger.debug(f"Active connections: {list(connections.keys())}")
        return {"error": f"User not found. Invalid client_id: {client_id}"}

    # Get and validate room
    room = await room_manager.get_room(room_id)
    if not room:
        return {"error": "Room not found"}

    if not room.active:
        return {"error": "Chat has ended"}

    # Verify user is in the room
    if not room.has_user(user.user_id):
        return {"error": "You are not in this room"}

    # Create a message queue for this user if not exists
    if room_id not in message_queues:
        message_queues[room_id] = {}

    # Create queue with reasonable size limit
    message_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=100)
    message_queues[room_id][user.user_id] = message_queue

    logger.info(
        f"User {user.name} waiting for messages in room {room_id} (timeout: {timeout}s)"
    )

    try:
        # Wait for a message with timeout
        message_data = await asyncio.wait_for(
            message_queue.get(), timeout=float(timeout)
        )

        logger.info(
            f"Message received for {user.name}: {message_data.get('content', '')[:50]}..."
        )

        return {
            "message": message_data["content"],
            "sender": message_data["sender_name"],
            "timestamp": message_data["timestamp"],
            "message_id": message_data["message_id"],
        }

    except asyncio.TimeoutError:
        logger.info(f"Timeout waiting for message for {user.name}")
        return {"timeout": True, "message": "No message received within timeout period"}
    
    except asyncio.CancelledError:
        # Client cancelled the request - this is normal behavior
        logger.info(f"Wait cancelled for {user.name}")
        # Re-raise to let the framework handle it properly
        raise

    except Exception as e:
        logger.error(f"Error in wait_for_message: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

    finally:
        # Clean up queue registration
        if room_id in message_queues and user.user_id in message_queues[room_id]:
            del message_queues[room_id][user.user_id]
            # Clean up empty room entries
            if not message_queues[room_id]:
                del message_queues[room_id]
            logger.info(f"Cleaned up message queue for {user.name}")


async def send_notification(
    connection_id: str, method: str, params: Dict[str, Any]
) -> None:
    """Send a notification to a specific client connection.

    This is a placeholder for the actual notification mechanism.
    In a real implementation, this would use the SSE transport
    to push notifications to the client.
    """
    # Log notification for now
    logger.info(f"Notification to {connection_id}: {method} - {params}")

    # In actual implementation, this would use the transport layer
    # to send the notification to the specific connection


async def handle_disconnect(connection_id: str) -> None:
    """Handle user disconnection."""
    user = connections.get(connection_id)
    if not user:
        return

    # Remove from queue if waiting
    await queue_manager.remove_user(user.user_id)

    # Handle room cleanup if in a room
    room = await room_manager.remove_user(user.user_id)
    if room and room.active:
        # Notify partner
        partner = room.get_partner(user.user_id)
        if partner:
            await send_notification(
                partner.connection_id,
                "partner.disconnected",
                {"room_id": room.room_id, "reason": "disconnected"},
            )

    # Remove from connections
    connections.pop(connection_id, None)
    logger.info(f"User {user.name} disconnected")


def main() -> None:
    """Main entry point for the server."""
    import uvicorn

    uvicorn.run("mcp_chat.server:mcp", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
