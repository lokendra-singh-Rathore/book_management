import api from '../lib/api';

export const bookService = {
  async getBooks() {
    const { data } = await api.get('/books');
    return data;
  },

  async getBook(id) {
    const { data } = await api.get(`/books/${id}`);
    return data;
  },

  async createBook(book) {
    const { data } = await api.post('/books', book);
    return data;
  },

  async updateBook(id, book) {
    const { data } = await api.put(`/books/${id}`, book);
    return data;
  },

  async deleteBook(id) {
    await api.delete(`/books/${id}`);
  },
};
