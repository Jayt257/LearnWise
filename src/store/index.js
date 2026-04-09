/**
 * src/store/index.js
 * Redux store configuration with all slices combined.
 */
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice.js';
import progressReducer from './progressSlice.js';
import uiReducer from './uiSlice.js';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    progress: progressReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({ serializableCheck: false }),
});
