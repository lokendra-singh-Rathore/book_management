"""
WebSocket connection manager for real-time chat.

Manages active WebSocket connections, room subscriptions, and message broadcasting.
"""
import json
import logging
from typing import Dict, Set, Optional
from fastapi import WebSocket

from app.chat.redis_client import redis_client


logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time chat.
    
    Features:
    - Connection pooling per user
    - Room subscription management
    - Message broadcasting to rooms
    - Presence tracking
    - Graceful disconnect handling
    """
    
    def __init__(self):
        # user_id -> WebSocket connection
        self.active_connections: Dict[int, WebSocket] = {}
        
        # room_id -> Set[user_id] (who's subscribed)
        self.room_subscribers: Dict[int, Set[int]] = {}
        
        # user_id -> Set[room_id] (what rooms user is in)
        self.user_rooms: Dict[int, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Accept and register WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance
            user_id: User ID connecting
        """
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        # Update presence in Redis
        await redis_client.set_user_online(user_id)
        
        logger.info(f"👤 User {user_id} connected via WebSocket")
        
        # Broadcast presence to all rooms user is in
        if user_id in self.user_rooms:
            for room_id in self.user_rooms[user_id]:
                await self.broadcast_to_room(
                    room_id,
                    {
                        "type": "user_presence",
                        "user_id": user_id,
                        "status": "online"
                    },
                    exclude_user_id=user_id
                )
    
    async def disconnect(self, user_id: int):
        """
        Remove user connection and cleanup.
        
        Args:
            user_id: User ID disconnecting
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Update presence
        await redis_client.set_user_offline(user_id)
        
        # Cleanup room subscriptions
        if user_id in self.user_rooms:
            for room_id in self.user_rooms[user_id]:
                if room_id in self.room_subscribers:
                    self.room_subscribers[room_id].discard(user_id)
                
                # Broadcast offline status
                await self.broadcast_to_room(
                    room_id,
                    {
                        "type": "user_presence",
                        "user_id": user_id,
                        "status": "offline"
                    }
                )
            
            del self.user_rooms[user_id]
        
        logger.info(f"👋 User {user_id} disconnected from WebSocket")
    
    async def subscribe_to_room(self, user_id: int, room_id: int):
        """
        Subscribe user to room for real-time updates.
        
        Args:
            user_id: User ID
            room_id: Room ID to subscribe to
        """
        # Add to room subscribers
        if room_id not in self.room_subscribers:
            self.room_subscribers[room_id] = set()
        self.room_subscribers[room_id].add(user_id)
        
        # Track user's rooms
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(room_id)
        
        logger.debug(f"📡 User {user_id} subscribed to room {room_id}")
    
    async def unsubscribe_from_room(self, user_id: int, room_id: int):
        """Unsubscribe user from room."""
        if room_id in self.room_subscribers:
            self.room_subscribers[room_id].discard(user_id)
        
        if user_id in self.user_rooms:
            self.user_rooms[user_id].discard(room_id)
        
        logger.debug(f"📴 User {user_id} unsubscribed from room {room_id}")
    
    async def broadcast_to_room(
        self,
        room_id: int,
        message: dict,
        exclude_user_id: Optional[int] = None
    ):
        """
        Broadcast message to all users in a room.
        
        Args:
            room_id: Room ID to broadcast to
            message: Message dictionary to send
            exclude_user_id: Optional user ID to exclude from broadcast
        """
        if room_id not in self.room_subscribers:
            return
        
        message_json = json.dumps(message)
        disconnected_users = []
        
        for user_id in self.room_subscribers[room_id]:
            # Skip excluded user (e.g., sender)
            if exclude_user_id and user_id == exclude_user_id:
                continue
            
            # Send to connected users only
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected_users.append(user_id)
        
        # Cleanup disconnected users
        for user_id in disconnected_users:
            await self.disconnect(user_id)
    
    async def send_to_user(self, user_id: int, message: dict):
        """
        Send message to specific user.
        
        Args:
            user_id: User ID to send to
            message: Message dictionary
        """
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                await self.disconnect(user_id)
    
    async def broadcast_typing(
        self,
        room_id: int,
        user_id: int,
        username: str,
        is_typing: bool
    ):
        """
        Broadcast typing indicator to room.
        
        Args:
            room_id: Room ID
            user_id: User who is typing
            username: Username for display
            is_typing: Whether user is typing or stopped
        """
        # Update Redis typing indicator
        await redis_client.set_typing(room_id, user_id, is_typing)
        
        # Broadcast to room
        await self.broadcast_to_room(
            room_id,
            {
                "type": "user_typing",
                "room_id": room_id,
                "user_id": user_id,
                "username": username,
                "is_typing": is_typing
            },
            exclude_user_id=user_id
        )
    
    def get_online_users_in_room(self, room_id: int) -> Set[int]:
        """Get set of online user IDs in a room."""
        if room_id not in self.room_subscribers:
            return set()
        
        # Filter for actually connected users
        return {
            user_id for user_id in self.room_subscribers[room_id]
            if user_id in self.active_connections
        }
    
    def is_user_connected(self, user_id: int) -> bool:
        """Check if user has active WebSocket connection."""
        return user_id in self.active_connections


# Global connection manager instance
connection_manager = ConnectionManager()
