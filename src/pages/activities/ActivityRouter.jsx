/**
 * src/pages/activities/ActivityRouter.jsx
 * Reads the activity type from route params and renders the correct activity page.
 * All activities receive: activityFile, activityId, maxXP, pairId via location.state or params.
 */
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
  vocab: VocabPage,
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
  const { activityFile, activityId, maxXP, label } = state;

  if (!activityFile) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--color-text-muted)' }}>Activity not found. Please go back to the roadmap.</p>
        <button className="btn btn-primary mt-4" onClick={() => navigate('/dashboard')}>← Back to Roadmap</button>
      </div>
    );
  }

  const Component = ACTIVITY_COMPONENTS[type];
  if (!Component) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--color-danger-light)' }}>Unknown activity type: {type}</p>
        <button className="btn btn-secondary mt-4" onClick={() => navigate('/dashboard')}>← Back</button>
      </div>
    );
  }

  return (
    <Component
      pairId={pairId}
      activityFile={activityFile}
      activityId={activityId}
      maxXP={maxXP}
      label={label || type}
    />
  );
}
