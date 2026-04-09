/**
 * src/hooks/useActivity.js
 * Shared hook: loads activity JSON, handles submission + completion recording.
 * Used by all 8 activity pages — centralizes all API calls and state.
 */
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { getActivity } from '../api/content.js';
import { validateActivity, completeActivity } from '../api/progress.js';

export function useActivity({ pairId, activityFile, activitySeqId, activityJsonId, maxXP, monthNumber, blockNumber, activityType }) {
  const navigate = useNavigate();
  const { user } = useSelector(s => s.auth);

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const attemptCount = useRef(1);

  // Load activity JSON
  useEffect(() => {
    if (!activityFile || !pairId) return;
    setLoading(true);
    setData(null);
    setError(null);
    setResult(null);
    setAnswers({});

    getActivity(pairId, activityFile)
      .then(r => { setData(r.data); setLoading(false); })
      .catch(err => {
        const status = err?.response?.status;
        setError(status === 404 ? 'content_missing' : 'load_error');
        setLoading(false);
      });
  }, [activityFile, pairId]);

  const submitAnswers = async (questions, autoPassData = null) => {
    setSubmitting(true);
    try {
      let res;

      if (autoPassData) {
        // Auto-pass for content-only activities (no interactive questions)
        res = autoPassData;
      } else {
        const { data: validated } = await validateActivity({
          activity_id: activitySeqId,
          activity_type: activityType,
          lang_pair_id: pairId,
          max_xp: maxXP,
          user_lang: user?.native_lang || 'hi',
          target_lang: pairId?.split('-')[1] || 'ja',
          questions,
          attempt_count: attemptCount.current,
        });
        res = validated;
      }

      setResult(res);
      attemptCount.current += 1;

      await completeActivity(pairId, {
        activity_seq_id: activitySeqId,
        activity_json_id: activityJsonId || data?.activityId,
        activity_type: activityType,
        lang_pair_id: pairId,
        month_number: monthNumber,
        block_number: blockNumber,
        score_earned: res.total_score,
        max_score: maxXP,
        passed: res.passed,
        ai_feedback: res.feedback,
        ai_suggestion: res.suggestion,
      });

      return res;
    } catch (e) {
      console.error('Activity submission failed:', e);
      return null;
    } finally {
      setSubmitting(false);
    }
  };

  const retryActivity = () => {
    setResult(null);
    setAnswers({});
  };

  const goToDashboard = () => navigate('/dashboard');

  return {
    data, loading, error, answers, setAnswers,
    submitting, result, showFeedback, setShowFeedback,
    submitAnswers, retryActivity, goToDashboard, user,
  };
}
