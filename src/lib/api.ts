import axios from 'axios';
import type { ApiResponse, LoginCredentials, RegisterData, User} from '../types/api';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8080',
});

// Add request interceptor to include auth token in all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const auth = {
  login: async (email: string, password: string) => {
    const response = await api.get<ApiResponse<string>>('/login/signin', {
      params: { email, password }
    });
    return response.data;
  },
  register: async (data: RegisterData) => {
    const response = await api.post<ApiResponse<boolean>>('/login/signup', data);
    return response.data;
  },
};

export const users = {
  getProfile: async () => {
    const response = await api.get<User>('/user/me');
    return response.data;
  }
};

export default api;
