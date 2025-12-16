import { create } from 'zustand';
import { chatService } from '../services/chatService';
import { wsClient } from '../lib/websocket';

export const useChatStore = create((set, get) => ({
  rooms: [],
  currentRoom: null,
  messages: [],
  connected: false,
  
  connectWebSocket: (token) => {
    wsClient.connect(token);
    
    wsClient.on((data) => {
      // Handle different message types
      switch (data.type) {
        case 'new_message':
          // Only add message if it belongs to current room
          const { currentRoom } = get();
          if (currentRoom && data.message.room_id === currentRoom.id) {
            set((state) => ({ messages: [...state.messages, data.message] }));
          }
          // Update unread count or move room to top
          set((state) => {
            const updatedRooms = state.rooms.map(room => {
               if (room.id === data.message.room_id) {
                 // If not current room, increment unread
                 if (!currentRoom || currentRoom.id !== room.id) {
                   return { ...room, unread_count: (room.unread_count || 0) + 1 };
                 }
               }
               return room;
            });
            return { rooms: updatedRooms };
          });
          break;
          
        case 'user_typing':
          // Handle typing indicators (future)
          break;
          
        case 'presence_update':
          // Handle online status (future)
          break;
      }
    });
    
    set({ connected: true });
  },
  
  disconnectWebSocket: () => {
    wsClient.disconnect();
    set({ connected: false });
  },
  
  fetchRooms: async () => {
    try {
      const rooms = await chatService.getRooms();
      set({ rooms });
    } catch (error) {
      console.error('Failed to fetch rooms:', error);
    }
  },
  
  selectRoom: async (room) => {
    set({ currentRoom: room, messages: [] });
    try {
      const messages = await chatService.getMessages(room.id);
      set({ messages });
      
      // Notify backend we joined room (optional depending on backend logic)
      wsClient.send({ type: 'join_room', room_id: room.id });
      
      // Reset unread count locally
      set((state) => ({
        rooms: state.rooms.map(r => 
          r.id === room.id ? { ...r, unread_count: 0 } : r
        )
      }));
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  },
  
  sendMessage: (content) => {
    const { currentRoom } = get();
    if (!currentRoom) return;
    
    const messagePayload = {
      type: 'send_message',
      room_id: currentRoom.id,
      content,
    };
    
    wsClient.send(messagePayload);
  },
}));
