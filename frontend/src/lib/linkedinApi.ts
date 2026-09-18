import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // Adjust base URL if needed based on Vite proxy
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getLinkedInStatus = async () => {
  const response = await api.get('/linkedin/status');
  return response.data;
};

export const connectLinkedIn = async (state: string) => {
  const response = await api.get(`/linkedin/connect?state=${state}`);
  return response.data;
};

export const connectLinkedInManual = async (profileUrl: string) => {
  const response = await api.post('/linkedin/connect_manual', { profile_url: profileUrl });
  return response.data;
};

export const disconnectLinkedIn = async () => {
  const response = await api.post('/linkedin/disconnect');
  return response.data;
};

export const generateLinkedInPost = async (data: any) => {
  const response = await api.post('/linkedin/generate', data);
  return response.data;
};

export const approveLinkedInPost = async (postId: number, data: any) => {
  const response = await api.post(`/linkedin/posts/${postId}/approve`, data);
  return response.data;
};

export const publishLinkedInPost = async (postId: number) => {
  const response = await api.post(`/linkedin/posts/${postId}/publish`);
  return response.data;
};

export const refreshLinkedInImage = async (postId: number) => {
  const response = await api.post(`/linkedin/posts/${postId}/refresh_image`);
  return response.data;
};
