import { useEffect, useState } from 'react';
import { Card, Button, Input, List, Typography, Modal, Form, Empty, Tag, message } from 'antd';
import { PlusOutlined, DeleteOutlined, BookOutlined } from '@ant-design/icons';
import { useBookStore } from '../store/bookStore';
import { useAuthStore } from '../store/authStore';

const { Title, Text } = Typography;
const { TextArea } = Input;

export default function Books() {
  const { books, loading, fetchBooks, addBook, deleteBook } = useBookStore();
  const { user } = useAuthStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchBooks();
  }, []);

  const handleAdd = async (values) => {
    try {
      await addBook(values);
      message.success('Book created successfully');
      setIsModalOpen(false);
      form.resetFields();
    } catch (error) {
      console.error(error);
    }
  };

  const handleDelete = (id) => {
    Modal.confirm({
      title: 'Delete Book',
      content: 'Are you sure you want to delete this book?',
      okText: 'Delete',
      okType: 'danger',
      onOk: async () => {
        try {
          await deleteBook(id);
          message.success('Book deleted');
        } catch (error) {
          console.error(error);
        }
      },
    });
  };

  return (
    <>
      <div className="flex justify-between items-center mb-6">
        <Title level={2} className="m-0">My Library</Title>
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          size="large"
          onClick={() => setIsModalOpen(true)}
        >
          Add Book
        </Button>
      </div>

      <List
        grid={{ gutter: 24, xs: 1, sm: 2, md: 2, lg: 3, xl: 3, xxl: 4 }}
        dataSource={books}
        loading={loading}
        locale={{ emptyText: <Empty description="No books found. Add your first book!" /> }}
        renderItem={(book) => (
          <List.Item>
            <Card
              hoverable
              title={<div className="flex items-center gap-2"><BookOutlined /> {book.title}</div>}
              extra={
                book.owner_id === user?.id && (
                  <Button 
                    type="text" 
                    danger 
                    icon={<DeleteOutlined />} 
                    onClick={() => handleDelete(book.id)} 
                  />
                )
              }
              className="h-full shadow-sm hover:shadow-md transition-shadow rounded-lg"
            >
              <div className="mb-4">
                <Text type="secondary" className="block mb-1">Author</Text>
                <Text strong className="text-lg">{book.author}</Text>
              </div>
              
              {book.isbn && (
                <div className="mb-4">
                  <Tag color="blue">{book.isbn}</Tag>
                </div>
              )}
              
              {book.description && (
                <div>
                  <Text type="secondary" className="block mb-1">Description</Text>
                  <Text className="text-gray-600 line-clamp-3">{book.description}</Text>
                </div>
              )}
            </Card>
          </List.Item>
        )}
      />

      <Modal
        title="Add New Book"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleAdd}
          className="mt-4"
        >
          <Form.Item
            name="title"
            label="Title"
            rules={[{ required: true, message: 'Please enter book title' }]}
          >
            <Input placeholder="e.g. The Great Gatsby" />
          </Form.Item>

          <Form.Item
            name="author"
            label="Author"
            rules={[{ required: true, message: 'Please enter author name' }]}
          >
            <Input placeholder="e.g. F. Scott Fitzgerald" />
          </Form.Item>

          <Form.Item name="isbn" label="ISBN">
            <Input placeholder="Optional" />
          </Form.Item>

          <Form.Item name="description" label="Description">
            <TextArea rows={4} placeholder="Optional" />
          </Form.Item>

          <div className="flex justify-end gap-2 mt-6">
            <Button onClick={() => setIsModalOpen(false)}>Cancel</Button>
            <Button type="primary" htmlType="submit">Add Book</Button>
          </div>
        </Form>
      </Modal>
    </>
  );
}
