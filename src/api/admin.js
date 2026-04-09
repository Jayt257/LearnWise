/** src/api/admin.js — Admin-only API calls (all require admin JWT) */
import client from './client.js';

// ── Stats & Analytics ──────────────────────────────────────────
export const getAdminStats = () => client.get('/admin/stats');
export const getAdminAnalytics = () => client.get('/admin/analytics');
export const getActivityTypes = () => client.get('/admin/activity-types');

// ── Users ──────────────────────────────────────────────────────
export const listAdminUsers = (params = {}) => client.get('/admin/users', { params });
export const updateUserRole = (userId, role) => client.put(`/admin/users/${userId}/role`, { role });
export const deactivateUser = (userId) => client.delete(`/admin/users/${userId}`);
export const activateUser = (userId) => client.put(`/admin/users/${userId}/activate`);

// ── Languages ──────────────────────────────────────────────────
export const listLanguages = () => client.get('/admin/languages');
export const createLanguage = (data) => client.post('/admin/languages', data);
export const deleteLanguage = (pairId) => client.delete(`/admin/languages/${pairId}`);

// ── Content (activity files) ───────────────────────────────────
export const listContent = (pairId) => client.get(`/admin/content/${pairId}`);
export const getContentFile = (pairId, file) =>
  client.get(`/admin/content/${pairId}/file`, { params: { file } });
export const updateContent = (pairId, filePath, content) =>
  client.put(`/admin/content/${pairId}`, { file_path: filePath, content });
export const createActivity = (pairId, filePath, content) =>
  client.post(`/admin/content/${pairId}/activity`, { file_path: filePath, content });
export const deleteActivity = (pairId, file) =>
  client.delete(`/admin/content/${pairId}/activity`, { params: { file } });
export const updateMeta = (pairId, content) =>
  client.put(`/admin/content/${pairId}/meta`, { file_path: 'meta.json', content });
