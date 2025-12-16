import api from '../lib/api';

export const chatService = {
  async getRooms() {
    const { data } = await api.get('/chat/rooms');
    return data;
  },

  async createRoom(room) {
    const { data } = await api.post('/chat/rooms', room);
    return data;
  },

  async getMessages(roomId, limit = 50) {
    const { data } = await api.get(`/chat/messages/room/${roomId}?limit=${limit}`);
    return data.messages || []; // Ensure array is returned
  },

  async sendMessage(message) {
    const { data } = await api.post('/chat/messages', message);
    return data;
  },
};
