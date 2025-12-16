import api from '../lib/api';

export const authService = {
  async login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    // Using x-www-form-urlencoded as required by OAuth2PasswordRequestForm in FastAPI
    const { data } = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    
    if (data.access_token) {
      localStorage.setItem('token', data.access_token);
    }
    return data;
  },

  async register(email, password, full_name) {
    const { data } = await api.post('/auth/register', { 
      email, 
      password, 
      full_name 
    });
    return data;
  },

  async getMe() {
    const { data } = await api.get('/auth/me');
    return data;
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
};
