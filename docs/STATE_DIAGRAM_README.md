# LearnWise — State Diagram Reference

> **Purpose:** Complete reference for building ALL State Diagrams for the LearnWise platform.  
> Every state object, event trigger, guard condition, action on transition, and final state is documented.  
> Do NOT omit any state machine. Cover every stateful entity in the system.

---

## HOW TO READ THIS DOCUMENT

```
[StateName] — a discrete state the entity is in
STATE_NAME / entry: action  — action performed when entering state
STATE_NAME / exit: action   — action performed when leaving state
(event [guard]) / action → TARGET_STATE   — transition with optional guard and action
[*] → Initial State   — initial pseudostate
STATE_NAME → [*]      — final state
<<composite>> — a state that contains nested sub-states
```

---

## STATE MACHINE 1: User Account Lifecycle

**Entity:** `User` (database record)  
**File:** `backend/app/models/user.py`, `backend/app/routers/auth.py`, `backend/app/routers/admin.py`

```
[*] → UNREGISTERED

UNREGISTERED
  (POST /api/auth/register [valid form, unique email+username]) → REGISTERED_ACTIVE

REGISTERED_ACTIVE
  entry: created_at = utcnow(), is_active = True, role = "user"
  (admin calls POST /users/{id}/deactivate) → DEACTIVATED
  (POST /api/auth/login [password valid]) → LOGGED_IN
  (DELETE user cascade) → [*]  // account deleted

DEACTIVATED
  entry: is_active = False
  exit: is_active = True
  (admin calls POST /users/{id}/activate) → REGISTERED_ACTIVE

LOGGED_IN
  entry: last_active = utcnow(), JWT issued
  (GET /api/auth/me [JWT valid]) → LOGGED_IN (self-loop)
  (any protected API call [JWT expired or invalid]) → LOGGED_OUT
  (client calls logout) → LOGGED_OUT
  (admin deactivates account [JWT still valid]) → DEACTIVATED

LOGGED_OUT
  entry: localStorage.removeItem("lw_token"), removeItem("lw_user")
  (POST /api/auth/login [password valid]) → LOGGED_IN
  (browser close + token still valid in localStorage) → LOGGED_IN (on next visit, token auto-attached)

ADMIN_ROLE
  // Special sub-state of REGISTERED_ACTIVE for users with role="admin"
  (seeded at startup or upgraded manually in DB) → ADMIN_ROLE
  (POST /api/auth/admin/login [password valid]) → ADMIN_LOGGED_IN
  NOTE: Admin cannot deactivate their own account (guard: user_id != current_user.id)
```

---

## STATE MACHINE 2: JWT Token Lifecycle

**Entity:** JWT Bearer Token  
**Files:** `backend/app/core/security.py`, `src/api/client.js`

```
[*] → DOES_NOT_EXIST

DOES_NOT_EXIST
  (successful login/register) → ACTIVE
  entry: stored in localStorage as "lw_token"

ACTIVE
  entry: exp = utcnow() + 7 days (10080 minutes), algorithm = HS256
  (Axios request interceptor reads token) → ACTIVE (self-loop, token attached to header)
  (FastAPI decode_token [signature valid, not expired]) → VALID
  (FastAPI decode_token [JWTError raised]) → INVALID
  (time > exp) → EXPIRED

VALID
  // Not a standalone state — token is decoded and payload returned to dependencies
  (get_current_user called [user found in DB, is_active=True]) → ACCEPTED
  (get_current_user called [user not found or is_active=False]) → REJECTED

INVALID
  (Axios receives 401) → CLEARED

EXPIRED
  (Axios receives 401) → CLEARED

CLEARED
  entry: localStorage.removeItem("lw_token"), removeItem("lw_user")
  (user.role == "admin") → redirect to /admin/login
  (user.role == "user") → redirect to /login
  → DOES_NOT_EXIST

ACCEPTED
  // Request proceeds to endpoint handler

REJECTED
  → returns HTTPException 401
```

---

## STATE MACHINE 3: User's Language Progress

**Entity:** `UserLanguageProgress`  
**File:** `backend/app/models/progress.py`, `backend/app/routers/progress.py`

```
[*] → NOT_STARTED

NOT_STARTED
  // User has not started this language pair yet
  (POST /api/progress/{pair_id}/start) → ACTIVE
  entry: total_xp=0, current_month=1, current_block=1, current_activity_id=1

ACTIVE
  entry: started_at = utcnow()
  COMPOSITE STATE containing:

  <<composite>> ACTIVITY_POSITION
    // Tracks where the user currently is in the curriculum (1-144 sequential)
    sub-states:
      AT_ACTIVITY(n) where n = current_activity_id (1 to 144)
      entry: current_month = derived, current_block = derived

      (POST /api/progress/{pair_id}/complete [passed=True, seq_id == current_activity_id])
        / action: current_activity_id++, re-derive month/block
        → AT_ACTIVITY(n+1)

      (POST /api/progress/{pair_id}/complete [passed=False OR seq_id != current_activity_id])
        / action: only XP delta applied if new score better
        → AT_ACTIVITY(n)  [self-loop, no position advance]

      (AT_ACTIVITY(144) AND passed=True) → CURRICULUM_COMPLETE

  <<composite>> XP_LEVEL
    // XP is always accumulating, not bounded
    sub-states (conceptual milestones, no hard state change):
      BEGINNER    : total_xp < 500
      INTERMEDIATE: total_xp 500-2000
      ADVANCED    : total_xp > 2000
    (POST complete [score_earned > existing_score]) / action: total_xp += xp_delta → XP_LEVEL (updated)

CURRICULUM_COMPLETE
  // User has passed all 144 activities (3 months × 6 blocks × 8 activities)
  NOTE: User can still retry activities and earn XP improvement, but position stays at 144
  (retry any past activity) → ACTIVE (XP improvement only, no position advance)
```

---

## STATE MACHINE 4: Activity Completion Record

**Entity:** `ActivityCompletion`  
**File:** `backend/app/models/progress.py`, `backend/app/routers/progress.py`

```
[*] → NEVER_ATTEMPTED

NEVER_ATTEMPTED
  (POST /api/progress/{pair_id}/complete [first attempt]) → ATTEMPTED
  entry: INSERT ActivityCompletion {attempts=1, score_earned, passed, ai_feedback}

ATTEMPTED
  // Record exists; user can retry

  <<composite>> PASS_STATE
    sub-states:
      FAILED
        entry: passed = False
        (POST /api/progress/{pair_id}/complete [passes, new score > old]) → PASSED

      PASSED
        entry: passed = True
        (POST /api/progress/{pair_id}/complete [any retry WITH improvement])
          / action: xp_delta = new_score - old_score, total_xp += xp_delta
          → PASSED (self-loop, attempts++)

        (POST /api/progress/{pair_id}/complete [retry, new score <= old score])
          / action: no XP delta, attempts++
          → PASSED (self-loop, score not changed)

  (any subsequent completion) / action: attempts++, completed_at updated → ATTEMPTED

NOTE:
  - Score only improves upward (new_score > existing.score_earned is required for XP award)
  - Attempts counter increments on every call regardless of score
  - ai_feedback and ai_suggestion always overwritten with latest call
```

---

## STATE MACHINE 5: Friend Request

**Entity:** `FriendRequest`  
**File:** `backend/app/models/friends.py`, `backend/app/routers/friends.py`

```
[*] → DOES_NOT_EXIST

DOES_NOT_EXIST
  // No friend relation between User A and User B
  (POST /api/friends/request/{user_id} [target exists, not self, no existing request]) → PENDING
  entry: INSERT FriendRequest {sender_id=A, receiver_id=B, status="pending"}

PENDING
  entry: status = "pending", created_at = utcnow()

  (PUT /api/friends/request/{req_id}/accept [caller == receiver_id]) → ACCEPTED
    action: UPDATE status = "accepted", updated_at = utcnow()

  (PUT /api/friends/request/{req_id}/decline [caller == receiver_id]) → DECLINED
    action: UPDATE status = "declined", updated_at = utcnow()

  NOTE: While PENDING, a second request between the same pair returns 400
        (unique constraint on sender_id + receiver_id)

ACCEPTED
  entry: status = "accepted"
  // Both users appear on each other's friends list and friends leaderboard
  (DELETE /api/friends/{user_id} [caller is either sender or receiver]) → REMOVED
    action: DELETE FriendRequest row from DB

DECLINED
  entry: status = "declined"
  // Request is effectively dead. User A could theoretically send a new request
  // but the unique constraint prevents it unless the declined row is deleted.
  // In current implementation: DECLINED is a terminal state.
  → [*]

REMOVED
  // Friendship deleted — row removed
  → DOES_NOT_EXIST
  NOTE: Either user can send a new request after removal (unique constraint no longer blocking)

[Guard Rules]
  - Cannot send request to self → guard: sender_id != receiver_id
  - Cannot accept a request sent to a different user → guard: receiver_id == current_user.id
  - Cannot accept an already-ACCEPTED or DECLINED request → guard: status == "pending"
```

---

## STATE MACHINE 6: Frontend Authentication State (Redux authSlice)

**Entity:** Redux `auth` state  
**File:** `src/store/authSlice.js`

```
[*] → UNAUTHENTICATED

UNAUTHENTICATED
  entry: token=null, user=null, isAuthenticated=false
  // Check localStorage on page load
  (localStorage has lw_token AND lw_user) → AUTHENTICATED (hydrated from storage)
  (dispatch(loginUser) [pending]) → LOADING
  (dispatch(registerUser) [pending]) → LOADING
  (dispatch(adminLoginUser) [pending]) → LOADING

LOADING
  entry: loading=true, error=null
  (loginUser.fulfilled OR registerUser.fulfilled OR adminLoginUser.fulfilled) → AUTHENTICATED
  (loginUser.rejected OR registerUser.rejected OR adminLoginUser.rejected) → ERROR

AUTHENTICATED
  entry: token=JWT, user=UserOut object, isAuthenticated=true
         localStorage.setItem("lw_token"), localStorage.setItem("lw_user")
         loading=false
  (dispatch(logout)) → UNAUTHENTICATED
  (Axios 401 interceptor fires) → UNAUTHENTICATED / redirect
  (dispatch(updateUser(patch))) → AUTHENTICATED [self-loop: user merged with patch]
  (dispatch(clearError)) → AUTHENTICATED [self-loop: error=null]

ERROR
  entry: loading=false, error="error message string"
  (dispatch(clearError)) → UNAUTHENTICATED
  (user tries login again → dispatch loginUser.pending) → LOADING
```

---

## STATE MACHINE 7: Frontend Progress State (Redux progressSlice)

**Entity:** Redux `progress` state  
**File:** `src/store/progressSlice.js`

```
[*] → EMPTY

EMPTY
  entry: allProgress=[], pairs=[], currentPairId=null, loading=false
  (dispatch(fetchAllProgress).pending) → LOADING_PROGRESS
  (dispatch(fetchPairs).pending) → LOADING_PAIRS

LOADING_PROGRESS
  entry: loading=true
  (fetchAllProgress.fulfilled) → LOADED
    action: allProgress = payload
            if no currentPairId AND payload.length > 0:
              currentPairId = payload[0].lang_pair_id
              localStorage.setItem("lw_pair", pairId)
  (fetchAllProgress.rejected) → EMPTY [loading=false]

LOADING_PAIRS
  (fetchPairs.fulfilled) → PAIRS_LOADED
    action: pairs = payload

LOADED
  entry: loading=false
  // All progress data available

  (dispatch(setCurrentPair(pairId))) → LOADED [self-loop]
    action: currentPairId = pairId, localStorage.setItem("lw_pair", pairId)

  (dispatch(updateProgressXP({pairId, xpDelta}))) → LOADED [self-loop]
    action: find matching ProgressOut, total_xp += xpDelta

  (dispatch(advanceProgress({pairId, newProgress}))) → LOADED [self-loop]
    action: merge newProgress into matching allProgress entry

  (dispatch(startLanguagePair(pairId).fulfilled)) → LOADED [self-loop]
    action: if not existing → push new ProgressOut
            setCurrentPairId = newPairId

  (dispatch(fetchPairProgress(pairId).fulfilled)) → LOADED [self-loop]
    action: replace or add matching ProgressOut entry

  (dispatch(fetchAllProgress)) → LOADING_PROGRESS [refresh]
```

---

## STATE MACHINE 8: Activity Page State (Generic — any activity page)

**Entity:** Individual Activity Page component  
**Files:** `src/pages/activities/LessonPage.jsx`, `WritingPage.jsx`, `SpeakingPage.jsx`, etc.

```
[*] → LOADING_CONTENT

LOADING_CONTENT
  entry: fetch GET /api/content/{pairId}/activity?file={activityFile}
  (fetch success) → CONTENT_READY
  (fetch error) → LOAD_ERROR

LOAD_ERROR
  // Show error message with ← Back button
  (user clicks Back) → [*] (navigate to /dashboard)

CONTENT_READY
  entry: activityData loaded and parsed
  // Activity renders: instructions, content, questions

  COMPOSITE ACTIVITY_INTERACTION:
    IDLE — user reading content, not yet started answering
      (user starts filling answers) → ANSWERING

    ANSWERING
      entry: one or more questions answered
      (user un-answers all questions) → IDLE [self-loop]
      (user completes all required answers AND clicks Submit) → SUBMITTING

      // For Speech-only activities (SpeakingPage, PronunciationPage):
      ANSWERING contains nested <<composite>> RECORDING:
        NOT_RECORDING
          (user clicks Record) → RECORDING_ACTIVE
        RECORDING_ACTIVE
          entry: MediaRecorder.start()
          (user clicks Stop) → PROCESSING_AUDIO
        PROCESSING_AUDIO
          entry: POST /api/speech/transcribe
          (transcription success [is_mock=False]) → TRANSCRIBED
            action: user_answer = text
          (transcription success [is_mock=True]) → MOCK_WARNING
          (transcription error) → NOT_RECORDING
        TRANSCRIBED
          // user sees their spoken text, can re-record
          (user clicks Re-record) → NOT_RECORDING
          (user clicks Submit) → parent: SUBMITTING
        MOCK_WARNING
          // informational warning that Whisper is unavailable
          // Submit blocked
          (user clicks Re-record) → NOT_RECORDING

  SUBMITTING
  entry: POST /api/validate payload
         loading spinner shown
  (validate success [passed=True]) → PASSED_RESULT
  (validate success [passed=False]) → FAILED_RESULT
  (validate network error) → ANSWERING (error toast shown)

PASSED_RESULT
  entry: ScoreModal shown {score, XP earned, green pass indicator, feedback}
         POST /api/progress/{pairId}/complete (in background)
         dispatch(fetchPairProgress) to refresh dashboard
  (user clicks Continue) → [*] (navigate to /dashboard, next activity unlocked)
  (user clicks Retry) → CONTENT_READY [reset to initial state]

FAILED_RESULT
  entry: ScoreModal shown {score, red fail indicator, suggestion, hint}
         POST /api/progress/{pairId}/complete (record attempt even if failed)
         attempt_count incremented
  (user clicks Try Again) → CONTENT_READY [reset, attempt_count++)
  (user clicks Back) → [*] (navigate to /dashboard)
```

---

## STATE MACHINE 9: Whisper Service Availability

**Entity:** `WhisperService` module state  
**File:** `backend/app/services/whisper_service.py`

```
[*] → UNINITIALIZED

UNINITIALIZED
  // Module loaded but _load_model() not yet called
  // _whisper_available = None, _whisper_model = None
  (first call to transcribe_audio()) → LOADING

LOADING
  entry: _load_model() called
  attempt: import whisper; whisper.load_model(settings.WHISPER_MODEL)

  (whisper import success AND model loads) → AVAILABLE
    action: _whisper_model = model, _whisper_available = True

  (ImportError or any Exception during load) → UNAVAILABLE
    action: _whisper_available = False

AVAILABLE
  entry: model cached in _whisper_model
  NOTE: Subsequent calls skip LOADING (guard: _whisper_available is not None)
  
  (transcribe_audio called) → TRANSCRIBING

  TRANSCRIBING
    entry: ffmpeg transcode → whisper_model.transcribe()
    (success) → AVAILABLE [return {text, language, confidence, is_mock:False}]
    (exception during transcription) → AVAILABLE [return {text:"", confidence:0.0, is_mock:False}]

UNAVAILABLE
  entry: _whisper_available = False
  NOTE: All subsequent calls return immediately without retrying load
  (transcribe_audio called) → UNAVAILABLE [self-loop, return {text:"", is_mock:True}]
  NOTE: is_mock=True is the critical signal to the frontend to block submission
```

---

## STATE MACHINE 10: Groq AI Service Call State

**Entity:** Single Groq API call in `GroqService`  
**File:** `backend/app/services/groq_service.py`

```
[*] → IDLE

IDLE
  (validate_activity() or generate_tier_feedback() called) → BUILDING_PROMPT

BUILDING_PROMPT
  entry: _build_prompt(activity_type, questions, max_xp, user_lang, target_lang, feedback_tier)
         Combines: system rubric + romanization rules + generosity note + per-question instructions
  (prompt ready) → CALLING_GROQ

CALLING_GROQ
  entry: client.chat.completions.create(model="llama3-8b-8192", temperature=0.1, messages=[...])
  (API responds with valid JSON) → PARSING_RESPONSE
  (API timeout or network error) → ERROR

PARSING_RESPONSE
  entry: extract JSON from response text
         merge user_answer + correct_answer from original questions into question_results
  (JSON parse success) → RESULT_READY
  (JSON parse failure / malformed) → ERROR
    action: return fallback {question_results: [], overall_feedback: "Unable to evaluate", suggestion: "..."}

RESULT_READY
  → IDLE [return dict to caller]

ERROR
  → IDLE [return fallback dict to caller]
  NOTE: Validate router wraps generate_tier_feedback in try/except; errors silently fall back to original feedback

// Second call state for tier feedback refinement:
BUILDING_TIER_PROMPT
  entry: different prompt focusing on feedback_tier (hint/praise/lesson) style
  → CALLING_GROQ (same as above)
```

---

## STATE MACHINE 11: Audio File Upload / Recording

**Entity:** `AudioRecorder` component  
**File:** `src/components/AudioRecorder.jsx`

```
[*] → READY

READY
  entry: audioBlob=null, chunks=[], is_recording=false
  (user clicks record button) → REQUESTING_PERMISSION

REQUESTING_PERMISSION
  entry: navigator.mediaDevices.getUserMedia({audio:true})
  (permission granted) → RECORDING
  (permission denied) → PERMISSION_DENIED

PERMISSION_DENIED
  entry: show error "Microphone access denied"
  (user closes error) → READY

RECORDING
  entry: MediaRecorder(stream).start()
        recording indicator shown (red pulse animation)
  (dataavailable event) → RECORDING [self-loop, push chunk to chunks[]]
  (user clicks Stop) → PROCESSING_LOCAL

PROCESSING_LOCAL
  entry: mediaRecorder.stop()
  (stop event fired) → PREVIEW
    action: blob = new Blob(chunks, {type:"audio/webm"})
            objectURL = URL.createObjectURL(blob)

PREVIEW
  entry: <audio src={objectURL} controls> rendered
  // User can listen back to their recording
  (user clicks Re-record) → READY [URL.revokeObjectURL, reset chunks]
  (user clicks Submit Recording) → UPLOADING

UPLOADING
  entry: FormData append(blob)
         POST /api/speech/transcribe
         loading spinner shown

  (response [is_mock=False, text returned]) → TRANSCRIBED
    action: pass transcribed text up to parent ActivityPage
  (response [is_mock=True]) → MOCK_FALLBACK
  (network error) → UPLOAD_ERROR

TRANSCRIBED
  // Parent component receives text as user_answer
  → READY [reset for potential re-recording]

MOCK_FALLBACK
  entry: show "Whisper unavailable — demo mode" warning
         Submit button blocked
  (user clicks Re-record) → READY

UPLOAD_ERROR
  entry: show "Upload failed, please try again" toast
  (user clicks Retry) → UPLOADING
  (user clicks Re-record) → READY
```

---

## STATE MACHINE 12: Admin Dashboard Page State

**Entity:** `AdminDashboard` React component  
**File:** `src/pages/admin/AdminDashboard.jsx`

```
[*] → LOADING_ADMIN_DATA

LOADING_ADMIN_DATA
  entry: GET /api/admin/users
         GET /api/admin/content/pairs
         GET /api/admin/analytics (or /api/admin/stats)

  (all fetches complete) → VIEWING_DASHBOARD
  (any fetch fails [403]) → ACCESS_DENIED [redirect to /admin/login]

VIEWING_DASHBOARD
  entry: render user list, pair list, stats panels

  COMPOSITE SELECTED_SECTION:
    USERS_TAB
      (click Activate on user) → MODIFYING_USER
      (click Deactivate on user) → MODIFYING_USER

    MODIFYING_USER
      entry: POST /api/admin/users/{id}/activate OR deactivate
      (success) → USERS_TAB [refresh user list]
      (error) → USERS_TAB [show error toast]

    CURRICULUM_TAB
      (click pair) → PAIR_SELECTED
      (click Create Pair) → CREATING_PAIR
      (click Delete Pair) → DELETING_PAIR

    PAIR_SELECTED
      (select month) → MONTH_SELECTED
      (click Add Month) → CREATING_MONTH
      (click Delete Month) → DELETING_MONTH

    MONTH_SELECTED
      (select block) → BLOCK_SELECTED
      (click Add Block) → CREATING_BLOCK
      (click Delete Block) → DELETING_BLOCK

    BLOCK_SELECTED
      (select activity type) → EDITING_ACTIVITY

    EDITING_ACTIVITY
      entry: GET /api/admin/content/{pair}/{m}/{b}/{type}
             render JSON editor or form
      (user edits fields, clicks Save) → SAVING_ACTIVITY
      (user clicks Cancel) → BLOCK_SELECTED

    SAVING_ACTIVITY
      entry: PUT /api/admin/content/{pair}/{m}/{b}/{type}
      (success) → BLOCK_SELECTED [show "Saved" toast]
      (error) → EDITING_ACTIVITY [show error]

    CREATING_PAIR
      entry: POST /api/admin/content/pairs {pair_id}
      (success) → CURRICULUM_TAB [refresh pairs]
      (error) → CURRICULUM_TAB [show error]

    DELETING_PAIR
      entry: DELETE /api/admin/content/pairs/{pair_id}
      (success) → CURRICULUM_TAB [refresh pairs]
      (error) → CURRICULUM_TAB [show error]

ACCESS_DENIED
  → redirect to /admin/login
```

---

## STATE MACHINE 13: Frontend Route Guard Lifecycle

**Entity:** `ProtectedRoute` and `AdminRoute` components  
**Files:** `src/components/ProtectedRoute.jsx`, `src/components/AdminRoute.jsx`

```
--- ProtectedRoute ---

[*] → CHECKING_AUTH

CHECKING_AUTH
  entry: read Redux state.auth.isAuthenticated

  [Decision] isAuthenticated == true?
  → [YES] → AUTHORIZED: render children (MainLayout + Outlet)
  → [NO] → UNAUTHORIZED: Navigate to /login (replace:true)

AUTHORIZED
  (user dispatches logout) → UNAUTHORIZED
  (JWT expires + next API call 401) → UNAUTHORIZED
  → render protected page

UNAUTHORIZED
  → [*] (redirect to /login, no back history entry)

--- AdminRoute ---

[*] → CHECKING_ADMIN

CHECKING_ADMIN
  entry: read Redux state.auth.isAuthenticated AND state.auth.user.role

  [Decision] isAuthenticated AND role == "admin"?
  → [YES] → ADMIN_AUTHORIZED: render <Outlet /> (AdminDashboard)
  → [NO] → ADMIN_UNAUTHORIZED: Navigate to /admin/login (replace:true)

ADMIN_AUTHORIZED
  → render admin pages

ADMIN_UNAUTHORIZED
  → [*] (redirect to /admin/login)
```

---

## COMPLETE STATEFUL ENTITIES SUMMARY TABLE

| Entity | State Machine # | Key States | Trigger Events |
|---|---|---|---|
| `User` (DB) | SM-1 | UNREGISTERED → REGISTERED_ACTIVE → DEACTIVATED ↔ LOGGED_IN | register, login, logout, admin activate/deactivate |
| `JWT Token` | SM-2 | DOES_NOT_EXIST → ACTIVE → EXPIRED/INVALID → CLEARED | login, token decode, 401 response |
| `UserLanguageProgress` (DB) | SM-3 | NOT_STARTED → ACTIVE (AT_ACTIVITY n) → CURRICULUM_COMPLETE | start pair, complete activity (passed) |
| `ActivityCompletion` (DB) | SM-4 | NEVER_ATTEMPTED → ATTEMPTED (FAILED/PASSED) | POST /progress/complete |
| `FriendRequest` (DB) | SM-5 | DOES_NOT_EXIST → PENDING → ACCEPTED/DECLINED/REMOVED | send, accept, decline, unfriend |
| `authSlice` (Redux) | SM-6 | UNAUTHENTICATED → LOADING → AUTHENTICATED/ERROR | loginUser, logout, 401 interceptor |
| `progressSlice` (Redux) | SM-7 | EMPTY → LOADING → LOADED | fetchAllProgress, startPair, advanceProgress |
| `ActivityPage` (React) | SM-8 | LOADING → CONTENT_READY → ANSWERING → SUBMITTING → PASSED/FAILED | content fetch, submit, retry |
| `WhisperService` (Python) | SM-9 | UNINITIALIZED → LOADING → AVAILABLE/UNAVAILABLE → TRANSCRIBING | first transcribe_audio call |
| `GroqService` call (Python) | SM-10 | IDLE → BUILDING_PROMPT → CALLING_GROQ → PARSING → RESULT/ERROR | validate_activity(), generate_tier_feedback() |
| `AudioRecorder` (React) | SM-11 | READY → REQUESTING_PERMISSION → RECORDING → PREVIEW → UPLOADING → TRANSCRIBED | record, stop, submit, re-record |
| `AdminDashboard` (React) | SM-12 | LOADING → VIEWING → EDITING (per section) → SAVING | page load, item select, save, delete |
| `ProtectedRoute` (React) | SM-13 | CHECKING → AUTHORIZED/UNAUTHORIZED | route change, auth state change |
