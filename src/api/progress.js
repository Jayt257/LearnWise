/**
 * src/api/progress.js — Progress tracking API (schema v2: block-based)
 */
import client from './client.js';

export const getAllProgress = () => client.get('/progress');
export const getPairProgress = (pairId) => client.get(`/progress/${pairId}`);
export const startPair = (pairId) => client.post(`/progress/${pairId}/start`);
export const getCompletions = (pairId) => client.get(`/progress/${pairId}/completions`);

/**
 * Record an activity completion.
 * @param {string} pairId
 * @param {object} payload - { activity_seq_id, activity_json_id, activity_type, lang_pair_id,
 *                            month_number, block_number, score_earned, max_score, passed,
 *                            ai_feedback?, ai_suggestion? }
 */
export const completeActivity = (pairId, payload) => client.post(`/progress/${pairId}/complete`, payload);

export const validateActivity = (payload) => client.post('/validate', payload);

// NOTE: getLeaderboard was removed from here — it was pointing to a
// non-existent /social/leaderboard route. Use getLeaderboard from users.js
// which calls the correct /leaderboard/{pairId} endpoint.
