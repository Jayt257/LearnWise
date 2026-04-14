/
  src/pages/activities/ActivityRouter.jsx
  Reads activity type from route params and renders the correct page.
  Activity data is loaded from JSON via backend; no hardcoding.
  Supports: lesson, vocabulary, pronunciation, reading, writing, listening, speaking, test
 /
import React from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import LessonPage from './LessonPage.jsx';
import VocabPage from './VocabPage.jsx';
import ReadingPage from './ReadingPage.jsx';
import WritingPage from './WritingPage.jsx';
import ListeningPage from './ListeningPage.jsx';
import SpeakingPage from './SpeakingPage.jsx';
import PronunciationPage from './PronunciationPage.jsx';
import TestPage from './TestPage.jsx';

const ACTIVITY_COMPONENTS = {
  lesson: LessonPage,
  vocabulary: VocabPage,
  vocab: VocabPage,        // backward compat
  reading: ReadingPage,
  writing: WritingPage,
  listening: ListeningPage,
  speaking: SpeakingPage,
  pronunciation: PronunciationPage,
  test: TestPage,
};

export default function ActivityRouter() {
  const { pairId, type } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const state = location.state || {};
  const { activityFile, activitySeqId, activityJsonId, maxXP, label, monthNumber, blockNumber } = state;

  if (!activityFile) {
    return (
      <div style={{ padding: 'rem', textAlign: 'center' }}>
        <p style={{ fontSize: 'rem', marginBottom: 'rem' }}></p>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '.rem' }}>
          Activity not found. Please go back to the roadmap.
        </p>
        <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>← Back to Roadmap</button>
      </div>
    );
  }

  const Component = ACTIVITY_COMPONENTS[type];
  if (!Component) {
    return (
      <div style={{ padding: 'rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--color-danger-light)' }}>Unknown activity type: <strong>{type}</strong></p>
        <button className="btn btn-secondary" style={{ marginTop: 'rem' }} onClick={() => navigate('/dashboard')}>← Back</button>
      </div>
    );
  }

  return (
    <Component
      pairId={pairId}
      activityFile={activityFile}
      activitySeqId={activitySeqId}
      activityJsonId={activityJsonId}
      maxXP={maxXP}
      label={label || type}
      monthNumber={monthNumber}
      blockNumber={blockNumber}
    />
  );
}
