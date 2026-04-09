/**
 * src/store/progressSlice.js
 * Redux slice for user's language learning progress across all pairs.
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
    allProgress: [],   // array of UserLanguageProgress
    pairs: [],         // available language pairs
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
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAllProgress.fulfilled, (state, action) => { state.allProgress = action.payload; })
      .addCase(fetchPairs.fulfilled, (state, action) => { state.pairs = action.payload; })
      .addCase(startLanguagePair.fulfilled, (state, action) => {
        const existing = state.allProgress.find(p => p.lang_pair_id === action.payload.lang_pair_id);
        if (!existing) state.allProgress.push(action.payload);
      });
  },
});

export const { setCurrentPair, updateProgressXP } = progressSlice.actions;
export default progressSlice.reducer;
