# LearnWise — Class Diagram Reference

> **Purpose:** Complete reference for building the Class Diagram for the LearnWise AI language‑learning platform.  
> All class names, attributes (with types), methods, relationships, multiplicities, and notes are documented here.  
> Do NOT omit any class. Do NOT omit any attribute.

---

## LAYER 1 — BACKEND DATABASE MODELS (`backend/app/models/`)

### Class: `User`
**File:** `backend/app/models/user.py`  
**Table:** `users`  
**Stereotype:** `<<SQLAlchemy ORM>>`

| Attribute | Type | Constraint |
|---|---|---|
| `id` | UUID (PK) | auto-generated, uuid4 |
| `username` | String(50) | UNIQUE, NOT NULL, indexed |
| `email` | String(255) | UNIQUE, NOT NULL, indexed |
| `password_hash` | String(255) | NOT NULL |
| `display_name` | String(100) | nullable |
| `avatar_url` | String(500) | nullable |
| `native_lang` | String(5) | nullable, default "en" |
| `role` | Enum(UserRole) | NOT NULL, default "user" |
| `is_active` | Boolean | default True |
| `created_at` | DateTime | default utcnow |
| `last_active` | DateTime | default utcnow, on update utcnow |

**Methods:**
- `__repr__() -> str`

**Relationships:**
- `language_progress` → `UserLanguageProgress` (1‑to‑many, cascade delete‑orphan)
- `activity_completions` → `ActivityCompletion` (1‑to‑many, cascade delete‑orphan)
- `sent_requests` → `FriendRequest[sender_id]` (1‑to‑many, cascade delete‑orphan)
- `received_requests` → `FriendRequest[receiver_id]` (1‑to‑many, cascade delete‑orphan)

---

### Enum: `UserRole`
**File:** `backend/app/models/user.py`  
**Stereotype:** `<<Enum>>`

| Value |
|---|
| `user` |
| `admin` |

---

### Class: `UserLanguageProgress`
**File:** `backend/app/models/progress.py`  
**Table:** `user_language_progress`  
**Stereotype:** `<<SQLAlchemy ORM>>`  
**Unique Constraint:** (`user_id`, `lang_pair_id`)

| Attribute | Type | Constraint |
|---|---|---|
| `id` | UUID (PK) | auto-generated |
| `user_id` | UUID (FK → users.id) | NOT NULL, CASCADE DELETE |
| `lang_pair_id` | String(10) | NOT NULL e.g. "hi-ja" |
| `total_xp` | Integer | default 0 |
| `current_month` | Integer | default 1 |
| `current_block` | Integer | default 1 |
| `current_activity_id` | Integer | default 1, global seq 1–144 |
| `started_at` | DateTime | default utcnow |
| `last_activity_at` | DateTime | default utcnow, on update |

**Methods:**
- `__repr__() -> str`

**Relationships:**
- `user` → `User` (many‑to‑1, back_populates="language_progress")

---

### Class: `ActivityCompletion`
**File:** `backend/app/models/progress.py`  
**Table:** `activity_completions`  
**Stereotype:** `<<SQLAlchemy ORM>>`  
**Unique Constraint:** (`user_id`, `lang_pair_id`, `activity_seq_id`)

| Attribute | Type | Constraint |
|---|---|---|
| `id` | UUID (PK) | auto-generated |
| `user_id` | UUID (FK → users.id) | NOT NULL, CASCADE DELETE |
| `lang_pair_id` | String(10) | NOT NULL |
| `activity_seq_id` | Integer | NOT NULL, default 1 |
| `activity_json_id` | String(80) | nullable e.g. "ja_hi_M1B1_lesson_1" |
| `activity_type` | String(20) | NOT NULL (lesson/pronunciation/reading/writing/listening/vocabulary/speaking/test) |
| `month_number` | Integer | nullable |
| `block_number` | Integer | nullable |
| `score_earned` | Integer | default 0 |
| `max_score` | Integer | NOT NULL |
| `passed` | Boolean | default False |
| `attempts` | Integer | default 1 |
| `ai_feedback` | Text | nullable |
| `ai_suggestion` | Text | nullable |
| `completed_at` | DateTime | default utcnow |

**Methods:**
- `__repr__() -> str`

**Relationships:**
- `user` → `User` (many‑to‑1, back_populates="activity_completions")

---

### Class: `FriendRequest`
**File:** `backend/app/models/friends.py`  
**Table:** `friend_requests`  
**Stereotype:** `<<SQLAlchemy ORM>>`  
**Unique Constraint:** (`sender_id`, `receiver_id`)

| Attribute | Type | Constraint |
|---|---|---|
| `id` | UUID (PK) | auto-generated |
| `sender_id` | UUID (FK → users.id) | NOT NULL, CASCADE DELETE |
| `receiver_id` | UUID (FK → users.id) | NOT NULL, CASCADE DELETE |
| `status` | Enum(FriendRequestStatus) | NOT NULL, default "pending" |
| `created_at` | DateTime | default utcnow |
| `updated_at` | DateTime | default utcnow, on update |

**Methods:**
- `__repr__() -> str`

**Relationships:**
- `sender` → `User[sender_id]` (many‑to‑1)
- `receiver` → `User[receiver_id]` (many‑to‑1)

---

### Enum: `FriendRequestStatus`
**File:** `backend/app/models/friends.py`  
**Stereotype:** `<<Enum>>`

| Value |
|---|
| `pending` |
| `accepted` |
| `declined` |

---

## LAYER 2 — BACKEND PYDANTIC SCHEMAS (`backend/app/schemas/`)

### Class: `RegisterRequest`
**File:** `backend/app/schemas/auth.py`  
**Stereotype:** `<<Pydantic Schema>>`

| Field | Type | Validation |
|---|---|---|
| `username` | str | 3–50 chars, alphanumeric+underscore, lowercased |
| `email` | EmailStr | valid email |
| `password` | str | min 8 chars |
| `display_name` | Optional[str] | — |
| `native_lang` | Optional[str] | default "en" |

**Methods:**
- `username_valid(v) -> str` (validator)
- `password_strong(v) -> str` (validator)

---

### Class: `LoginRequest`
**File:** `backend/app/schemas/auth.py`  
**Stereotype:** `<<Pydantic Schema>>`

| Field | Type |
|---|---|
| `email` | EmailStr |
| `password` | str |

---

### Class: `AdminLoginRequest`
**File:** `backend/app/schemas/auth.py`  
**Stereotype:** `<<Pydantic Schema>>`

| Field | Type |
|---|---|
| `email` | EmailStr |
| `password` | str |

---

### Class: `TokenResponse`
**File:** `backend/app/schemas/auth.py`  
**Stereotype:** `<<Pydantic Schema>>`

| Field | Type |
|---|---|
| `access_token` | str |
| `token_type` | str (default "bearer") |
| `user` | UserOut |

---

### Class: `UserOut`
**File:** `backend/app/schemas/auth.py`  
**Stereotype:** `<<Pydantic Schema>>`

| Field | Type |
|---|---|
| `id` | UUID |
| `username` | str |
| `email` | str |
| `display_name` | Optional[str] |
| `avatar_url` | Optional[str] |
| `native_lang` | Optional[str] |
| `role` | str |

---

### Class: `UserProfileOut`
**File:** `backend/app/schemas/user.py`  
**Stereotype:** `<<Pydantic Schema>>`

| Field | Type |
|---|---|
| `id` | UUID |
| `username` | str |
| `display_name` | Optional[str] |
| `avatar_url` | Optional[str] |
| `native_lang` | Optional[str] |
| `role` | str |
| `created_at` | datetime |
| `last_active` | Optional[datetime] |

---

### Class: `UserPublicOut`
**File:** `backend/app/schemas/user.py`  
**Stereotype:** `<<Pydantic Schema>>`

| Field | Type |
|---|---|
| `id` | UUID |
| `username` | str |
| `display_name` | Optional[str] |
| `avatar_url` | Optional[str] |
| `native_lang` | Optional[str] |

---

### Class: `UpdateProfileRequest`
**File:** `backend/app/schemas/user.py`

| Field | Type |
|---|---|
| `display_name` | Optional[str] |
| `avatar_url` | Optional[str] |
| `native_lang` | Optional[str] |

---

### Class: `UserSearchResult`
**File:** `backend/app/schemas/user.py`

| Field | Type |
|---|---|
| `users` | List[UserPublicOut] |
| `total` | int |

---

### Class: `ProgressOut`
**File:** `backend/app/schemas/progress.py`  
**Stereotype:** `<<Pydantic Schema>>`

| Field | Type |
|---|---|
| `id` | UUID |
| `user_id` | UUID |
| `lang_pair_id` | str |
| `total_xp` | int |
| `current_month` | int |
| `current_block` | int |
| `current_activity_id` | int |
| `started_at` | Optional[datetime] |
| `last_activity_at` | Optional[datetime] |

---

### Class: `CompleteActivityRequest`
**File:** `backend/app/schemas/progress.py`

| Field | Type |
|---|---|
| `activity_seq_id` | int |
| `activity_json_id` | Optional[str] |
| `activity_type` | str |
| `lang_pair_id` | str |
| `month_number` | Optional[int] |
| `block_number` | Optional[int] |
| `score_earned` | int |
| `max_score` | int |
| `passed` | bool |
| `ai_feedback` | Optional[str] |
| `ai_suggestion` | Optional[str] |

---

### Class: `CompletionOut`
**File:** `backend/app/schemas/progress.py`

| Field | Type |
|---|---|
| `id` | UUID |
| `activity_seq_id` | int |
| `activity_json_id` | Optional[str] |
| `activity_type` | str |
| `month_number` | Optional[int] |
| `block_number` | Optional[int] |
| `score_earned` | int |
| `max_score` | int |
| `passed` | bool |
| `attempts` | int |
| `ai_feedback` | Optional[str] |
| `ai_suggestion` | Optional[str] |
| `completed_at` | datetime |

---

### Class: `LeaderboardEntry`
**File:** `backend/app/schemas/progress.py`

| Field | Type |
|---|---|
| `rank` | int |
| `user_id` | UUID |
| `username` | str |
| `display_name` | Optional[str] |
| `avatar_url` | Optional[str] |
| `total_xp` | int |

---

### Class: `QuestionSubmission`
**File:** `backend/app/schemas/activity.py`

| Field | Type | Notes |
|---|---|---|
| `question_id` | str | e.g. "b1" |
| `block_type` | str | quiz/fill_blank/writing/speaking/etc |
| `user_answer` | Any | str, int, or list |
| `correct_answer` | Optional[Any] | — |
| `prompt` | Optional[str] | — |
| `sample_answer` | Optional[str] | — |

**Constants:**
- `MAX_ANSWER_LENGTH = 2000`
- `MAX_QUESTIONS = 50`

**Methods:**
- `validate_answer_length(v) -> Any`
- `validate_prompt_length(v) -> Optional[str]`

---

### Class: `ValidateRequest`
**File:** `backend/app/schemas/activity.py`

| Field | Type | Notes |
|---|---|---|
| `activity_id` | int | — |
| `activity_type` | str | lesson/vocab/reading/writing/listening/speaking/pronunciation/test |
| `lang_pair_id` | str | — |
| `max_xp` | int | — |
| `user_lang` | str | default "hi" |
| `target_lang` | str | default "en" |
| `questions` | List[QuestionSubmission] | max 50 |
| `attempt_count` | int | default 1 |

**Methods:**
- `validate_questions_count(v) -> list`
- `validate_max_xp(v) -> int`
- `validate_activity_type(v) -> str`

---

### Class: `ValidateResponse`
**File:** `backend/app/schemas/activity.py`

| Field | Type |
|---|---|
| `activity_id` | int |
| `total_score` | int |
| `max_score` | int |
| `percentage` | float |
| `passed` | bool |
| `feedback` | str |
| `suggestion` | str |
| `question_results` | List[QuestionResult] |
| `feedback_tier` | str (hint/lesson/praise) |

---

### Class: `QuestionResult`
**File:** `backend/app/schemas/activity.py`

| Field | Type |
|---|---|
| `question_id` | str |
| `correct` | bool |
| `score` | int |
| `feedback` | Optional[str] |
| `user_answer` | Optional[Any] |
| `correct_answer` | Optional[Any] |

---

### Class: `TranscribeResponse`
**File:** `backend/app/schemas/activity.py`

| Field | Type |
|---|---|
| `text` | str |
| `confidence` | Optional[float] |
| `language` | Optional[str] |
| `is_mock` | bool (default False) |

---

## LAYER 3 — BACKEND CORE (`backend/app/core/`)

### Class: `Settings`
**File:** `backend/app/core/config.py`  
**Stereotype:** `<<Pydantic BaseSettings>>`

| Attribute | Type | Default |
|---|---|---|
| `APP_NAME` | str | "LearnWise" |
| `DEBUG` | bool | True |
| `DATABASE_URL` | str | required |
| `SECRET_KEY` | str | required |
| `ALGORITHM` | str | "HS256" |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | 10080 (7 days) |
| `GROQ_API_KEY` | str | required |
| `GROQ_MODEL` | str | "llama3-8b-8192" |
| `WHISPER_MODEL` | str | "small" |
| `ALLOWED_ORIGINS` | str | "http://localhost:5173" |
| `ADMIN_EMAIL` | str | "admin@learnwise.app" |
| `ADMIN_PASSWORD` | str | "Admin@LearnWise2026" |
| `ADMIN_USERNAME` | str | "admin" |
| `SCORE_THRESHOLD_OVERRIDE` | int | -1 (disabled) |
| `DATA_DIR` | str | "data" |

**Properties:**
- `origins_list -> List[str]`
- `data_path -> str`

**Singleton:** `settings = Settings()` (module-level)

---

### Class: `Database`
**File:** `backend/app/core/database.py`  
**Stereotype:** `<<Module>>`

| Element | Type | Notes |
|---|---|---|
| `engine` | SQLAlchemy Engine | pool_size=10, max_overflow=20 (Postgres); StaticPool (SQLite) |
| `SessionLocal` | sessionmaker | autocommit=False, autoflush=False |
| `Base` | DeclarativeBase | parent of all ORM models |

**Functions:**
- `get_db() -> Generator[Session, None, None]` — FastAPI dependency, yields & closes session
- `create_tables()` — imports all models, calls `Base.metadata.create_all()`

---

### Class: `Security`
**File:** `backend/app/core/security.py`  
**Stereotype:** `<<Module>>`

**Constants:**
- `pwd_context` — bcrypt CryptContext

**Functions:**
- `hash_password(password: str) -> str`
- `verify_password(plain: str, hashed: str) -> bool`
- `create_access_token(data: dict, expires_delta: Optional[timedelta]) -> str` — creates HS256 JWT
- `decode_token(token: str) -> Optional[dict]` — returns payload or None on JWTError

---

### Class: `Dependencies`
**File:** `backend/app/core/dependencies.py`  
**Stereotype:** `<<Module>>`

**Functions:**
- `get_current_user(credentials, db) -> User` — decodes Bearer JWT, returns active User or 401
- `get_current_active_user(user) -> User` — wraps get_current_user, checks is_active
- `require_admin(user) -> User` — wraps get_current_user, checks role == admin or 403

---

## LAYER 4 — BACKEND SERVICES (`backend/app/services/`)

### Class: `ScoringService`
**File:** `backend/app/services/scoring_service.py`  
**Stereotype:** `<<Service Module>>`

**Constants:**
- `PASS_THRESHOLD = 0.2` (20% of max_xp)

**Functions:**
- `calculate_score(questions: List[QuestionSubmission], max_xp: int, groq_scores: List[dict]) -> dict`
  - Clamps per-question scores to [0, per_q_max]
  - Returns: `{total_score, percentage, passed, question_results}`
- `score_mcq_locally(questions: List[QuestionSubmission], max_xp: int) -> dict`
  - Compares `str(user_answer).strip() == str(correct_answer).strip()`
  - Delegates final pass/fail to `calculate_score()`

---

### Class: `GroqService`
**File:** `backend/app/services/groq_service.py`  
**Stereotype:** `<<Service Module>>`

**Constants/Lookup Tables:**
- `RUBRICS: dict` — per activity_type rubric strings (lesson/vocab/reading/writing/listening/speaking/pronunciation)
- `TIER_CONFIG: dict` — feedback_tier → prompt instructions (hint/lesson/praise)

**Functions:**
- `get_client() -> Groq` — returns Groq API client (uses GROQ_API_KEY)
- `_determine_feedback_tier(percentage: float, attempt_count: int) -> str` — returns "hint"/"lesson"/"praise"
- `_build_prompt(activity_type, questions, max_xp, user_lang, target_lang, feedback_tier) -> str`
- `validate_activity(activity_type, questions, max_xp, user_lang, target_lang, attempt_count) -> dict`
  - Calls Groq API with built prompt
  - Merges `user_answer`/`correct_answer` back from original questions
  - Returns: `{question_results, overall_feedback, suggestion}`
- `generate_tier_feedback(activity_type, feedback_tier, overall_feedback, suggestion, user_lang, target_lang) -> dict`
  - Calls Groq again for refined high/low tier feedback

---

### Class: `WhisperService`
**File:** `backend/app/services/whisper_service.py`  
**Stereotype:** `<<Service Module>>`

**Module-level State:**
- `_whisper_model` — cached model reference (None initially)
- `_whisper_available` — cached bool (None initially)

**Functions:**
- `_load_model() -> bool` — lazy-loads Whisper model once; sets `_whisper_available`
- `transcribe_audio(audio_bytes: bytes, filename: str) -> dict`
  - If Whisper unavailable → returns `{text:"", is_mock:True}`
  - Uses ffmpeg to transcode to 16kHz WAV before Whisper
  - Returns `{text, language, confidence, is_mock}`
- `save_audio_file(audio_bytes: bytes, filename: str, pair_id: str) -> str`
  - Saves to `backend/uploads/{pair_id}/` as WAV
  - Returns relative URL `/uploads/{pair_id}/{uuid}.wav`

---

### Class: `ContentService`
**File:** `backend/app/services/content_service.py`  
**Stereotype:** `<<Service Module>>`

**Functions (all file-system based):**
- `get_all_pairs() -> List[dict]` — walks `data/languages/` returning pair IDs
- `get_meta(pair_id: str) -> dict` — reads `data/languages/{src}/{tgt}/meta.json`
- `get_content_file(pair_id: str, file_path: str) -> dict` — reads a specific activity JSON
- `check_activity_exists(pair_id, file_path) -> bool`
- `get_activity_template(activity_type: str) -> dict` — returns blank scaffold for type
- `get_activity_types() -> List[str]`
- `scaffold_pair(pair_id: str)` — creates full directory + 6 blocks × 8 activities
- `add_month(pair_id, month_num)` — adds month folder + all block JSON files
- `add_block(pair_id, month_num, block_num)` — adds one block of 8 activity files
- `add_activity(pair_id, month_num, block_num, activity_type)` — adds single activity file
- `delete_pair(pair_id)` — removes pair directory, prunes source if empty
- `delete_month(pair_id, month_num)`
- `delete_block(pair_id, month_num, block_num)`
- `delete_activity(pair_id, month_num, block_num, activity_type)`
- `get_analytics() -> dict` — counts total pairs, activities per type

---

## LAYER 5 — BACKEND ROUTERS (`backend/app/routers/`)

### Class: `AuthRouter`
**File:** `backend/app/routers/auth.py`  
**URL Prefix:** `/api/auth`  
**Stereotype:** `<<FastAPI Router>>`

**Endpoints (methods):**
- `register(req: RegisterRequest, db) -> TokenResponse` — POST /register
- `login(req: LoginRequest, db) -> TokenResponse` — POST /login
- `admin_login(req: AdminLoginRequest, db) -> TokenResponse` — POST /admin/login
- `get_me(current_user) -> UserOut` — GET /me

---

### Class: `UsersRouter`
**File:** `backend/app/routers/users.py`  
**URL Prefix:** `/api/users`

**Endpoints:**
- `get_my_profile() -> UserProfileOut` — GET /me
- `update_profile(req: UpdateProfileRequest) -> UserProfileOut` — PUT /me
- `search_users(q, limit) -> UserSearchResult` — GET /search
- `get_user_profile(user_id) -> UserPublicOut` — GET /{user_id}
- `get_user_progress_public(user_id) -> dict` — GET /{user_id}/progress

---

### Class: `ProgressRouter`
**File:** `backend/app/routers/progress.py`  
**URL Prefix:** `/api/progress`

**Endpoints:**
- `get_all_progress() -> List[ProgressOut]` — GET /
- `get_pair_progress(pair_id) -> ProgressOut` — GET /{pair_id}
- `start_pair(pair_id) -> ProgressOut` — POST /{pair_id}/start
- `complete_activity(pair_id, req: CompleteActivityRequest) -> CompletionOut` — POST /{pair_id}/complete
- `get_completions(pair_id) -> List[CompletionOut]` — GET /{pair_id}/completions

**Private Helper:**
- `_derive_month_block(activity_seq_id: int) -> tuple[int, int]` — maps 1–144 to (month, block)

---

### Class: `ValidateRouter`
**File:** `backend/app/routers/validate.py`  
**URL Prefix:** `/api/validate`

**Constants:**
- `MCQ_TYPES = {"test"}` — uses local scoring
- `GROQ_TYPES = {"writing","speaking","pronunciation","listening","reading","vocabulary","vocab","lesson"}`

**Endpoints:**
- `validate_activity(req: ValidateRequest) -> ValidateResponse` — POST /

---

### Class: `SpeechRouter`
**File:** `backend/app/routers/speech.py`  
**URL Prefix:** `/api/speech`

**Constants:**
- `MAX_AUDIO_SIZE = 25MB`
- `MIN_AUDIO_SIZE = 100 bytes`
- `ALLOWED_MIME_PREFIXES = (audio/webm, audio/wav, audio/mpeg, audio/mp4, audio/ogg, audio/x-m4a, audio/m4a, audio/flac, application/octet-stream)`

**Endpoints:**
- `transcribe(audio: UploadFile) -> TranscribeResponse` — POST /transcribe

**Private Helper:**
- `_is_allowed_audio(content_type: str) -> bool`

---

### Class: `LeaderboardRouter`
**File:** `backend/app/routers/leaderboard.py`  
**URL Prefix:** `/api/leaderboard`

**Endpoints:**
- `get_leaderboard(pair_id, limit=50) -> List[LeaderboardEntry]` — GET /{pair_id}
- `get_friends_leaderboard(pair_id) -> List[LeaderboardEntry]` — GET /{pair_id}/friends

---

### Class: `FriendsRouter`
**File:** `backend/app/routers/friends.py`  
**URL Prefix:** `/api/friends`

**Endpoints:**
- `get_friends() -> dict` — GET /
- `get_incoming_requests() -> dict` — GET /requests
- `send_request(user_id) -> dict` — POST /request/{user_id}
- `accept_request(req_id) -> dict` — PUT /request/{req_id}/accept
- `decline_request(req_id) -> dict` — PUT /request/{req_id}/decline
- `remove_friend(user_id) -> dict` — DELETE /{user_id}

---

### Class: `AdminRouter`
**File:** `backend/app/routers/admin.py`  
**URL Prefix:** `/api/admin`  
**Auth:** All endpoints require `require_admin` dependency

**Endpoints:**
- `get_all_users() -> List[UserOut]` — GET /users
- `activate_user(user_id) -> dict` — POST /users/{user_id}/activate
- `deactivate_user(user_id) -> dict` — POST /users/{user_id}/deactivate
- `get_analytics() -> dict` — GET /analytics
- `get_pairs() -> List[dict]` — GET /content/pairs
- `create_pair(pair_id) -> dict` — POST /content/pairs
- `delete_pair(pair_id) -> dict` — DELETE /content/pairs/{pair_id}
- `add_month(pair_id, month_num) -> dict` — POST /content/pairs/{pair_id}/months
- `delete_month(pair_id, month_num) -> dict` — DELETE /content/pairs/{pair_id}/months/{month_num}
- `add_block(pair_id, month_num, block_num) -> dict` — POST /content/pairs/{pair_id}/months/{month_num}/blocks
- `delete_block(...) -> dict` — DELETE `.../blocks/{block_num}`
- `get_activity(pair_id, month_num, block_num, activity_type) -> dict` — GET
- `update_activity(pair_id, month_num, block_num, activity_type, body) -> dict` — PUT
- `add_activity(...) -> dict` — POST
- `delete_activity(...) -> dict` — DELETE
- `get_admin_stats() -> dict` — GET /stats

---

## LAYER 6 — FRONTEND REDUX STORE (`src/store/`)

### Class: `AuthSlice`
**File:** `src/store/authSlice.js`  
**Stereotype:** `<<Redux Slice>>`

**State Shape:**
| Field | Type |
|---|---|
| `token` | string or null |
| `user` | UserOut or null |
| `isAuthenticated` | boolean |
| `loading` | boolean |
| `error` | string or null |

**Reducers (sync actions):**
- `logout()` — clears state + localStorage
- `updateUser(payload)` — merges patch into user
- `clearError()` — clears error field

**AsyncThunks:**
- `loginUser(credentials)` — calls `authApi.login()`
- `registerUser(data)` — calls `authApi.register()`
- `adminLoginUser(credentials)` — calls `authApi.adminLogin()`

**Storage:** persists `lw_token` + `lw_user` to localStorage

---

### Class: `ProgressSlice`
**File:** `src/store/progressSlice.js`  
**Stereotype:** `<<Redux Slice>>`

**State Shape:**
| Field | Type |
|---|---|
| `allProgress` | Array[ProgressOut] |
| `pairs` | Array[{id, source, target}] |
| `currentPairId` | string or null |
| `loading` | boolean |
| `error` | string or null |

**Reducers:**
- `setCurrentPair(pairId)` — updates currentPairId + localStorage `lw_pair`
- `updateProgressXP({pairId, xpDelta})` — adds xpDelta to matching progress
- `advanceProgress({pairId, newProgress})` — merges newProgress into matching entry

**AsyncThunks:**
- `fetchAllProgress()` — GET /api/progress
- `fetchPairProgress(pairId)` — GET /api/progress/{pairId}
- `startLanguagePair(pairId)` — POST /api/progress/{pairId}/start
- `fetchPairs()` — GET /api/content/pairs

---

### Class: `UISlice`
**File:** `src/store/uiSlice.js`  
**Stereotype:** `<<Redux Slice>>`

**State Shape:**
| Field | Type |
|---|---|
| `theme` | string ("dark"/"light") |

---

## LAYER 7 — FRONTEND API CLIENTS (`src/api/`)

### Class: `ApiClient`
**File:** `src/api/client.js`  
**Stereotype:** `<<Axios Instance>>`

| Property | Value |
|---|---|
| `baseURL` | `${VITE_API_BASE_URL}/api` |
| `Content-Type` | application/json |

**Interceptors:**
- **Request:** Attaches `Authorization: Bearer {lw_token}` from localStorage
- **Response 401:** Clears localStorage → redirects admin to `/admin/login`, user to `/login`

**Module exports:**
- `default client` — the axios instance
- `API_URL` — base URL string (used by AudioPlayer for static assets)

---

### Class: `AuthApiModule`
**File:** `src/api/auth.js`  
**Stereotype:** `<<API Module>>`

- `login(credentials)` — POST /api/auth/login
- `register(data)` — POST /api/auth/register
- `adminLogin(credentials)` — POST /api/auth/admin/login

---

### Class: `ProgressApiModule`
**File:** `src/api/progress.js`  
**Stereotype:** `<<API Module>>`

- `getAllProgress()` — GET /api/progress
- `getPairProgress(pairId)` — GET /api/progress/{pairId}
- `startPair(pairId)` — POST /api/progress/{pairId}/start
- `getCompletions(pairId)` — GET /api/progress/{pairId}/completions
- `completeActivity(pairId, payload)` — POST /api/progress/{pairId}/complete
- `validateActivity(payload)` — POST /api/validate

---

### Class: `ContentApiModule`
**File:** `src/api/content.js`

- `getPairs()` — GET /api/content/pairs
- `getMeta(pairId)` — GET /api/content/{pairId}/meta

---

### Class: `UsersApiModule`
**File:** `src/api/users.js`

- `getMyProfile()` — GET /api/users/me
- `updateProfile(data)` — PUT /api/users/me
- `searchUsers(q)` — GET /api/users/search?q={q}
- `getUserProfile(userId)` — GET /api/users/{userId}
- `getLeaderboard(pairId)` — GET /api/leaderboard/{pairId}
- `getFriends()` — GET /api/friends
- `sendFriendRequest(userId)` — POST /api/friends/request/{userId}

---

## LAYER 8 — FRONTEND PAGES

### Class: `App`
**File:** `src/App.jsx`  
Routes: `/login`, `/register`, `/admin/login`, `/onboarding`, `/dashboard`, `/activity/:pairId/:type`, `/leaderboard`, `/profile`, `/search`, `/admin`  
Guards: `ProtectedRoute` (user JWT), `AdminRoute` (admin JWT)

---

### Class: `DashboardPage`
**File:** `src/pages/dashboard/DashboardPage.jsx`

**State:** `meta`, `completions`, `selectedPair`, `loading`, `expandedMonth`  
**Redux:** `allProgress`, `currentPairId`, `pairs`  
**Key Logic:** `isUnlocked(seqId)`, `isCompleted(seqId)`, `handleActivityClick()` → navigate to `/activity/:pairId/:type`

---

### Class: `ActivityRouter`
**File:** `src/pages/activities/ActivityRouter.jsx`

**Props from navigate state:** `activityFile`, `activitySeqId`, `activityJsonId`, `maxXP`, `label`, `monthNumber`, `blockNumber`  
**Routes to:** LessonPage, VocabPage, ReadingPage, WritingPage, ListeningPage, SpeakingPage, PronunciationPage, TestPage

---

### Activity Page Classes (all share same prop interface)
All receive: `{pairId, activityFile, activitySeqId, activityJsonId, maxXP, label, monthNumber, blockNumber}`

| Class | File | Key Feature |
|---|---|---|
| `LessonPage` | `LessonPage.jsx` | Renders lesson content sections, comprehension Qs |
| `VocabPage` | `VocabPage.jsx` | Flashcard + MCQ vocab activity |
| `ReadingPage` | `ReadingPage.jsx` | Passage display + short answer |
| `WritingPage` | `WritingPage.jsx` | Free-text essay submission |
| `ListeningPage` | `ListeningPage.jsx` | AudioPlayer + MCQ answers |
| `SpeakingPage` | `SpeakingPage.jsx` | AudioRecorder + Whisper STT |
| `PronunciationPage` | `PronunciationPage.jsx` | STT + phonetic comparison |
| `TestPage` | `TestPage.jsx` | Multi-type MCQ assessment |

---

### Class: `LoginPage` / `RegisterPage`
**File:** `src/pages/auth/`  
**Dispatches:** `loginUser()`, `registerUser()`

### Class: `AdminLoginPage`
**File:** `src/pages/admin/`  
**Dispatches:** `adminLoginUser()`

### Class: `LeaderboardPage`
**File:** `src/pages/social/`  
Fetches `/api/leaderboard/{pairId}` and `/api/leaderboard/{pairId}/friends`

### Class: `ProfilePage`
**File:** `src/pages/social/`  
Fetches `/api/users/me`, `/api/progress`, `/api/progress/{pairId}/completions`

### Class: `SearchFriendsPage`
**File:** `src/pages/social/`  
Fetches `/api/users/search`, `/api/friends`, sends friend requests

### Class: `OnboardingPage`
**File:** `src/pages/onboarding/`  
Starts first language pair → dispatches `startLanguagePair(pairId)`

### Class: `AdminDashboard`
**File:** `src/pages/admin/AdminDashboard.jsx`  
Calls all Admin API endpoints for user management + curriculum CRUD

---

## LAYER 9 — FRONTEND COMPONENTS

| Class | File | Purpose |
|---|---|---|
| `Sidebar` | `Sidebar.jsx` | Navigation links + logout |
| `ProtectedRoute` | `ProtectedRoute.jsx` | Redirects unauthenticated to /login |
| `AdminRoute` | `AdminRoute.jsx` | Redirects non-admins to /admin/login |
| `AudioPlayer` | `AudioPlayer.jsx` | Renders `<audio>` from `{API_URL}/static/{path}`; hides when path=null |
| `AudioRecorder` | `AudioRecorder.jsx` | Captures mic audio → sends to `/api/speech/transcribe` |
| `DynamicQuiz` | `DynamicQuiz.jsx` | Renders MCQ/fill-blank/short-answer from JSON |
| `ScoreModal` | `ScoreModal.jsx` | Shows pass/fail results, XP earned, AI feedback |
| `ActivityFeedback` | `ActivityFeedback.jsx` | Feedback + suggestion display component |
| `TargetTextBlock` | `TargetTextBlock.jsx` | Highlighted target language text display |
| `AssetRenderer` | `AssetRenderer.jsx` | Renders image/video assets from activity JSON |
| `XPBurst` | `XPBurst.jsx` | Animated XP gained notification |
| `ErrorBoundary` | `ErrorBoundary.jsx` | React error boundary wrapper |
| `NebulaWeb` | `NebulaWeb.jsx` | Animated background canvas effect |
| `ThemeToggle` | `ThemeToggle.jsx` | Light/dark mode switcher |

---

## KEY RELATIONSHIPS SUMMARY

```
User "1" ──────────────────── "*" UserLanguageProgress
User "1" ──────────────────── "*" ActivityCompletion
User "1" ──────────────────── "*" FriendRequest (as sender)
User "1" ──────────────────── "*" FriendRequest (as receiver)

AuthSlice ──uses──> AuthApiModule ──uses──> ApiClient
ProgressSlice ──uses──> ProgressApiModule ──uses──> ApiClient
ProgressSlice ──uses──> ContentApiModule ──uses──> ApiClient

ActivityRouter ──renders──> [LessonPage | VocabPage | ReadingPage | WritingPage
                              | ListeningPage | SpeakingPage | PronunciationPage | TestPage]

ValidateRouter ──uses──> GroqService ──uses──> ScoringService
ValidateRouter ──uses──> ScoringService
SpeechRouter ──uses──> WhisperService
ProgressRouter ──uses──> UserLanguageProgress
ProgressRouter ──uses──> ActivityCompletion
AdminRouter ──uses──> ContentService

Settings ──injected into──> [Database, Security, GroqService, WhisperService, ContentService]
Database ──provides──> get_db() ──injected into──> [All Routers]
Dependencies ──provides──> get_current_user(), require_admin() ──injected into──> [All Protected Routers]
```
