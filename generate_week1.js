import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const basePath = path.join(__dirname, 'public', 'data', 'languages');

const vocabularyLists = {
  'hi-en': [
    { source: "नमस्ते", target: "Hello", targetPronunciation: "He-lo" },
    { source: "धन्यवाद", target: "Thank you", targetPronunciation: "Th-ank y-ou" },
    { source: "हाँ", target: "Yes", targetPronunciation: "Y-es" },
    { source: "नहीं", target: "No", targetPronunciation: "N-o" },
    { source: "परिवार", target: "Family", targetPronunciation: "Fa-mi-ly" }
  ],
  'en-hi': [
    { source: "Hello", target: "नमस्ते", targetPronunciation: "Namaste" },
    { source: "Thank you", target: "धन्यवाद", targetPronunciation: "Dhanyavaad" },
    { source: "Yes", target: "हाँ", targetPronunciation: "Haan" },
    { source: "No", target: "नहीं", targetPronunciation: "Nahi" },
    { source: "Family", target: "परिवार", targetPronunciation: "Parivaar" }
  ],
  'en-ja': [
    { source: "Hello", target: "こんにちは", targetPronunciation: "Konnichiwa" },
    { source: "Thank you", target: "ありがとう", targetPronunciation: "Arigatou" },
    { source: "Yes", target: "はい", targetPronunciation: "Hai" },
    { source: "No", target: "いいえ", targetPronunciation: "Iie" },
    { source: "Family", target: "家族", targetPronunciation: "Kazoku" }
  ],
  'ja-hi': [
    { source: "こんにちは", target: "नमस्ते", targetPronunciation: "Namaste" },
    { source: "ありがとう", target: "धन्यवाद", targetPronunciation: "Dhanyavaad" },
    { source: "はい", target: "हाँ", targetPronunciation: "Haan" },
    { source: "いいえ", target: "नहीं", targetPronunciation: "Nahi" },
    { source: "家族", target: "परिवार", targetPronunciation: "Parivaar" }
  ],
  'ja-en': [
    { source: "こんにちは", target: "Hello", targetPronunciation: "Hello" },
    { source: "ありがとう", target: "Thank you", targetPronunciation: "Thank you" },
    { source: "はい", target: "Yes", targetPronunciation: "Yes" },
    { source: "いいえ", target: "No", targetPronunciation: "No" },
    { source: "家族", target: "Family", targetPronunciation: "Family" }
  ],
};

const texts = {
  'hi-en': { title: "अंग्रेजी में आपका स्वागत है!", explanation: "आज हम अंग्रेजी की मूल बातें सीखेंगे। अंग्रेजी एक बहुत ही महत्वपूर्ण भाषा है।" },
  'en-hi': { title: "Welcome to Hindi!", explanation: "Today we will learn the basics of Hindi. It is built on the Devanagari script." },
  'en-ja': { title: "Welcome to Japanese!", explanation: "Today we will begin learning Japanese. We will start with standard greetings." },
  'ja-hi': { title: "ヒンディー語へようこそ！", explanation: "今日はヒンディー語の基本を学びます。デーヴァナーガリー文字を使用します。" },
  'ja-en': { title: "英語へようこそ！", explanation: "今日は英語の基本を学びます。アルファベットを使用します。" },
};

const activities = [
  { id: 1, type: "lesson", file: "month-1/week-1-lesson.json", xp: 30, title: "Basic Greetings" },
  { id: 2, type: "vocab", file: "month-1/week-1-vocab.json", xp: 20, title: "Greetings & Family Vocab" },
  { id: 3, type: "reading", file: "month-1/week-1-reading.json", xp: 25, title: "Reading Short Sentences" },
  { id: 4, type: "pronunciation", file: "month-1/week-1-pronunciation.json", xp: 30, title: "Pronunciation Practice 1" },
  { id: 5, type: "writing", file: "month-1/week-1-writing.json", xp: 35, title: "Writing Simple Words" },
  { id: 6, type: "listening", file: "month-1/week-1-listening.json", xp: 40, title: "Listening to Natives" },
  { id: 7, type: "test", file: "month-1/week-1-test.json", xp: 50, title: "Weekly Test" },
  { id: 8, type: "speaking", file: "month-1/week-1-speaking.json", xp: 35, title: "Speaking Practice" },
  { id: 9, type: "vocab", file: "month-1/week-1-vocab-review.json", xp: 20, title: "Vocab Review" },
  { id: 10, type: "pronunciation", file: "month-1/week-1-pronunciation-2.json", xp: 30, title: "Pronunciation Practice 2" }
];

const paths = ['hi-en', 'en-hi', 'en-ja', 'ja-hi', 'ja-en'];

paths.forEach(pair => {
  const [s, t] = pair.split('-');
  
  // Create folders
  const pairDir = path.join(basePath, s, t);
  const m1Dir = path.join(pairDir, 'month-1');
  if (!fs.existsSync(m1Dir)) {
    fs.mkdirSync(m1Dir, { recursive: true });
  }

  // Update meta.json
  const metaPath = path.join(pairDir, 'meta.json');
  // Read existing meta.json or just blindly overwrite? We should rewrite the months array to exist
  let meta = {
    _status: "active",
    pairId: pair,
    source: { id: s },
    target: { id: t },
    months: [
      {
        month: 1,
        title: "Foundation & Greetings",
        weeks: [
          {
            week: 1,
            title: "Basics",
            activities: activities.map(a => ({ id: a.id, type: a.type, file: a.file, xp: a.xp, label: a.title }))
          }
        ]
      }
    ]
  };
  fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));

  // Write the 10 files
  activities.forEach(act => {
    const vocab = vocabularyLists[pair];
    const textData = texts[pair];
    
    let blocks = [];
    
    if (act.type === 'lesson') {
      blocks.push({ id: "b1", type: "text", title: textData.title, body: textData.explanation });
      blocks.push({ id: "b2", type: "grammar_rule", title: "Key Rule", explanation: textData.explanation, examples: [{sentence: vocab[0].target, translation: vocab[0].source}] });
    } else if (act.type === 'vocab') {
      blocks.push({ id: "b1", type: "text", title: "Study these words", body: "Memorize the following." });
      blocks.push({ id: "b2", type: "vocab_table", items: vocab.map(v => ({ term: v.target, meaning: v.source, note: v.targetPronunciation })) });
    } else if (act.type === 'test') {
      blocks.push({ id: "b1", type: "multiple_choice", question: `How do you say "${vocab[0].source}"?`, options: [vocab[0].target, vocab[1].target, vocab[2].target], correctIndex: 0 });
    } else {
      blocks.push({ id: "b1", type: "text", title: act.title, body: "Practice activity block generated automatically." });
      blocks.push({ id: "b2", type: "progress_checkpoint", title: "Are you ready?", items: ["Completed section", "Understood topics"] });
    }

    const fileContent = {
      id: act.id,
      pairId: pair,
      type: act.type,
      title: act.title,
      xp: act.xp,
      blocks: blocks
    };
    
    fs.writeFileSync(path.join(pairDir, act.file), JSON.stringify(fileContent, null, 2));
  });

  console.log(`Generated week 1 data for ${pair}`);
});
