# LearnWise — Hindi → Japanese Content Generation Guide

> **For AI Agents & Human Admins**  
> This file + `data/README.md` is everything needed to generate the complete Hindi→Japanese roadmap.

---

## AI AGENT INSTRUCTIONS

You are generating a **Japanese language learning course** where the **teaching language is Hindi**.

- **All explanations and instructions must be in Hindi**
- **All target language text must be in Japanese** (Mixed (Hiragana/Katakana/Kanji) script) with romanization + Hindi translation
- **Cultural notes should reflect Japanese-speaking culture and customs**

---

## Language Pair Identity

| Property | Value |
|----------|-------|
| Pair ID | `hi-ja` |
| Source Language | Hindi 🇮🇳 |
| Target Language | Japanese 🇯🇵 (日本語) |
| Script | Mixed (Hiragana/Katakana/Kanji) |
| CEFR Difficulty | **C** |
| Key Fact | 3 scripts, 128M speakers, highly formal speech levels |
| Language Family | Japonic |

---

## Difficulty Notes for Content Creators

- **High difficulty**: Completely different script and grammar system
- Month 1 must dedicate significant content to script/character learning
- Always provide romanization alongside native script
- Grammar may be SOV, honor levels, or tonal — explain clearly in English
- Script note: Mixed (Hiragana/Katakana/Kanji)
- **3 scripts**: Introduce Hiragana first (Month 1), then Katakana (Month 2), then Kanji
- Honorific levels: Start with polite (masu/desu) form

---

## 6-Month Curriculum Outline

**Month 1: Sound Foundation & Survival Basics (A1)**
- Themes: Script/sounds, vowels, basic greetings, numbers 1-100, family
- IDs: 1–43
- Files: `month-1/`

**Month 2: Sentence Building & Core Grammar (A1+)**
- Themes: Present tense, shopping, food & restaurants, directions & transport
- IDs: 101–143
- Files: `month-2/`

**Month 3: Functional Communication (A2)**
- Themes: Past/future tense, professions & work, travel & tourism
- IDs: 201–243
- Files: `month-3/`

**Month 4: Intermediate Fluency & Culture (A2+)**
- Themes: Social life, weather & seasons, health & body, media & news
- IDs: 301–343
- Files: `month-4/`

**Month 5: Advanced Expression & Immersion (B1)**
- Themes: Conditionals, opinions & debate, idioms & literature, abstract concepts
- IDs: 401–443
- Files: `month-5/`

**Month 6: Mastery & Certification (B1+)**
- Themes: Regional dialects, professional communication, advanced reading, final exam
- IDs: 501–543
- Files: `month-6/`


---

## Complete File Manifest

For each month, generate these **43 files** (change month-1/ to month-2/, etc. and add 100 to IDs):

```
month-1/week-1-lesson.json           ID: 1   → week-2: ID 11 | week-3: ID 22 | week-4: ID 33
month-1/week-1-vocab.json            ID: 2
month-1/week-1-reading.json          ID: 3
month-1/week-1-pronunciation.json    ID: 4
month-1/week-1-writing.json          ID: 5
month-1/week-1-listening.json        ID: 6
month-1/week-1-test.json             ID: 7
month-1/week-1-speaking.json         ID: 8
month-1/week-1-vocab-review.json     ID: 9
month-1/week-1-pronunciation-2.json  ID: 10
month-1/week-2-[all above + midtest] IDs 11-21
month-1/week-3-[all above + midtest] IDs 22-32
month-1/week-4-[all above]           IDs 33-42
month-1/milestone.json               ID: 43
```

Month ID ranges: M1=1-43 | M2=101-143 | M3=201-243 | M4=301-343 | M5=401-443 | M6=501-544

---

## Content Rules for This Language Pair

1. **Explanations**: Always write in Hindi
2. **Target text**: Always include Japanese script + romanization + Hindi meaning
3. **Vocabulary**: 25+ words per vocab activity, increase to 30 in Month 4+
4. **Tests**: 10 questions for weekly test, 20 for midtest
5. **Writing**: 30 words min Month 1, increase by 10 each month
6. **Reading passages**: 150 words Month 1, 300+ words Month 6
7. **Cultural notes**: Include at least 1 per week about Japanese culture

---

## Sample AI Prompt

```
You are generating LearnWise content for Hindi→Japanese.

File: data/languages/hi/ja/month-1/week-1-lesson.json
Activity ID: 1 | Type: lesson | Week: 1, Month: 1 | Level: A1

Generate 7+ blocks using: text, grammar_rule, dialogue, comparison_table, fill_blank, tip, progress_checkpoint
All explanations in Hindi. All Japanese text with romanization + Hindi translation.
Week 1 theme: Script/sounds, vowels, basic greetings, numbers 1-100, family

Follow JSON schema from data/README.md Section 5.
Set: "langPair": "hi-ja", "id": 1, "xp": 30, "week": 1, "month": 1
```

---

*Hindi→Japanese Content Guide | See data/README.md for complete block type schemas*
