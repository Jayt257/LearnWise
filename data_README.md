# Language Learning App — Content Creation Guide
### Complete README for AI Agents and Developers

---

> **Purpose of this document:** This README is the single source of truth for creating language learning content in JSON format for this application. Any AI agent or developer who reads this document should be able to produce a complete, valid, and high-quality 3-month language course for any language pair without any additional guidance.

---

## Table of Contents

1. [Overview and Philosophy](#1-overview-and-philosophy)
2. [Content Quality Standard](#2-content-quality-standard)
3. [Universal 3-Month Learning Roadmap](#3-universal-3-month-learning-roadmap)
4. [Block Structure Per Month](#4-block-structure-per-month)
5. [Activity Types — Complete Reference](#5-activity-types--complete-reference)
6. [Universal JSON Schema — Common Fields](#6-universal-json-schema--common-fields)
7. [Universal Transliteration Rule — MANDATORY](#7-universal-transliteration-rule--mandatory)
8. [The adminCorrectAnswerSet Field](#8-the-admincorrectanswerset-field)
9. [The audioAssets Field](#9-the-audioassets-field)
10. [Activity-Specific JSON Schemas](#10-activity-specific-json-schemas)
   - [10.1 Lesson](#101-lesson-activity)
   - [10.2 Pronunciation](#102-pronunciation-activity)
   - [10.3 Reading](#103-reading-activity)
   - [10.4 Writing](#104-writing-activity)
   - [10.5 Listening](#105-listening-activity)
   - [10.6 Vocabulary](#106-vocabulary-activity)
   - [10.7 Speaking](#107-speaking-activity)
   - [10.8 Test](#108-test-activity)
11. [Evaluation Pipeline Logic](#11-evaluation-pipeline-logic)
12. [JSON Data Separation Rules](#12-json-data-separation-rules)
13. [File and Folder Naming Convention](#13-file-and-folder-naming-convention)
14. [Full JSON Example — One Activity](#14-full-json-example--one-activity)
15. [Validation Checklist Before Submission](#15-validation-checklist-before-submission)

---

## 1. Overview and Philosophy

This application teaches any target language to learners who speak any base language. The content is delivered through structured JSON data files. Every piece of content — lessons, audio, evaluations, scores, and feedback — is defined in these files.

The 3-month curriculum follows this universal pattern:

| Month | Theme | Learner Goal |
|-------|-------|--------------|
| Month 1 | Understand the language | Get comfortable with sound, script, and survival words |
| Month 2 | Use the language | Form sentences and communicate in simple daily situations |
| Month 3 | Apply the language | Have short real-world conversations with confidence |

### Key Terms Used in This Document

- **baseLanguage** — The language the learner already speaks (e.g., `en` for English)
- **targetLanguage** — The language the learner wants to learn (e.g., `ja` for Japanese)
- **Block** — A themed group of 8 activities inside one month
- **Activity** — A single learning unit of one specific type (lesson, vocabulary, etc.)
- **adminCorrectAnswerSet** — The baseline answer stored by the content creator, used by the evaluation engine for scoring
- **audioAssets** — All audio-related fields for a given activity

---

## 2. Content Quality Standard

### Minimum Time Requirement — MANDATORY

> ⚠️ **Every single activity must contain at least 30 minutes of genuine learning content.**
>
> Activities with less than 30 minutes of content **will not be accepted** and must be rewritten.

"30 minutes of content" means the learner must be actively engaged — reading, listening, practicing, writing, speaking, or reviewing — for a minimum of 30 continuous minutes within that single activity. This is not optional. Thin, short, or minimal activities are rejected.

### What "30 Minutes" Looks Like Per Activity Type

| Activity Type | What 30+ Minutes Requires |
|---------------|--------------------------|
| Lesson | Detailed concept explanation, multiple examples, grammar breakdown, cultural context, at least 5–8 sub-sections of real content |
| Pronunciation | Multiple target words or phrases, phonetic breakdown for each, slow and normal audio, practice drills, error examples |
| Reading | A passage of at least 300–600 words in the target language, glossary, comprehension questions, base language support |
| Writing | A meaningful prompt, detailed rubric, word bank, multiple example outputs, guided sub-tasks |
| Listening | Audio of 3–5 minutes minimum, multiple questions, transcript, replay support, context setup |
| Vocabulary | At least 15–20 words/phrases with meanings, examples, audio, and a quiz section |
| Speaking | A detailed scenario, multiple speaking prompts, sample responses, feedback rubric, role context |
| Test | Covers all 8 skill areas, minimum 20–30 questions across sections, weighted scoring |

---

## 3. Universal 3-Month Learning Roadmap

### Month 1 — Understand the Language

**Goal:** Make the learner comfortable with the new language and remove the fear of it.

By the end of Month 1, the learner will:
- Understand the sound system and rhythm of the language
- Recognize the writing system or script (if different from base language)
- Know the most basic words, greetings, and numbers
- Understand beginner-level culture and social etiquette
- Feel ready to attempt simple communication in Month 2

### Month 2 — Use the Language

**Goal:** Help the learner communicate in simple daily situations.

By the end of Month 2, the learner will:
- Form short, correct sentences in the target language
- Ask and answer basic questions
- Improve listening comprehension of slow, clear speech
- Read short practical texts
- Expand vocabulary across daily life topics
- Practice writing and speaking in guided, supported ways

### Month 3 — Apply the Language

**Goal:** Make the learner ready for simple real-world communication.

By the end of Month 3, the learner will:
- Hold short conversations on familiar topics
- Handle common daily and travel situations
- Read short practical texts without heavy support
- Write short responses and messages
- Use polite and culturally appropriate expressions
- Complete a final review and full assessment

---

## 4. Block Structure Per Month

Each month is divided into **6 Blocks**. Each block contains **8 Activities** — one of each type. This gives **48 activities per month** and **144 activities for the full 3-month course**.

### Month 1 — Block Themes

| Block | Number | Theme | Goal |
|-------|--------|-------|------|
| Block 1 | M1B1 | Orientation | Introduce the language and the learning journey |
| Block 2 | M1B2 | Sounds and Script | Teach pronunciation basics and writing system familiarity |
| Block 3 | M1B3 | Core Survival Words | Teach greetings, identity, numbers, and very common words |
| Block 4 | M1B4 | First Communication | Teach self-introduction and simple polite expressions |
| Block 5 | M1B5 | Culture Basics | Teach simple customs, manners, and social behavior |
| Block 6 | M1B6 | Review and Confidence Check | Check understanding and prepare for Month 2 |

### Month 2 — Block Themes

| Block | Number | Theme | Goal |
|-------|--------|-------|------|
| Block 1 | M2B1 | Sentence Building | Teach how basic sentence patterns work |
| Block 2 | M2B2 | Daily Vocabulary | Teach words for routine life, food, places, people, and time |
| Block 3 | M2B3 | Listening Practice | Improve understanding of slow, clear spoken language |
| Block 4 | M2B4 | Reading Practice | Teach the learner to read short practical text |
| Block 5 | M2B5 | Speaking Practice | Help the learner speak in short real-life situations |
| Block 6 | M2B6 | Culture in Context | Teach culture through real examples and daily situations |

### Month 3 — Block Themes

| Block | Number | Theme | Goal |
|-------|--------|-------|------|
| Block 1 | M3B1 | Travel and Survival Language | Language for transport, food, shopping, and asking for help |
| Block 2 | M3B2 | Polite Communication | Respectful and socially correct expressions |
| Block 3 | M3B3 | Real-Life Scenarios | Practice through roleplay and guided tasks |
| Block 4 | M3B4 | Mixed Skill Practice | Combine reading, writing, listening, speaking, and vocabulary |
| Block 5 | M3B5 | Review and Correction | Fix weak areas and strengthen important knowledge |
| Block 6 | M3B6 | Final Test | Measure overall progress and readiness for the next level |

---

## 5. Activity Types — Complete Reference

Each block contains exactly **8 activities** — one per type. Below is the purpose of each type.

| # | Activity Type | Core Purpose |
|---|---------------|-------------|
| 1 | **Lesson** | Teach the main concept, grammar rule, or cultural point through structured explanation |
| 2 | **Pronunciation** | Correct audio, phonetic guidance, user speech check, score, and improvement tips |
| 3 | **Reading** | A reading passage with native-language support, glossary, and comprehension questions |
| 4 | **Writing** | A writing prompt with hints, rubric, and scoring based on correctness and clarity |
| 5 | **Listening** | An audio clip with transcript, questions, and answer evaluation |
| 6 | **Vocabulary** | Word groups with meanings, usage examples, audio support, and quizzes |
| 7 | **Speaking** | A scenario-based speaking task with time limit, transcript support, and scoring |
| 8 | **Test** | End-of-block or end-of-month evaluation covering all skill areas |

---

## 6. Universal JSON Schema — Common Fields

Every activity, regardless of type, **must contain all of the following fields**. Optional fields should be present with `null` or empty values rather than omitted entirely.

```json
{
  "activityId": "string — unique identifier, format: {targetLang}_{baseLang}_M{month}B{block}_{activityType}_{sequence}",
  "monthNumber": "integer — 1, 2, or 3",
  "blockNumber": "integer — 1 through 6",
  "activityType": "string — one of: lesson | pronunciation | reading | writing | listening | vocabulary | speaking | test",
  "title": "string — human-readable title of this activity",
  "learningGoal": "string — one clear sentence describing what the learner will be able to do after this activity",
  "difficultyLevel": "string — one of: beginner | elementary | pre-intermediate",
  "baseLanguage": "string — ISO 639-1 code, e.g. en, hi, ar",
  "targetLanguage": "string — ISO 639-1 code, e.g. ja, fr, de",
  "estimatedTime": "integer — estimated minutes to complete. Must be 30 or higher",
  "prerequisites": ["array of activityId strings that should be completed before this one"],
  "instructions": "string — full instructions shown to the learner before they begin. Be specific and detailed.",
  "contentItems": ["array — the main content blocks of this activity. Structure depends on activityType. See Section 9."],
  "adminCorrectAnswerSet": {},
  "evaluationMode": "string — one of: exact_match | keyword_match | rubric | groq_comparison | manual",
  "scoreThreshold": "integer — minimum score (0–100) required to pass this activity",
  "feedbackRules": {
    "onPass": "string — feedback message shown when learner passes",
    "onFail": "string — feedback message shown when learner fails",
    "onPartial": "string — feedback message shown for partial scores"
  },
  "audioAssets": {},
  "tags": ["array of topic or skill tags, e.g. greetings, numbers, script, pronunciation"],
  "status": "string — one of: draft | review | published",
  "createdAt": "string — ISO 8601 date, e.g. 2025-01-15T00:00:00Z",
  "version": "string — e.g. 1.0.0",

  "thumbnail": "string or null — URL or file path to thumbnail image",
  "imageAssets": [],
  "videoAssets": [],
  "hintText": "string or null — optional hint shown to the learner if they struggle",
  "commonMistakes": ["array of strings — common errors learners make in this topic"],
  "reviewLinks": [],
  "nextActivityIds": ["array of activityId strings for suggested next activities"],
  "attemptLimit": "integer or null — max number of attempts allowed. null means unlimited",
  "metadata": {}
}
```

### Field Rules

- `activityId` must be **globally unique** across the entire dataset
- `estimatedTime` must be **30 or higher** — no exceptions
- `status` should be `"published"` only after all fields are complete and reviewed
- `adminCorrectAnswerSet` and `audioAssets` are **required in every activity** — never omit or leave as `null` at the top level. Use an empty object `{}` if not applicable.

---

## 7. Universal Transliteration Rule — MANDATORY

> ⚠️ **This rule applies to every activity except Test. In Test activities, these fields go inside a `questionHints` block — see Section 10.8.**

### The Rule

Wherever **any target language text** appears in a JSON file, it must **always** be accompanied by all three of the following fields together. You must never write target language text alone.

| Field | Purpose | Example (Japanese) |
|-------|---------|-------------------|
| `targetText` | The word or sentence in native script | `おはようございます` |
| `transliteration` | Romanized or phonetic pronunciation guide using base language sounds | `Ohayou gozaimasu` |
| `baseTranslation` | The meaning in the learner's base language | `Good morning (formal)` |

These three fields are a **single inseparable unit**. If you write one, you must write all three. Missing even one field is a content error and will be rejected.

### The Standard Target Language Text Object

Whenever target language text is required in any field of any activity, always use this structure:

```json
{
  "targetText": "string — the word, phrase, or sentence in the target language native script",
  "transliteration": "string — phonetic reading using base language alphabet or sounds",
  "baseTranslation": "string — meaning or translation in the learner's base language"
}
```

### Where This Rule Applies — Complete List

The three-field rule applies in every one of the following locations:

| Activity | Where Target Language Text Appears |
|----------|------------------------------------|
| Lesson | `lessonContent` examples, `importantRules` examples, `cultureContext` quotes, `summary` inline words, `checkpointQuestions` |
| Pronunciation | All `targetPhrasesOrWords` items |
| Reading | `glossary` terms, `baseLanguageSupportText` sentence pairs, `comprehensionQuestions` that quote the text |
| Writing | `wordBank` entries, `modelExampleOutputs`, `referenceHints` that include target text |
| Listening | `audioTranscript` sentence pairs, question text that quotes target language |
| Vocabulary | All `wordList` entries, all `exampleSentences` |
| Speaking | `scenario` inline quotes, `subTasks` prompts and sample responses, `baselineTranscript` sentences |
| **Test** | ❌ Not inline — goes inside `questionHints` object only (see Section 10.8) |

### Special Rule for Test Activity

In Test activities, target language text appears inside questions for the learner to answer. The three fields must **not** be shown inline with the question (that would give away the answer). Instead, every question in a test that contains target language text must have a `questionHints` object:

```json
{
  "questionId": "q001",
  "questionText": "What does こんにちは mean?",
  "questionType": "multiple_choice",
  "options": ["Good morning", "Good night", "Hello / Good afternoon", "Thank you"],
  "questionHints": {
    "targetText": "こんにちは",
    "transliteration": "Konnichiwa",
    "baseTranslation": "Hello / Good afternoon"
  },
  "marks": 2,
  "correctAnswerRef": "adminCorrectAnswerSet.answerKey.q001"
}
```

The `questionHints` field is visible to the learner only **after** they have attempted the question — it is a support tool, not a giveaway. For questions that do not contain any target language text, `questionHints` can be `null`.

### Quick Reference — Wrong vs Correct

```json
// ❌ WRONG — target language text written alone
{
  "term": "おはようございます",
  "definition": "Good morning"
}

// ✅ CORRECT — all three fields present together
{
  "targetText": "おはようございます",
  "transliteration": "Ohayou gozaimasu",
  "baseTranslation": "Good morning (formal)"
}
```

```json
// ❌ WRONG — example sentence without transliteration
{
  "sentence": "おはようございます、田中さん。",
  "translation": "Good morning, Mr. Tanaka."
}

// ✅ CORRECT — all three fields present
{
  "targetText": "おはようございます、田中さん。",
  "transliteration": "Ohayou gozaimasu, Tanaka-san.",
  "baseTranslation": "Good morning, Mr. Tanaka."
}
```

---

## 8. The adminCorrectAnswerSet Field

This field stores the **baseline evaluation data** used by the scoring engine to compare against the learner's response. It is the most important field for automated grading.

### Universal Sub-fields

The following sub-fields may be used inside `adminCorrectAnswerSet` depending on the activity type:

```json
"adminCorrectAnswerSet": {
  "expectedText": "string — the exact or model correct answer",
  "acceptedVariants": ["array of strings — other valid answers that should be accepted"],
  "keywordsRequired": ["array — keywords that MUST appear in the answer to score correctly"],
  "keywordsOptional": ["array — keywords that improve the score if present but are not required"],
  "allowedParaphrases": ["array — semantically equivalent rephrasing that should be accepted"],
  "strictnessLevel": "string — one of: strict | moderate | lenient",
  "rubric": {
    "criteria": [
      {
        "name": "string — criterion name, e.g. Accuracy",
        "weight": "integer — percentage weight, all weights must sum to 100",
        "description": "string — what this criterion evaluates"
      }
    ]
  },
  "modelHints": ["array — hints passed to the Groq evaluation engine for better comparison"],
  "scoringWeight": "integer — percentage weight this answer set carries in the total score",
  "languageOfAnswer": "string — ISO 639-1 code of the expected answer language",
  "translationMapping": {},
  "transliterationMapping": {}
}
```

### How adminCorrectAnswerSet Behaves Per Activity Type

| Activity | What to Put in adminCorrectAnswerSet |
|----------|--------------------------------------|
| Lesson | Key takeaways, checkpoint answers, concept summary, expected understanding points |
| Pronunciation | Correct pronunciation transcript, syllable split, phonetic approximation, accepted variants |
| Reading | Correct answers to comprehension questions, acceptable paraphrases, keyword scoring rules |
| Writing | Sample answer, required keywords, grammar baseline, length expectation, scoring rubric |
| Listening | Correct answer keys, accepted short and long answers, scoring keywords, partial credit rules |
| Vocabulary | Correct meanings, accepted translations, MCQ answer key, matching key |
| Speaking | Expected speaking points, required keywords, acceptable paraphrases, rubric, sample answer |
| Test | Full answer key per question, section-wise rubric, partial credit rules, section pass marks |

---

## 9. The audioAssets Field

Audio support is **mandatory** in every activity. Even when an activity does not heavily use audio, the `audioAssets` field must exist with all applicable sub-fields. Leave unused sub-fields as `null`.

```json
"audioAssets": {
  "promptAudio": "string or null — URL/path to the audio version of the main prompt or question",
  "nativeAudio": "string or null — URL/path to a native speaker recording of the target content",
  "referenceAudio": "string or null — URL/path to a reference sample the learner should compare to",
  "instructionAudio": "string or null — URL/path to an audio version of the activity instructions",
  "sampleAudio": "string or null — URL/path to an example audio clip for the activity",
  "slowAudio": "string or null — URL/path to a slowed-down version for learner clarity",
  "normalAudio": "string or null — URL/path to the normal-speed audio version",
  "audioTranscript": "string or null — full text transcript of the main audio",
  "audioLanguage": "string or null — ISO 639-1 code of the audio language",
  "audioDuration": "integer or null — duration in seconds",
  "audioRepeatAllowed": "boolean — true if the learner is allowed to replay the audio"
}
```

### Audio Use by Activity Type

| Activity | Primary Audio Use |
|----------|------------------|
| Lesson | Short explanation audio, example sentence audio, cultural note audio |
| Pronunciation | Native pronunciation, slow version, repeatable sample, user recording support |
| Reading | Read-aloud audio, sentence-by-sentence audio, slow reading version |
| Writing | Prompt audio, instruction audio, optional hint audio |
| Listening | Main scenario audio, replay audio, slow playback, separated question audio |
| Vocabulary | Word audio, example sentence audio, pronunciation support audio |
| Speaking | Prompt audio, scenario audio, sample response audio, hint audio |
| Test | Test instructions audio, listening section audio, speaking prompt audio, review audio |

---

## 10. Activity-Specific JSON Schemas

Each activity type extends the common schema (Section 6) with its own specific fields. The fields listed below go **inside** the common schema alongside the universal fields.

---

### 10.1 Lesson Activity

**Purpose:** Teach a concept, grammar rule, cultural point, or language structure.

**Content depth requirement:** A lesson must have at least 5–8 sub-sections with real explanations, not just one or two sentences per section.

```json
{
  "conceptTitle": "string — short title of the concept being taught",
  "lessonContent": [
    {
      "sectionId": "string",
      "sectionTitle": "string — e.g. What is this concept?",
      "bodyText": "string — detailed explanation in baseLanguage for learner understanding",
      "targetLanguageExamples": [
        {
          "targetText": "string — example in target language native script",
          "transliteration": "string — phonetic reading using base language sounds",
          "baseTranslation": "string — meaning in base language",
          "audioRef": "string or null — reference to audioAssets key"
        }
      ]
    }
  ],
  "learningObjective": "string — specific, measurable objective for this lesson",
  "examples": [
    {
      "targetText": "string — example sentence in target language native script",
      "transliteration": "string — phonetic reading of the example sentence",
      "baseTranslation": "string — base language translation of the example",
      "explanation": "string — why this example is relevant to the concept"
    }
  ],
  "importantRules": [
    {
      "ruleNumber": "integer",
      "ruleText": "string — a clear grammar or usage rule",
      "exceptionNotes": "string or null — any exceptions to this rule"
    }
  ],
  "cultureContext": {
    "isApplicable": "boolean",
    "contextText": "string or null — cultural background relevant to this lesson",
    "dosList": ["array of culturally appropriate behaviors"],
    "dontsList": ["array of culturally inappropriate behaviors to avoid"]
  },
  "summary": "string — a paragraph summarizing the key points of this lesson",
  "checkpointQuestions": [
    {
      "questionId": "string",
      "questionText": "string — a comprehension check question",
      "expectedAnswer": "string — stored in adminCorrectAnswerSet as well"
    }
  ],
  "adminCorrectAnswerSet": {
    "keyTakeaways": ["array of must-know points from this lesson"],
    "conceptSummary": "string — the core idea in one or two sentences",
    "importantFacts": ["array of critical facts the learner must retain"],
    "checkpointAnswers": {},
    "expectedUnderstanding": "string — what the learner should be able to explain after this lesson"
  }
}
```

---

### 10.2 Pronunciation Activity

**Purpose:** Teach correct pronunciation with audio support, phonetic guidance, and user speech evaluation.

**Content depth requirement:** Must cover at least 8–12 target words or phrases with full phonetic breakdowns, native audio, and practice drills for each.

```json
{
  "targetPhrasesOrWords": [
    {
      "itemId": "string",
      "targetText": "string — the word or phrase in target language native script",
      "transliteration": "string — phonetic reading using base language sounds",
      "baseTranslation": "string — meaning in the learner's base language",
      "phoneticHint": "string — additional phonetic approximation using base language letter sounds",
      "syllableSplit": "string — e.g. ko-n-ni-chi-wa",
      "nativeAudioRef": "string — reference to audioAssets.nativeAudio",
      "slowAudioRef": "string — reference to audioAssets.slowAudio",
      "commonMispronunciation": "string or null — how learners typically mispronounce this"
    }
  ],
  "userInputMode": "string — one of: speech | text | both",
  "sttTranscript": "string or null — populated at runtime with learner's speech-to-text result",
  "expectedPronunciationText": "string — the exact text that correct pronunciation should produce",
  "scoreThreshold": "integer — minimum score to pass this pronunciation activity",
  "feedbackRules": {
    "onPass": "string",
    "onFail": "string",
    "onPartial": "string"
  },
  "adminCorrectAnswerSet": {
    "exactCorrectTranscript": "string — the exact expected STT output",
    "acceptedVariants": ["array — acceptable alternate transcriptions"],
    "syllableSplitReference": "string",
    "phoneticApproximation": "string",
    "nativeScriptReference": "string or null",
    "transliteration": "string or null",
    "strictnessLevel": "string — strict | moderate | lenient"
  }
}
```

---

### 10.3 Reading Activity

**Purpose:** Present a reading passage in the target language with comprehension questions and base language support.

**Content depth requirement:** Reading passage must be at least 300–600 words. Must include a full glossary and minimum 6–10 comprehension questions.

```json
{
  "readingTitle": "string — title of the reading passage",
  "readingText": "string — full passage in target language",
  "textInTargetLanguage": "string — same as readingText, kept for schema clarity",
  "baseLanguageSupportText": "string or null — a translation or paraphrase in base language for support",
  "glossary": [
    {
      "targetText": "string — word or phrase in target language native script",
      "transliteration": "string — phonetic reading",
      "baseTranslation": "string — meaning in base language",
      "exampleSentence": {
        "targetText": "string or null — usage example in target language",
        "transliteration": "string or null",
        "baseTranslation": "string or null"
      },
      "audioRef": "string or null"
    }
  ],
  "sentenceSupportPairs": [
    {
      "targetText": "string — one sentence from the reading passage in target language",
      "transliteration": "string — phonetic reading of that sentence",
      "baseTranslation": "string — translation of that sentence in base language"
    }
  ],
  "comprehensionQuestions": [
    {
      "questionId": "string",
      "questionText": "string — the reading comprehension question",
      "questionType": "string — one of: multiple_choice | short_answer | true_false | fill_blank",
      "options": ["array — options for multiple_choice type, null for others"],
      "correctAnswerRef": "string — reference key to adminCorrectAnswerSet"
    }
  ],
  "readAloudMode": "boolean — whether the learner is expected to read aloud",
  "adminCorrectAnswerSet": {
    "correctAnswers": {},
    "acceptableParaphrases": {},
    "keywordScoringRules": {},
    "expectedSummaryPoints": ["array — main points a correct summary must include"]
  }
}
```

---

### 10.4 Writing Activity

**Purpose:** Prompt the learner to produce written output in the target language and evaluate it against a baseline.

**Content depth requirement:** The prompt must be rich enough to produce at least 80–150 words. Must include a detailed rubric, word bank, and at least 2–3 model example outputs.

```json
{
  "writingPrompt": "string — the full writing prompt shown to the learner",
  "promptGoal": "string — what the learner should be trying to express in their writing",
  "expectedWritingType": "string — one of: sentence | paragraph | short_essay | dialogue | description | message",
  "wordBank": [
    {
      "targetText": "string — word in target language native script",
      "transliteration": "string — phonetic reading",
      "baseTranslation": "string — meaning in base language",
      "partOfSpeech": "string — noun | verb | adjective | etc."
    }
  ],
  "referenceHints": ["array of strings — grammatical or structural hints to guide the learner"],
  "modelExampleOutputs": [
    {
      "targetText": "string — a complete model answer in target language native script",
      "transliteration": "string — phonetic reading of the full model answer",
      "baseTranslation": "string — full translation of the model answer in base language",
      "qualityLevel": "string — excellent | good | acceptable",
      "annotation": "string — explanation of what makes this a good or acceptable answer"
    }
  ],
  "evaluationCriteria": [
    {
      "criterion": "string — e.g. Grammar Accuracy",
      "weight": "integer — percentage, all weights must sum to 100",
      "description": "string — what is being evaluated"
    }
  ],
  "minimumWordCount": "integer — minimum words required in the learner's submission",
  "maximumWordCount": "integer or null — maximum words allowed",
  "adminCorrectAnswerSet": {
    "sampleAnswer": "string — a model answer",
    "acceptableAlternates": ["array — other valid answers"],
    "requiredKeywords": ["array — words that must appear"],
    "grammarBaseline": "string — grammar structures that should be used",
    "lengthExpectation": "string — e.g. 80 to 120 words",
    "scoringRubric": {}
  }
}
```

---

### 10.5 Listening Activity

**Purpose:** Play an audio clip and evaluate the learner's comprehension through questions.

**Content depth requirement:** The audio must be at least 3–5 minutes. Must have 8–12 questions covering different comprehension levels (literal, inferential, vocabulary).

```json
{
  "listeningGoal": "string — what the learner is expected to extract from the audio",
  "audioScenario": "string — description of who is speaking and in what context",
  "audioTranscriptSentences": [
    {
      "targetText": "string — one sentence from the audio in target language native script",
      "transliteration": "string — phonetic reading of that sentence",
      "baseTranslation": "string — translation of that sentence in base language"
    }
  ],
  "audioTranscriptFull": "string — full audio transcript as plain text in target language (for STT comparison)",
  "questionSet": [
    {
      "questionId": "string",
      "questionText": "string",
      "questionType": "string — multiple_choice | short_answer | true_false | fill_blank",
      "options": ["array or null"],
      "audioTimestamp": "string or null — timestamp in audio where answer is found, e.g. 01:24",
      "correctAnswerRef": "string — key reference to adminCorrectAnswerSet.correctAnswers"
    }
  ],
  "replayAllowed": "boolean",
  "slowPlaybackAllowed": "boolean",
  "scoringRules": {
    "pointsPerQuestion": "integer",
    "partialCreditAllowed": "boolean",
    "partialCreditRules": "string or null"
  },
  "adminCorrectAnswerSet": {
    "correctAnswers": {},
    "acceptedShortAnswers": {},
    "acceptedLongAnswers": {},
    "scoringKeywords": {},
    "partialCreditRules": {}
  }
}
```

---

### 10.6 Vocabulary Activity

**Purpose:** Teach a themed set of words with meanings, examples, audio, and quiz-based reinforcement.

**Content depth requirement:** Must contain at least 15–20 vocabulary items with full entries. Must include a quiz section with at least 10 questions.

```json
{
  "vocabTheme": "string — the theme of this vocabulary set, e.g. Food and Drink, Directions, Numbers",
  "wordList": [
    {
      "wordId": "string",
      "targetText": "string — word in target language native script",
      "transliteration": "string — phonetic reading using base language sounds",
      "baseTranslation": "string — meaning in the learner's base language",
      "partOfSpeech": "string",
      "formalityLevel": "string — formal | informal | neutral",
      "audioRef": "string or null — reference to audioAssets"
    }
  ],
  "meaningList": ["array of base-language meanings matching wordList order"],
  "exampleSentences": [
    {
      "wordId": "string — reference to wordList",
      "targetText": "string — usage sentence in target language native script",
      "transliteration": "string — phonetic reading of the full sentence",
      "baseTranslation": "string — translation of the sentence in base language"
    }
  ],
  "quizType": "string — one of: multiple_choice | matching | fill_blank | flashcard | mixed",
  "quizQuestions": [
    {
      "questionId": "string",
      "questionText": "string",
      "questionType": "string",
      "options": ["array or null"],
      "correctAnswerRef": "string"
    }
  ],
  "adminCorrectAnswerSet": {
    "correctMeanings": {},
    "acceptedTranslations": {},
    "matchingKey": {},
    "mcqAnswerKey": {},
    "pronunciationReference": {}
  }
}
```

---

### 10.7 Speaking Activity

**Purpose:** Give the learner a scenario to respond to verbally, evaluate spoken output against a rubric.

**Content depth requirement:** Must include a detailed scenario, at least 3–5 speaking sub-tasks or prompts, a full sample response, and a complete scoring rubric.

```json
{
  "speakingPrompt": "string — the main speaking task instruction given to the learner",
  "scenario": "string — full description of the context and situation for the speaking task",
  "role": "string — the role the learner is playing, e.g. tourist, customer, student",
  "conversationPartner": "string or null — description of who the learner is speaking to",
  "subTasks": [
    {
      "subTaskId": "string",
      "prompt": "string — specific speaking sub-prompt in base language",
      "expectedSpeakingPoints": ["array — key points expected in the response, written in base language"],
      "sampleResponse": {
        "targetText": "string — a model response in target language native script",
        "transliteration": "string — phonetic reading of the full sample response",
        "baseTranslation": "string — full translation of the sample response in base language"
      }
    }
  ],
  "scenarioContext": {
    "targetText": "string — scenario description or opening line in target language native script",
    "transliteration": "string — phonetic reading of the scenario text",
    "baseTranslation": "string — base language translation of the scenario"
  },
  "baselineTranscriptSentences": [
    {
      "targetText": "string — one sentence of the model spoken response in target language",
      "transliteration": "string — phonetic reading",
      "baseTranslation": "string — translation in base language"
    }
  ],
  "scoringRules": {
    "fluencyWeight": "integer",
    "contentWeight": "integer",
    "grammarWeight": "integer",
    "vocabularyWeight": "integer"
  },
  "adminCorrectAnswerSet": {
    "expectedSpeakingPoints": ["array — required content points"],
    "requiredKeywords": ["array — words or phrases that should appear"],
    "acceptableParaphrases": ["array — acceptable rewordings of key points"],
    "scoringRubric": {},
    "sampleAnswer": "string — full model spoken response",
    "minimumContentCoverage": "integer — percentage of expected points that must be covered to pass"
  }
}
```

---

### 10.8 Test Activity

**Purpose:** Evaluate the learner's cumulative knowledge of all 8 skill areas for the block or month.

**Content depth requirement:** Must include at least 20–30 questions across all skill sections. Must have distinct sections for each skill type being tested. Each section must have weighted scoring.

```json
{
  "testTitle": "string — title of the test",
  "testScope": "string — one of: block_test | month_test | final_test",
  "coveredActivityTypes": ["array — which activity types are covered, e.g. lesson, vocabulary, listening"],
  "testInstructions": "string — full instructions for the learner before starting",
  "questionSections": [
    {
      "sectionId": "string",
      "sectionTitle": "string — e.g. Listening Comprehension",
      "activityTypeRef": "string — which activity type this section tests",
      "questions": [
        {
          "questionId": "string",
          "questionText": "string — the question shown to the learner. May contain target language text.",
          "questionType": "string — multiple_choice | short_answer | true_false | fill_blank | speaking | writing",
          "options": ["array or null"],
          "marks": "integer — marks for this question",
          "audioRef": "string or null",
          "questionHints": {
            "targetText": "string or null — target language word or phrase this question is about, in native script",
            "transliteration": "string or null — phonetic reading of the target text",
            "baseTranslation": "string or null — meaning in base language. Set all three to null if the question contains no target language text."
          },
          "correctAnswerRef": "string"
        }
      ],
      "sectionMarks": "integer — total marks for this section",
      "sectionPassMarks": "integer — minimum marks to pass this section"
    }
  ],
  "scoreWeights": {
    "lesson": "integer — percentage weight",
    "pronunciation": "integer",
    "reading": "integer",
    "writing": "integer",
    "listening": "integer",
    "vocabulary": "integer",
    "speaking": "integer"
  },
  "totalMarks": "integer — sum of all section marks",
  "passMarks": "integer — overall minimum marks to pass the test",
  "userResponses": {},
  "finalScore": "integer or null — populated after submission",
  "sectionScores": {},
  "resultSummary": "string or null — populated after submission",
  "adminCorrectAnswerSet": {
    "answerKey": {},
    "scoringRubric": {},
    "partialCreditRules": {},
    "alternateValidAnswers": {},
    "sectionPassMarks": {}
  }
}
```

---

## 11. Evaluation Pipeline Logic

When a learner submits an answer, the system uses the following fields to evaluate and score:

```
Input Fields Used for Evaluation:
  - userAnswer (submitted by learner at runtime)
  - adminCorrectAnswerSet (from the JSON activity file)
  - activityType (determines which evaluation mode to use)
  - baseLanguage + targetLanguage (for multilingual comparison)
  - audioTranscript (if applicable)
  - scoringRules
  - feedbackRules

Output Fields Populated After Evaluation:
  - finalScore
  - sectionScores (for tests)
  - resultSummary
  - feedbackMessage (from feedbackRules)
  - passOrFail status
  - retryAllowed (based on attemptLimit)
```

### Evaluation Modes

| Mode | When to Use |
|------|-------------|
| `exact_match` | When the answer must match exactly — vocabulary quizzes, MCQ |
| `keyword_match` | When specific keywords must appear — listening answers, fill-in-the-blank |
| `rubric` | When scoring is based on multiple criteria — writing, speaking |
| `groq_comparison` | When semantic comparison is needed — free writing, open speaking, paraphrase detection |
| `manual` | When human review is required — advanced open-ended tasks |

---

## 12. JSON Data Separation Rules

Every activity JSON must clearly separate its data into four sections. This separation is enforced by field grouping and is essential for the evaluation engine to function correctly.

### Section 1 — Teaching Data (What the learner sees)
Fields: `contentItems`, `lessonContent`, `readingText`, `wordList`, `speakingPrompt`, `audioAssets`, `instructions`, `glossary`, `examples`

### Section 2 — Admin Baseline Data (What the system uses for evaluation)
Fields: `adminCorrectAnswerSet`, `evaluationMode`, `scoreThreshold`, `feedbackRules`, `scoringRules`, `evaluationCriteria`

### Section 3 — User Response Data (Populated at runtime — leave empty in source files)
Fields: `userAnswer`, `userResponses`, `sttTranscript`, `userSpeechInput`, `finalScore`, `sectionScores`

### Section 4 — Result Data (Populated after evaluation — leave empty in source files)
Fields: `resultSummary`, `passOrFail`, `retryStatus`, `feedbackMessage`

> **Rule:** Source JSON files should have Section 3 and Section 4 fields set to `null` or `{}`. They are populated by the application at runtime and never hardcoded by content creators.

---

## 13. File and Folder Naming Convention

Organize all JSON files using the following structure:

```
/content/
  /{targetLanguage}_{baseLanguage}/
    /month_1/
      /block_1/
        lesson.json
        pronunciation.json
        reading.json
        writing.json
        listening.json
        vocabulary.json
        speaking.json
        test.json
      /block_2/
        ...
      /block_3/
        ...
      /block_4/
        ...
      /block_5/
        ...
      /block_6/
        ...
    /month_2/
      ...
    /month_3/
      ...
```

### Activity ID Format

```
{targetLang}_{baseLang}_M{month}B{block}_{activityType}_{sequenceNumber}

Examples:
  ja_en_M1B1_lesson_001
  ja_en_M1B1_pronunciation_002
  fr_hi_M2B3_listening_001
  de_en_M3B6_test_001
```

---

## 14. Full JSON Example — One Activity Per Type

Below are two complete examples demonstrating the 3-field transliteration rule in practice — one standard activity and one Test activity showing `questionHints`.

---

### Example A — Vocabulary Activity (Standard 3-field pattern everywhere)

Japanese course · Month 1 · Block 3

```json
{
  "activityId": "ja_en_M1B3_vocabulary_001",
  "monthNumber": 1,
  "blockNumber": 3,
  "activityType": "vocabulary",
  "title": "Core Survival Words — Greetings and Everyday Essentials",
  "learningGoal": "The learner will be able to recognize, pronounce, and use at least 15 essential Japanese greeting and survival words in the correct context.",
  "difficultyLevel": "beginner",
  "baseLanguage": "en",
  "targetLanguage": "ja",
  "estimatedTime": 35,
  "prerequisites": ["ja_en_M1B2_pronunciation_001"],
  "instructions": "In this activity, you will learn 18 essential Japanese words and phrases used every day. Read each word carefully, listen to the native audio, and practice the pronunciation. Then complete the quiz section to test your memory.",
  "contentItems": [
    {
      "type": "introduction",
      "text": "Japanese greetings depend on the time of day and the level of formality. This set covers the most essential survival words you will use from day one."
    }
  ],
  "vocabTheme": "Greetings, Politeness, and Basic Survival Words",
  "wordList": [
    {
      "wordId": "w001",
      "targetText": "おはようございます",
      "transliteration": "Ohayou gozaimasu",
      "baseTranslation": "Good morning (formal)",
      "partOfSpeech": "greeting",
      "formalityLevel": "formal",
      "audioRef": "audioAssets.nativeAudio"
    },
    {
      "wordId": "w002",
      "targetText": "こんにちは",
      "transliteration": "Konnichiwa",
      "baseTranslation": "Hello / Good afternoon",
      "partOfSpeech": "greeting",
      "formalityLevel": "neutral",
      "audioRef": "audioAssets.nativeAudio"
    },
    {
      "wordId": "w003",
      "targetText": "こんばんは",
      "transliteration": "Konbanwa",
      "baseTranslation": "Good evening",
      "partOfSpeech": "greeting",
      "formalityLevel": "neutral",
      "audioRef": "audioAssets.nativeAudio"
    },
    {
      "wordId": "w004",
      "targetText": "ありがとうございます",
      "transliteration": "Arigatou gozaimasu",
      "baseTranslation": "Thank you very much (formal)",
      "partOfSpeech": "expression",
      "formalityLevel": "formal",
      "audioRef": "audioAssets.nativeAudio"
    },
    {
      "wordId": "w005",
      "targetText": "すみません",
      "transliteration": "Sumimasen",
      "baseTranslation": "Excuse me / I am sorry",
      "partOfSpeech": "expression",
      "formalityLevel": "formal",
      "audioRef": "audioAssets.nativeAudio"
    }
  ],
  "meaningList": [
    "Good morning (formal)",
    "Hello / Good afternoon",
    "Good evening",
    "Thank you very much (formal)",
    "Excuse me / I am sorry"
  ],
  "exampleSentences": [
    {
      "wordId": "w001",
      "targetText": "おはようございます、田中さん。",
      "transliteration": "Ohayou gozaimasu, Tanaka-san.",
      "baseTranslation": "Good morning, Mr. Tanaka."
    },
    {
      "wordId": "w002",
      "targetText": "こんにちは！元気ですか？",
      "transliteration": "Konnichiwa! Genki desu ka?",
      "baseTranslation": "Hello! How are you?"
    },
    {
      "wordId": "w005",
      "targetText": "すみません、駅はどこですか？",
      "transliteration": "Sumimasen, eki wa doko desu ka?",
      "baseTranslation": "Excuse me, where is the train station?"
    }
  ],
  "quizType": "mixed",
  "quizQuestions": [
    {
      "questionId": "q001",
      "questionText": "What does こんにちは mean?",
      "questionType": "multiple_choice",
      "options": ["Good morning", "Good night", "Hello / Good afternoon", "Thank you"],
      "correctAnswerRef": "adminCorrectAnswerSet.mcqAnswerKey.q001"
    },
    {
      "questionId": "q002",
      "questionText": "Which word would you use to say 'Excuse me' when asking a stranger for directions?",
      "questionType": "multiple_choice",
      "options": ["こんばんは", "すみません", "ありがとう", "おはよう"],
      "correctAnswerRef": "adminCorrectAnswerSet.mcqAnswerKey.q002"
    }
  ],
  "adminCorrectAnswerSet": {
    "correctMeanings": {
      "w001": "Good morning (formal)",
      "w002": "Hello / Good afternoon",
      "w003": "Good evening",
      "w004": "Thank you very much (formal)",
      "w005": "Excuse me / I am sorry"
    },
    "acceptedTranslations": {
      "w001": ["Good morning", "Ohayou"],
      "w002": ["Hello", "Hi", "Good afternoon"],
      "w003": ["Good evening"],
      "w004": ["Thank you", "Thanks", "Thank you very much"],
      "w005": ["Excuse me", "Sorry", "Pardon me"]
    },
    "mcqAnswerKey": {
      "q001": "Hello / Good afternoon",
      "q002": "すみません"
    },
    "pronunciationReference": {
      "w001": "oh-HAH-yoh go-ZAI-mas",
      "w002": "kon-NEE-chee-wah",
      "w003": "kon-BAN-wah",
      "w004": "ah-ree-GAH-toh go-ZAI-mas",
      "w005": "su-mee-MAH-sen"
    },
    "strictnessLevel": "moderate",
    "languageOfAnswer": "en"
  },
  "evaluationMode": "keyword_match",
  "scoreThreshold": 70,
  "feedbackRules": {
    "onPass": "Excellent! You have learned the core Japanese greeting words. Move on to the next activity when you are ready.",
    "onFail": "Good effort! Review the words again, paying special attention to the audio. Retry the quiz when you are ready.",
    "onPartial": "You are making progress! Review any words you missed and try the quiz again."
  },
  "audioAssets": {
    "promptAudio": null,
    "nativeAudio": "audio/ja_en/m1/b3/vocab/native_greetings.mp3",
    "referenceAudio": null,
    "instructionAudio": "audio/ja_en/m1/b3/vocab/instructions.mp3",
    "sampleAudio": "audio/ja_en/m1/b3/vocab/sample_phrases.mp3",
    "slowAudio": "audio/ja_en/m1/b3/vocab/slow_greetings.mp3",
    "normalAudio": "audio/ja_en/m1/b3/vocab/normal_greetings.mp3",
    "audioTranscript": "おはようございます。こんにちは。こんばんは。ありがとうございます。すみません。",
    "audioLanguage": "ja",
    "audioDuration": 240,
    "audioRepeatAllowed": true
  },
  "tags": ["greetings", "survival", "formal", "informal", "beginner", "month1", "block3"],
  "status": "published",
  "createdAt": "2025-01-15T00:00:00Z",
  "version": "1.0.0",
  "thumbnail": null,
  "imageAssets": [],
  "videoAssets": [],
  "hintText": "Japanese greetings change depending on the time of day. おはよう is morning, こんにちは is daytime, こんばんは is evening.",
  "commonMistakes": [
    "Using おはよう instead of おはようございます in formal situations",
    "Confusing こんにちは and こんばんは"
  ],
  "reviewLinks": [],
  "nextActivityIds": ["ja_en_M1B3_speaking_001"],
  "attemptLimit": null,
  "metadata": {}
}
```

---

### Example B — Test Activity (3-field pattern inside questionHints only)

Japanese course · Month 1 · Block 3 · End-of-block Test

```json
{
  "activityId": "ja_en_M1B3_test_001",
  "monthNumber": 1,
  "blockNumber": 3,
  "activityType": "test",
  "title": "Block 3 Test — Core Survival Words",
  "learningGoal": "The learner will demonstrate their ability to recognize, translate, and correctly use the core survival words and greetings taught in Block 3.",
  "difficultyLevel": "beginner",
  "baseLanguage": "en",
  "targetLanguage": "ja",
  "estimatedTime": 40,
  "prerequisites": [
    "ja_en_M1B3_vocabulary_001",
    "ja_en_M1B3_lesson_001",
    "ja_en_M1B3_pronunciation_001"
  ],
  "instructions": "This test covers everything you learned in Block 3. Read each question carefully. For listening questions, press play before answering. You may not replay audio more than twice. Your hints will appear after you submit each answer.",
  "testTitle": "Block 3 Test — Core Survival Words",
  "testScope": "block_test",
  "coveredActivityTypes": ["lesson", "vocabulary", "pronunciation", "listening"],
  "testInstructions": "Answer all questions. Each section is worth a different number of marks. You need 70 out of 100 marks to pass.",
  "questionSections": [
    {
      "sectionId": "sec_vocab",
      "sectionTitle": "Vocabulary Recognition",
      "activityTypeRef": "vocabulary",
      "questions": [
        {
          "questionId": "q001",
          "questionText": "What does こんにちは mean?",
          "questionType": "multiple_choice",
          "options": ["Good morning", "Good night", "Hello / Good afternoon", "Thank you"],
          "marks": 5,
          "audioRef": null,
          "questionHints": {
            "targetText": "こんにちは",
            "transliteration": "Konnichiwa",
            "baseTranslation": "Hello / Good afternoon"
          },
          "correctAnswerRef": "adminCorrectAnswerSet.answerKey.q001"
        },
        {
          "questionId": "q002",
          "questionText": "Which Japanese phrase means 'Excuse me' and is used to get someone's attention?",
          "questionType": "multiple_choice",
          "options": ["ありがとう", "すみません", "おはよう", "さようなら"],
          "marks": 5,
          "audioRef": null,
          "questionHints": {
            "targetText": "すみません",
            "transliteration": "Sumimasen",
            "baseTranslation": "Excuse me / I am sorry"
          },
          "correctAnswerRef": "adminCorrectAnswerSet.answerKey.q002"
        },
        {
          "questionId": "q003",
          "questionText": "Is this statement true or false: おはようございます is used in the evening.",
          "questionType": "true_false",
          "options": ["True", "False"],
          "marks": 5,
          "audioRef": null,
          "questionHints": {
            "targetText": "おはようございます",
            "transliteration": "Ohayou gozaimasu",
            "baseTranslation": "Good morning (formal) — used only in the morning, not the evening"
          },
          "correctAnswerRef": "adminCorrectAnswerSet.answerKey.q003"
        }
      ],
      "sectionMarks": 25,
      "sectionPassMarks": 15
    },
    {
      "sectionId": "sec_listening",
      "sectionTitle": "Listening Comprehension",
      "activityTypeRef": "listening",
      "questions": [
        {
          "questionId": "q004",
          "questionText": "Listen to the audio and choose what the speaker said.",
          "questionType": "multiple_choice",
          "options": [
            "こんばんは、お元気ですか？",
            "おはようございます、田中さん。",
            "ありがとうございます、先生。",
            "すみません、トイレはどこですか？"
          ],
          "marks": 10,
          "audioRef": "audioAssets.promptAudio",
          "questionHints": {
            "targetText": "おはようございます、田中さん。",
            "transliteration": "Ohayou gozaimasu, Tanaka-san.",
            "baseTranslation": "Good morning, Mr. Tanaka."
          },
          "correctAnswerRef": "adminCorrectAnswerSet.answerKey.q004"
        }
      ],
      "sectionMarks": 25,
      "sectionPassMarks": 15
    },
    {
      "sectionId": "sec_writing",
      "sectionTitle": "Short Writing",
      "activityTypeRef": "writing",
      "questions": [
        {
          "questionId": "q005",
          "questionText": "Write the Japanese phrase for 'Thank you very much' in formal style.",
          "questionType": "short_answer",
          "options": null,
          "marks": 10,
          "audioRef": null,
          "questionHints": {
            "targetText": "ありがとうございます",
            "transliteration": "Arigatou gozaimasu",
            "baseTranslation": "Thank you very much (formal)"
          },
          "correctAnswerRef": "adminCorrectAnswerSet.answerKey.q005"
        }
      ],
      "sectionMarks": 25,
      "sectionPassMarks": 15
    }
  ],
  "scoreWeights": {
    "lesson": 10,
    "pronunciation": 10,
    "reading": 10,
    "writing": 15,
    "listening": 25,
    "vocabulary": 25,
    "speaking": 5
  },
  "totalMarks": 100,
  "passMarks": 70,
  "userResponses": {},
  "finalScore": null,
  "sectionScores": {},
  "resultSummary": null,
  "adminCorrectAnswerSet": {
    "answerKey": {
      "q001": "Hello / Good afternoon",
      "q002": "すみません",
      "q003": "False",
      "q004": "おはようございます、田中さん。",
      "q005": "ありがとうございます"
    },
    "scoringRubric": {
      "q005": "Full marks for correct script. Half marks for correct romanization only."
    },
    "partialCreditRules": {
      "q005": "5 marks awarded if transliteration is correct but native script is missing"
    },
    "alternateValidAnswers": {
      "q005": ["ありがとうございます", "Arigatou gozaimasu", "arigatou gozaimasu"]
    },
    "sectionPassMarks": {
      "sec_vocab": 15,
      "sec_listening": 15,
      "sec_writing": 15
    }
  },
  "evaluationMode": "exact_match",
  "scoreThreshold": 70,
  "feedbackRules": {
    "onPass": "Well done! You have passed the Block 3 test. You are ready to move into Block 4.",
    "onFail": "You did not pass this time. Review your weakest sections and try again. You can retry as many times as needed.",
    "onPartial": "You are close! Review the sections where you lost marks and retry."
  },
  "audioAssets": {
    "promptAudio": "audio/ja_en/m1/b3/test/listening_q004.mp3",
    "nativeAudio": null,
    "referenceAudio": null,
    "instructionAudio": "audio/ja_en/m1/b3/test/instructions.mp3",
    "sampleAudio": null,
    "slowAudio": null,
    "normalAudio": null,
    "audioTranscript": "おはようございます、田中さん。",
    "audioLanguage": "ja",
    "audioDuration": 5,
    "audioRepeatAllowed": true
  },
  "tags": ["test", "block3", "greetings", "survival", "beginner", "month1"],
  "status": "published",
  "createdAt": "2025-01-15T00:00:00Z",
  "version": "1.0.0",
  "thumbnail": null,
  "imageAssets": [],
  "videoAssets": [],
  "hintText": null,
  "commonMistakes": [],
  "reviewLinks": [],
  "nextActivityIds": ["ja_en_M1B4_lesson_001"],
  "attemptLimit": null,
  "metadata": {}
}
```

---

## 15. Validation Checklist Before Submission

Before submitting or publishing any activity JSON, verify every item in this checklist:

### Universal Checks (All Activities)

- [ ] `activityId` is globally unique and follows the naming convention
- [ ] `monthNumber` is 1, 2, or 3
- [ ] `blockNumber` is 1 through 6
- [ ] `activityType` is one of the 8 valid types
- [ ] `estimatedTime` is **30 or higher** — this is a hard requirement
- [ ] `learningGoal` is a single, clear, measurable sentence
- [ ] `instructions` are detailed enough for the learner to know exactly what to do
- [ ] `adminCorrectAnswerSet` is fully populated and not empty or null
- [ ] `audioAssets` is present and all applicable fields are filled
- [ ] `evaluationMode` matches the activity type
- [ ] `scoreThreshold` is set to a reasonable value (typically 60–80)
- [ ] `feedbackRules` has all three states: `onPass`, `onFail`, `onPartial`
- [ ] `status` is set — only use `"published"` when fully complete
- [ ] All runtime-only fields (userAnswer, finalScore, etc.) are `null` or `{}`
- [ ] Content is appropriate for the block's theme and month's learning goal

### Transliteration Checks — MANDATORY

- [ ] Every target language text object contains all three fields: `targetText`, `transliteration`, `baseTranslation`
- [ ] No target language text appears alone without its `transliteration` and `baseTranslation`
- [ ] In Lesson: all `targetLanguageExamples`, `examples`, and `checkpointQuestions` use the 3-field structure
- [ ] In Pronunciation: all `targetPhrasesOrWords` items have all three fields
- [ ] In Reading: all `glossary` entries and all `sentenceSupportPairs` have all three fields
- [ ] In Writing: all `wordBank` entries and all `modelExampleOutputs` have all three fields
- [ ] In Listening: all `audioTranscriptSentences` have all three fields
- [ ] In Vocabulary: all `wordList` entries and all `exampleSentences` have all three fields
- [ ] In Speaking: `scenarioContext`, all `subTasks.sampleResponse`, and all `baselineTranscriptSentences` have all three fields
- [ ] In Test: target language text does **not** appear inline — it is inside `questionHints` only
- [ ] In Test: `questionHints` is present on every question that references target language text
- [ ] In Test: questions that contain no target language text have `questionHints` set to `null`

### Content Depth Checks

- [ ] Lesson: At least 5–8 content sections with real explanations
- [ ] Pronunciation: At least 8–12 target items with full phonetic breakdowns
- [ ] Reading: Passage is at least 300–600 words with 6–10 questions
- [ ] Writing: Prompt supports 80–150 word responses, includes a rubric and model outputs
- [ ] Listening: Audio is at least 3–5 minutes, 8–12 questions provided
- [ ] Vocabulary: At least 15–20 words with full entries and 10+ quiz questions
- [ ] Speaking: At least 3–5 sub-tasks with sample responses and a rubric
- [ ] Test: At least 20–30 questions across all sections with weighted scoring

### Language-Specific Checks

- [ ] All target language text is accurate and native-appropriate
- [ ] Transliterations match the target language phonology
- [ ] Formality levels are correctly labeled (formal, informal, neutral)
- [ ] Cultural notes are accurate and respectful
- [ ] Audio file paths are correctly referenced and follow naming conventions

---

## Final Notes for Content Creators

1. **Never sacrifice depth for speed.** A thin activity that takes 10 minutes is not acceptable. If the content is not enough, add more words, more examples, more questions, or more explanation.

2. **adminCorrectAnswerSet is sacred.** This field drives all automated evaluation. Incomplete or vague values will produce inaccurate scoring.

3. **audioAssets must be consistent.** Even if the audio file does not exist yet, define the expected file path so the engineering team can prepare it.

4. **Keep Section 3 and Section 4 fields empty.** Never hardcode user responses or scores — these are runtime values.

5. **Test your activity by reading it as a learner.** If you could not spend 30 minutes genuinely learning from it, it is not ready.

6. **Language pairs must be consistent throughout a course.** Do not mix language codes or use inconsistent transliteration styles within the same course dataset.

---

*This document is the authoritative specification for content creation in this language learning application. Any ambiguity should be resolved in favor of adding more content, more detail, and more accuracy.*
