import { create } from 'zustand';
import { authService } from '../services/authService';

export const useAuthStore = create((set) => ({
  user: (() => {
    try {
      return JSON.parse(localStorage.getItem('user'));
    } catch {
      return null;
    }
  })(),
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  loading: false,
  error: null,
  
  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const data = await authService.login(email, password);
      // Fetch full user details after login if not provided in login response
      const user = data.user || await authService.getMe();
      
      localStorage.setItem('user', JSON.stringify(user));
      set({ user, token: data.access_token, isAuthenticated: true, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },
  
  register: async (email, password, full_name) => {
    set({ loading: true, error: null });
    try {
      await authService.register(email, password, full_name);
      set({ loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },
  
  logout: () => {
    authService.logout();
    set({ user: null, token: null, isAuthenticated: false });
  },
  
  fetchUser: async () => {
    try {
      const user = await authService.getMe();
      localStorage.setItem('user', JSON.stringify(user));
      set({ user });
    } catch (error) {
      // Token might be invalid
      authService.logout();
      set({ user: null, token: null, isAuthenticated: false });
    }
  },
}));
