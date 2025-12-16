import { Layout, Menu, Button, Avatar, Dropdown, Space, Typography } from 'antd';
import { BookOutlined, MessageOutlined, LogoutOutlined, UserOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const { Header, Content } = Layout;
const { Text } = Typography;

export default function AppLayout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    {
      key: '/books',
      icon: <BookOutlined />,
      label: 'Books',
      onClick: () => navigate('/books'),
    },
    {
      key: '/chat',
      icon: <MessageOutlined />,
      label: 'Chat',
      onClick: () => navigate('/chat'),
    },
  ];

  const userMenu = {
    items: [
      {
        key: 'logout',
        icon: <LogoutOutlined />,
        label: 'Logout',
        onClick: handleLogout,
      },
    ],
  };

  return (
    <Layout className="min-h-screen">
      <Header className="flex items-center justify-between px-6 bg-white shadow-sm sticky top-0 z-50">
        <div className="flex items-center">
          <div className="text-xl font-bold text-blue-600 mr-8 flex items-center">
            <BookOutlined className="mr-2" />
            BookChat
          </div>
          <Menu
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            className="border-b-0 min-w-[200px]"
          />
        </div>

        <Dropdown menu={userMenu}>
          <Space className="cursor-pointer hover:bg-gray-50 px-3 py-2 rounded-md transition-colors">
            <Avatar icon={<UserOutlined />} className="bg-blue-500" />
            <div className="hidden sm:block">
              <Text strong className="block text-sm leading-tight">
                {user?.full_name || 'User'}
              </Text>
              <Text type="secondary" className="text-xs">
                {user?.email}
              </Text>
            </div>
          </Space>
        </Dropdown>
      </Header>

      <Content className="p-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </Content>
    </Layout>
  );
}
