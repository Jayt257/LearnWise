# LearnWise — Sequence Diagram Reference

> **Purpose:** Complete reference for building all Sequence Diagrams for the LearnWise platform.  
> Every actor, lifeline, message, return value, condition, and alt/loop/opt block is documented in order.  
> Include ALL of the following scenarios — do NOT omit any.

---

## PARTICIPANTS (Lifelines used across all diagrams)

| Lifeline | Type | Notes |
|---|---|---|
| `Browser / User` | Actor | The human user |
| `React Frontend` | System | React + Vite SPA |
| `Redux Store` | System | Redux Toolkit state |
| `Axios Client` | System | `src/api/client.js` |
| `FastAPI Backend` | System | Uvicorn server |
| `Auth Router` | Component | `/api/auth` |
| `Progress Router` | Component | `/api/progress` |
| `Validate Router` | Component | `/api/validate` |
| `Speech Router` | Component | `/api/speech` |
| `Leaderboard Router` | Component | `/api/leaderboard` |
| `Friends Router` | Component | `/api/friends` |
| `Admin Router` | Component | `/api/admin` |
| `Content Router` | Component | `/api/content` |
| `JWT / Security` | Component | `core/security.py` |
| `Database (PostgreSQL)` | System | SQLAlchemy ORM |
| `Groq AI Service` | External | Groq LLM API |
| `Whisper Service` | Component | Local Whisper model |
| `ContentService` | Component | File-system JSON reader |
| `ScoringService` | Component | Local scoring logic |
| `localStorage` | System | Browser storage |

---

## SEQUENCE 1: User Registration

**Trigger:** User fills the Register form and clicks Submit  
**Route:** POST /api/auth/register

```
User → React Frontend: fills {username, email, password}
React Frontend → Redux Store: dispatch(registerUser(credentials))
Redux Store → Axios Client: POST /api/auth/register {username,email,password}
Axios Client → FastAPI Backend: HTTP POST /api/auth/register

FastAPI Backend → Auth Router: registerUser(req)
Auth Router → Database: query User WHERE email == req.email
Database → Auth Router: User (or None)

ALT email already exists:
  Auth Router → FastAPI Backend: HTTPException 400 "Email already registered"
  FastAPI Backend → Axios Client: 400 Error
  Axios Client → Redux Store: rejectWithValue("Email already registered")
  Redux Store → React Frontend: state.error = "Email already registered"
  React Frontend → User: show error toast

ALT username already taken:
  Auth Router → Database: query User WHERE username == req.username
  Database → Auth Router: User found
  Auth Router → FastAPI Backend: HTTPException 400 "Username already taken"
  (same error path as above)

ELSE success:
  Auth Router → Security: hash_password(req.password)
  Security → Auth Router: password_hash (bcrypt)
  Auth Router → Database: INSERT User {username, email, password_hash, role=user}
  Database → Auth Router: User (with id)
  Auth Router → Security: create_access_token({sub: user.id, role: "user"})
  Security → Auth Router: JWT string
  Auth Router → FastAPI Backend: TokenResponse {access_token, token_type:"bearer", user}
  FastAPI Backend → Axios Client: 201 TokenResponse
  Axios Client → Redux Store: resolved payload
  Redux Store → localStorage: setItem("lw_token", token); setItem("lw_user", user)
  Redux Store → React Frontend: state.isAuthenticated=true, state.user=user
  React Frontend → User: navigate("/dashboard")
```

---

## SEQUENCE 2: User Login

**Trigger:** User fills Login form, clicks Login  
**Route:** POST /api/auth/login

```
User → React Frontend: fills {email, password}
React Frontend → Redux Store: dispatch(loginUser({email, password}))
Redux Store → Axios Client: POST /api/auth/login
Axios Client → FastAPI Backend: HTTP POST /api/auth/login

FastAPI Backend → Auth Router: login(req)
Auth Router → Database: query User WHERE email == req.email AND role == "user"
Database → Auth Router: User or None

ALT user not found OR wrong password:
  Auth Router → Security: verify_password(req.password, user.password_hash)
  Security → Auth Router: False
  Auth Router → FastAPI Backend: HTTPException 401 "Invalid email or password"
  FastAPI Backend → Axios Client: 401
  Axios Client → Redux Store: rejectWithValue(...)
  Redux Store → React Frontend: state.error = "Invalid email or password"
  React Frontend → User: show error

ALT user is_active == False:
  Auth Router → FastAPI Backend: HTTPException 403 "Account is deactivated"

ELSE success:
  Auth Router → Security: verify_password(req.password, user.password_hash) → True
  Auth Router → Database: UPDATE User.last_active = utcnow()
  Auth Router → Security: create_access_token({sub: user.id, role: "user"})
  Security → Auth Router: JWT string
  Auth Router → FastAPI Backend: 200 TokenResponse
  FastAPI Backend → Axios Client: 200 TokenResponse
  Axios Client → Redux Store: resolved
  Redux Store → localStorage: store token + user
  Redux Store → React Frontend: isAuthenticated = true
  React Frontend → User: navigate("/dashboard")
```

---

## SEQUENCE 3: JWT Authentication on Every Protected Request

**Trigger:** Any API call to a protected endpoint  
**Used by:** ALL /api/* endpoints except /api/auth/register and /api/auth/login

```
Axios Client → Axios Client: request interceptor reads localStorage.getItem("lw_token")
Axios Client → FastAPI Backend: HTTP request with "Authorization: Bearer {token}"

FastAPI Backend → Dependencies: get_current_user(credentials, db)
Dependencies → Security: decode_token(token)
Security → Dependencies: payload {sub: user_id, role, exp} OR None

ALT token invalid/expired:
  Dependencies → FastAPI Backend: HTTPException 401 "Invalid or missing authentication token"
  FastAPI Backend → Axios Client: 401
  Axios Client → Axios Client: response interceptor triggers
  Axios Client → localStorage: removeItem("lw_token"), removeItem("lw_user")

  ALT user is admin:
    Axios Client → Browser: redirect to /admin/login
  ELSE:
    Axios Client → Browser: redirect to /login

ELSE valid token:
  Dependencies → Database: query User WHERE id == user_id AND is_active == True
  Database → Dependencies: User object
  Dependencies → FastAPI Backend: return User (injected into endpoint)
```

---

## SEQUENCE 4: Dashboard Load

**Trigger:** User navigates to /dashboard  
**Multiple parallel API calls**

```
React Frontend → Redux Store: dispatch(fetchAllProgress())
React Frontend → Redux Store: dispatch(fetchPairs())

PARALLEL {
  Redux Store → Axios Client: GET /api/progress
  Axios Client → FastAPI Backend: GET /api/progress (with JWT)
  FastAPI Backend → Progress Router: get_all_progress()
  Progress Router → Database: query UserLanguageProgress WHERE user_id == current_user.id
  Database → Progress Router: List[UserLanguageProgress]
  Progress Router → FastAPI Backend: List[ProgressOut]
  FastAPI Backend → Axios Client: 200 List[ProgressOut]
  Axios Client → Redux Store: state.allProgress = [...]

  Redux Store → Axios Client: GET /api/content/pairs
  Axios Client → FastAPI Backend: GET /api/content/pairs
  FastAPI Backend → Content Router: get_all_pairs()
  Content Router → ContentService: get_all_pairs()
  ContentService → FileSystem: walk data/languages/*/* directories
  FileSystem → ContentService: pair IDs
  ContentService → Content Router: List[{id, source, target}]
  Content Router → FastAPI Backend: 200 pairs list
  FastAPI Backend → Axios Client: 200
  Axios Client → Redux Store: state.pairs = [...]
}

Redux Store → React Frontend: allProgress, pairs ready
React Frontend → React Frontend: auto-select first pair if currentPairId is null

React Frontend → Axios Client: GET /api/content/{pairId}/meta
Axios Client → FastAPI Backend: GET /api/content/{pairId}/meta
FastAPI Backend → Content Router: get_meta(pair_id)
Content Router → ContentService: get_meta(pair_id)
ContentService → FileSystem: read data/languages/{src}/{tgt}/meta.json
FileSystem → ContentService: meta JSON {months: [...blocks: [...activities]]}
ContentService → Content Router: meta dict
Content Router → FastAPI Backend: 200 meta
FastAPI Backend → Axios Client: 200 meta
Axios Client → React Frontend: meta data

React Frontend → Axios Client: GET /api/progress/{pairId}/completions
Axios Client → FastAPI Backend: GET /api/progress/{pairId}/completions
FastAPI Backend → Progress Router: get_completions(pair_id)
Progress Router → Database: query ActivityCompletion WHERE user_id AND lang_pair_id
Database → Progress Router: List[ActivityCompletion]
Progress Router → FastAPI Backend: List[CompletionOut]
FastAPI Backend → Axios Client: 200 List[CompletionOut]
Axios Client → React Frontend: completions array

React Frontend → React Frontend: build completedSeqIds = Set of passed activity_seq_ids
React Frontend → React Frontend: determine isUnlocked(seqId) = seqId <= current_activity_id
React Frontend → User: render roadmap (months → blocks → activity nodes, colored by type)
```

---

## SEQUENCE 5: Activity Start (Click on Activity Node)

**Trigger:** User clicks an unlocked activity node on the dashboard

```
User → DashboardPage: click activity node (if isUnlocked)
DashboardPage → Router: navigate("/activity/{pairId}/{activityType}", {
    state: {
      activityFile,        // e.g. "month_1/block_1/M1B1_lesson.json"
      activitySeqId,       // e.g. 1
      activityJsonId,      // null (set after load)
      maxXP,              // e.g. 100
      label,              // e.g. "lesson"
      monthNumber,        // e.g. 1
      blockNumber         // e.g. 1
    }
})
Router → ActivityRouter: render /activity/:pairId/:type
ActivityRouter → ActivityRouter: lookup ACTIVITY_COMPONENTS[type]

ALT activityFile missing:
  ActivityRouter → User: show "Activity not found" message with ← Back button

ALT type not in ACTIVITY_COMPONENTS:
  ActivityRouter → User: show "Unknown activity type" error

ELSE valid:
  ActivityRouter → SpecificActivityPage: render with props

SpecificActivityPage → Axios Client: GET /api/content/{pairId}/activity?file={activityFile}
Axios Client → FastAPI Backend: GET /api/content/{pairId}/activity?file=...
FastAPI Backend → Content Router: get_content_file(pair_id, file_path)
Content Router → ContentService: get_content_file(pair_id, file_path)
ContentService → FileSystem: read data/languages/{src}/{tgt}/{file_path}.json
FileSystem → ContentService: activity JSON
ContentService → Content Router: dict
Content Router → FastAPI Backend: 200 dict
FastAPI Backend → Axios Client: 200 activity JSON
Axios Client → SpecificActivityPage: activity data (JSON)

SpecificActivityPage → User: render activity UI (content, questions, audio if available)
```

---

## SEQUENCE 6: Activity Submission and Scoring (Groq Path — lesson/reading/writing/speaking/pronunciation/listening/vocab)

**Trigger:** User clicks Submit on an open-ended activity

```
User → ActivityPage: click Submit
ActivityPage → ActivityPage: build payload {
    activity_id, activity_type, lang_pair_id, max_xp,
    user_lang, target_lang, attempt_count,
    questions: [{question_id, block_type, user_answer, correct_answer, prompt}]
}

ActivityPage → Axios Client: POST /api/validate {payload}
Axios Client → FastAPI Backend: POST /api/validate

FastAPI Backend → Validate Router: validate_activity(req)
Validate Router → Validate Router: check req.questions not empty (else HTTPException 400)

ALT activity_type in MCQ_TYPES ("test"):
  Validate Router → ScoringService: score_mcq_locally(req.questions, req.max_xp)
  ScoringService → ScoringService: compare str(user_answer) == str(correct_answer) per question
  ScoringService → ScoringService: call calculate_score() internally
  ScoringService → Validate Router: {total_score, percentage, passed, question_results}
  Validate Router → Validate Router: set overall_feedback based on passed bool

ELSE (GROQ_TYPES — lesson/vocab/reading/writing/listening/speaking/pronunciation):
  Validate Router → GroqService: validate_activity(type, questions, max_xp, user_lang, target_lang, attempt_count)
  GroqService → GroqService: _build_prompt(activity_type, questions, max_xp, user_lang, target_lang, feedback_tier)
    NOTE: prompt includes rubric, scoring rules, generosity guidelines, romanization rules
  GroqService → Groq AI Service: POST completions {model:"llama3-8b-8192", messages:[{role:system,content:prompt}], temperature:0.1}
  Groq AI Service → GroqService: JSON response {question_results:[{question_id, score, correct, feedback}], overall_feedback, suggestion}
  GroqService → GroqService: parse JSON, merge user_answer + correct_answer from original questions
  GroqService → Validate Router: groq_result dict

  Validate Router → ScoringService: calculate_score(req.questions, req.max_xp, groq_scores)
  ScoringService → ScoringService: clamp each score to [0, per_q_max], sum
  ScoringService → ScoringService: percentage = (total / max_xp) * 100
  ScoringService → ScoringService: passed = percentage >= 20.0
  ScoringService → Validate Router: {total_score, percentage, passed, question_results}

Validate Router → GroqService: _determine_feedback_tier(percentage, attempt_count)
  NOTE: tier logic:
    attempt >= 3 OR percentage < 30% → "hint"
    percentage >= 80% → "praise"
    else → "lesson"
GroqService → Validate Router: feedback_tier string

ALT feedback_tier != "lesson" AND activity_type in GROQ_TYPES:
  Validate Router → GroqService: generate_tier_feedback(type, tier, feedback, suggestion, user_lang, target_lang)
  GroqService → Groq AI Service: second Groq call for refined feedback
  Groq AI Service → GroqService: {overall_feedback, suggestion}
  GroqService → Validate Router: refined feedback

ALT SCORE_THRESHOLD_OVERRIDE > 0:
  Validate Router → Validate Router: effective_passed = total_score >= SCORE_THRESHOLD_OVERRIDE

Validate Router → FastAPI Backend: ValidateResponse {activity_id, total_score, max_score, percentage, passed, feedback, suggestion, question_results, feedback_tier}
FastAPI Backend → Axios Client: 200 ValidateResponse
Axios Client → ActivityPage: result

ActivityPage → ActivityPage: show ScoreModal {score, passed, feedback, suggestion, feedback_tier}
```

---

## SEQUENCE 7: Activity Completion Recording (After Submit)

**Trigger:** After receiving ValidateResponse, the activity page records completion

```
ActivityPage → Axios Client: POST /api/progress/{pairId}/complete {
    activity_seq_id,
    activity_json_id,
    activity_type,
    lang_pair_id,
    month_number,
    block_number,
    score_earned: total_score,
    max_score,
    passed: effective_passed,
    ai_feedback: feedback,
    ai_suggestion: suggestion
}

Axios Client → FastAPI Backend: POST /api/progress/{pairId}/complete
FastAPI Backend → Progress Router: complete_activity(pair_id, req)

Progress Router → Progress Router: apply SCORE_THRESHOLD_OVERRIDE if > 0

Progress Router → Progress Router: derive month/block if not provided
  _derive_month_block(activity_seq_id):
    zero_based = activity_seq_id - 1
    month = (zero_based // 48) + 1
    block = ((zero_based % 48) // 8) + 1

Progress Router → Database: query UserLanguageProgress WHERE user_id AND lang_pair_id

ALT progress record not found:
  Progress Router → Database: INSERT new UserLanguageProgress (month=1, block=1, activity=req.seq_id)

Progress Router → Database: query ActivityCompletion WHERE user_id AND lang_pair_id AND activity_seq_id

ALT completion already exists (retry):
  ALT new score > existing.score_earned:
    Progress Router → Progress Router: xp_delta = new_score - old_score
    Progress Router → Database: UPDATE completion.score_earned, passed
  Progress Router → Database: UPDATE completion.attempts += 1, ai_feedback, completed_at

ELSE first attempt:
  Progress Router → Progress Router: xp_delta = score_earned
  Progress Router → Database: INSERT ActivityCompletion {all fields}

Progress Router → Database: UPDATE progress.total_xp += xp_delta
Progress Router → Database: UPDATE progress.last_activity_at = utcnow()

ALT effective_passed AND req.activity_seq_id == progress.current_activity_id:
  Progress Router → Progress Router: next_id = current_activity_id + 1
  Progress Router → Database: UPDATE progress.current_activity_id = next_id
  Progress Router → Database: UPDATE progress.current_month, current_block = _derive_month_block(next_id)
  NOTE: This is the UNLOCK mechanism — the next activity becomes accessible

Progress Router → Database: commit + refresh
Progress Router → FastAPI Backend: CompletionOut
FastAPI Backend → Axios Client: 200 CompletionOut
Axios Client → ActivityPage: completion record

ActivityPage → Redux Store: dispatch(fetchPairProgress(pairId)) [refresh progress]
ActivityPage → User: show XPBurst animation if XP earned
```

---

## SEQUENCE 8: Speech Transcription (Speaking / Pronunciation Activity)

**Trigger:** User finishes recording and clicks Stop / Submit

```
User → AudioRecorder: clicks record button
AudioRecorder → Browser MediaRecorder API: mediaRecorder.start()
Browser MediaRecorder API → AudioRecorder: dataavailable events (audio chunks)
User → AudioRecorder: clicks stop button
AudioRecorder → Browser MediaRecorder API: mediaRecorder.stop()
Browser MediaRecorder API → AudioRecorder: final chunk + stop event
AudioRecorder → AudioRecorder: concatenate chunks → Blob(webm/audio)

AudioRecorder → Axios Client: POST /api/speech/transcribe (multipart FormData: audio file)
Axios Client → FastAPI Backend: POST /api/speech/transcribe

FastAPI Backend → Speech Router: transcribe(audio: UploadFile)
Speech Router → Speech Router: validate MIME type using startswith()

ALT MIME type not allowed:
  Speech Router → FastAPI Backend: HTTPException 400 "Unsupported audio format"

Speech Router → Speech Router: audio_bytes = await audio.read()

ALT len(audio_bytes) < 100:
  Speech Router → FastAPI Backend: HTTPException 400 "Audio too small"

ALT len(audio_bytes) > 25MB:
  Speech Router → FastAPI Backend: HTTPException 413 "Audio too large"

Speech Router → Whisper Service: transcribe_audio(audio_bytes, filename)
Whisper Service → Whisper Service: _load_model() [lazy-load on first call]

ALT Whisper not installed / model load failed:
  Whisper Service → Speech Router: {text:"", language:"unknown", confidence:None, is_mock:True}
  Speech Router → FastAPI Backend: TranscribeResponse(is_mock=True)
  FastAPI Backend → Axios Client: 200 {is_mock:True}
  Axios Client → AudioRecorder: is_mock=True
  AudioRecorder → User: show "Whisper unavailable — demo mode" warning

ELSE Whisper available:
  Whisper Service → ffmpeg: transcode audio to 16kHz 1-channel WAV (temp file)
  ffmpeg → Whisper Service: out.wav path
  Whisper Service → _whisper_model: transcribe(out_wav, fp16=False)
  _whisper_model → Whisper Service: {text, language, segments}
  Whisper Service → Whisper Service: calculate avg_confidence from segments (1 - no_speech_prob)
  Whisper Service → Whisper Service: cleanup temp files
  Whisper Service → Speech Router: {text, language, confidence, is_mock:False}
  Speech Router → FastAPI Backend: TranscribeResponse
  FastAPI Backend → Axios Client: 200 TranscribeResponse
  Axios Client → ActivityPage (SpeakingPage/PronunciationPage): {text, confidence, is_mock}

ActivityPage → ActivityPage: populate user_answer with transcribed text
ActivityPage → User: display transcription, enable Submit button
```

---

## SEQUENCE 9: Friend Request Flow

**Full flow from search to accepted friend**

```
--- SEARCH ---
User → SearchFriendsPage: types username query
SearchFriendsPage → Axios Client: GET /api/users/search?q={query}
Axios Client → FastAPI Backend: GET /api/users/search?q={query}
FastAPI Backend → Users Router: search_users(q, limit=20)
Users Router → Database: query User WHERE username ILIKE %q% AND id != current AND is_active
Database → Users Router: List[User]
Users Router → FastAPI Backend: UserSearchResult {users, total}
FastAPI Backend → Axios Client: 200 UserSearchResult
Axios Client → SearchFriendsPage: display user cards

--- SEND REQUEST ---
User → SearchFriendsPage: clicks "Add Friend" on a user card
SearchFriendsPage → Axios Client: POST /api/friends/request/{target_user_id}
Axios Client → FastAPI Backend: POST /api/friends/request/{user_id}
FastAPI Backend → Friends Router: send_request(user_id)
Friends Router → Friends Router: check current_user.id != user_id (else 400)
Friends Router → Database: query User (target)
ALT target not found: HTTPException 404
Friends Router → Database: query FriendRequest (existing between pair)
ALT request already exists: HTTPException 400 "Request already exists"
Friends Router → Database: INSERT FriendRequest {sender_id, receiver_id, status="pending"}
Friends Router → FastAPI Backend: {message:"Friend request sent", request_id}
FastAPI Backend → Axios Client: 201
Axios Client → SearchFriendsPage: show "Request sent" feedback

--- ACCEPT REQUEST ---
User B → SearchFriendsPage (Receiver): opens friend requests
SearchFriendsPage → Axios Client: GET /api/friends/requests
Axios Client → Friends Router: get_incoming_requests()
Friends Router → Database: query FriendRequest WHERE receiver_id == current_user AND status=="pending"
Database → Friends Router: List[FriendRequest]
Friends Router → FastAPI Backend: {requests, total}
FastAPI Backend → Axios Client: 200
Axios Client → User B: show pending requests

User B → SearchFriendsPage: clicks Accept on a request
SearchFriendsPage → Axios Client: PUT /api/friends/request/{req_id}/accept
Axios Client → Friends Router: accept_request(req_id)
Friends Router → Database: find FriendRequest WHERE id==req_id AND receiver_id==current AND status=="pending"
ALT not found: 404
Friends Router → Database: UPDATE FriendRequest.status = "accepted"
Friends Router → FastAPI Backend: {message:"Accepted"}
FastAPI Backend → Axios Client: 200

--- FRIENDS LEADERBOARD ---
Both User A and User B appear on each other's /leaderboard/{pairId}/friends results.
```

---

## SEQUENCE 10: Leaderboard Load

```
User → LeaderboardPage: navigates to /leaderboard
LeaderboardPage → Axios Client: GET /api/leaderboard/{pairId}?limit=50
Axios Client → FastAPI Backend: GET /api/leaderboard/{pairId}
FastAPI Backend → Leaderboard Router: get_leaderboard(pair_id, limit=50)
Leaderboard Router → Database: JOIN UserLanguageProgress + User WHERE lang_pair_id=pair_id AND is_active ORDER BY total_xp DESC LIMIT 50
Database → Leaderboard Router: List[(UserLanguageProgress, User)]
Leaderboard Router → FastAPI Backend: List[LeaderboardEntry {rank, user_id, username, display_name, avatar_url, total_xp}]
FastAPI Backend → Axios Client: 200 List[LeaderboardEntry]
Axios Client → LeaderboardPage: global leaderboard data

LeaderboardPage → Axios Client: GET /api/leaderboard/{pairId}/friends
Axios Client → FastAPI Backend: GET /api/leaderboard/{pairId}/friends
FastAPI Backend → Leaderboard Router: get_friends_leaderboard(pair_id)
Leaderboard Router → Database: query accepted FriendRequests involving current_user
Database → Leaderboard Router: friend_ids set (includes current_user.id)
Leaderboard Router → Database: JOIN UserLanguageProgress + User WHERE user_id IN friend_ids AND lang_pair_id ORDER BY total_xp DESC
Database → Leaderboard Router: List[(UserLanguageProgress, User)]
Leaderboard Router → FastAPI Backend: List[LeaderboardEntry]
FastAPI Backend → Axios Client: 200 List[LeaderboardEntry]
Axios Client → LeaderboardPage: friends leaderboard data

LeaderboardPage → User: render both global + friends leaderboard tabs
```

---

## SEQUENCE 11: Admin Curriculum Management (Create Language Pair)

```
Admin User → AdminDashboard: fills "New Language Pair" form (e.g. "hi-ja")
AdminDashboard → Axios Client: POST /api/admin/content/pairs {pair_id: "hi-ja"}
Axios Client → FastAPI Backend: POST /api/admin/content/pairs (with admin JWT)

FastAPI Backend → Admin Router: create_pair(pair_id)
Admin Router → Dependencies: require_admin() [validates role == "admin"]
Admin Router → ContentService: scaffold_pair("hi-ja")

ContentService → FileSystem: create data/languages/hi/ja/meta.json
ContentService → FileSystem: create 3 months × 6 blocks = 18 blocks
  LOOP for each month (1-3):
    LOOP for each block (1-6):
      LOOP for each activity type (lesson, vocab, reading, writing, listening, speaking, pronunciation, test):
        ContentService → FileSystem: create month_{m}/block_{b}/M{m}B{b}_{type}.json

ContentService → Admin Router: success

Admin Router → FastAPI Backend: {message: "Pair hi-ja created", files_created: N}
FastAPI Backend → Axios Client: 201 success
Axios Client → AdminDashboard: show success notification
AdminDashboard → AdminDashboard: refresh pairs list
```

---

## SEQUENCE 12: App Startup / Server Initialization

```
Uvicorn → FastAPI (lifespan): startup event

FastAPI → Database: create_tables()
Database → Database: import all ORM models (user, progress, friends)
Database → PostgreSQL: Base.metadata.create_all() (creates tables if not exist)
PostgreSQL → Database: tables confirmed

FastAPI → main.py: seed_admin()
main.py → Database (SessionLocal): open session
main.py → Database: query User WHERE email == ADMIN_EMAIL
Database → main.py: existing admin or None

ALT admin exists:
  main.py → Logger: "Admin user already exists"

ELSE:
  main.py → Security: hash_password(ADMIN_PASSWORD)
  Security → main.py: hashed password
  main.py → Database: INSERT User {role=admin, email=ADMIN_EMAIL, ...}
  Database → main.py: committed
  main.py → Logger: "Admin user created: admin@learnwise.app"

FastAPI → FileSystem: create uploads/ directory (if not exists)
FastAPI → FastAPI: mount /uploads → StaticFiles(uploads/)
FastAPI → FastAPI: mount /static → StaticFiles(data/languages/)
FastAPI → FastAPI: register all routers (auth, users, content, progress, validate, speech, leaderboard, friends, admin) under /api prefix

FastAPI → Logger: "Startup complete. Server ready."
```

---

## SEQUENCE 13: 401 Token Expiry / Auto-Logout

```
Axios Client → FastAPI Backend: any API request
FastAPI Backend → Security: decode_token(token)
Security → FastAPI Backend: JWTError (token expired)
FastAPI Backend → Axios Client: 401 Unauthorized

Axios Client → Axios Client: response interceptor triggers
Axios Client → localStorage: check lw_user.role

ALT role == "admin" OR path starts with /admin:
  Axios Client → Browser: window.location.href = "/admin/login"

ELSE:
  Axios Client → localStorage: removeItem("lw_token"), removeItem("lw_user")
  Axios Client → Browser: window.location.href = "/login"

Browser → User: show Login page (session expired)
```
