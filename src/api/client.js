/**
 * src/api/client.js
 * Axios client configured with base URL + JWT auth interceptor.
 *
 * Bug Fix #4: The 401 interceptor now checks if the current user is an admin
 * before redirecting — admin sessions redirect to /admin/login, not /login.
 * Also reads from lw_token which is shared between user and admin sessions.
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const API_URL = API_BASE;

const client = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT to every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('lw_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On 401: clear token and redirect to the correct login page
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const userRaw = localStorage.getItem('lw_user');
      const isAdmin = userRaw ? JSON.parse(userRaw)?.role === 'admin' : false;

      localStorage.removeItem('lw_token');
      localStorage.removeItem('lw_user');

      // Redirect admin to admin login, regular users to /login
      if (isAdmin || window.location.pathname.startsWith('/admin')) {
        window.location.href = '/admin/login';
      } else {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default client;
