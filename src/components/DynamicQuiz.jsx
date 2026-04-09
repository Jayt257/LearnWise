/**
 * src/components/DynamicQuiz.jsx
 * Universal quiz renderer — supports mcq, true_false, fill_blank, short_answer.
 * 100% driven by the question object from JSON. No hardcoded content.
 */
import React from 'react';
import TargetTextBlock from './TargetTextBlock.jsx';
import AudioPlayer from './AudioPlayer.jsx';

const OPTION_LABELS = ['A', 'B', 'C', 'D', 'E'];

export default function DynamicQuiz({ question, index, answer, onChange, showResult = false }) {
  if (!question) return null;

  const qType = question.questionType || question.type;
  const qid = question.questionId || question.id || `q_${index}`;

  return (
    <div className="card" style={{ marginBottom: '1rem' }}>
      {/* Question number + audio */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
          Q{index + 1} · {qType?.replace('_', ' ')}
        </span>
        {question.audioRef && <AudioPlayer audioUrl={question.audioRef} label="Listen" />}
      </div>

      {/* Question text */}
      {question.questionText && (
        <div style={{ fontWeight: 600, marginBottom: '0.75rem', fontSize: '0.95rem' }}>
          {question.questionText}
        </div>
      )}

      {/* Target-lang question display if present */}
      {question.questionInTargetLanguage && (
        <div style={{ marginBottom: '0.75rem' }}>
          <TargetTextBlock data={question.questionInTargetLanguage} size="sm" />
        </div>
      )}

      {/* Render by type */}
      {(qType === 'mcq' || qType === 'multiple_choice') && (
        <MCQRenderer qid={qid} options={question.options} answer={answer} onChange={onChange} showResult={showResult} correctAnswer={question.correctAnswer} />
      )}
      {qType === 'true_false' && (
        <TrueFalseRenderer qid={qid} answer={answer} onChange={onChange} showResult={showResult} correctAnswer={question.correctAnswer} />
      )}
      {(qType === 'fill_blank' || qType === 'fill_in_blank') && (
        <FillBlankRenderer qid={qid} answer={answer} onChange={onChange} blankedSentence={question.blankedSentence} />
      )}
      {(qType === 'short_answer' || qType === 'open') && (
        <ShortAnswerRenderer qid={qid} answer={answer} onChange={onChange} placeholder={question.placeholder} />
      )}
      {qType === 'matching' && (
        <MatchingRenderer qid={qid} pairs={question.matchingPairs} answer={answer} onChange={onChange} />
      )}
    </div>
  );
}

function MCQRenderer({ qid, options, answer, onChange, showResult, correctAnswer }) {
  if (!options || options.length === 0) return null;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {options.map((opt, i) => {
        const label = OPTION_LABELS[i];
        const isSelected = answer === i || answer === label;
        const optText = typeof opt === 'object' ? (opt.text || opt.targetText || JSON.stringify(opt)) : opt;
        const isCorrect = showResult && (correctAnswer === i || correctAnswer === label || correctAnswer === optText);
        return (
          <button key={i} type="button"
            onClick={() => !showResult && onChange(i)}
            style={{
              padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', textAlign: 'left',
              border: `2px solid ${isCorrect ? 'var(--color-success)' : isSelected ? 'var(--color-primary)' : 'var(--color-border)'}`,
              background: isCorrect ? 'rgba(16,185,129,0.1)' : isSelected ? 'var(--color-primary-glow)' : 'var(--color-surface-2)',
              cursor: showResult ? 'default' : 'pointer', fontSize: '0.875rem', transition: 'all 0.15s',
            }}>
            <span style={{ marginRight: '0.5rem', fontWeight: 700, color: 'var(--color-text-muted)' }}>{label}.</span>
            {optText}
          </button>
        );
      })}
    </div>
  );
}

function TrueFalseRenderer({ qid, answer, onChange, showResult, correctAnswer }) {
  return (
    <div style={{ display: 'flex', gap: '0.75rem' }}>
      {['True', 'False'].map(v => {
        const isSelected = answer === v;
        const isCorrect = showResult && correctAnswer === v;
        return (
          <button key={v} type="button" onClick={() => !showResult && onChange(v)}
            style={{
              flex: 1, padding: '0.75rem', borderRadius: 'var(--radius-md)', fontWeight: 600, fontSize: '0.9rem',
              border: `2px solid ${isCorrect ? 'var(--color-success)' : isSelected ? 'var(--color-primary)' : 'var(--color-border)'}`,
              background: isCorrect ? 'rgba(16,185,129,0.1)' : isSelected ? 'var(--color-primary-glow)' : 'var(--color-surface-2)',
              cursor: showResult ? 'default' : 'pointer', transition: 'all 0.15s',
            }}>
            {v === 'True' ? '✓ True' : '✗ False'}
          </button>
        );
      })}
    </div>
  );
}

function FillBlankRenderer({ qid, answer, onChange, blankedSentence }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {blankedSentence && <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>{blankedSentence}</p>}
      <input className="form-input" placeholder="Fill in the blank..."
        value={answer || ''} onChange={e => onChange(e.target.value)} />
    </div>
  );
}

function ShortAnswerRenderer({ qid, answer, onChange, placeholder }) {
  return (
    <textarea className="form-input" rows={3}
      placeholder={placeholder || 'Write your answer here...'}
      value={answer || ''} onChange={e => onChange(e.target.value)}
      style={{ resize: 'vertical', minHeight: 80 }}
    />
  );
}

function MatchingRenderer({ qid, pairs, answer = {}, onChange }) {
  if (!pairs || pairs.length === 0) return <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>No matching pairs defined.</p>;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {pairs.map((pair, i) => (
        <div key={i} style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ flex: 1, padding: '0.5rem 0.75rem', background: 'var(--color-surface-2)', borderRadius: 'var(--radius-sm)', fontSize: '0.875rem' }}>{pair.left}</div>
          <span style={{ color: 'var(--color-text-dim)' }}>→</span>
          <input className="form-input" style={{ flex: 1 }} placeholder={`Match for: ${pair.left}`}
            value={answer[i] || ''} onChange={e => onChange({ ...answer, [i]: e.target.value })} />
        </div>
      ))}
    </div>
  );
}
