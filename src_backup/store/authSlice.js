/**
 * src/store/authSlice.js
 * Redux slice for authentication state.
 * Persists token + user to localStorage for session persistence.
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import * as authApi from '../api/auth.js';

const loadFromStorage = () => {
  try {
    const token = localStorage.getItem('lw_token');
    const user = JSON.parse(localStorage.getItem('lw_user') || 'null');
    return { token, user, isAuthenticated: !!(token && user) };
  } catch { return { token: null, user: null, isAuthenticated: false }; }
};

export const loginUser = createAsyncThunk('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    const { data } = await authApi.login(credentials);
    return data;
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Login failed');
  }
});

export const adminLoginUser = createAsyncThunk('auth/adminLogin', async (credentials, { rejectWithValue }) => {
  try {
    const { data } = await authApi.adminLogin(credentials);
    return data;
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Admin login failed');
  }
});

export const registerUser = createAsyncThunk('auth/register', async (data, { rejectWithValue }) => {
  try {
    const res = await authApi.register(data);
    return res.data;
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Registration failed');
  }
});

const authSlice = createSlice({
  name: 'auth',
  initialState: { ...loadFromStorage(), loading: false, error: null },
  reducers: {
    logout(state) {
      state.token = null;
      state.user = null;
      state.isAuthenticated = false;
      localStorage.removeItem('lw_token');
      localStorage.removeItem('lw_user');
    },
    updateUser(state, action) {
      state.user = { ...state.user, ...action.payload };
      localStorage.setItem('lw_user', JSON.stringify(state.user));
    },
    clearError(state) { state.error = null; },
  },
  extraReducers: (builder) => {
    const handlePending = (state) => { state.loading = true; state.error = null; };
    const handleFulfilled = (state, action) => {
      state.loading = false;
      state.token = action.payload.access_token;
      state.user = action.payload.user;
      state.isAuthenticated = true;
      localStorage.setItem('lw_token', action.payload.access_token);
      localStorage.setItem('lw_user', JSON.stringify(action.payload.user));
    };
    const handleRejected = (state, action) => {
      state.loading = false;
      state.error = action.payload;
    };
    builder
      .addCase(loginUser.pending, handlePending)
      .addCase(loginUser.fulfilled, handleFulfilled)
      .addCase(loginUser.rejected, handleRejected)
      .addCase(registerUser.pending, handlePending)
      .addCase(registerUser.fulfilled, handleFulfilled)
      .addCase(registerUser.rejected, handleRejected)
      .addCase(adminLoginUser.pending, handlePending)
      .addCase(adminLoginUser.fulfilled, handleFulfilled)
      .addCase(adminLoginUser.rejected, handleRejected);
  },
});

export const { logout, updateUser, clearError } = authSlice.actions;
export default authSlice.reducer;
