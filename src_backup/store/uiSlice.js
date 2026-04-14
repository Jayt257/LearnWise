/**
 * src/store/uiSlice.js
 * Redux slice for global UI state (notifications, modals).
 */
import { createSlice } from '@reduxjs/toolkit';

const uiSlice = createSlice({
  name: 'ui',
  initialState: { toast: null },
  reducers: {
    showToast(state, action) {
      state.toast = { message: action.payload.message, type: action.payload.type || 'info', id: Date.now() };
    },
    clearToast(state) { state.toast = null; },
  },
});

export const { showToast, clearToast } = uiSlice.actions;
export default uiSlice.reducer;
