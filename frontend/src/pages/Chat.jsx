import { useEffect, useState, useRef } from 'react';
import { Layout, Menu, Input, Avatar, Button, Typography, Badge, Empty, Space } from 'antd';
import { SendOutlined, UserOutlined, TeamOutlined, NumberOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { format } from 'date-fns';
import { useChatStore } from '../store/chatStore';
import { useAuthStore } from '../store/authStore';

const { Sider, Content } = Layout;
const { Text, Title } = Typography;

export default function Chat() {
  const { rooms, currentRoom, messages, fetchRooms, selectRoom, sendMessage, connectWebSocket } = useChatStore();
  const { token, user } = useAuthStore();
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  useEffect(() => {
    if (token) {
      fetchRooms();
      connectWebSocket(token);
      setConnectionStatus('connected');
    }
  }, [token]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (inputMessage.trim() && currentRoom) {
      sendMessage(inputMessage);
      setInputMessage('');
    }
  };

  const getRoomIcon = (type) => {
    switch (type) {
      case 'group': return <TeamOutlined />;
      case 'channel': return <NumberOutlined />;
      default: return <UserOutlined />;
    }
  };

  return (
    <Layout className="h-[calc(100vh-140px)] bg-white rounded-lg overflow-hidden border border-gray-200">
      <Sider width={300} theme="light" className="border-r border-gray-100">
        <div className="p-4 border-b border-gray-100">
          <Input.Search placeholder="Search conversations" allowClear />
        </div>
        <div className="overflow-y-auto h-[calc(100%-65px)]">
          <Menu
            mode="inline"
            selectedKeys={[currentRoom?.id?.toString()]}
            items={rooms.map(room => ({
              key: room.id,
              icon: getRoomIcon(room.room_type),
              label: (
                <div className="flex justify-between items-center w-full">
                  <span className="truncate">{room.name}</span>
                  {room.unread_count > 0 && (
                    <Badge count={room.unread_count} size="small" className="ml-2" />
                  )}
                </div>
              ),
              onClick: () => selectRoom(room),
              className: "h-12 flex items-center"
            }))}
            className="border-0"
          />
        </div>
      </Sider>

      <Content className="flex flex-col bg-gray-50 h-full">
        {currentRoom ? (
          <>
            <div className="h-16 px-6 bg-white border-b border-gray-100 flex items-center justify-between shadow-sm">
              <div className="flex items-center gap-3">
                <Avatar 
                  icon={getRoomIcon(currentRoom.room_type)} 
                  className="bg-blue-100 text-blue-600"
                />
                <div>
                  <Title level={5} className="m-0 leading-tight">{currentRoom.name}</Title>
                  <Text type="secondary" className="text-xs">
                    {currentRoom.room_type === 'direct' ? 'Direct Message' : `${currentRoom.room_type} • Online`}
                  </Text>
                </div>
              </div>
              <Button type="text" icon={<InfoCircleOutlined />} />
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 ? (
                <div className="h-full flex items-center justify-center">
                  <Empty description="No messages yet. Start the conversation!" />
                </div>
              ) : (
                messages.map((msg) => {
                  const isMine = msg.sender_id === user?.id;
                  return (
                    <div
                      key={msg.id}
                      className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[70%] ${isMine ? 'items-end' : 'items-start'} flex flex-col`}>
                        {!isMine && <Text type="secondary" className="text-xs ml-1 mb-1">{msg.username || 'User'}</Text>}
                        <div
                          className={`px-4 py-2 rounded-2xl shadow-sm text-sm break-words ${
                            isMine 
                              ? 'bg-blue-600 text-white rounded-tr-sm' 
                              : 'bg-white text-gray-800 rounded-tl-sm'
                          }`}
                        >
                          {msg.content}
                        </div>
                        <Text type="secondary" className="text-[10px] mt-1 px-1">
                          {format(new Date(msg.created_at), 'HH:mm')}
                        </Text>
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="p-4 bg-white border-t border-gray-100">
              <Space.Compact style={{ width: '100%' }}>
                <Input
                  size="large"
                  placeholder="Type a message..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onPressEnter={handleSend}
                />
                <Button 
                  size="large" 
                  type="primary" 
                  icon={<SendOutlined />} 
                  onClick={handleSend}
                >
                  Send
                </Button>
              </Space.Compact>
            </div>
          </>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-gray-400">
            <MessageOutlined style={{ fontSize: 64, marginBottom: 16, opacity: 0.2 }} />
            <Title level={4} type="secondary">Select a chat to start messaging</Title>
          </div>
        )}
      </Content>
    </Layout>
  );
}
