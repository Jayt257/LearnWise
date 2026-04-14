/**
 * src/api/content.js — Content API calls (block-based schema v4)
 */
import client from './client.js';

export const getPairs = () => client.get('/content/pairs');
export const getMeta = (pairId) => client.get(`/content/${pairId}/meta`);
export const getActivity = (pairId, file) => client.get(`/content/${pairId}/activity`, { params: { file } });
export const checkActivity = (pairId, file) => client.get(`/content/${pairId}/check`, { params: { file } });
