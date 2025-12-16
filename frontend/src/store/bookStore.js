import { create } from 'zustand';
import { bookService } from '../services/bookService';

export const useBookStore = create((set) => ({
  books: [],
  loading: false,
  error: null,
  
  fetchBooks: async () => {
    set({ loading: true, error: null });
    try {
      const books = await bookService.getBooks();
      set({ books, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
  
  addBook: async (book) => {
    set({ loading: true });
    try {
      const newBook = await bookService.createBook(book);
      set((state) => ({ books: [...state.books, newBook], loading: false }));
      return newBook;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },
  
  updateBook: async (id, book) => {
    set({ loading: true });
    try {
      const updated = await bookService.updateBook(id, book);
      set((state) => ({
        books: state.books.map((b) => (b.id === id ? updated : b)),
        loading: false
      }));
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },
  
  deleteBook: async (id) => {
    set({ loading: true });
    try {
      await bookService.deleteBook(id);
      set((state) => ({ 
        books: state.books.filter((b) => b.id !== id),
        loading: false 
      }));
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },
}));
