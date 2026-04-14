/
  src/components/DynamicQuiz.jsx
  Universal quiz renderer — supports mcq, true_false, fill_blank, short_answer.
  % driven by the question object from JSON. No hardcoded content.
 /
import React from 'react';
import TargetTextBlock from './TargetTextBlock.jsx';
import AudioPlayer from './AudioPlayer.jsx';

const OPTION_LABELS = ['A', 'B', 'C', 'D', 'E'];

export default function DynamicQuiz({ question, index, answer, onChange, showResult = false }) {
  if (!question) return null;

  const qType = question.questionType || question.type;
  const qid = question.questionId || question.id || `q_${index}`;

  return (
    <div className="card" style={{ marginBottom: 'rem' }}>
      {/ Question number + audio /}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '.rem' }}>
        <span style={{ fontSize: '.rem', fontWeight: , color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
          Q{index + } · {qType?.replace('_', ' ')}
        </span>
        {question.audioRef && <AudioPlayer audioUrl={question.audioRef} label="Listen" />}
      </div>

      {/ Question text /}
      {question.questionText && (
        <div style={{ fontWeight: , marginBottom: '.rem', fontSize: '.rem' }}>
          {question.questionText}
        </div>
      )}

      {/ Target-lang question display if present /}
      {question.questionInTargetLanguage && (
        <div style={{ marginBottom: '.rem' }}>
          <TargetTextBlock data={question.questionInTargetLanguage} size="sm" />
        </div>
      )}

      {/ Render by type /}
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
      {/ Fallback: if questionType is missing or unrecognized → short answer textarea /}
      {!qType || !['mcq','multiple_choice','true_false','fill_blank','fill_in_blank','short_answer','open','matching'].includes(qType) ? (
        <ShortAnswerRenderer qid={qid} answer={answer} onChange={onChange} placeholder={question.placeholder || 'Type your answer...'} />
      ) : null}
    </div>
  );
}

function MCQRenderer({ qid, options, answer, onChange, showResult, correctAnswer }) {
  if (!options || options.length === ) return null;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '.rem' }}>
      {options.map((opt, i) => {
        const label = OPTION_LABELS[i];
        const isSelected = answer === i || answer === label;
        const optText = typeof opt === 'object' ? (opt.text || opt.targetText || JSON.stringify(opt)) : opt;
        const isCorrect = showResult && (correctAnswer === i || correctAnswer === label || correctAnswer === optText);
        return (
          <button key={i} type="button"
            onClick={() => !showResult && onChange(i)}
            style={{
              padding: '.rem rem', borderRadius: 'var(--radius-md)', textAlign: 'left',
              border: `px solid ${isCorrect ? 'var(--color-success)' : isSelected ? 'var(--color-primary)' : 'var(--color-border)'}`,
              background: isCorrect ? 'rgba(,,,.)' : isSelected ? 'var(--color-primary-glow)' : 'var(--color-surface-)',
              cursor: showResult ? 'default' : 'pointer', fontSize: '.rem', transition: 'all .s',
            }}>
            <span style={{ marginRight: '.rem', fontWeight: , color: 'var(--color-text-muted)' }}>{label}.</span>
            {optText}
          </button>
        );
      })}
    </div>
  );
}

function TrueFalseRenderer({ qid, answer, onChange, showResult, correctAnswer }) {
  return (
    <div style={{ display: 'flex', gap: '.rem' }}>
      {['True', 'False'].map(v => {
        const isSelected = answer === v;
        const isCorrect = showResult && correctAnswer === v;
        return (
          <button key={v} type="button" onClick={() => !showResult && onChange(v)}
            style={{
              flex: , padding: '.rem', borderRadius: 'var(--radius-md)', fontWeight: , fontSize: '.rem',
              border: `px solid ${isCorrect ? 'var(--color-success)' : isSelected ? 'var(--color-primary)' : 'var(--color-border)'}`,
              background: isCorrect ? 'rgba(,,,.)' : isSelected ? 'var(--color-primary-glow)' : 'var(--color-surface-)',
              cursor: showResult ? 'default' : 'pointer', transition: 'all .s',
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '.rem' }}>
      {blankedSentence && <p style={{ fontSize: '.rem', color: 'var(--color-text-muted)' }}>{blankedSentence}</p>}
      <input className="form-input" placeholder="Fill in the blank..."
        value={answer || ''} onChange={e => onChange(e.target.value)} />
    </div>
  );
}

function ShortAnswerRenderer({ qid, answer, onChange, placeholder }) {
  return (
    <textarea className="form-input" rows={}
      placeholder={placeholder || 'Write your answer here...'}
      value={answer || ''} onChange={e => onChange(e.target.value)}
      style={{ resize: 'vertical', minHeight:  }}
    />
  );
}

function MatchingRenderer({ qid, pairs, answer = {}, onChange }) {
  if (!pairs || pairs.length === ) return <p style={{ color: 'var(--color-text-muted)', fontSize: '.rem' }}>No matching pairs defined.</p>;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '.rem' }}>
      {pairs.map((pair, i) => (
        <div key={i} style={{ display: 'flex', gap: 'rem', alignItems: 'center' }}>
          <div style={{ flex: , padding: '.rem .rem', background: 'var(--color-surface-)', borderRadius: 'var(--radius-sm)', fontSize: '.rem' }}>{pair.left}</div>
          <span style={{ color: 'var(--color-text-dim)' }}>→</span>
          <input className="form-input" style={{ flex:  }} placeholder={`Match for: ${pair.left}`}
            value={answer[i] || ''} onChange={e => onChange({ ...answer, [i]: e.target.value })} />
        </div>
      ))}
    </div>
  );
}
