/** src/api/content.js — Language content API calls */
import client from './client.js';

export const getPairs = () => client.get('/content/pairs');
export const getMeta = (pairId) => client.get(`/content/${pairId}/meta`);
export const getActivity = (pairId, file) =>
  client.get(`/content/${pairId}/activity`, { params: { file } });
