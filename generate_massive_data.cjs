const fs = require('fs');
const path = require('path');

const basePath = path.join(__dirname, 'public', 'data', 'languages');

// Core Vocabularies (30 items per pair)
// English, Hindi, Japanese, Romaji/Pronunciation
const concepts = [
  { en: "Hello", hi: "नमस्ते", ja: "こんにちは", enPron: "He-lo", hiPron: "namaste", jaPron: "Konnichiwa", emoji: "👋", type: "greetings" },
  { en: "Good morning", hi: "शुभ प्रभात", ja: "おはようございます", enPron: "Gud mor-ning", hiPron: "shubh prabhat", jaPron: "Ohayou gozaimasu", emoji: "🌅", type: "greetings" },
  { en: "Good evening", hi: "शुभ संध्या", ja: "こんばんは", enPron: "Gud eve-ning", hiPron: "shubh sandhya", jaPron: "Konbanwa", emoji: "🌙", type: "greetings" },
  { en: "Goodbye", hi: "अलविदा", ja: "さようなら", enPron: "Gud-bye", hiPron: "alvida", jaPron: "Sayounara", emoji: "👋", type: "greetings" },
  { en: "Thank you", hi: "धन्यवाद", ja: "ありがとう", enPron: "Thank you", hiPron: "dhanyavad", jaPron: "Arigatou", emoji: "🙏", type: "essentials" },
  { en: "Sorry", hi: "माफ़ करें", ja: "ごめんなさい", enPron: "So-rry", hiPron: "maaf kare", jaPron: "Gomennasai", emoji: "🙇", type: "essentials" },
  { en: "Excuse me", hi: "सुनिए", ja: "すみません", enPron: "Ex-cuse me", hiPron: "suniye", jaPron: "Sumimasen", emoji: "🗣️", type: "essentials" },
  { en: "Yes", hi: "हाँ", ja: "はい", enPron: "Yes", hiPron: "haan", jaPron: "Hai", emoji: "✅", type: "essentials" },
  { en: "No", hi: "नहीं", ja: "いいえ", enPron: "No", hiPron: "nahi", jaPron: "Iie", emoji: "❌", type: "essentials" },
  { en: "Please", hi: "कृपया", ja: "お願いします", enPron: "Please", hiPron: "kripaya", jaPron: "Onegaishimasu", emoji: "🙏", type: "essentials" },
  { en: "I", hi: "मैं", ja: "わたし", enPron: "I", hiPron: "main", jaPron: "Watashi", emoji: "🧍", type: "pronouns" },
  { en: "You", hi: "तुम / आप", ja: "あなた", enPron: "You", hiPron: "tum", jaPron: "Anata", emoji: "🧍‍♂️", type: "pronouns" },
  { en: "Name", hi: "नाम", ja: "なまえ", enPron: "Name", hiPron: "naam", jaPron: "Namae", emoji: "🏷️", type: "nouns" },
  { en: "Family", hi: "परिवार", ja: "家族", enPron: "Family", hiPron: "parivar", jaPron: "Kazoku", emoji: "👨‍👩‍👦", type: "nouns" },
  { en: "Mother", hi: "माता", ja: "母", enPron: "Mother", hiPron: "mata", jaPron: "Haha", emoji: "👩", type: "family" },
  { en: "Father", hi: "पिता", ja: "父", enPron: "Father", hiPron: "pita", jaPron: "Chichi", emoji: "👨", type: "family" },
  { en: "Friend", hi: "मित्र / दोस्त", ja: "友達", enPron: "Friend", hiPron: "dost", jaPron: "Tomodachi", emoji: "🤝", type: "nouns" },
  { en: "One", hi: "एक", ja: "一", enPron: "One", hiPron: "ek", jaPron: "Ichi", emoji: "1️⃣", type: "numbers" },
  { en: "Two", hi: "दो", ja: "二", enPron: "Two", hiPron: "do", jaPron: "Ni", emoji: "2️⃣", type: "numbers" },
  { en: "Three", hi: "तीन", ja: "三", enPron: "Three", hiPron: "teen", jaPron: "San", emoji: "3️⃣", type: "numbers" },
  { en: "Four", hi: "चार", ja: "四", enPron: "Four", hiPron: "char", jaPron: "Yon", emoji: "4️⃣", type: "numbers" },
  { en: "Five", hi: "पाँच", ja: "五", enPron: "Five", hiPron: "paanch", jaPron: "Go", emoji: "5️⃣", type: "numbers" },
  { en: "Water", hi: "पानी", ja: "水", enPron: "Water", hiPron: "paani", jaPron: "Mizu", emoji: "💧", type: "nouns" },
  { en: "Food", hi: "खाना", ja: "食べ物", enPron: "Food", hiPron: "khaana", jaPron: "Tabemono", emoji: "🍱", type: "nouns" },
  { en: "Good", hi: "अच्छा", ja: "良い", enPron: "Good", hiPron: "achha", jaPron: "Yoi", emoji: "👍", type: "adjectives" },
  { en: "Bad", hi: "बुरा", ja: "悪い", enPron: "Bad", hiPron: "bura", jaPron: "Warui", emoji: "👎", type: "adjectives" },
  { en: "Big", hi: "बड़ा", ja: "大きい", enPron: "Big", hiPron: "bada", jaPron: "Ookii", emoji: "🐘", type: "adjectives" },
  { en: "Small", hi: "छोटा", ja: "小さい", enPron: "Small", hiPron: "chhota", jaPron: "Chiisai", emoji: "🐁", type: "adjectives" },
  { en: "Beautiful", hi: "सुंदर", ja: "きれい", enPron: "Beauti-ful", hiPron: "sundar", jaPron: "Kirei", emoji: "✨", type: "adjectives" },
  { en: "Love", hi: "प्यार", ja: "愛", enPron: "Love", hiPron: "pyaar", jaPron: "Ai", emoji: "❤️", type: "nouns" }
];

const pairsConfig = [
  { id: 'hi-en', s: 'hi', t: 'en', sL: "Hindi", tL: "English" },
  { id: 'en-hi', s: 'en', t: 'hi', sL: "English", tL: "Hindi" },
  { id: 'en-ja', s: 'en', t: 'ja', sL: "English", tL: "Japanese" },
  { id: 'ja-hi', s: 'ja', t: 'hi', sL: "Japanese", tL: "Hindi" },
  { id: 'ja-en', s: 'ja', t: 'en', sL: "Japanese", tL: "English" }
];

// Returns text for a concept based on lang code
const getConceptTerm = (concept, lang) => concept[lang];
const getConceptPron = (concept, lang) => lang === 'ja' ? concept.jaPron : lang === 'hi' ? concept.hiPron : concept.enPron;

pairsConfig.forEach(config => {
  const { id, s, t, sL, tL } = config;
  const targetDir = path.join(basePath, s, t, 'month-1');
  
  if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });

  // Helper block builders
  
  // 1: Vocab table with heavily constructed entries (~20-25 items)
  const generateVocabTableBlocks = () => {
    let items = [];
    for(let i=0; i<30; i++) {
        items.push({
            word: getConceptTerm(concepts[i], t),
            meaning: getConceptTerm(concepts[i], s),
            example: `${getConceptTerm(concepts[i], t)}! — ${getConceptTerm(concepts[i], s)}!`,
            note: getConceptPron(concepts[i], t)
        });
    }
    return [
      {
        id: "b1", type: "image_word", title: "Visual Introduction",
        items: concepts.slice(0, 10).map(c => ({
          emoji: c.emoji, word: getConceptTerm(c, t), meaning: getConceptTerm(c, s), example: getConceptPron(c, t)
        }))
      },
      { id: "b2", type: "vocab_table", title: "Essential Vocabulary", words: items }
    ];
  };

  // 2: Matching
  const generateMatchingBlocks = () => {
    return {
      id: "bm", type: "matching", title: "Match the pairs",
      instruction: `Match the ${tL} word to its ${sL} meaning.`,
      leftItems: concepts.slice(0, 5).map(c => getConceptTerm(c, t)),
      rightItems: concepts.slice(0, 5).map(c => getConceptTerm(c, s)),
      pairs: [[0,0], [1,1], [2,2], [3,3], [4,4]] // Frontend randomizes UI render naturally
    };
  };

  const generateMultipleChoice = (count, startIdx) => {
    let blocks = [];
    for (let i = 0; i < count; i++) {
      let idx = startIdx + i;
      if (idx >= concepts.length) break;
      let target = concepts[idx];
      let wrong1 = concepts[(idx + 1) % concepts.length];
      let wrong2 = concepts[(idx + 2) % concepts.length];
      
      blocks.push({
        id: `bmc_${i}`, type: "multiple_choice",
        question: `Translate: ${getConceptTerm(target, s)}`,
        options: [getConceptTerm(wrong1, t), getConceptTerm(target, t), getConceptTerm(wrong2, t)],
        correctIndex: 1
      });
    }
    return blocks;
  };

  // ACT 1: LESSON
  fs.writeFileSync(path.join(targetDir, 'week-1-lesson.json'), JSON.stringify({
    id: 1, pairId: id, type: "lesson", title: `Lesson 1: Introduction to ${tL}`, xp: 30, tags: ["grammar", "basics"],
    blocks: [
      { id: "b1", type: "text", title: `Welcome to ${tL}`, body: `This is your first step into ${tL}. In this highly intensive course, we will heavily practice the core characters and greetings.` },
      { id: "b2", type: "grammar_rule", title: "Key Structure & Greetings", explanation: `Pay close attention to pronunciation notes. ${getConceptTerm(concepts[0], t)} is widely used.`, examples: [{sentence: getConceptTerm(concepts[0], t), translation: getConceptTerm(concepts[0], s)}] },
      { id: "b3", type: "dialogue", title: "First Conversation", context: "Meeting at the park", lines: [
        { speaker: "A", text: getConceptTerm(concepts[0], t), translation: getConceptTerm(concepts[0], s) },
        { speaker: "B", text: getConceptTerm(concepts[1], t), translation: getConceptTerm(concepts[1], s) },
        { speaker: "A", text: getConceptTerm(concepts[11], t) + "?", translation: getConceptTerm(concepts[11], s) + "?" },
        { speaker: "B", text: getConceptTerm(concepts[7], t), translation: getConceptTerm(concepts[7], s) }
      ]},
      generateMatchingBlocks()
    ]
  }, null, 2));

  // ACT 2: VOCAB (Massive table matching the original)
  fs.writeFileSync(path.join(targetDir, 'week-1-vocab.json'), JSON.stringify({
    id: 2, pairId: id, type: "vocab", title: `Extensive Vocabulary: Essentials`, xp: 20, tags: ["vocabulary", "massive"],
    blocks: generateVocabTableBlocks().concat([generateMatchingBlocks()])
  }, null, 2));

  // ACT 3: READING
  fs.writeFileSync(path.join(targetDir, 'week-1-reading.json'), JSON.stringify({
    id: 3, pairId: id, type: "reading", title: `Reading Comprehension`, xp: 25,
    blocks: [
      { id: "b1", type: "text", title: "Daily Life", body: `${getConceptTerm(concepts[0], t)}. ${getConceptTerm(concepts[10], t)} ${getConceptTerm(concepts[16], t)}. ${getConceptTerm(concepts[4], t)}!` },
      { id: "b2", type: "text", title: "Translation", body: `${getConceptTerm(concepts[0], s)}. ${getConceptTerm(concepts[10], s)} ${getConceptTerm(concepts[16], s)}. ${getConceptTerm(concepts[4], s)}!` },
      ...generateMultipleChoice(3, 0)
    ]
  }, null, 2));

  // ACT 4: PRONUNCIATION
  fs.writeFileSync(path.join(targetDir, 'week-1-pronunciation.json'), JSON.stringify({
    id: 4, pairId: id, type: "pronunciation", title: `Pronunciation Accuracy`, xp: 30,
    blocks: concepts.slice(0, 5).map((c, i) => ({
      id: `bp_${i}`, type: "pronunciation", word: getConceptTerm(c, t), meaning: getConceptTerm(c, s)
    }))
  }, null, 2));

  // ACT 5: WRITING
  fs.writeFileSync(path.join(targetDir, 'week-1-writing.json'), JSON.stringify({
    id: 5, pairId: id, type: "writing", title: `Writing Structure`, xp: 35,
    blocks: [
      { id: "bw1", type: "text", title: "Instruction", body: "Fill in the missing words based on the context." },
      { id: "bw2", type: "fill_blank", sentence: `___, how are you?`, answers: [getConceptTerm(concepts[0], t)], blanks: ["word"] },
      { id: "bw3", type: "fill_blank", sentence: `I have ___ (one) apple.`, answers: [getConceptTerm(concepts[17], t)], blanks: ["word"] }
    ]
  }, null, 2));

  // ACT 6: LISTENING
  fs.writeFileSync(path.join(targetDir, 'week-1-listening.json'), JSON.stringify({
    id: 6, pairId: id, type: "listening", title: `Listening Practice`, xp: 40,
    blocks: [
      { id: "b1", type: "text", title: "Listening Dialogue", body: "A native speaker reads the following..." },
      { id: "b2", type: "dialogue", title: "Audio transcript", lines: [
        { speaker: "Voice", text: getConceptTerm(concepts[22], t), translation: getConceptTerm(concepts[22], s) },
        { speaker: "Voice", text: getConceptTerm(concepts[23], t), translation: getConceptTerm(concepts[23], s) }
      ]},
      ...generateMultipleChoice(2, 22)
    ]
  }, null, 2));

  // ACT 7: TEST
  fs.writeFileSync(path.join(targetDir, 'week-1-test.json'), JSON.stringify({
    id: 7, pairId: id, type: "test", title: `Deep Weekly Challenge`, xp: 50,
    blocks: generateMultipleChoice(10, 10).concat([generateMatchingBlocks()])
  }, null, 2));

  // ACT 8: SPEAKING
  fs.writeFileSync(path.join(targetDir, 'week-1-speaking.json'), JSON.stringify({
    id: 8, pairId: id, type: "speaking", title: `Speaking Scenarios`, xp: 35,
    blocks: concepts.slice(0, 3).map((c, i) => ({
      id: `bs_${i}`, type: "speaking_scenario", title: `Scenario ${i+1}`, scenario: getConceptTerm(c, s), hint: "Speak this", expectedAnswer: getConceptTerm(c, t)
    }))
  }, null, 2));

  // ACT 9: VOCAB REVIEW
  fs.writeFileSync(path.join(targetDir, 'week-1-vocab-review.json'), JSON.stringify({
    id: 9, pairId: id, type: "vocab", title: `Intensive Vocab Review`, xp: 20,
    blocks: [
      { id: "b1", type: "vocab_table", title: "Review Set", words: concepts.slice(15, 30).map(c => ({word: getConceptTerm(c, t), meaning: getConceptTerm(c, s), example: ""})) },
      generateMatchingBlocks()
    ]
  }, null, 2));

  // ACT 10: PRONUNCIATION 2
  fs.writeFileSync(path.join(targetDir, 'week-1-pronunciation-2.json'), JSON.stringify({
    id: 10, pairId: id, type: "pronunciation", title: `Advanced Sounds`, xp: 30,
    blocks: concepts.slice(10, 15).map((c, i) => ({
      id: `bp2_${i}`, type: "pronunciation", word: getConceptTerm(c, t), meaning: getConceptTerm(c, s)
    }))
  }, null, 2));

});

console.log("Massive scaled dataset generation complete.");
