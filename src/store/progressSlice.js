/**
 * src/store/progressSlice.js
 * Redux slice for user's language learning progress across all pairs.
 * Schema v2: current_week → current_block, activity_id → activity_seq_id
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import * as progressApi from '../api/progress.js';
import * as contentApi from '../api/content.js';

export const fetchAllProgress = createAsyncThunk('progress/fetchAll', async (_, { rejectWithValue }) => {
  try {
    const { data } = await progressApi.getAllProgress();
    return data;
  } catch (err) { return rejectWithValue(err.response?.data?.detail); }
});

export const fetchPairProgress = createAsyncThunk('progress/fetchPair', async (pairId, { rejectWithValue }) => {
  try {
    const { data } = await progressApi.getPairProgress(pairId);
    return data;
  } catch (err) { return rejectWithValue(err.response?.data?.detail); }
});

export const startLanguagePair = createAsyncThunk('progress/start', async (pairId, { rejectWithValue }) => {
  try {
    const { data } = await progressApi.startPair(pairId);
    return data;
  } catch (err) { return rejectWithValue(err.response?.data?.detail); }
});

export const fetchPairs = createAsyncThunk('progress/fetchPairs', async (_, { rejectWithValue }) => {
  try {
    const { data } = await contentApi.getPairs();
    return data;
  } catch (err) { return rejectWithValue(err.response?.data?.detail); }
});

const progressSlice = createSlice({
  name: 'progress',
  initialState: {
    allProgress: [],   // array of UserLanguageProgress (block-based)
    pairs: [],         // available language pairs from language_pairs.json
    currentPairId: localStorage.getItem('lw_pair') || null,
    loading: false,
    error: null,
  },
  reducers: {
    setCurrentPair(state, action) {
      state.currentPairId = action.payload;
      localStorage.setItem('lw_pair', action.payload);
    },
    updateProgressXP(state, action) {
      const { pairId, xpDelta } = action.payload;
      const prog = state.allProgress.find(p => p.lang_pair_id === pairId);
      if (prog) prog.total_xp += xpDelta;
    },
    advanceProgress(state, action) {
      // Called after successful activity completion
      const { pairId, newProgress } = action.payload;
      const idx = state.allProgress.findIndex(p => p.lang_pair_id === pairId);
      if (idx >= 0 && newProgress) {
        state.allProgress[idx] = { ...state.allProgress[idx], ...newProgress };
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAllProgress.pending, (state) => { state.loading = true; })
      .addCase(fetchAllProgress.fulfilled, (state, action) => {
        state.allProgress = action.payload;
        state.loading = false;
        // Auto-select first pair if none selected
        if (!state.currentPairId && action.payload.length > 0) {
          state.currentPairId = action.payload[0].lang_pair_id;
          localStorage.setItem('lw_pair', action.payload[0].lang_pair_id);
        }
      })
      .addCase(fetchAllProgress.rejected, (state) => { state.loading = false; })
      .addCase(fetchPairs.fulfilled, (state, action) => { state.pairs = action.payload; })
      .addCase(startLanguagePair.fulfilled, (state, action) => {
        const existing = state.allProgress.find(p => p.lang_pair_id === action.payload.lang_pair_id);
        if (!existing) {
          state.allProgress.push(action.payload);
        }
        state.currentPairId = action.payload.lang_pair_id;
        localStorage.setItem('lw_pair', action.payload.lang_pair_id);
      })
      .addCase(fetchPairProgress.fulfilled, (state, action) => {
        const idx = state.allProgress.findIndex(p => p.lang_pair_id === action.payload.lang_pair_id);
        if (idx >= 0) state.allProgress[idx] = action.payload;
        else state.allProgress.push(action.payload);
      });
  },
});

export const { setCurrentPair, updateProgressXP, advanceProgress } = progressSlice.actions;
export default progressSlice.reducer;
