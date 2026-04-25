# LearnWise — Activity Diagram Reference

> **Purpose:** Complete reference for building ALL Activity Diagrams for the LearnWise platform.  
> Every swimlane, action node, decision node, fork/join (parallel), and guard condition is documented.  
> Do NOT omit any flow. Cover every major user journey and backend process end-to-end.

---

## HOW TO READ THIS DOCUMENT

Each activity diagram is described using this notation:
- `[Decision]` — diamond decision node with condition
- `ACTION` — a single action/activity node
- `fork ──>` — parallel split (fork)
- `<── join` — parallel merge (join)
- `(swim: X)` — the swimlane this action belongs to
- `→` — flow arrow
- `END` — activity end node
- `[guard]` — guard condition on a transition

---

## ACTIVITY DIAGRAM 1: User Registration Flow

**Swimlanes:** User | Frontend | Backend | Database

```
START
  (swim: User)
  → FILL registration form {username, email, password}
  → CLICK "Register" button

  (swim: Frontend)
  → VALIDATE form locally (username 3-50 chars, alphanumeric+underscore; password min 8; email format)

  [Decision] Form valid?
  → [NO] SHOW inline validation errors → return to FILL form
  → [YES] DISPATCH registerUser(credentials) to Redux

  (swim: Frontend/Redux)
  → SET state.loading = true
  → CALL POST /api/auth/register via Axios

  (swim: Backend)
  → RECEIVE POST /api/auth/register
  → VALIDATE Pydantic schema (RegisterRequest)

  [Decision] Schema valid?
  → [NO] RETURN 422 Unprocessable Entity → Frontend: SHOW error → END

  → [YES] QUERY users WHERE email == req.email

  [Decision] Email already exists?
  → [YES] RETURN 400 "Email already registered" → Frontend: SHOW error → END

  (swim: Backend)
  → QUERY users WHERE username == req.username

  [Decision] Username already taken?
  → [YES] RETURN 400 "Username already taken" → Frontend: SHOW error → END

  → [NO] HASH password (bcrypt)
  → INSERT new User into database
  → ISSUE JWT (HS256, 7-day expiry)
  → RETURN 201 TokenResponse

  (swim: Database)
  → COMMIT new User record

  (swim: Frontend/Redux)
  → RECEIVE TokenResponse
  → SET state.token, state.user, state.isAuthenticated = true
  → WRITE lw_token to localStorage
  → WRITE lw_user JSON to localStorage
  → SET state.loading = false

  (swim: Frontend)
  → NAVIGATE to /dashboard

END
```

---

## ACTIVITY DIAGRAM 2: User Login Flow

**Swimlanes:** User | Frontend | Backend | Database

```
START
  (swim: User)
  → FILL login form {email, password}
  → CLICK "Login"

  (swim: Frontend)
  → DISPATCH loginUser(credentials)
  → SET state.loading = true
  → Axios POST /api/auth/login

  (swim: Backend)
  → QUERY users WHERE email == req.email AND role == "user"

  [Decision] User found?
  → [NO] RETURN 401 "Invalid email or password" → Frontend: SHOW error → END

  → [YES] VERIFY bcrypt password

  [Decision] Password matches?
  → [NO] RETURN 401 "Invalid email or password" → Frontend: SHOW error → END

  [Decision] user.is_active == True?
  → [NO] RETURN 403 "Account is deactivated" → Frontend: SHOW error → END

  → [YES] UPDATE user.last_active = utcnow()
  → ISSUE JWT
  → RETURN 200 TokenResponse

  (swim: Database)
  → COMMIT updated last_active

  (swim: Frontend/Redux)
  → STORE token + user in localStorage + state
  → SET isAuthenticated = true

  (swim: Frontend)
  → NAVIGATE to /dashboard

END
```

---

## ACTIVITY DIAGRAM 3: Admin Login Flow

**Swimlanes:** Admin User | Frontend | Backend

```
START
  (swim: Admin User)
  → NAVIGATE to /admin/login
  → FILL {email, password}
  → CLICK "Admin Login"

  (swim: Frontend)
  → DISPATCH adminLoginUser(credentials)
  → Axios POST /api/auth/admin/login

  (swim: Backend)
  → QUERY users WHERE email == req.email AND role == "admin"

  [Decision] Admin user found?
  → [NO] RETURN 401 "Invalid admin credentials" → Frontend: SHOW error → END

  → [YES] VERIFY password

  [Decision] Password matches?
  → [NO] RETURN 401 → Frontend: SHOW error → END

  → [YES] ISSUE JWT (with role="admin")
  → RETURN 200 TokenResponse

  (swim: Frontend/Redux)
  → STORE token + user (role=admin) in localStorage
  → SET isAuthenticated = true
  → NAVIGATE to /admin (AdminDashboard)

END
```

---

## ACTIVITY DIAGRAM 4: Dashboard Load and Render

**Swimlanes:** User | Dashboard Component | Redux | Backend | File System

```
START
  (swim: User)
  → NAVIGATE to /dashboard (or post-login redirect)

  (swim: Dashboard Component)
  → ProtectedRoute CHECK: isAuthenticated?
  [Decision] Authenticated?
  → [NO] REDIRECT to /login → END
  → [YES] RENDER DashboardPage skeleton / loading state

  fork ──────────────────────────────────────────────────────
  (swim: Redux)                        │  (swim: Redux)
  DISPATCH fetchAllProgress()          │  DISPATCH fetchPairs()
  → GET /api/progress                  │  → GET /api/content/pairs
  → RECEIVE List[ProgressOut]          │  → RECEIVE List[pair ids]
  → SET allProgress in Redux           │  → SET pairs in Redux
  ─────────────────────────────── join ──────────────────────

  (swim: Dashboard Component)
  → AUTO-SELECT first pair if currentPairId is null

  fork ──────────────────────────────────────────────────────
  GET /api/content/{pairId}/meta       │  GET /api/progress/{pairId}/completions
  → RECEIVE meta.json                  │  → RECEIVE List[CompletionOut]
  → SET meta state                     │  → SET completions state (filter passed)
  ─────────────────────────────── join ──────────────────────

  (swim: Dashboard Component)
  → BUILD completedSeqIds = Set(completion.activity_seq_id WHERE passed=True)
  → DETERMINE currentActivityId from progress (default 1)
  → isUnlocked(seqId) = seqId <= currentActivityId
  → isCompleted(seqId) = seqId in completedSeqIds

  (swim: Dashboard Component)
  → RENDER pair selector (if multiple pairs)
  → RENDER expandable month sections (Month 1, 2, 3)
  → For each month → RENDER blocks (1-6)
  → For each block → RENDER 8 activity nodes

  For each activity node:
    [Decision] isCompleted(seqId)?
    → [YES] RENDER with completed style (green ring + checkmark)
    [Decision] isUnlocked(seqId)?
    → [YES] RENDER as clickable node (colored by activity type)
    → [NO] RENDER as locked node (greyed out, lock icon)

  (swim: User)
  → SEE roadmap with progress state

END
```

---

## ACTIVITY DIAGRAM 5: Activity Execution — General Flow

**Swimlanes:** User | Activity Page | Backend Validate | Groq AI | Scoring | Backend Progress | Database

```
START
  (swim: User)
  → CLICK unlocked activity node
  → NAVIGATE to /activity/{pairId}/{type}

  (swim: Activity Page)
  → ActivityRouter: determine component from type
  → FETCH activity JSON via GET /api/content/{pairId}/activity?file={activityFile}
  → PARSE JSON (activityId, questions, instructions, resources)
  → RENDER activity UI

  (swim: User)
  → READ lesson content / listen to audio / record speech / fill answers
  → COMPLETE all required inputs
  → CLICK "Submit"

  (swim: Activity Page)
  → VALIDATE user has answered all required questions

  [Decision] Answers complete?
  → [NO] SHOW "Please answer all questions" → USER re-fills → loop back

  → [YES] BUILD ValidateRequest payload
  → POST /api/validate

  (swim: Backend Validate)
  [Decision] activity_type in MCQ_TYPES ("test")?

    → [YES] — MCQ Local Scoring path:
      (swim: Scoring)
      → score_mcq_locally(questions, max_xp)
      → for each question: compare str(user_answer) == str(correct_answer)
      → calculate_score() → clamp, sum, compute percentage
      → pass = percentage >= 20%
      → return {total_score, percentage, passed, question_results}

    → [NO] — Groq AI Scoring path:
      (swim: Groq AI)
      → _build_prompt(activity_type, questions, max_xp, user_lang, target_lang)
      → POST to Groq API (llama3-8b-8192, temp=0.1)
      → PARSE JSON response {question_results, overall_feedback, suggestion}
      → MERGE user_answer/correct_answer from original questions

      (swim: Scoring)
      → calculate_score(questions, max_xp, groq_scores)
      → CLAMP per-question scores to [0, per_q_max]
      → SUM total, compute percentage
      → passed = percentage >= 20%

  (swim: Backend Validate)
  → _determine_feedback_tier(percentage, attempt_count)
    NOTE: hint if attempts >= 3 OR percentage < 30%
          praise if percentage >= 80%
          lesson otherwise

  [Decision] feedback_tier != "lesson" AND GROQ type?
  → [YES] generate_tier_feedback() → second Groq call for refined feedback
  → [NO] use original feedback

  [Decision] SCORE_THRESHOLD_OVERRIDE > 0?
  → [YES] effective_passed = total_score >= SCORE_THRESHOLD_OVERRIDE
  → [NO] use passed from scoring

  → RETURN ValidateResponse {total_score, max_score, percentage, passed, feedback, suggestion, question_results, feedback_tier}

  (swim: Activity Page)
  → SHOW ScoreModal {score, passed, XP earned, feedback, suggestion}

  (swim: Backend Progress)
  → POST /api/progress/{pairId}/complete
  → [Decision] First completion OR improvement?
    → award xp_delta
  → [Decision] passed AND activity == current_activity_id?
    → [YES] INCREMENT current_activity_id (UNLOCK next activity)
    → UPDATE month/block from new position
  → COMMIT to database

  (swim: Activity Page)
  → DISPATCH fetchPairProgress to refresh dashboard

  (swim: User)
  → SEE result popup
  → CLICK "Continue" → back to Dashboard (next activity unlocked)

END
```

---

## ACTIVITY DIAGRAM 6: STT Recording Flow (Speaking / Pronunciation)

**Swimlanes:** User | AudioRecorder Component | Browser API | Backend Speech | Whisper | Activity Page

```
START
  (swim: User)
  → CLICK "Start Recording" button

  (swim: AudioRecorder Component)
  → REQUEST microphone permission

  [Decision] Permission granted?
  → [NO] SHOW "Microphone access denied" error → END
  → [YES] INITIALIZE MediaRecorder(stream, webm/opus)
  → mediaRecorder.start()
  → START visual recording indicator (red pulse)

  (swim: Browser API)
  → EMIT dataavailable events every 250ms
  → AudioRecorder COLLECTS audio chunks array

  (swim: User)
  → SPEAKS into microphone

  (swim: User)
  → CLICK "Stop Recording"

  (swim: AudioRecorder Component)
  → mediaRecorder.stop()
  → Browser API: EMIT final chunk + stop event
  → COMBINE chunks: new Blob(chunks, {type:"audio/webm"})
  → SET audioBlob state

  [Decision] Show preview?
  → [YES] CREATE object URL, render <audio> preview controls
  → User listens back

  (swim: User)
  → CLICK "Submit Recording"

  (swim: AudioRecorder Component)
  → CREATE FormData, append Blob as audio file
  → POST /api/speech/transcribe (multipart)

  (swim: Backend Speech)
  → VALIDATE MIME type (startswith checks)
  → READ all bytes
  → VALIDATE size (100 bytes < size < 25MB)

  [Decision] Whisper available?
  → [NO] RETURN {text:"", is_mock:True}
      → Activity Page: SHOW "Transcription unavailable" warning
      → Block submit if is_mock = True
      → END

  → [YES]
  (swim: Whisper)
  → WRITE audio bytes to temp file
  → TRANSCODE via ffmpeg to 16kHz mono WAV
  → whisper_model.transcribe(wav_path, fp16=False)
  → EXTRACT text, language, confidence from result
  → CLEAN UP temp files
  → RETURN {text, language, confidence, is_mock:False}

  (swim: Backend Speech)
  → RETURN TranscribeResponse

  (swim: Activity Page)
  → SET user_answer = transcribed text
  → DISPLAY user's spoken text to them
  → ENABLE Submit Answers button

  (swim: User)
  → REVIEWS transcription
  → CLICKS "Submit Answers" → proceed to standard Validate flow

END
```

---

## ACTIVITY DIAGRAM 7: Friend System Flow

**Swimlanes:** User A (Sender) | User B (Receiver) | Frontend | Backend Friends | Database

```
START

--- SEND PHASE ---
  (swim: User A)
  → NAVIGATE to /search
  → TYPE username in search box

  (swim: Frontend)
  → GET /api/users/search?q={query}
  → DISPLAY matching user cards

  (swim: User A)
  → FIND User B in results
  → CLICK "Add Friend"

  (swim: Backend Friends)
  [Decision] Is self-request?
  → [YES] RETURN 400 → END

  → QUERY User B exists AND is_active

  [Decision] User B found?
  → [NO] RETURN 404 → END

  → QUERY existing FriendRequest (either direction)

  [Decision] Request already exists?
  → [YES] RETURN 400 "Already sent or already friends" → END

  → [NO] INSERT FriendRequest {sender=A, receiver=B, status="pending"}
  → Database: COMMIT
  → RETURN 201 {message:"Friend request sent"}

  (swim: Frontend)
  → SHOW "Request sent" toast

--- RECEIVE PHASE ---
  (swim: User B)
  → NAVIGATES to /search (or notifications)
  → VIEWS incoming friend requests

  (swim: Frontend)
  → GET /api/friends/requests
  → DISPLAY pending requests list

  (swim: User B)
  [Decision] Accept or Decline?

  → [ACCEPT]:
    (swim: Frontend)
    → PUT /api/friends/request/{req_id}/accept

    (swim: Backend Friends)
    → QUERY FriendRequest WHERE id=req_id AND receiver_id=B AND status="pending"
    [Decision] Found?
    → [NO] RETURN 404 → END
    → [YES] UPDATE status = "accepted"
    → Database COMMIT
    → RETURN {message:"Accepted"}

    (swim: Frontend)
    → SHOW "Now friends!" confirmation

  → [DECLINE]:
    (swim: Frontend)
    → PUT /api/friends/request/{req_id}/decline

    (swim: Backend Friends)
    → UPDATE status = "declined"
    → Database COMMIT
    → RETURN {message:"Declined"}

    (swim: Frontend)
    → REMOVE request from list

--- RESULT ---
  Both User A and User B appear on each other's /leaderboard/{pair}/friends

END
```

---

## ACTIVITY DIAGRAM 8: Admin Curriculum CRUD Flow

**Swimlanes:** Admin | AdminDashboard | Backend Admin Router | Content Service | File System

```
START
  (swim: Admin)
  → LOGIN via /admin/login (admin JWT issued)
  → NAVIGATE to /admin (AdminDashboard)

  (swim: AdminDashboard)
  → GET /api/admin/content/pairs → DISPLAY existing language pairs
  → GET /api/admin/analytics → DISPLAY user + completion stats
  → GET /api/admin/users → DISPLAY user list

  (swim: Admin)
  → CHOOSE an action:

--- ACTION: CREATE NEW LANGUAGE PAIR ---
  → ENTER pair_id (e.g. "hi-ja") in form, CLICK Create

  (swim: Backend Admin Router)
  → require_admin() check
  → CALL ContentService.scaffold_pair("hi-ja")

  (swim: Content Service)
  → CREATE data/languages/hi/ja/ directory
  → CREATE meta.json
  → LOOP Month 1 to 3:
      LOOP Block 1 to 6:
        LOOP Activity types (lesson, vocab, reading, writing, listening, speaking, pronunciation, test):
          CREATE M{m}B{b}_{type}.json (empty template)

  (swim: File System)
  → WRITE all files (up to 3×6×8 = 144 JSON files)

  (swim: AdminDashboard)
  → REFRESH pairs list → SHOW new pair

--- ACTION: ADD A MONTH ---
  → SELECT existing pair, ENTER month number, CLICK Add Month

  (swim: Content Service)
  → CREATE month_{n}/ directory
  → LOOP Block 1 to 6:
      LOOP each activity type:
        CREATE activity JSON with empty template

  File System → WRITE all block/activity files for new month

--- ACTION: ADD A BLOCK ---
  → Similar to Add Month but only creates one block's 8 activity files

--- ACTION: EDIT ACTIVITY CONTENT ---
  → SELECT pair → SELECT month → SELECT block → SELECT activity type
  → GET /api/admin/content/{pairId}/months/{m}/blocks/{b}/activities/{type}
  → Frontend: RENDER JSON editor or form
  → Admin EDITS fields (title, questions, instructions, etc.)
  → CLICK Save
  → PUT /api/admin/content/{pairId}/months/{m}/blocks/{b}/activities/{type} {body}

  (swim: Content Service)
  → WRITE updated JSON to file system
  → File System: OVERWRITE activity .json file

  → RETURN 200 {message:"Updated"}

--- ACTION: DELETE LANGUAGE PAIR ---
  → CLICK DELETE on a pair

  (swim: Content Service)
  → REMOVE data/languages/{src}/{tgt}/ directory recursively
  [Decision] Source dir is now empty?
  → [YES] REMOVE data/languages/{src}/ directory too
  → [NO] leave source directory

--- ACTION: MANAGE USERS ---
  → GET /api/admin/users → view list
  [Decision] Activate/Deactivate?
  → POST /api/admin/users/{id}/activate OR deactivate
  → Database UPDATE user.is_active

  [Decision] Trying to deactivate own admin account?
  → [YES] RETURN 400 "Cannot deactivate yourself" → END
  → [NO] proceed

END
```

---

## ACTIVITY DIAGRAM 9: Progress Advancement / Activity Unlock Logic

**Swimlanes:** Progress Router | Scoring Logic | Database

```
START
  → RECEIVE CompleteActivityRequest {activity_seq_id, score_earned, max_score, passed, ...}

  [Decision] SCORE_THRESHOLD_OVERRIDE > 0?
  → [YES] effective_passed = score_earned >= SCORE_THRESHOLD_OVERRIDE
  → [NO] effective_passed = req.passed (from Groq/ScoringService)

  → DERIVE month/block from seq_id (if not provided):
    zero_based = activity_seq_id - 1
    month = (zero_based // 48) + 1
    block = ((zero_based % 48) // 8) + 1

  → QUERY UserLanguageProgress WHERE user_id AND lang_pair_id

  [Decision] Progress record exists?
  → [NO] CREATE new UserLanguageProgress (month=1, block=1, activity=seq_id)
  → COMMIT

  → QUERY ActivityCompletion WHERE user_id AND lang_pair_id AND activity_seq_id

  [Decision] Completion already exists?

  → [YES — Retry]:
    [Decision] new score > existing.score_earned?
    → [YES] xp_delta = new_score - existing.score_earned
              UPDATE completion.score_earned, passed
    → [NO] xp_delta = 0 (no XP for same or lower score)
    UPDATE completion.attempts += 1
    UPDATE completion.ai_feedback, ai_suggestion, completed_at
    (optionally update activity_json_id)

  → [NO — First attempt]:
    xp_delta = score_earned
    INSERT new ActivityCompletion {all fields}

  → UPDATE progress.total_xp += xp_delta
  → UPDATE progress.last_activity_at = utcnow()

  [Decision] effective_passed == True AND activity_seq_id == progress.current_activity_id?
  → [YES — Advance]:
    next_id = current_activity_id + 1
    UPDATE progress.current_activity_id = next_id
    UPDATE progress.current_month, current_block = _derive_month_block(next_id)
    NOTE: This unlocks the next activity on the dashboard

  → [NO — Don't advance]:
    NOTE: Activity already passed, or failed, or jumped ahead — position stays

  → COMMIT all changes
  → REFRESH completion record
  → RETURN CompletionOut

END
```

---

## ACTIVITY DIAGRAM 10: Application Startup Sequence

**Swimlanes:** Uvicorn | FastAPI App | Database | File System | Logger

```
START
  (swim: Uvicorn)
  → LOAD environment variables from backend/.env (DATABASE_URL, SECRET_KEY, GROQ_API_KEY, etc.)
  → INITIALIZE FastAPI app with lifespan handler
  → CALL lifespan(app).__aenter__()

  (swim: FastAPI App)
  → CALL create_tables()

  (swim: Database)
  → IMPORT models (user, progress, friends) to register with SQLAlchemy
  → CALL Base.metadata.create_all(bind=engine)

  [Decision] Database reachable?
  → [NO] raise connection error → Uvicorn restarts (Docker restart policy) → retry
  → [YES] CREATE tables if not exist (users, user_language_progress, activity_completions, friend_requests)

  (swim: FastAPI App)
  → CALL seed_admin()
  → QUERY User WHERE email == ADMIN_EMAIL

  [Decision] Admin exists?
  → [YES] LOG "Admin already exists" → skip
  → [NO] HASH password → INSERT admin user → COMMIT → LOG "Admin created"

  (swim: File System)
  → CREATE uploads/ directory (if not exists)

  (swim: FastAPI App)
  → ADD CORSMiddleware (allowed origins from ALLOWED_ORIGINS env var)
  → MOUNT /uploads → StaticFiles(uploads/)
  → MOUNT /static → StaticFiles(data/languages/)
  → REGISTER routers: /api/auth, /api/users, /api/content, /api/progress, /api/validate, /api/speech, /api/leaderboard, /api/friends, /api/admin

  (swim: Logger)
  → LOG "Startup complete. Server ready."

  (swim: Uvicorn)
  → BIND to 0.0.0.0:8000
  → BEGIN accepting HTTP connections

END
```

---

## ACTIVITY DIAGRAM 11: JWT Refresh / Token Expiry Handling

**Swimlanes:** User | Frontend (Axios Interceptor) | Browser Storage

```
START
  (swim: User)
  → PERFORMS any action that triggers an API call

  (swim: Frontend)
  → Request interceptor: READ localStorage.getItem("lw_token")
  → ATTACH Authorization: Bearer {token} to request headers

  → SEND request to Backend

  (swim: Frontend)
  → Response interceptor checks status

  [Decision] Response status == 401?
  → [NO] PASS response through normally → END

  → [YES]
  → READ localStorage.getItem("lw_user")
  → PARSE user JSON

  [Decision] user.role == "admin" OR pathname starts with "/admin"?
  → [YES] isAdmin = true
  → [NO] isAdmin = false

  → REMOVE lw_token from localStorage
  → REMOVE lw_user from localStorage
  → CLEAR Redux auth state (implicitly via page reload)

  [Decision] isAdmin?
  → [YES] window.location.href = "/admin/login"
  → [NO] window.location.href = "/login"

  (swim: User)
  → SEES login page
  → MUST log in again to continue

END
```

---

## ACTIVITY DIAGRAM 12: Leaderboard View Flow

**Swimlanes:** User | Frontend | Backend Leaderboard | Database

```
START
  (swim: User)
  → NAVIGATE to /leaderboard

  (swim: Frontend)
  → ProtectedRoute CHECK
  → DETERMINE currentPairId from Redux state
  → SET active tab to "Global"

  fork ──────────────────────────────────────────────────────
  (Global leaderboard)                 │  (Friends leaderboard)
  GET /api/leaderboard/{pairId}        │  GET /api/leaderboard/{pairId}/friends
                                        │
  Backend: JOIN UserLanguageProgress   │  Backend: QUERY accepted FriendRequests
  + User WHERE lang_pair_id = pair_id  │  → collect friend_ids (include self)
  ORDER BY total_xp DESC LIMIT 50      │  → JOIN UserLanguageProgress + User
                                        │  WHERE user_id IN friend_ids
                                        │  ORDER BY total_xp DESC
  RETURN List[LeaderboardEntry]        │  RETURN List[LeaderboardEntry]
  ─────────────────────────────── join ──────────────────────

  (swim: Frontend)
  → RENDER rank table (rank, avatar, username, XP)
  → HIGHLIGHT current user's row

  (swim: User)
  → SWITCH between "Global" and "Friends" tabs

  [Decision] Switched tab?
  → [YES] display pre-fetched data for selected tab
  → [NO] stay on current tab

END
```

---

## ACTIVITY DIAGRAM 13: Onboarding Flow (New User First Login)

**Swimlanes:** User | Frontend | Backend Progress | Database

```
START
  (swim: User)
  → COMPLETES registration (or first login)
  → REDIRECTED to /onboarding (if no active language pair)

  (swim: Frontend)
  → DISPLAY available language pairs (from /api/content/pairs)
  → SHOW pair cards (e.g. Hindi → Japanese, English → Hindi)

  (swim: User)
  → SELECTS a language pair (e.g. "hi-ja")
  → CLICKS "Start Learning"

  (swim: Frontend)
  → DISPATCH startLanguagePair("hi-ja")
  → POST /api/progress/hi-ja/start

  (swim: Backend Progress)
  → QUERY UserLanguageProgress WHERE user_id AND lang_pair_id

  [Decision] Already started?
  → [YES] RETURN existing ProgressOut (idempotent)
  → [NO] INSERT UserLanguageProgress {total_xp=0, current_month=1, current_block=1, current_activity_id=1}
  → COMMIT
  → RETURN ProgressOut

  (swim: Frontend/Redux)
  → ADD new progress to allProgress array in state
  → SET currentPairId = "hi-ja"
  → WRITE "lw_pair" to localStorage

  (swim: Frontend)
  → NAVIGATE to /dashboard

  (swim: User)
  → SEES roadmap with Month 1, Block 1, Activity #1 (lesson) UNLOCKED
  → All other activities LOCKED
  → Begins learning journey

END
```
