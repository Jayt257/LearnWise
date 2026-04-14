/** src/api/users.js — User profile and social API calls */
import client from './client.js';

export const getMyProfile = () => client.get('/users/me');
export const updateProfile = (data) => client.put('/users/me', data);
export const searchUsers = (q, limit = 20) => client.get('/users/search', { params: { q, limit } });
export const getUserProfile = (userId) => client.get(`/users/${userId}`);
export const getUserProgress = (userId) => client.get(`/users/${userId}/progress`);

// Friends
export const getFriends = () => client.get('/friends');
export const getFriendRequests = () => client.get('/friends/requests');
export const sendFriendRequest = (userId) => client.post(`/friends/request/${userId}`);
export const acceptFriendRequest = (reqId) => client.put(`/friends/request/${reqId}/accept`);
export const declineFriendRequest = (reqId) => client.put(`/friends/request/${reqId}/decline`);
export const removeFriend = (userId) => client.delete(`/friends/${userId}`);

// Leaderboard
export const getLeaderboard = (pairId) => client.get(`/leaderboard/${pairId}`);
export const getFriendsLeaderboard = (pairId) => client.get(`/leaderboard/${pairId}/friends`);
