# LearnWise — Full QA, Admin Rebuild & Feedback System

## Overview

A comprehensive overhaul of the LearnWise platform covering four pillars:

1. **Activity Testing** — Exhaustive pytest suites for all 8 activity types (lesson, vocab, reading, writing, listening, speaking, pronunciation, test) covering functional, negative, edge, and Groq API cases.
2. **Post-Activity Feedback Notifications** — Contextual in-app notifications after every activity based on score tier (hint on repeated failure, lesson insight on mid score, praise + tips on high score) with beautiful UI.
3. **Admin Dashboard Rebuild** — Fully functional, backend-connected admin dashboard with CRUD for languages, activities, and users; plus new management features (activity templates, content editor, platform analytics).
4. **Bug Fixes** — All discovered bugs, vulnerabilities, and design flaws fixed across frontend and backend.

---

## User Review Required

> [!IMPORTANT]
> **Admin Dashboard is currently broken** — `AdminDashboard.jsx` calls `getAdminStats()` and `listAdminUsers()` but the admin routes require an `Authorization: Bearer <token>` header. The `AdminLoginPage.jsx` stores the token but the `api/client.js` only reads from the regular user auth state. We will fix this by unifying auth headers to also pull from localStorage admin token.

> [!WARNING]
> **Input token overflow protection is missing** — Writing, Reading, and Lesson pages allow users to paste unlimited text into textareas before submitting to Groq. If a user pastes 10,000+ words, Groq will either fail or return bad results. We will add client-side character limits (2000 chars per textarea) AND server-side token estimation on the validate endpoint.

> [!WARNING]
> **Whisper is used as a local model** (not Groq Whisper API). This means the backend must have `openai-whisper` and `ffmpeg` installed. The mock fallback currently returns a placeholder string which, when submitted to Groq for speaking/pronunciation evaluation, will give a nonsensical score. We will improve the mock to signal to the frontend that transcription failed rather than silently submitting a bad answer.

> [!CAUTION]
> **No MIME type validation on audio upload** — The speech router checks `content_type` but browsers often send `audio/webm;codecs=opus` which won't match the strict set. We will fix the type validation to use `startswith()` matching.

---

## Open Questions

> [!NOTE]
> **Notification display style**: The plan is to show notifications as a slide-in overlay panel (not a toast, not a modal blocker) that appears after the ScoreModal is dismissed. It will have three visual tiers: 🔴 Hint (red/orange, repeated failures), 🟡 Lesson (yellow/amber, 50–79%), 🟢 Praise (green, 80%+). Do you want the Groq-generated lesson content to appear inline in this panel, or should it link to a separate page?

> [!NOTE]
> **Admin content editor**: For editing activity JSON files, we plan to use a Monaco/CodeMirror-style JSON editor in the admin UI. Alternatively we can use a simpler form-based editor for common fields. Which do you prefer?

---

## Discovered Bugs

| # | Location | Bug | Severity |
|---|----------|-----|----------|
| 1 | `speech.py` | MIME type check uses `==` instead of `startswith()` — rejects `audio/webm;codecs=opus` | High |
| 2 | `WritingPage.jsx` | No character limit on textarea — can send 10k+ tokens to Groq | High |
| 3 | `AdminDashboard.jsx` | API calls fail silently — no error handling, `setStats(r.data)` crashes if request fails | High |
| 4 | `api/admin.js` | Uses regular `client` which only attaches user JWT, not admin JWT | High |
| 5 | `groq_service.py` | Fallback JSON stripping only handles one code fence pattern — fails on ` ```json\n` with trailing newline | Medium |
| 6 | `SpeakingPage.jsx` | `alert()` used for transcription failure — breaks UX, not recoverable gracefully | Medium |
| 7 | `LessonPage.jsx` | `useEffect` only depends on `activityFile` not `pairId` — if pairId changes, data isn't reloaded | Medium |
| 8 | `ScoreModal.jsx` | `onNext` is called on overlay click even when user scrolls — accidental dismissal | Low |
| 9 | `whisper_service.py` | Mock returns `[Transcription unavailable...]` string — submitted to Groq as "user answer" | Medium |
| 10 | `progress.py` | `current_activity_id` advance logic `req.activity_id >= progress.current_activity_id` allows skipping | Low |
| 11 | `admin.py` | `list_languages()` requires admin role but `content.py` `/content/pairs` is public — inconsistency | Low |
| 12 | `AdminDashboard.jsx` | No language management UI even though backend has full CRUD for it | High |
| 13 | `validate.py` | No per-question token length guard — one large question can overflow Groq context | Medium |
| 14 | `scoring_service.py` | Score calculation unchecked — if Groq returns `score > per_q_max`, total can exceed max_xp | Medium |

---

## Proposed Changes

### 1. Bug Fixes (Backend)

#### [MODIFY] [speech.py](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/backend/app/routers/speech.py)
- Fix MIME type check to use `startswith()` — handles `audio/webm;codecs=opus`
- Add file size check early (before reading full bytes)

#### [MODIFY] [validate.py](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/backend/app/routers/validate.py)
- Add per-question `user_answer` length guard (max 2000 chars) — returns 422 if exceeded
- Add total questions guard (max 50 questions per submission)

#### [MODIFY] [groq_service.py](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/backend/app/services/groq_service.py)
- Improve JSON extraction — handle all code fence variants robustly
- Add `max_tokens` guard based on question count
- Add score clamping in response parsing (ensure no score > per_q_max)

#### [MODIFY] [whisper_service.py](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/backend/app/services/whisper_service.py)
- Return `is_mock: true` flag in mock response so frontend can detect it

#### [MODIFY] [scoring_service.py](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/backend/app/services/scoring_service.py)
- Clamp all scores to `[0, per_q_max]` range after Groq response

#### [MODIFY] [progress.py](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/backend/app/routers/progress.py)
- Fix activity advance logic: only advance by 1 step, not skip ahead

---

### 2. Bug Fixes (Frontend)

#### [MODIFY] [WritingPage.jsx](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/src/pages/activities/WritingPage.jsx)
- Add `maxLength={2000}` + character counter on all textareas
- Add submission guard: warn if any field is empty

#### [MODIFY] [LessonPage.jsx](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/src/pages/activities/LessonPage.jsx)
- Fix `useEffect` dependency array to include `pairId`

#### [MODIFY] [SpeakingPage.jsx](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI\learnwise-react_till_now_6/learnwise-react/src/pages/activities/SpeakingPage.jsx)
- Replace `alert()` with in-component error state display
- Handle `is_mock: true` from transcription — show warning "Whisper not available, demo mode"

#### [MODIFY] [PronunciationPage.jsx](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/src/pages/activities/PronunciationPage.jsx)
- Same Whisper mock detection as SpeakingPage

#### [MODIFY] [ScoreModal.jsx](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/src/components/ScoreModal.jsx)
- Fix overlay click: only dismiss if `mousedown` target === overlay (prevent accidental dismiss on scroll/drag)

#### [MODIFY] [api/client.js](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/src/api/client.js)
- Axios interceptor should also check `localStorage.getItem('admin_token')` as fallback

#### [MODIFY] [api/admin.js](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/src/api/admin.js)
- Add `createActivity`, `deleteActivity` calls to match all backend endpoints
- Export all needed language CRUD functions

---

### 3. Post-Activity Feedback Notification System

#### [NEW] [src/components/ActivityFeedback.jsx](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/src/components/ActivityFeedback.jsx)
A slide-in notification panel shown after ScoreModal is dismissed. Features:
- **3 Tiers based on score + attempt count:**
  - 🔴 `hint` tier: score < 50% AND attempts ≥ 2 — "Keep Trying" hint with specific mistake analysis
  - 🟡 `lesson` tier: score 50–79% — AI-generated mini-lesson related to the activity topic
  - 🟢 `praise` tier: score ≥ 80% — Congratulations + improvement tip for mastery
- **Content from Groq API** (passed through from `ValidateResponse.feedback` and `suggestion`)
- **Animated slide-in from right**, dismissible with swipe or X button
- **Auto-dismiss after 15s** for praise tier (with countdown bar)

#### [MODIFY] [backend/app/schemas/activity.py]
- Add `attempt_count: int = 0` to `ValidateRequest` so frontend can pass retry count
- Add `feedback_tier: str` (`hint|lesson|praise`) to `ValidateResponse` so frontend knows which tier

#### [MODIFY] [validate.py](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/backend/app/routers/validate.py)
- Calculate `feedback_tier` based on `percentage` and `attempt_count`
- Adjust Groq system prompt to generate tier-appropriate feedback

#### [MODIFY] [groq_service.py]
- Add `feedback_tier` parameter to prompt builder
- Tier-specific instructions:
  - `hint`: "Focus on what the student got wrong, give 2 concrete hints for next attempt"  
  - `lesson`: "Provide a brief 3-sentence lesson explaining the concept they need to improve"
  - `praise`: "Celebrate their success and give 1 advanced tip to further improve"

---

### 4. Admin Dashboard Rebuild

#### [MODIFY] [src/pages/admin/AdminDashboard.jsx](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/src/pages/admin/AdminDashboard.jsx)
Complete rebuild with tabbed interface:
- **Tab 1: Overview** — Platform stats (users, XP, completions, top language pair, activity type breakdown)
- **Tab 2: Users** — Searchable/filterable user table, role management, deactivate/reactivate
- **Tab 3: Languages** — List all language pairs, create new pair, delete pair (with confirmation)
- **Tab 4: Content** — Select a language pair → browse JSON files → inline JSON editor with syntax highlighting → save
- **Tab 5: Activity Templates** — Quick-add activity scaffolds (lesson/vocab/reading/writing/test) for any pair

Full error handling with toast notifications for all API calls.

#### [MODIFY] [src/pages/admin/AdminLoginPage.jsx](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/src/pages/admin/AdminLoginPage.jsx)
- Store admin token in `localStorage` key `admin_token` (already does this in Redux, but also persist to localStorage for the API client interceptor)

#### [MODIFY] [backend/app/routers/admin.py](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/backend/app/routers/admin.py)
- Add `GET /api/admin/content/{pair_id}/file` → already exists, no change
- Add `DELETE /api/admin/content/{pair_id}/activity` → delete an activity file
- Add `GET /api/admin/activity-types` → return list of supported activity types + templates
- Add `GET /api/admin/analytics` → per-activity-type completion rate, avg score, top users
- Add `PUT /api/admin/users/{user_id}/activate` → re-activate deactivated user

#### [MODIFY] [src/api/admin.js](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/src/api/admin.js)
- Add all missing API call functions matching new backend endpoints

---

### 5. Comprehensive Backend Test Suite

#### [MODIFY] [backend/tests/test_validate.py](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/backend/tests/test_validate.py)
Extended test coverage:
- All 8 activity types (lesson, vocab, reading, writing, listening, speaking, pronunciation, test)
- Input overflow protection (user_answer > 2000 chars)
- Token injection attempt (user_answer contains special chars, JSON, SQL)
- Groq timeout / rate-limit fallback behavior
- `attempt_count` based tier assignment
- Empty, null, whitespace-only answers
- Very large number of questions (edge: 50 questions)
- `max_xp=0` edge case
- Wrong field types (number as string, etc.)

#### [NEW] [backend/tests/test_speech.py](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/backend/tests/test_speech.py)
- Upload valid audio (mocked Whisper)
- Upload empty audio → 400
- Upload oversized audio → 413
- Upload invalid MIME (image/png) → 400
- Upload `audio/webm;codecs=opus` → accepted (regression for Bug #1)
- Unauthenticated upload → 401
- Whisper unavailable → returns mock with `is_mock: true`

#### [MODIFY] [backend/tests/test_admin.py](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/backend/tests/test_admin.py)
Extended coverage:
- Create language pair (happy path, duplicate, invalid pair_id format)
- Delete language pair (happy path, non-existent)
- Create activity file (new, conflict → 409)
- Update activity file (valid, malformed JSON)
- Delete activity file
- Analytics endpoint
- Reactivate user
- Non-admin user denied access to all `/admin/*` routes (403)

#### [MODIFY] [backend/tests/test_progress.py](file:///c:/Users/jayta/OneDrive/Desktop/Mtech/Sem-2/GenAI/_Project/GenAI/learnwise-react_till_now_6/learnwise-react/backend/tests/test_progress.py)
Extended coverage:
- Complete same activity twice: XP awarded only for improvement
- Complete with score = 0 → XP = 0, passed = false
- Attempt to skip activity_id (non-sequential)
- `ai_feedback` and `ai_suggestion` stored correctly
- List completions returns ordered results

---

### 6. Frontend Improvements to Activity Pages

#### [MODIFY] [src/pages/activities/ReadingPage.jsx]
- Add character limit to any text input fields
- Show question count and estimated reading time

#### [MODIFY] [src/pages/activities/ListeningPage.jsx]
- Add character limit to gap-fill inputs
- Audio player controls improvement

#### [MODIFY] [src/pages/activities/TestPage.jsx]
- Add timer feature (optional, visible countdown)
- Show question index (Q 1/5)

#### [MODIFY] [src/pages/activities/VocabPage.jsx]
- Add character limit to translation inputs

---

## Verification Plan

### Backend Tests
```bash
cd backend
.\venv\Scripts\activate
pytest tests/ -v --tb=short -x
```
All existing tests must pass (no regressions).
New tests must achieve >90% pass rate on first run.

### Admin Dashboard Verification
1. Login at `/admin/login` with admin credentials
2. Verify all 5 tabs load with real data from backend
3. Create a new language pair → verify appears in user onboarding
4. Upload/edit an activity JSON → verify changes visible in activity pages
5. Deactivate a user → verify they cannot login
6. Reactivate user → verify they can login again

### Activity Feedback Verification
1. Complete a writing activity with a poor answer (< 50%) twice → see red "hint" notification
2. Complete with 65% → see yellow "lesson" notification
3. Complete with 90% → see green "praise" notification with auto-dismiss timer

### Bug Regression Tests
- Upload `audio/webm;codecs=opus` → no 400 error (Bug #1 fix)
- Paste 3000 chars into writing textarea → blocked at 2000 (Bug #2 fix)
- Open admin dashboard → no silent failures, error toast shown if backend down (Bug #3 fix)

---

## Implementation Order

1. **Backend Bug Fixes** (30 min) — Fix bugs #1–#14, no new features
2. **Backend New Endpoints** (45 min) — Add admin analytics, delete-activity, activate-user
3. **Extended Test Suite** (60 min) — Write all new pytest tests, run full suite
4. **Groq Feedback Tier System** (30 min) — Update schemas + validate router + groq_service
5. **ActivityFeedback Component** (45 min) — New animated notification UI
6. **Admin Dashboard Rebuild** (90 min) — Full 5-tab admin dashboard with all CRUD
7. **Frontend Bug Fixes** (30 min) — Input limits, LessonPage dep fix, modal fix
8. **Final Test Run + Verification** (30 min)
