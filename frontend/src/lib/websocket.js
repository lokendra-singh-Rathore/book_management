class WebSocketClient {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect(token) {
    const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/chat/ws';
    // Close existing connection if any
    if (this.ws) {
      this.ws.close();
    }

    this.ws = new WebSocket(`${WS_URL}?token=${token}`);

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.listeners.forEach((callback) => callback(data));
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
      }
    };

    this.ws.onclose = () => {
      console.log('❌ WebSocket disconnected');
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        const timeout = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 5000);
        setTimeout(() => {
          console.log(`Attempting reconnect (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})...`);
          this.reconnectAttempts++;
          this.connect(token);
        }, timeout);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not open. Cannot send message.');
    }
  }

  on(callback) {
    const id = Math.random().toString(36).substr(2, 9);
    this.listeners.set(id, callback);
    return () => this.listeners.delete(id);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners.clear();
  }
}

export const wsClient = new WebSocketClient();
