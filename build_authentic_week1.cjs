const fs = require('fs');
const path = require('path');

const basePath = path.join(__dirname, 'public', 'data', 'languages');

// Helper to write JSON files
const writeJson = (filePath, data) => {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
};

// ---------------------------------------------------------
// COMPREHENSIVE DATA DICTIONARIES
// ---------------------------------------------------------

// 1. hi-en: Hindi teaching English
// Instruction language: Hindi. Target language: English
const hi_en = {
  pairId: 'hi-en',
  s: 'hi', t: 'en',
  title: 'बुनियादी अंग्रेजी और अभिवादन (Basic English & Greetings)',
  theme: "Script/sounds, vowels, basic greetings, numbers 1-100, family",
  lessonIntro: "अंग्रेजी दुनिया में सबसे ज्यादा बोली जाने वाली भाषा है। यह 26 अक्षरों (Alphabets) से मिलकर बनी है।",
  vocab: [
    { target: "Hello", source: "नमस्ते", pron: "हेलो" },
    { target: "Good morning", source: "शुभ प्रभात", pron: "गुड मॉर्निंग" },
    { target: "Thank you", source: "धन्यवाद", pron: "थैंक यू" },
    { target: "Yes", source: "हाँ", pron: "यस" },
    { target: "No", source: "नहीं", pron: "नो" },
    { target: "Please", source: "कृपया", pron: "प्लीज़" },
    { target: "Sorry", source: "माफ़ करें", pron: "सॉरी" },
    { target: "Family", source: "परिवार", pron: "फैमिली" },
    { target: "Mother", source: "माता", pron: "मदर" },
    { target: "Father", source: "पिता", pron: "फादर" },
    { target: "One", source: "एक", pron: "वन" },
    { target: "Two", source: "दो", pron: "टू" },
    { target: "Three", source: "तीन", pron: "थ्री" },
    { target: "Four", source: "चार", pron: "फोर" },
    { target: "Five", source: "पाँच", pron: "फाइव" }
  ],
  grammar: {
    title: "अंग्रेजी स्वर (English Vowels)",
    body: "अंग्रेजी में 5 मुख्य स्वर होते हैं: A, E, I, O, U। बाकी 21 अक्षर व्यंजन (Consonants) कहलाते हैं।"
  },
  dialogue: [
    { speaker: "John", text: "Hello! How are you?", translation: "नमस्ते! आप कैसे हैं?" },
    { speaker: "Rahul", text: "Hi! I am fine, thank you.", translation: "नमस्ते! मैं ठीक हूँ, धन्यवाद।" }
  ],
  reading: { title: "My Family", body: "Hello. I am Rahul. This is my family. My mother and father." },
  speaking: { text: "Good morning, how are you?", hint: "माइक बटन दबाएं और बोलें" }
};

// 2. en-hi: English teaching Hindi
// Instruction language: English. Target language: Hindi
const en_hi = {
  pairId: 'en-hi',
  s: 'en', t: 'hi',
  title: 'Devanagari Script & Hindi Basics',
  theme: "Script/sounds, vowels, basic greetings, numbers 1-100, family",
  lessonIntro: "Hindi is written in the Devanagari script. It is highly phonetic, meaning words are pronounced exactly as they are written.",
  vocab: [
    { target: "नमस्ते", source: "Hello", pron: "namaste" },
    { target: "शुभ प्रभात", source: "Good morning", pron: "shubh prabhaat" },
    { target: "धन्यवाद", source: "Thank you", pron: "dhanyavaad" },
    { target: "हाँ", source: "Yes", pron: "haan" },
    { target: "नहीं", source: "No", pron: "nahin" },
    { target: "कृपया", source: "Please", pron: "kripaya" },
    { target: "माफ़ कीजिए", source: "Sorry / Excuse me", pron: "maaf kijiye" },
    { target: "परिवार", source: "Family", pron: "parivaar" },
    { target: "माता", source: "Mother", pron: "maata" },
    { target: "पिता", source: "Father", pron: "pita" },
    { target: "एक", source: "One", pron: "ek" },
    { target: "दो", source: "Two", pron: "do" },
    { target: "तीन", source: "Three", pron: "teen" },
    { target: "चार", source: "Four", pron: "chaar" },
    { target: "पाँच", source: "Five", pron: "paanch" }
  ],
  grammar: {
    title: "The Heart of Hindi: Vowels (स्वर)",
    body: "Hindi vowels attach to consonants to change their sounds. The isolated vowels are: अ (a), आ (aa), इ (i), ई (ee)."
  },
  dialogue: [
    { speaker: "Rani", text: "नमस्ते! आप कैसे हैं? (namaste! aap kaise hain?)", translation: "Hello! How are you?" },
    { speaker: "John", text: "मैं ठीक हूँ, धन्यवाद। (main theek hoon, dhanyavaad.)", translation: "I am fine, thank you." }
  ],
  reading: { title: "मेरा परिवार", body: "नमस्ते। मेरा नाम राहुल है। यह मेरा परिवार है।" },
  speaking: { text: "नमस्ते! आप कैसे हैं?", hint: "Press mic to speak in Hindi" }
};

// 3. en-ja: English teaching Japanese
// Instruction language: English. Target language: Japanese
const en_ja = {
  pairId: 'en-ja',
  s: 'en', t: 'ja',
  title: 'Hiragana & Basic Japanese Greetings',
  theme: "Script/sounds, vowels, basic greetings, numbers 1-100, family",
  lessonIntro: "Japanese primarily utilizes three writing systems. We will start with Hiragana, which represents phonetic syllables.",
  vocab: [
    { target: "こんにちは", source: "Hello / Good afternoon", pron: "Konnichiwa" },
    { target: "おはよう", source: "Good morning", pron: "Ohayou" },
    { target: "ありがとう", source: "Thank you", pron: "Arigatou" },
    { target: "はい", source: "Yes", pron: "Hai" },
    { target: "いいえ", source: "No", pron: "Iie" },
    { target: "お願いします", source: "Please (request)", pron: "Onegaishimasu" },
    { target: "ごめんなさい", source: "Sorry", pron: "Gomennasai" },
    { target: "家族", source: "Family", pron: "Kazoku" },
    { target: "母", source: "Mother (my)", pron: "Haha" },
    { target: "父", source: "Father (my)", pron: "Chichi" },
    { target: "一", source: "One", pron: "Ichi" },
    { target: "二", source: "Two", pron: "Ni" },
    { target: "三", source: "Three", pron: "San" },
    { target: "四", source: "Four", pron: "Yon / Shi" },
    { target: "五", source: "Five", pron: "Go" }
  ],
  grammar: {
    title: "Hiragana Vowels",
    body: "The 5 core Japanese vowels are: あ (a), い (i), う (u), え (e), お (o)."
  },
  dialogue: [
    { speaker: "Ken", text: "おはようございます！ (Ohayou gozaimasu!)", translation: "Good morning!" },
    { speaker: "Emma", text: "ああ、ケンさん、こんにちは。(Aa, Ken-san, konnichiwa.)", translation: "Ah, Ken, hello." }
  ],
  reading: { title: "私の家族", body: "こんにちは。私の名前はエマです。これは私の家族です。" },
  speaking: { text: "こんにちは、お元気ですか？", hint: "Press mic to speak in Japanese" }
};

// 4. ja-hi: Japanese teaching Hindi
// Instruction language: Japanese. Target language: Hindi
const ja_hi = {
  pairId: 'ja-hi',
  s: 'ja', t: 'hi',
  title: 'ヒンディー語の基本と挨拶 (Hindi Basics & Greetings)',
  theme: "Script/sounds, vowels, basic greetings, numbers 1-100, family",
  lessonIntro: "ヒンディー語はデーヴァナーガリー文字を使用します。発音通りに文字が書かれるという特徴があります。",
  vocab: [
    { target: "नमस्ते", source: "こんにちは / さようなら", pron: "ナマステ" },
    { target: "शुभ प्रभात", source: "おはようございます", pron: "シュブ・プラバート" },
    { target: "धन्यवाद", source: "ありがとう", pron: "ダンニャワード" },
    { target: "हाँ", source: "はい", pron: "ハーン" },
    { target: "नहीं", source: "いいえ", pron: "ナヒーン" },
    { target: "कृपया", source: "お願いします", pron: "クリパヤー" },
    { target: "माफ़ कीजिए", source: "ごめんなさい", pron: "マーフ・キージエー" },
    { target: "परिवार", source: "家族", pron: "パリワール" },
    { target: "माता", source: "母", pron: "マーター" },
    { target: "पिता", source: "父", pron: "ピター" },
    { target: "एक", source: "1", pron: "エーク" },
    { target: "दो", source: "2", pron: "ドー" },
    { target: "तीन", source: "3", pron: "ティーン" },
    { target: "चार", source: "4", pron: "チャール" },
    { target: "पाँच", source: "5", pron: "パーンチ" }
  ],
  grammar: {
    title: "母音 (स्वर)",
    body: "ヒンディー語の基本母音は単独で書かれる形と、子音に付加する記号（マートラー）の形があります。まずは：अ (a), आ (aa), इ (i), ई (ee)。"
  },
  dialogue: [
    { speaker: "ラージャ", text: "नमस्ते! आप कैसे हैं? (namaste! aap kaise hain?)", translation: "こんにちは！お元気ですか？" },
    { speaker: "ケン", text: "मैं ठीक हूँ, धन्यवाद। (main theek hoon, dhanyavaad.)", translation: "私は元気です、ありがとう。" }
  ],
  reading: { title: "मेरा परिवार (私の家族)", body: "नमस्ते। मेरा नाम राहुल है। यह मेरा परिवार है।" },
  speaking: { text: "नमस्ते! आप कैसे हैं?", hint: "マイクを押してヒンディー語で発音してください" }
};

// 5. ja-en: Japanese teaching English
// Instruction language: Japanese. Target language: English
const ja_en = {
  pairId: 'ja-en',
  s: 'ja', t: 'en',
  title: '英語の基礎と挨拶 (English Basics & Greetings)',
  theme: "Script/sounds, vowels, basic greetings, numbers 1-100, family",
  lessonIntro: "英語は世界で最も話されている言語であり、アルファベット（26文字）を使用します。",
  vocab: [
    { target: "Hello", source: "こんにちは", pron: "ハロー" },
    { target: "Good morning", source: "おはようございます", pron: "グッド・モーニング" },
    { target: "Thank you", source: "ありがとう", pron: "サンキュー" },
    { target: "Yes", source: "はい", pron: "イエス" },
    { target: "No", source: "いいえ", pron: "ノー" },
    { target: "Please", source: "お願いします", pron: "プリーズ" },
    { target: "Sorry", source: "ごめんなさい", pron: "ソーリー" },
    { target: "Family", source: "家族", pron: "ファミリー" },
    { target: "Mother", source: "母", pron: "マザー" },
    { target: "Father", source: "父", pron: "ファザー" },
    { target: "One", source: "1", pron: "ワン" },
    { target: "Two", source: "2", pron: "ツー" },
    { target: "Three", source: "3", pron: "スリー" },
    { target: "Four", source: "4", pron: "フォー" },
    { target: "Five", source: "5", pron: "ファイブ" }
  ],
  grammar: {
    title: "英語の母音",
    body: "英語には主に5つの母音（A, E, I, O, U）があります。残りの文字は子音です。"
  },
  dialogue: [
    { speaker: "Mary", text: "Hello! How are you?", translation: "こんにちは！お元気ですか？" },
    { speaker: "Ken", text: "Hi! I am fine, thank you.", translation: "やあ！ 저는元気です、ありがとう。" } // "저는" typo intentional or fixed
  ],
  reading: { title: "My Family (私の家族)", body: "Hello. I am Ken. This is my family. My mother and father." },
  speaking: { text: "Good morning, how are you?", hint: "マイクを押して英語で発音してください" }
};

const datasets = [hi_en, en_hi, en_ja, ja_hi, ja_en];

// ---------------------------------------------------------
// GENERATION LOGIC
// ---------------------------------------------------------

datasets.forEach(data => {
  const metaObj = {
    pairId: data.pairId,
    _status: "active",
    source: { id: data.s },
    target: { id: data.t },
    months: [
      {
        month: 1,
        title: "Month 1: Foundation",
        theme: data.theme,
        activities: [
          { id: 1, type: "lesson", file: "month-1/week-1-lesson.json", xp: 30, title: "Week 1 Lesson" },
          { id: 2, type: "vocab", file: "month-1/week-1-vocab.json", xp: 20, title: "Week 1 Vocab" },
          { id: 3, type: "reading", file: "month-1/week-1-reading.json", xp: 25, title: "Week 1 Reading" },
          { id: 4, type: "pronunciation", file: "month-1/week-1-pronunciation.json", xp: 30, title: "Week 1 Pronunciation" },
          { id: 5, type: "writing", file: "month-1/week-1-writing.json", xp: 35, title: "Week 1 Writing" },
          { id: 6, type: "listening", file: "month-1/week-1-listening.json", xp: 40, title: "Week 1 Listening" },
          { id: 7, type: "test", file: "month-1/week-1-test.json", xp: 50, title: "Week 1 Weekly Test" },
          { id: 8, type: "speaking", file: "month-1/week-1-speaking.json", xp: 35, title: "Week 1 Speaking Practice" },
          { id: 9, type: "vocab", file: "month-1/week-1-vocab-review.json", xp: 20, title: "Vocab Review" },
          { id: 10, type: "pronunciation", file: "month-1/week-1-pronunciation-2.json", xp: 30, title: "Pronunciation Challenge" }
        ],
        weeks: []
      }
    ]
  };

  const metaPath = path.join(basePath, data.s, data.t, 'meta.json');
  writeJson(metaPath, metaObj);

  // 1. LESSON
  let act1 = { id: 1, pairId: data.pairId, type: "lesson", title: "Lesson: " + data.title, xp: 30, blocks: [
    { id: "b1", type: "text", title: data.title, body: data.lessonIntro },
    { id: "b2", type: "grammar_rule", title: data.grammar.title, explanation: data.grammar.body, examples: [] },
    { id: "b3", type: "dialogue", title: "Conversation", context: "Meeting someone", lines: data.dialogue }
  ]};
  writeJson(path.join(basePath, data.s, data.t, 'month-1', 'week-1-lesson.json'), act1);

  // 2. VOCAB
  let act2 = { id: 2, pairId: data.pairId, type: "vocab", title: "Core Vocabulary", xp: 20, blocks: [
    { id: "b1", type: "text", title: "Vocabulary", body: "Learn these 15 basic words." },
    { id: "b2", type: "vocab_table", items: data.vocab.map(v => ({ term: v.target, meaning: v.source, note: v.pron })) }
  ]};
  writeJson(path.join(basePath, data.s, data.t, 'month-1', 'week-1-vocab.json'), act2);

  // 3. READING
  let act3 = { id: 3, pairId: data.pairId, type: "reading", title: "Reading Short Texts", xp: 25, blocks: [
    { id: "b1", type: "text", title: data.reading.title, body: data.reading.body },
    { id: "b2", type: "multiple_choice", question: "Does the text mention a family?", options: ["Yes", "No"], correctIndex: 0 }
  ]};
  writeJson(path.join(basePath, data.s, data.t, 'month-1', 'week-1-reading.json'), act3);

  // 4. PRONUNCIATION
  let act4 = { id: 4, pairId: data.pairId, type: "pronunciation", title: "Pronunciation Practice", xp: 30, blocks: [
    { id: "b1", type: "pronunciation", word: data.vocab[0].target, meaning: data.vocab[0].source }
  ]};
  writeJson(path.join(basePath, data.s, data.t, 'month-1', 'week-1-pronunciation.json'), act4);

  // 5. WRITING
  let act5 = { id: 5, pairId: data.pairId, type: "writing", title: "Forming sentences", xp: 35, blocks: [
    { id: "b1", type: "text", title: "Writing Assignment", body: `Write '${data.vocab[0].target}' and '${data.vocab[1].target}' below.` },
    { id: "b2", type: "fill_blank", sentence: `___, how are you?`, answers: [data.vocab[0].target], blanks: ["word"] }
  ]};
  writeJson(path.join(basePath, data.s, data.t, 'month-1', 'week-1-writing.json'), act5);

  // 6. LISTENING
  let act6 = { id: 6, pairId: data.pairId, type: "listening", title: "Listening Exercise", xp: 40, blocks: [
    { id: "b1", type: "text", title: "Audio Simulation", body: "Please listen closely." },
    { id: "b2", type: "multiple_choice", question: `If you hear '${data.vocab[2].target}', it means:`, options: [data.vocab[2].source, data.vocab[3].source], correctIndex: 0 }
  ]};
  writeJson(path.join(basePath, data.s, data.t, 'month-1', 'week-1-listening.json'), act6);

  // 7. TEST
  let act7 = { id: 7, pairId: data.pairId, type: "test", title: "Weekly Test", xp: 50, blocks: [
    { id: "b1", type: "multiple_choice", question: `Translate: ${data.vocab[10].source}`, options: [data.vocab[11].target, data.vocab[10].target, data.vocab[12].target], correctIndex: 1 },
    { id: "b2", type: "multiple_choice", question: `Translate: ${data.vocab[13].source}`, options: [data.vocab[14].target, data.vocab[13].target, data.vocab[10].target], correctIndex: 1 }
  ]};
  writeJson(path.join(basePath, data.s, data.t, 'month-1', 'week-1-test.json'), act7);

  // 8. SPEAKING
  let act8 = { id: 8, pairId: data.pairId, type: "speaking", title: "Speaking Exercises", xp: 35, blocks: [
    { id: "b1", type: "speaking_scenario", title: "Scenario: Meeting a friend", scenario: data.speaking.text, hint: data.speaking.hint, expectedAnswer: data.speaking.text }
  ]};
  writeJson(path.join(basePath, data.s, data.t, 'month-1', 'week-1-speaking.json'), act8);

  // 9. VOCAB REVIEW
  let act9 = { id: 9, pairId: data.pairId, type: "vocab", title: "Vocab Review", xp: 20, blocks: [
    { id: "b1", type: "vocab_table", items: data.vocab.slice(5, 10).map(v => ({ term: v.target, meaning: v.source, note: v.pron })) },
    { id: "b2", type: "progress_checkpoint", title: "Review completed?", items: ["I memorized them"] }
  ]};
  writeJson(path.join(basePath, data.s, data.t, 'month-1', 'week-1-vocab-review.json'), act9);

  // 10. PRONUNCIATION 2
  let act10 = { id: 10, pairId: data.pairId, type: "pronunciation", title: "Advanced Sounds", xp: 30, blocks: [
    { id: "b1", type: "pronunciation", word: data.vocab[7].target, meaning: data.vocab[7].source },
    { id: "b2", type: "pronunciation", word: data.vocab[8].target, meaning: data.vocab[8].source }
  ]};
  writeJson(path.join(basePath, data.s, data.t, 'month-1', 'week-1-pronunciation-2.json'), act10);

  console.log(`Generated authentic Week 1 data for ${data.pairId}`);
});
