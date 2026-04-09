/** src/api/progress.js — Progress tracking API calls */
import client from './client.js';

export const getAllProgress = () => client.get('/progress');
export const getPairProgress = (pairId) => client.get(`/progress/${pairId}`);
export const startPair = (pairId) => client.post(`/progress/${pairId}/start`);
export const completeActivity = (pairId, data) => client.post(`/progress/${pairId}/complete`, data);
export const getCompletions = (pairId) => client.get(`/progress/${pairId}/completions`);

export const validateActivity = (data) => client.post('/validate', data);

export const transcribeAudio = (audioBlob, filename = 'audio.webm') => {
  const formData = new FormData();
  formData.append('audio', audioBlob, filename);
  return client.post('/speech/transcribe', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
