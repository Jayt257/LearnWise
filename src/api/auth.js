/** src/api/auth.js — Authentication API calls */
import client from './client.js';

export const register = (data) => client.post('/auth/register', data);
export const login = (data) => client.post('/auth/login', data);
export const adminLogin = (data) => client.post('/auth/admin/login', data);
export const getMe = () => client.get('/auth/me');
