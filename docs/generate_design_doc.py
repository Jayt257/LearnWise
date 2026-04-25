#!/usr/bin/env python3
"""
LearnWise — Software Design Document Generator
Produces DESIGN_DOCUMENT.docx with REAL UML diagram images (Class, Sequence, Activity, State).
Diagrams rendered via PlantUML web service → PNG → embedded in Word.
Industry-standard IEEE Std 1016 structure. Oracle-style presentation.

Run: python docs/generate_design_doc.py
"""

import os, zlib, sys
from pathlib import Path
import requests
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ─────────────────────────────────────────────────────────────────
# PlantUML encoding + rendering
# ─────────────────────────────────────────────────────────────────
_PUML_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"

def _encode3(b1, b2, b3):
    return (
        _PUML_CHARS[b1 >> 2]
        + _PUML_CHARS[((b1 & 3) << 4) | (b2 >> 4)]
        + _PUML_CHARS[((b2 & 15) << 2) | (b3 >> 6)]
        + _PUML_CHARS[b3 & 63]
    )

def _puml_b64(data: bytes) -> str:
    out = []
    for i in range(0, len(data), 3):
        chunk = data[i:i+3]
        while len(chunk) < 3:
            chunk += b'\x00'
        out.append(_encode3(chunk[0], chunk[1], chunk[2]))
    return "".join(out)

def encode_plantuml(text: str) -> str:
    compressed = zlib.compress(text.encode("utf-8"), 9)[2:-4]
    return _puml_b64(compressed)

def render_diagram(puml_text: str, out_path: str, timeout: int = 45) -> bool:
    """Render a PlantUML diagram to PNG via web service and save to out_path."""
    encoded = encode_plantuml(puml_text)
    url = f"https://www.plantuml.com/plantuml/png/{encoded}"
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            Path(out_path).write_bytes(resp.content)
            print(f"  ✓  {Path(out_path).name}")
            return True
        else:
            print(f"  ✗  HTTP {resp.status_code} for {Path(out_path).name}")
    except Exception as e:
        print(f"  ✗  {Path(out_path).name}: {e}")
    return False

# ─────────────────────────────────────────────────────────────────
# Common skinparam blocks
# ─────────────────────────────────────────────────────────────────
CLASS_SKIN = """
skinparam defaultFontName "Helvetica"
skinparam defaultFontSize 11
skinparam shadowing false
skinparam roundcorner 8
skinparam class {
    BackgroundColor #F5F8FF
    BorderColor #1F3864
    HeaderBackgroundColor #1F3864
    FontColor #1F3864
    HeaderFontColor #FFFFFF
    HeaderFontStyle Bold
    HeaderFontSize 12
    AttributeFontColor #222222
    AttributeFontSize 10
    StereotypeFontColor #7F7F7F
    StereotypeFontSize 9
}
skinparam arrow {
    Color #1F3864
    FontColor #333333
    FontSize 9
}
skinparam note {
    BackgroundColor #FFFDE7
    BorderColor #F9A825
    FontSize 9
}
"""

SEQ_SKIN = """
skinparam defaultFontName "Helvetica"
skinparam defaultFontSize 11
skinparam shadowing false
skinparam sequence {
    ArrowColor #1F3864
    ActorBorderColor #1F3864
    LifeLineBorderColor #1F3864
    LifeLineBackgroundColor #EBF2FF
    ParticipantBorderColor #1F3864
    ParticipantBackgroundColor #1F3864
    ParticipantFontColor #FFFFFF
    ParticipantFontSize 11
    ParticipantFontStyle Bold
    ActorBackgroundColor #D6E4FF
    ActorFontColor #1F3864
    ActorFontSize 11
    BoxBackgroundColor #F0F4FF
    BoxBorderColor #1F3864
    NoteBackgroundColor #FFFDE7
    NoteBorderColor #F9A825
    NoteFontSize 9
    DividerBackgroundColor #E8EDF5
    DividerBorderColor #1F3864
    DividerFontColor #1F3864
    DividerFontStyle Bold
}
skinparam arrow {
    FontColor #333333
    FontSize 10
}
"""

ACT_SKIN = """
skinparam defaultFontName "Helvetica"
skinparam defaultFontSize 11
skinparam shadowing false
skinparam activity {
    BackgroundColor #F5F8FF
    BorderColor #1F3864
    FontColor #1F3864
    StartColor #1F3864
    EndColor #1F3864
    BarColor #1F3864
    ArrowColor #1F3864
    DiamondBackgroundColor #FFF3E0
    DiamondBorderColor #E65100
    DiamondFontColor #E65100
    DiamondFontSize 10
    SwimlaneBorderColor #1F3864
    SwimlaneBorderThickness 2
    SwimlaneTitleFontColor #FFFFFF
    SwimlaneTitleFontStyle Bold
    SwimlaneWidth 220
}
skinparam arrow {
    Color #1F3864
    FontColor #333333
    FontSize 10
}
"""

STATE_SKIN = """
skinparam defaultFontName "Helvetica"
skinparam defaultFontSize 11
skinparam shadowing false
skinparam state {
    BackgroundColor #F5F8FF
    BorderColor #1F3864
    FontColor #1F3864
    StartColor #1F3864
    EndColor #1F3864
    ArrowColor #1F3864
    AttributeFontColor #555555
    AttributeFontSize 10
}
skinparam arrow {
    FontColor #333333
    FontSize 10
}
skinparam note {
    BackgroundColor #FFFDE7
    BorderColor #F9A825
    FontSize 9
}
"""

# ─────────────────────────────────────────────────────────────────
# ALL DIAGRAMS
# ─────────────────────────────────────────────────────────────────
DIAGRAMS = {}

# ══════════════════════════════════════════
# CLASS DIAGRAMS
# ══════════════════════════════════════════

DIAGRAMS["CD-01_DB_Models"] = f"""
@startuml CD-01_DB_Models
title <b>CD-01 — Backend Database Models Layer</b>\\n<i>Tables: users · user_language_progress · activity_completions · friend_requests</i>
left to right direction
{CLASS_SKIN}

enum UserRole <<Enumeration>> {{
  user
  admin
}}

enum FriendRequestStatus <<Enumeration>> {{
  pending
  accepted
  declined
}}

class User <<SQLAlchemy ORM>> {{
  +UUID id <<PK, auto-generated>>
  +String(50) username <<UNIQUE, NOT NULL>>
  +String(255) email <<UNIQUE, NOT NULL>>
  +String(255) password_hash <<NOT NULL>>
  +String(100) display_name
  +String(500) avatar_url
  +String(5) native_lang
  +UserRole role <<NOT NULL, default: user>>
  +Boolean is_active <<default: True>>
  +DateTime created_at <<default: utcnow>>
  +DateTime last_active <<on update: utcnow>>
  --
  +__repr__() : str
}}

class UserLanguageProgress <<SQLAlchemy ORM>> {{
  +UUID id <<PK, auto-generated>>
  +UUID user_id <<FK → users.id, CASCADE>>
  +String(10) lang_pair_id <<NOT NULL, e.g. hi-ja>>
  +Integer total_xp <<default: 0>>
  +Integer current_month <<default: 1>>
  +Integer current_block <<default: 1>>
  +Integer current_activity_id <<range: 1–144>>
  +DateTime started_at <<default: utcnow>>
  +DateTime last_activity_at <<on update: utcnow>>
  --
  +__repr__() : str
}}

class ActivityCompletion <<SQLAlchemy ORM>> {{
  +UUID id <<PK, auto-generated>>
  +UUID user_id <<FK → users.id, CASCADE>>
  +String(10) lang_pair_id <<NOT NULL>>
  +Integer activity_seq_id <<NOT NULL, range: 1–144>>
  +String(80) activity_json_id
  +String(20) activity_type <<NOT NULL>>
  +Integer month_number
  +Integer block_number
  +Integer score_earned <<default: 0>>
  +Integer max_score <<NOT NULL>>
  +Boolean passed <<default: False>>
  +Integer attempts <<default: 1>>
  +Text ai_feedback
  +Text ai_suggestion
  +DateTime completed_at <<default: utcnow>>
  --
  +__repr__() : str
}}

class FriendRequest <<SQLAlchemy ORM>> {{
  +UUID id <<PK, auto-generated>>
  +UUID sender_id <<FK → users.id, CASCADE>>
  +UUID receiver_id <<FK → users.id, CASCADE>>
  +FriendRequestStatus status <<NOT NULL, default: pending>>
  +DateTime created_at <<default: utcnow>>
  +DateTime updated_at <<on update: utcnow>>
  --
  +__repr__() : str
}}

User "1" *-down- "0..*" UserLanguageProgress : language_progress\\n(cascade delete-orphan)
User "1" *-down- "0..*" ActivityCompletion : activity_completions\\n(cascade delete-orphan)
User "1" *-right- "0..*" FriendRequest : sent_requests\\n(sender_id)
User "1" *-right- "0..*" FriendRequest : received_requests\\n(receiver_id)
User ..> UserRole : <<use>>
FriendRequest ..> FriendRequestStatus : <<use>>

note bottom of UserLanguageProgress
  Unique Constraint:
  (user_id, lang_pair_id)
end note

note bottom of ActivityCompletion
  Unique Constraint:
  (user_id, lang_pair_id, activity_seq_id)
end note

note right of FriendRequest
  Unique Constraint:
  (sender_id, receiver_id)
end note

@enduml
"""

DIAGRAMS["CD-02_Core_Services"] = f"""
@startuml CD-02_Core_Services
title <b>CD-02 — Backend Core & Services Layer</b>\\n<i>app/core/ · app/services/</i>
{CLASS_SKIN}

class Settings <<Pydantic BaseSettings>> {{
  +str APP_NAME = "LearnWise"
  +bool DEBUG = True
  +str DATABASE_URL
  +str SECRET_KEY
  +str ALGORITHM = "HS256"
  +int ACCESS_TOKEN_EXPIRE_MINUTES = 10080
  +str GROQ_API_KEY
  +str GROQ_MODEL = "llama3-8b-8192"
  +str WHISPER_MODEL = "small"
  +str ALLOWED_ORIGINS
  +str ADMIN_EMAIL
  +str ADMIN_PASSWORD
  +int SCORE_THRESHOLD_OVERRIDE = -1
  +str DATA_DIR = "data"
  --
  +origins_list() : List[str]
  +data_path() : str
}}

class Database <<Module>> {{
  +Engine engine
  +sessionmaker SessionLocal
  +DeclarativeBase Base
  --
  +get_db() : Generator[Session]
  +create_tables()
}}

class Security <<Module>> {{
  +CryptContext pwd_context
  --
  +hash_password(password: str) : str
  +verify_password(plain: str, hashed: str) : bool
  +create_access_token(data: dict, expires_delta) : str
  +decode_token(token: str) : Optional[dict]
}}

class Dependencies <<Module>> {{
  --
  +get_current_user(credentials, db) : User
  +get_current_active_user(user) : User
  +require_admin(user) : User
}}

class ScoringService <<Service>> {{
  +float PASS_THRESHOLD = 0.2
  --
  +calculate_score(questions, max_xp, groq_scores) : dict
  +score_mcq_locally(questions, max_xp) : dict
}}

class GroqService <<Service>> {{
  +dict RUBRICS
  +dict TIER_CONFIG
  --
  +get_client() : Groq
  -_determine_feedback_tier(pct, attempts) : str
  -_build_prompt(type, questions, max_xp, ...) : str
  +validate_activity(type, questions, max_xp, ...) : dict
  +generate_tier_feedback(type, tier, ...) : dict
}}

class WhisperService <<Service>> {{
  -_whisper_model : Any
  -_whisper_available : bool
  --
  -_load_model() : bool
  +transcribe_audio(audio_bytes, filename) : dict
  +save_audio_file(audio_bytes, filename, pair_id) : str
}}

class ContentService <<Service>> {{
  --
  +get_all_pairs() : List[dict]
  +get_meta(pair_id) : dict
  +get_content_file(pair_id, file_path) : dict
  +scaffold_pair(pair_id)
  +add_month(pair_id, month_num)
  +add_block(pair_id, month_num, block_num)
  +delete_pair(pair_id)
  +delete_month(pair_id, month_num)
  +delete_block(pair_id, month_num, block_num)
  +get_analytics() : dict
}}

Settings ..> Database : <<configures>>
Settings ..> Security : <<configures>>
Settings ..> GroqService : <<configures>>
Settings ..> WhisperService : <<configures>>
Database ..> Dependencies : <<provides get_db()>>
GroqService ..> ScoringService : <<delegates scoring>>

@enduml
"""

DIAGRAMS["CD-03_API_Routers"] = f"""
@startuml CD-03_API_Routers
title <b>CD-03 — Backend API Routers Layer</b>\\n<i>app/routers/ — all endpoints under /api prefix</i>
{CLASS_SKIN}

class AuthRouter <<FastAPI Router>> {{
  +prefix = /api/auth
  --
  +register(req: RegisterRequest) : TokenResponse
  +login(req: LoginRequest) : TokenResponse
  +admin_login(req: AdminLoginRequest) : TokenResponse
  +get_me(user) : UserOut
}}

class ProgressRouter <<FastAPI Router>> {{
  +prefix = /api/progress
  --
  +get_all_progress() : List[ProgressOut]
  +get_pair_progress(pair_id) : ProgressOut
  +start_pair(pair_id) : ProgressOut
  +complete_activity(pair_id, req) : CompletionOut
  +get_completions(pair_id) : List[CompletionOut]
  -_derive_month_block(seq_id) : tuple[int,int]
}}

class ValidateRouter <<FastAPI Router>> {{
  +prefix = /api/validate
  +MCQ_TYPES: set = {{"test"}}
  +GROQ_TYPES: set
  --
  +validate_activity(req: ValidateRequest) : ValidateResponse
}}

class SpeechRouter <<FastAPI Router>> {{
  +prefix = /api/speech
  +MAX_AUDIO_SIZE = 25 MB
  +MIN_AUDIO_SIZE = 100 bytes
  --
  +transcribe(audio: UploadFile) : TranscribeResponse
  -_is_allowed_audio(content_type) : bool
}}

class LeaderboardRouter <<FastAPI Router>> {{
  +prefix = /api/leaderboard
  --
  +get_leaderboard(pair_id, limit) : List[LeaderboardEntry]
  +get_friends_leaderboard(pair_id) : List[LeaderboardEntry]
}}

class FriendsRouter <<FastAPI Router>> {{
  +prefix = /api/friends
  --
  +get_friends() : dict
  +get_incoming_requests() : dict
  +send_request(user_id) : dict
  +accept_request(req_id) : dict
  +decline_request(req_id) : dict
  +remove_friend(user_id) : dict
}}

class UsersRouter <<FastAPI Router>> {{
  +prefix = /api/users
  --
  +get_my_profile() : UserProfileOut
  +update_profile(req) : UserProfileOut
  +search_users(q, limit) : UserSearchResult
  +get_user_profile(user_id) : UserPublicOut
  +get_user_progress_public(user_id) : dict
}}

class AdminRouter <<FastAPI Router>> {{
  +prefix = /api/admin
  +auth = require_admin
  --
  +get_all_users() : List[UserOut]
  +activate_user(user_id) : dict
  +deactivate_user(user_id) : dict
  +get_analytics() : dict
  +create_pair(pair_id) : dict
  +delete_pair(pair_id) : dict
  +add_month(pair_id, month_num) : dict
  +add_block(pair_id, month_num, block_num) : dict
  +update_activity(...) : dict
  +get_admin_stats() : dict
}}

ValidateRouter ..> GroqService : <<uses>>
ValidateRouter ..> ScoringService : <<uses>>
SpeechRouter ..> WhisperService : <<uses>>
AdminRouter ..> ContentService : <<uses>>
ProgressRouter ..> Dependencies : <<inject get_current_user>>
ValidateRouter ..> Dependencies : <<inject get_current_user>>
AdminRouter ..> Dependencies : <<inject require_admin>>

@enduml
"""

DIAGRAMS["CD-04_Frontend_State"] = f"""
@startuml CD-04_Frontend_State
title <b>CD-04 — Frontend State Management & API Client Layer</b>\\n<i>src/store/ · src/api/</i>
{CLASS_SKIN}

class AuthSlice <<Redux Slice>> {{
  +string token
  +UserOut user
  +boolean isAuthenticated
  +boolean loading
  +string error
  --
  +logout()
  +updateUser(payload)
  +clearError()
  +loginUser(credentials) : AsyncThunk
  +registerUser(data) : AsyncThunk
  +adminLoginUser(credentials) : AsyncThunk
}}

class ProgressSlice <<Redux Slice>> {{
  +Array allProgress
  +Array pairs
  +string currentPairId
  +boolean loading
  +string error
  --
  +setCurrentPair(pairId)
  +updateProgressXP(pairId, xpDelta)
  +advanceProgress(pairId, newProgress)
  +fetchAllProgress() : AsyncThunk
  +fetchPairProgress(pairId) : AsyncThunk
  +startLanguagePair(pairId) : AsyncThunk
  +fetchPairs() : AsyncThunk
}}

class UISlice <<Redux Slice>> {{
  +string theme
  --
  +setTheme(theme)
}}

class ApiClient <<Axios Instance>> {{
  +string baseURL
  --
  +requestInterceptor()
  +responseInterceptor401()
}}

class AuthApiModule <<API Module>> {{
  --
  +login(credentials) : Promise
  +register(data) : Promise
  +adminLogin(credentials) : Promise
}}

class ProgressApiModule <<API Module>> {{
  --
  +getAllProgress() : Promise
  +getPairProgress(pairId) : Promise
  +startPair(pairId) : Promise
  +completeActivity(pairId, payload) : Promise
  +validateActivity(payload) : Promise
  +getCompletions(pairId) : Promise
}}

class ContentApiModule <<API Module>> {{
  --
  +getPairs() : Promise
  +getMeta(pairId) : Promise
}}

class UsersApiModule <<API Module>> {{
  --
  +getMyProfile() : Promise
  +updateProfile(data) : Promise
  +searchUsers(q) : Promise
  +getUserProfile(userId) : Promise
  +getLeaderboard(pairId) : Promise
  +getFriends() : Promise
  +sendFriendRequest(userId) : Promise
}}

AuthSlice --> AuthApiModule : <<calls>>
ProgressSlice --> ProgressApiModule : <<calls>>
ProgressSlice --> ContentApiModule : <<calls>>
AuthApiModule --> ApiClient : <<HTTP>>
ProgressApiModule --> ApiClient : <<HTTP>>
ContentApiModule --> ApiClient : <<HTTP>>
UsersApiModule --> ApiClient : <<HTTP>>

@enduml
"""

DIAGRAMS["CD-05_Frontend_Pages"] = f"""
@startuml CD-05_Frontend_Pages
title <b>CD-05 — Frontend Pages & Components Layer</b>\\n<i>src/pages/ · src/components/</i>
{CLASS_SKIN}

class App <<React App>> {{
  +routes: /login, /register, /admin/login
  +routes: /onboarding, /dashboard
  +routes: /activity/:pairId/:type
  +routes: /leaderboard, /profile, /search, /admin
  --
  +render() : JSX
}}

class DashboardPage <<React Page>> {{
  +meta : object
  +completions : Array
  +selectedPair : string
  +loading : boolean
  --
  +isUnlocked(seqId) : boolean
  +isCompleted(seqId) : boolean
  +handleActivityClick(node)
}}

class ActivityRouter <<React Router>> {{
  +activityFile : string
  +activitySeqId : int
  +maxXP : int
  +monthNumber : int
  +blockNumber : int
  --
  +resolveComponent(type) : Component
}}

class LessonPage <<Activity Page>> {{
  +renders: lesson content + comprehension Qs
}}
class VocabPage <<Activity Page>> {{
  +renders: flashcard + MCQ vocab
}}
class ReadingPage <<Activity Page>> {{
  +renders: passage + short answer
}}
class WritingPage <<Activity Page>> {{
  +renders: free-text essay submission
}}
class ListeningPage <<Activity Page>> {{
  +renders: AudioPlayer + MCQ answers
}}
class SpeakingPage <<Activity Page>> {{
  +renders: AudioRecorder + Whisper STT
}}
class PronunciationPage <<Activity Page>> {{
  +renders: STT + phonetic comparison
}}
class TestPage <<Activity Page>> {{
  +renders: multi-type MCQ assessment
}}

class ScoreModal <<Component>> {{
  +score : int
  +passed : boolean
  +feedback : string
  +suggestion : string
  +feedbackTier : string
  +xpEarned : int
}}

class AudioRecorder <<Component>> {{
  +audioBlob : Blob
  +isRecording : boolean
  +transcribedText : string
  --
  +startRecording()
  +stopRecording()
  +submitAudio()
}}

class AudioPlayer <<Component>> {{
  +src : string
}}

class ProtectedRoute <<Guard Component>> {{
  +isAuthenticated : boolean
}}

class AdminRoute <<Guard Component>> {{
  +isAuthenticated : boolean
  +role : string
}}

App --> ProtectedRoute
App --> AdminRoute
App --> DashboardPage
App --> ActivityRouter
ActivityRouter --> LessonPage
ActivityRouter --> VocabPage
ActivityRouter --> ReadingPage
ActivityRouter --> WritingPage
ActivityRouter --> ListeningPage
ActivityRouter --> SpeakingPage
ActivityRouter --> PronunciationPage
ActivityRouter --> TestPage
SpeakingPage --> AudioRecorder
PronunciationPage --> AudioRecorder
ListeningPage --> AudioPlayer
LessonPage --> ScoreModal
WritingPage --> ScoreModal
SpeakingPage --> ScoreModal
ReadingPage --> ScoreModal

@enduml
"""

# ══════════════════════════════════════════
# SEQUENCE DIAGRAMS
# ══════════════════════════════════════════

DIAGRAMS["SD-01_User_Registration"] = f"""
@startuml SD-01_User_Registration
title <b>SD-01 — User Registration Flow</b>\\n<i>POST /api/auth/register</i>
{SEQ_SKIN}

actor       "User"               as U
participant "React\\nFrontend"   as R
participant "Redux\\nStore"      as RX
participant "Axios\\nClient"     as AX
participant "Auth\\nRouter"      as AR
participant "Security\\nModule"  as SEC
database    "PostgreSQL"         as DB

U  -> R  : fills {{username, email, password}}\\nclicks Register
R  -> RX : dispatch(registerUser(credentials))
RX -> AX : build POST /api/auth/register payload
AX -> AR : HTTP POST /api/auth/register

AR -> DB : SELECT * FROM users WHERE email = req.email

alt Email already registered
    DB --> AR : User found
    AR --> AX : 400 "Email already registered"
    AX --> RX : rejectWithValue(msg)
    RX --> R  : state.error = msg
    R  --> U  : show error toast
else Username taken
    AR -> DB : SELECT * FROM users WHERE username = req.username
    DB --> AR : User found
    AR --> AX : 400 "Username already taken"
    AX --> R  : show error toast
else Success
    AR  -> SEC : hash_password(req.password)
    SEC --> AR  : bcrypt hash
    AR  -> DB  : INSERT INTO users {{username, email, hash, role='user'}}
    DB  --> AR  : User {{id, username, email, role}}
    AR  -> SEC  : create_access_token({{sub: user.id, role: 'user'}})
    SEC --> AR  : HS256 JWT (exp: +7 days)
    AR  --> AX  : 201 TokenResponse {{access_token, user}}
    AX  --> RX  : resolved payload
    RX  -> RX   : localStorage.setItem('lw_token')\\nlocalStorage.setItem('lw_user')
    RX  --> R   : isAuthenticated = true, user = payload
    R   --> U   : navigate('/dashboard')
end

@enduml
"""

DIAGRAMS["SD-02_Activity_Submission"] = f"""
@startuml SD-02_Activity_Submission
title <b>SD-02 — Activity Submission & AI Grading</b>\\n<i>POST /api/validate → POST /api/progress/{{pair}}/complete</i>
{SEQ_SKIN}

actor       "User"               as U
participant "Activity\\nPage"    as AP
participant "Validate\\nRouter"  as VR
participant "Groq\\nService"     as GS
participant "Scoring\\nService"  as SS
participant "Groq Cloud\\nAPI"   as AI
participant "Progress\\nRouter"  as PR
database    "PostgreSQL"         as DB

U  -> AP : click Submit (all answers filled)
AP -> VR : POST /api/validate\\n{{activity_type, questions, max_xp, user_lang, target_lang, attempt_count}}

VR -> VR : check questions not empty\\n(else HTTP 400)

alt MCQ Path — activity_type in {{"test"}}
    VR -> SS : score_mcq_locally(questions, max_xp)
    SS -> SS : for each question:\\n  str(user_answer) == str(correct_answer)
    SS -> SS : calculate_score() → clamp [0, per_q_max]\\n  sum total, percentage = total/max_xp × 100\\n  passed = percentage >= 20.0
    SS --> VR : {{total_score, percentage, passed, question_results}}
else Groq AI Path — lesson/vocab/reading/writing/listening/speaking/pronunciation
    VR -> GS : validate_activity(type, questions, max_xp, ...)
    GS -> GS : _build_prompt() with:\\n  - activity rubric\\n  - romanization rules\\n  - generosity guidelines
    GS -> AI : POST /completions\\n  model: llama3-8b-8192, temp: 0.1
    AI --> GS : JSON {{question_results, overall_feedback, suggestion}}
    GS -> GS : parse JSON\\n  merge user_answer + correct_answer\\n  from original questions
    GS --> VR : groq_result dict
    VR -> SS  : calculate_score(questions, max_xp, groq_scores)
    SS --> VR : {{total_score, percentage, passed, question_results}}
end

VR -> GS : _determine_feedback_tier(percentage, attempt_count)
note right
  hint  : attempts >= 3 OR pct < 30%
  praise: pct >= 80%
  lesson: otherwise
end note
GS --> VR : feedback_tier string

opt feedback_tier != "lesson" AND Groq type
    VR -> GS : generate_tier_feedback(type, tier, feedback, ...)
    GS -> AI : 2nd Groq call — refined tier feedback
    AI -->GS  : {{overall_feedback, suggestion}}
    GS --> VR : refined feedback
end

opt SCORE_THRESHOLD_OVERRIDE > 0
    VR -> VR : effective_passed = total_score >= OVERRIDE
end

VR --> AP : ValidateResponse\\n{{score, percentage, passed, feedback, suggestion, tier}}
AP -> AP  : show ScoreModal

AP -> PR  : POST /api/progress/{{pairId}}/complete\\n{{activity_seq_id, score_earned, passed, ...}}
PR -> DB  : query UserLanguageProgress
PR -> DB  : query ActivityCompletion

alt First attempt
    PR -> DB : INSERT ActivityCompletion, xp_delta = score_earned
else Retry — higher score
    PR -> DB : UPDATE score_earned, xp_delta = new - old
else Retry — same or lower score
    PR -> DB : UPDATE attempts++, xp_delta = 0
end

PR -> DB : UPDATE total_xp += xp_delta

opt passed = True AND seq_id == current_activity_id
    PR -> DB : UPDATE current_activity_id = current + 1
    note right: NEXT ACTIVITY UNLOCKED
end

PR -> DB  : COMMIT
PR --> AP : CompletionOut
AP -> U   : show XPBurst animation, refresh dashboard

@enduml
"""

DIAGRAMS["SD-03_STT_Transcription"] = f"""
@startuml SD-03_STT_Transcription
title <b>SD-03 — Speech Transcription (Whisper STT)</b>\\n<i>POST /api/speech/transcribe</i>
{SEQ_SKIN}

actor       "User"                as U
participant "AudioRecorder\\nComponent" as AR
participant "Browser\\nMediaRecorder"   as BR
participant "Speech\\nRouter"          as SR
participant "Whisper\\nService"        as WS
participant "ffmpeg"                   as FF

U  -> AR : click Start Recording
AR -> BR : navigator.mediaDevices.getUserMedia({{audio:true}})

alt Permission denied
    BR --> AR : DOMException
    AR --> U  : show "Microphone access denied"
else Permission granted
    BR --> AR : MediaStream
    AR -> BR  : mediaRecorder.start()
    BR -> AR  : dataavailable event (250ms chunks)
    note right of AR: collecting chunks[]

    U  -> AR  : click Stop Recording
    AR -> BR  : mediaRecorder.stop()
    BR --> AR : final chunk + stop event
    AR -> AR  : blob = new Blob(chunks, 'audio/webm')
    AR --> U  : render <audio> preview

    U  -> AR  : click Submit Recording
    AR -> SR  : POST /api/speech/transcribe\\n(multipart FormData, blob as file)

    SR -> SR  : validate MIME type:\\n  audio/webm · audio/wav · audio/ogg · audio/mp4 etc.

    alt MIME not allowed
        SR --> AR : 400 "Unsupported audio format"
    else File too small (< 100 bytes)
        SR --> AR : 400 "Audio file too small"
    else File too large (> 25 MB)
        SR --> AR : 413 "Audio file too large"
    else Valid audio
        SR -> WS : transcribe_audio(audio_bytes, filename)
        WS -> WS : _load_model() [lazy, cached after first call]

        alt Whisper unavailable (ImportError or load failure)
            WS --> SR : {{text: "", is_mock: True}}
            SR --> AR : TranscribeResponse(is_mock=True)
            AR --> U  : show "Whisper unavailable - Demo Mode"\\nSubmit button blocked
        else Whisper available
            WS -> WS  : write audio_bytes to tempfile
            WS -> FF  : ffmpeg transcode\\naudio/webm → 16kHz mono WAV
            FF --> WS  : out.wav path
            WS -> WS  : _whisper_model.transcribe(out_wav, fp16=False)
            WS -> WS  : extract text, language, confidence\\nfrom result segments
            WS -> WS  : cleanup temp files (silent OSError handling)
            WS --> SR : {{text, language, confidence, is_mock: False}}
            SR --> AR : 200 TranscribeResponse
            AR --> U  : display transcribed text\\nenable Submit Answers button
        end
    end
end

@enduml
"""

DIAGRAMS["SD-04_Admin_Create_Pair"] = f"""
@startuml SD-04_Admin_Create_Pair
title <b>SD-04 — Admin: Create Language Pair & Server Startup</b>\\n<i>POST /api/admin/content/pairs · Uvicorn lifespan</i>
{SEQ_SKIN}

actor       "Admin User"           as ADM
participant "Admin\\nDashboard"    as DASH
participant "Admin\\nRouter"       as AR
participant "Dependencies"         as DEP
participant "ContentService"       as CS
participant "File System"          as FS

group Create Language Pair
    ADM  -> DASH : fill pair_id form (e.g. hi-ko)\\nclick Create
    DASH -> AR   : POST /api/admin/content/pairs\\n{{pair_id: "hi-ko"}}
    AR   -> DEP  : require_admin()
    DEP  --> AR  : Admin User validated

    AR   -> CS   : scaffold_pair("hi-ko")

    loop Month 1 to 3
        loop Block 1 to 6
            loop Activity types (×8: lesson, vocab, reading, writing,\\n          listening, speaking, pronunciation, test)
                CS -> FS : CREATE data/languages/hi/ko/\\n          month_{{m}}/block_{{b}}/M{{m}}B{{b}}_{{type}}.json
            end
        end
    end

    CS -> FS   : CREATE meta.json
    CS --> AR  : success (144 files created)
    AR --> DASH: 201 {{message: "Pair hi-ko created", files: 144}}
    DASH --> ADM: refresh pairs list + show notification
end

newpage

participant "Uvicorn"          as UV
participant "FastAPI App"      as APP
database    "PostgreSQL"       as DB
participant "Security"         as SEC
participant "Logger"           as LOG

group Server Startup (Uvicorn lifespan)
    UV  -> APP : startup event (lifespan __aenter__)
    APP -> DB  : create_tables()
    note right of DB
      import models: User, UserLanguageProgress,
      ActivityCompletion, FriendRequest
      Base.metadata.create_all(bind=engine)
      Creates tables IF NOT EXIST
    end note
    DB --> APP : tables ready

    APP -> APP : seed_admin()
    APP -> DB  : SELECT * FROM users WHERE email = ADMIN_EMAIL

    alt Admin already exists
        DB  --> APP : User found
        APP -> LOG  : "Admin user already exists"
    else First boot
        APP -> SEC  : hash_password(ADMIN_PASSWORD)
        SEC --> APP : bcrypt hash
        APP -> DB   : INSERT User {{role='admin', email=ADMIN_EMAIL}}
        DB  --> APP : committed
        APP -> LOG  : "Admin user created: admin@learnwise.app"
    end

    APP -> FS  : mkdir uploads/ (if not exists)
    APP -> APP : ADD CORSMiddleware (origins from ALLOWED_ORIGINS)
    APP -> APP : MOUNT /uploads → StaticFiles(uploads/)
    APP -> APP : MOUNT /static → StaticFiles(data/languages/)
    APP -> APP : REGISTER all routers:\\n  /api/auth · /api/users · /api/content\\n  /api/progress · /api/validate · /api/speech\\n  /api/leaderboard · /api/friends · /api/admin
    APP -> LOG : "Startup complete. Server ready."
    UV  -> UV  : BIND 0.0.0.0:8000\\nBegin accepting HTTP connections
end

@enduml
"""

# ══════════════════════════════════════════
# ACTIVITY DIAGRAMS
# ══════════════════════════════════════════

DIAGRAMS["AD-01_Registration"] = f"""
@startuml AD-01_Registration
title <b>AD-01 — User Registration & Login Activity Flow</b>
{ACT_SKIN}

|User|
start
:Fill registration form\\n{{username, email, password}};

|Frontend|
:Client-side validation\\n(username 3-50 chars, alphanumeric+_\\npassword min 8 chars, valid email);

if (Form valid?) then (NO)
  :Show inline\\nvalidation errors;
  |User|
  :Correct fields;
  |Frontend|
else (YES)
endif

:dispatch registerUser()\\nRedux → Axios;
:SET state.loading = true;

|Backend|
:Validate Pydantic\\nRegistration Schema;

if (Schema valid?) then (NO)
  :Return 422 Unprocessable;
  stop
else (YES)
endif

:Query users\\nWHERE email = req.email;

if (Email exists?) then (YES)
  :Return 400\\n"Email already registered";
  stop
else (NO)
endif

:Query users\\nWHERE username = req.username;

if (Username taken?) then (YES)
  :Return 400\\n"Username already taken";
  stop
else (NO)
endif

:Hash password (bcrypt);

|Database|
:INSERT INTO users\\n{{username, email, hash, role='user'}};
:COMMIT User record;

|Backend|
:Create HS256 JWT\\n(exp: +7 days);
:Return 201 TokenResponse;

|Frontend/ Redux|
:RECEIVE TokenResponse;
:localStorage.setItem('lw_token');
:localStorage.setItem('lw_user');
:SET isAuthenticated = true;
:SET state.loading = false;

|User|
:Redirected to /dashboard;
stop

@enduml
"""

DIAGRAMS["AD-02_Dashboard_Load"] = ("""
@startuml AD-02_Dashboard_Load
title <b>AD-02 — Dashboard Load & Activity Roadmap Render</b>
ACT_SKIN_PLACEHOLDER

|User|
start
:Navigate to /dashboard;

|Dashboard Component|
if (ProtectedRoute:
isAuthenticated?) then (NO)
  :Redirect to /login;
  stop
else (YES)
endif

:Render loading skeleton;

fork
  |Redux Store|
  :dispatch(fetchAllProgress())\nGET /api/progress;
  :SET allProgress in state;
fork again
  :dispatch(fetchPairs())\nGET /api/content/pairs;
  :SET pairs in state;
end fork

|Dashboard Component|
:Auto-select first pair\nif currentPairId = null;

fork
  :GET /api/content/PAIR_ID/meta\nRead meta.json tree;
  :SET meta state;
fork again
  :GET /api/progress/PAIR_ID/completions\nLoad completion records;
  :SET completions state;
end fork

:Build completedSeqIds Set\n(completions WHERE passed=True);
:Determine currentActivityId\nfrom progress (default=1);

repeat
  :Process next activity node;
  if (isCompleted(seqId)?) then (YES)
    :Render GREEN ring\n+ checkmark icon;
  else (NO)
    if (isUnlocked(seqId)?) then (YES)
      :Render COLORED clickable node\n(colored by activity type);
    else (NO)
      :Render LOCKED node\n(grey + lock icon);
    endif
  endif
repeat while (more nodes?) is (YES)
-> NO;

|User|
:View complete roadmap\nwith progress state;
stop

@enduml
""").replace("ACT_SKIN_PLACEHOLDER", ACT_SKIN)

DIAGRAMS["AD-03_Activity_Execution"] = ("""
@startuml AD-03_Activity_Execution
title <b>AD-03 — Activity Execution & Scoring General Flow</b>
ACT_SKIN_PLACEHOLDER

|User|
start
:Click unlocked activity node;

|Activity Page|
:Navigate to\n/activity/PAIR_ID/TYPE;
:ActivityRouter maps type\nto component;
:GET /api/content/PAIR_ID/activity\n?file=ACTIVITY_FILE;

|User|
:Read / listen / record / write;

|Activity Page|
if (All answers filled?) then (NO)
  :Show "Please answer\nall questions";
  |User|
  :Complete remaining answers;
  |Activity Page|
else (YES)
endif

:Build ValidateRequest payload;

|Backend Validate|
if (MCQ_TYPES\n(activity_type = "test")?) then (YES)
  |Scoring Service|
  :score_mcq_locally(questions, max_xp)\nstring compare each answer;
  :calculate_score()\nclamp, sum, percentage;
  :passed = percentage >= 20%;
else (NO — Groq AI path)
  |Groq Service|
  :_build_prompt() with rubrics;
  :POST to LLaMA-3-8B\ntemp=0.1 (deterministic);
  :PARSE JSON response;
  |Scoring Service|
  :calculate_score(groq_scores)\\nclamp to [0, per_q_max];
  :percentage, passed = pct >= 20%;
endif

|Backend Validate|
:_determine_feedback_tier\\n(percentage, attempt_count);

if (tier != "lesson"\\nAND Groq type?) then (YES)
  :generate_tier_feedback()\\n2nd Groq call for refined feedback;
else (NO)
endif

if (SCORE_THRESHOLD_OVERRIDE > 0?) then (YES)
  :effective_passed =\\nscore >= OVERRIDE;
else (NO)
endif

:Return ValidateResponse;

|Activity Page|
:Show ScoreModal\\n(score, passed, feedback, XP earned);

|Backend Progress|
:POST /api/progress/PAIR_ID/complete;

if (First attempt?) then (YES)
  :INSERT ActivityCompletion\\nxp_delta = score_earned;
else (NO — Retry)
  if (New score > old?) then (YES)
    :UPDATE score_earned\\nxp_delta = new - old;
  else (NO)
    :UPDATE attempts++\\nxp_delta = 0;
  endif
endif

:UPDATE total_xp += xp_delta;

if (passed AND seq_id\\n== current_activity_id?) then (YES)
  :INCREMENT current_activity_id;
  :UNLOCK next activity;
else (NO)
endif

:COMMIT;
:dispatch(fetchPairProgress);

|User|
:View result, click Continue\\nnext activity unlocked on dashboard;
stop

@enduml
""").replace("ACT_SKIN_PLACEHOLDER", ACT_SKIN)

DIAGRAMS["AD-04_STT_Recording"] = f"""
@startuml AD-04_STT_Recording
title <b>AD-04 — STT Recording Flow (Speaking / Pronunciation)</b>
{ACT_SKIN}

|User|
start
:Click "Start Recording";

|AudioRecorder Component|
:Request microphone permission\\nnavigator.mediaDevices.getUserMedia();

if (Permission granted?) then (NO)
  :Show "Microphone access denied";
  stop
else (YES)
endif

:INITIALIZE MediaRecorder\\n{{type: audio/webm, codec: opus}};
:mediaRecorder.start();
:Show red pulse recording indicator;

|Browser API|
:EMIT dataavailable events\\nevery 250ms;

|AudioRecorder Component|
:Collect audio chunks array;

|User|
:Speak into microphone;
:Click "Stop Recording";

|AudioRecorder Component|
:mediaRecorder.stop();

|Browser API|
:EMIT final chunk + stop event;

|AudioRecorder Component|
:blob = new Blob(chunks, 'audio/webm');
:CREATE object URL;
:Render <audio> preview controls;

|User|
:Listen to playback;
:Click "Submit Recording";

|AudioRecorder Component|
:Append blob to FormData;

|Backend Speech Router|
:POST /api/speech/transcribe;
:Validate MIME type;

if (MIME type allowed?) then (NO)
  :400 "Unsupported audio format";
  stop
else (YES)
endif

:Read audio bytes;

if (Size 100B < size < 25MB?) then (NO)
  :400 "Audio too small"\\nor 413 "Audio too large";
  stop
else (YES)
endif

|Whisper Service|
:transcribe_audio(audio_bytes, filename);
:_load_model() — lazy load, cached;

if (Whisper available?) then (NO)
  :Return {{is_mock: True}};
  |AudioRecorder Component|
  :Show "Whisper unavailable\\nDemo Mode" warning;
  :Block Submit button;
  stop
else (YES)
endif

:Write bytes to temp file;
:ffmpeg transcode → 16kHz mono WAV;
:_whisper_model.transcribe(wav, fp16=False);
:Extract text, language, confidence;
:Cleanup temp files (silent OSError);
:Return {{text, language, confidence, is_mock: False}};

|Activity Page|
:SET user_answer = transcribed text;
:Display transcription to user;
:Enable Submit Answers button;

|User|
:Review transcription;
:Click Submit Answers → Validate flow;
stop

@enduml
"""

DIAGRAMS["AD-05_Progress_Unlock"] = f"""
@startuml AD-05_Progress_Unlock
title <b>AD-05 — Progress Advancement & XP Unlock Logic</b>\\n<i>POST /api/progress/{{pair_id}}/complete internal flow</i>
{ACT_SKIN}

|Progress Router|
start
:RECEIVE CompleteActivityRequest\\n{{seq_id, score_earned, passed, lang_pair_id, ...}};

if (SCORE_THRESHOLD_OVERRIDE > 0?) then (YES)
  :effective_passed =\\nscore_earned >= OVERRIDE;
else (NO)
  :effective_passed = req.passed;
endif

:Derive month and block from seq_id\\nzero_based = seq_id - 1\\nmonth = (zero_based // 48) + 1\\nblock  = ((zero_based %  48) // 8) + 1;

|Database|
:SELECT UserLanguageProgress\\nWHERE user_id AND lang_pair_id;

if (Progress record exists?) then (NO)
  :INSERT new UserLanguageProgress\\nmonth=1, block=1, activity_id=seq_id;
  :COMMIT;
else (YES)
endif

:SELECT ActivityCompletion\\nWHERE user_id AND pair_id AND seq_id;

|Progress Router|
if (Completion already exists?) then (YES — Retry)
  if (new score > existing score?) then (YES)
    :xp_delta = new_score - old_score;
    |Database|
    :UPDATE score_earned = new_score;
    :UPDATE passed = True;
  else (NO)
    :xp_delta = 0\\n(no XP for same or lower score);
  endif
  |Database|
  :UPDATE attempts += 1;
  :UPDATE ai_feedback, ai_suggestion;
  :UPDATE completed_at = utcnow();
else (NO — First Attempt)
  :xp_delta = score_earned;
  |Database|
  :INSERT ActivityCompletion\\n{{all fields, attempts=1}};
endif

|Database|
:UPDATE total_xp += xp_delta;
:UPDATE last_activity_at = utcnow();

|Progress Router|
if (effective_passed = True\\nAND seq_id == current_activity_id?) then (YES — Advance)
  :next_id = current_activity_id + 1;
  |Database|
  :UPDATE current_activity_id = next_id;
  :UPDATE current_month, current_block\\n= _derive_month_block(next_id);
  note right
    This is the UNLOCK mechanism.
    The next activity becomes accessible
    on the learner's dashboard.
  end note
else (NO — Stay)
  note right
    Activity already passed, failed,
    or user jumped ahead — position stays.
  end note
endif

|Database|
:COMMIT all changes;
:REFRESH ActivityCompletion record;

|Progress Router|
:RETURN CompletionOut;
stop

@enduml
"""

# ══════════════════════════════════════════
# STATE DIAGRAMS
# ══════════════════════════════════════════

DIAGRAMS["SM-01_User_Account"] = f"""
@startuml SM-01_User_Account
title <b>SM-01 — User Account Lifecycle</b>\\n<i>Entity: User (database record)</i>
{STATE_SKIN}

[*] --> UNREGISTERED

UNREGISTERED : entry / No account exists
UNREGISTERED --> REGISTERED_ACTIVE : POST /api/auth/register\\n[valid form, unique email+username]

state REGISTERED_ACTIVE {{
  [*] --> ACTIVE_SESSION
  ACTIVE_SESSION : entry / created_at=utcnow(), is_active=True, role='user'
}}

REGISTERED_ACTIVE --> LOGGED_IN : POST /api/auth/login\\n[valid password, is_active=True]
REGISTERED_ACTIVE --> DEACTIVATED : admin calls POST /users/{{id}}/deactivate
REGISTERED_ACTIVE --> [*] : DELETE user (cascade)

state LOGGED_IN {{
  [*] --> SESSION_ACTIVE
  SESSION_ACTIVE : entry / last_active=utcnow(), JWT issued
  SESSION_ACTIVE --> SESSION_ACTIVE : GET /api/auth/me [JWT valid]
}}

LOGGED_IN --> LOGGED_OUT : client calls logout()\\nOR JWT expires/invalid
LOGGED_IN --> DEACTIVATED : admin deactivates account\\n[JWT constraint: user_id != current_admin.id]

LOGGED_OUT : entry / localStorage.removeItem('lw_token')\\nOR redirect to /login

LOGGED_OUT --> LOGGED_IN : POST /api/auth/login [valid credentials]

DEACTIVATED : entry / is_active = False
DEACTIVATED : exit  / is_active = True
DEACTIVATED --> REGISTERED_ACTIVE : admin calls POST /users/{{id}}/activate

state ADMIN_ROLE {{
  [*] --> ADMIN_SESSION
  ADMIN_SESSION : role = 'admin' (seeded at startup)
  ADMIN_SESSION --> ADMIN_SESSION : POST /api/auth/admin/login [valid]
}}

note right of ADMIN_ROLE
  Seeded automatically at server startup.
  Cannot deactivate own account.
  Guard: user_id != current_user.id
end note

@enduml
"""

DIAGRAMS["SM-02_JWT_Token"] = f"""
@startuml SM-02_JWT_Token
title <b>SM-02 — JWT Token Lifecycle</b>\\n<i>Entity: Bearer Token — security.py · src/api/client.js</i>
{STATE_SKIN}

[*] --> DOES_NOT_EXIST

DOES_NOT_EXIST : No token in localStorage
DOES_NOT_EXIST --> ACTIVE : successful login / register\\n/ entry: stored as lw_token

state ACTIVE {{
  [*] --> PENDING_DECODE
  PENDING_DECODE : Axios request interceptor\\nattaches Authorization header

  PENDING_DECODE --> VALID   : decode_token()\\n[signature ok, not expired]
  PENDING_DECODE --> INVALID : JWTError raised
  PENDING_DECODE --> EXPIRED : current_time > exp
}}

state VALID {{
  [*] --> CHECKING_USER
  CHECKING_USER --> ACCEPTED : get_current_user()\\n[user found, is_active=True]
  CHECKING_USER --> REJECTED : get_current_user()\\n[user not found OR is_active=False]
}}

ACCEPTED : Request proceeds to endpoint handler
REJECTED : Returns HTTPException 401

INVALID --> CLEARED : Axios response interceptor\\ndetects 401
EXPIRED --> CLEARED : Axios response interceptor\\ndetects 401

state CLEARED {{
  [*] --> REMOVING
  REMOVING : localStorage.removeItem('lw_token')\\nlocalStorage.removeItem('lw_user')
  REMOVING --> REDIRECT_ADMIN : user.role == 'admin' OR\\npath starts with /admin
  REMOVING --> REDIRECT_USER  : user.role == 'user'
}}

CLEARED --> DOES_NOT_EXIST

note bottom of CLEARED
  Admin → redirect /admin/login
  User  → redirect /login
end note

@enduml
"""

DIAGRAMS["SM-03_Language_Progress"] = f"""
@startuml SM-03_Language_Progress
title <b>SM-03 — UserLanguageProgress State Machine</b>\\n<i>Entity: UserLanguageProgress — curriculum progression 1→144</i>
{STATE_SKIN}

[*] --> NOT_STARTED

NOT_STARTED : No progress record for this pair
NOT_STARTED --> ACTIVE : POST /api/progress/{{pair_id}}/start\\n/ entry: xp=0, month=1, block=1, activity_id=1

state ACTIVE {{

  state ACTIVITY_POSITION {{
    [*] --> AT_ACTIVITY_N
    AT_ACTIVITY_N : current_activity_id = N (1…144)
    AT_ACTIVITY_N : entry / current_month = derived\\ncurrent_block = derived

    AT_ACTIVITY_N --> AT_ACTIVITY_N : POST /complete\\n[passed=False OR seq_id != current]\\n/ action: XP delta only, no advance

    AT_ACTIVITY_N --> AT_ACTIVITY_N_PLUS_1 : POST /complete\\n[passed=True AND seq_id == current]\\n/ action: current_activity_id++\\n  re-derive month/block
    AT_ACTIVITY_N_PLUS_1 : current_activity_id = N+1
  }}

  state XP_LEVEL {{
    [*] --> BEGINNER
    BEGINNER : total_xp < 500
    BEGINNER --> INTERMEDIATE : total_xp >= 500
    INTERMEDIATE : total_xp 500–2000
    INTERMEDIATE --> ADVANCED : total_xp >= 2000
    ADVANCED : total_xp > 2000
    ADVANCED --> ADVANCED : retry with improvement\\n/ total_xp += xp_delta
  }}
}}

ACTIVE --> CURRICULUM_COMPLETE : AT_ACTIVITY(144)\\n[passed=True]
CURRICULUM_COMPLETE : All 144 activities passed\\n(3 months × 6 blocks × 8 types)
CURRICULUM_COMPLETE --> ACTIVE : retry any past activity\\n/ XP improvement only, position stays at 144

note right of ACTIVITY_POSITION
  Formula for deriving position:
  zero = activity_seq_id - 1
  month = (zero // 48) + 1
  block = ((zero % 48) // 8) + 1
end note

@enduml
"""

DIAGRAMS["SM-04_Activity_Completion"] = f"""
@startuml SM-04_Activity_Completion
title <b>SM-04 — ActivityCompletion Record & Activity Page States</b>\\n<i>Entity: ActivityCompletion (DB) · ActivityPage (React)</i>
{STATE_SKIN}

state "ActivityCompletion (Database)" as DB_SM {{
  [*] --> NEVER_ATTEMPTED

  NEVER_ATTEMPTED : No completion row exists
  NEVER_ATTEMPTED --> ATTEMPTED : POST /progress/{{pair}}/complete\\n[first attempt]\\n/ INSERT completion, attempts=1

  state ATTEMPTED {{
    [*] --> FAILED

    FAILED : passed = False, score_earned = N
    FAILED --> PASSED : POST /complete\\n[passed=True, new_score > old_score]\\n/ xp_delta = new - old, UPDATE score

    PASSED : passed = True, score_earned = best
    PASSED --> PASSED : POST /complete [retry, new_score > old]\\n/ xp_delta = new - old, attempts++
    PASSED --> PASSED : POST /complete [retry, new_score <= old]\\n/ xp_delta = 0, attempts++
  }}

  note bottom of ATTEMPTED
    Score only improves upward.
    Attempts counter always increments.
    ai_feedback always overwritten with latest.
  end note
}}

state "ActivityPage (React Component)" as UI_SM {{
  [*] --> LOADING_CONTENT

  LOADING_CONTENT : entry / GET /api/content/PAIR_ID/activity
  LOADING_CONTENT --> CONTENT_READY : fetch success
  LOADING_CONTENT --> LOAD_ERROR : fetch error

  LOAD_ERROR --> [*] : user clicks ← Back

  state CONTENT_READY {{
    [*] --> IDLE
    IDLE --> ANSWERING : user starts filling answers

    state ANSWERING {{
      [*] --> FILLING
      FILLING --> SUBMITTING : all required answers filled\\nuser clicks Submit
    }}

    state RECORDING {{
      [*] --> NOT_RECORDING
      NOT_RECORDING --> RECORDING_ACTIVE : user clicks Record
      RECORDING_ACTIVE : entry / MediaRecorder.start()
      RECORDING_ACTIVE --> PROCESSING_AUDIO : user clicks Stop
      PROCESSING_AUDIO --> TRANSCRIBED : is_mock=False, text set
      PROCESSING_AUDIO --> MOCK_WARNING : is_mock=True (Whisper unavailable)
      TRANSCRIBED --> NOT_RECORDING : user clicks Re-record
      MOCK_WARNING --> NOT_RECORDING : user clicks Re-record
    }}
  }}

  CONTENT_READY --> PASSED_RESULT : POST /validate succeeds, passed=True
  CONTENT_READY --> FAILED_RESULT : POST /validate succeeds, passed=False
  CONTENT_READY --> CONTENT_READY : network error → toast → retry

  PASSED_RESULT : entry / ScoreModal (green), XP earned animation\\nPOST /progress/complete in background
  PASSED_RESULT --> [*] : user clicks Continue\\n/ navigate to /dashboard (next unlocked)
  PASSED_RESULT --> CONTENT_READY : user clicks Retry

  FAILED_RESULT : entry / ScoreModal (red), suggestion shown\\nPOST /progress/complete records attempt
  FAILED_RESULT --> CONTENT_READY : user clicks Try Again / attempt_count++
  FAILED_RESULT --> [*] : user clicks ← Back
}}

@enduml
"""

DIAGRAMS["SM-05_Services"] = f"""
@startuml SM-05_Services
title <b>SM-05 — Service Layer State Machines</b>\\n<i>WhisperService · GroqService · AudioRecorder · Redux Auth</i>
{STATE_SKIN}

state "WhisperService (Python)" as WS {{
  [*] --> UNINITIALIZED
  UNINITIALIZED : _whisper_model=None, _whisper_available=None
  UNINITIALIZED --> LOADING : first call to transcribe_audio()

  LOADING : entry / _load_model() called\\nimport whisper; whisper.load_model(settings.WHISPER_MODEL)
  LOADING --> AVAILABLE   : model loads successfully\\n/ _whisper_available=True, model cached
  LOADING --> UNAVAILABLE : ImportError or any exception\\n/ _whisper_available=False

  state AVAILABLE {{
    [*] --> IDLE_W
    IDLE_W --> TRANSCRIBING : transcribe_audio() called
    TRANSCRIBING : ffmpeg transcode → model.transcribe()
    TRANSCRIBING --> IDLE_W : success / return {{text, language, confidence, is_mock:False}}
    TRANSCRIBING --> IDLE_W : exception / return {{text:"", is_mock:False}}
  }}

  UNAVAILABLE --> UNAVAILABLE : transcribe_audio() called\\n/ return {{text:"", is_mock:True}}
  note right of UNAVAILABLE: No retry. is_mock=True signals\\nfrontend to block submission.
}}

state "GroqService Call (Python)" as GS {{
  [*] --> IDLE_G
  IDLE_G --> BUILDING_PROMPT : validate_activity() OR\\ngenerate_tier_feedback() called
  BUILDING_PROMPT : _build_prompt() combines:\\nrubric + romanization rules +\\ngenerosity note + questions
  BUILDING_PROMPT --> CALLING_GROQ : prompt ready

  CALLING_GROQ : client.chat.completions.create()\\nmodel=llama3-8b-8192, temperature=0.1
  CALLING_GROQ --> PARSING_RESPONSE : API returns JSON
  CALLING_GROQ --> ERROR_G          : timeout or network error

  PARSING_RESPONSE : extract JSON, merge user_answer +\\ncorrect_answer from originals
  PARSING_RESPONSE --> RESULT_READY : JSON parse success
  PARSING_RESPONSE --> ERROR_G      : malformed JSON

  RESULT_READY --> IDLE_G : return dict to caller
  ERROR_G --> IDLE_G : return fallback dict\\n{{overall_feedback: "AI unavailable"}}
}}

state "Redux authSlice (Frontend)" as AUTH {{
  [*] --> UNAUTHENTICATED
  UNAUTHENTICATED : token=null, isAuthenticated=false
  UNAUTHENTICATED --> LOADING_A  : dispatch loginUser / registerUser (pending)
  UNAUTHENTICATED --> AUTHENTICATED : localStorage has lw_token\\n[hydrated on page load]

  LOADING_A : loading=true, error=null
  LOADING_A --> AUTHENTICATED : fulfilled
  LOADING_A --> ERROR_A       : rejected

  AUTHENTICATED : token=JWT, isAuthenticated=true\\nlocalStorage written
  AUTHENTICATED --> UNAUTHENTICATED : dispatch logout\\nOR Axios 401 interceptor fires
  AUTHENTICATED --> AUTHENTICATED   : dispatch updateUser() [self-loop]

  ERROR_A : loading=false, error=message
  ERROR_A --> LOADING_A      : user retries login
  ERROR_A --> UNAUTHENTICATED : dispatch clearError()
}}

@enduml
"""


# ─────────────────────────────────────────────────────────────────
# WORD DOCUMENT BUILDER
# ─────────────────────────────────────────────────────────────────
def set_cell_bg(cell, hex_color):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)


def build_document(diagram_paths: dict) -> Document:
    doc = Document()

    # Page setup
    for section in doc.sections:
        section.page_width   = Inches(8.5)
        section.page_height  = Inches(11)
        section.left_margin  = Inches(0.9)
        section.right_margin = Inches(0.9)
        section.top_margin   = Inches(0.9)
        section.bottom_margin= Inches(0.9)

    # ── COVER PAGE ──────────────────────────────────────────────
    for _ in range(4):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("LearnWise")
    r.font.size = Pt(42); r.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("AI-Powered Language Learning Platform")
    r.font.size = Pt(16)
    r.font.color.rgb = RGBColor(0x27, 0x6E, 0xD8)

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("SOFTWARE DESIGN DOCUMENT")
    r.font.size = Pt(26); r.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Class Diagrams  ·  Sequence Diagrams  ·  Activity Diagrams  ·  State Diagrams")
    r.font.size = Pt(13); r.italic = True
    r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    doc.add_paragraph()
    doc.add_paragraph()

    meta = [
        ("Document Version",   "1.0"),
        ("Standard",           "IEEE Std 1016 — Software Design Descriptions"),
        ("Classification",     "Technical Reference – Stakeholder Presentation"),
        ("Backend",            "FastAPI (Python 3.10) · PostgreSQL · SQLAlchemy ORM"),
        ("AI / ML",            "Groq LLaMA-3-8B-8192 · OpenAI Whisper (on-premise)"),
        ("Frontend",           "React 18 · Redux Toolkit · Axios · Vite"),
        ("Date",               "April 2026"),
    ]
    t = doc.add_table(rows=len(meta), cols=2)
    t.style = 'Table Grid'
    for i, (k, v) in enumerate(meta):
        cells = t.rows[i].cells
        cells[0].text = k
        cells[1].text = v
        bg = "1F3864" if i == 0 else ("EBF2FA" if i % 2 == 0 else "FFFFFF")
        fc = "FFFFFF" if i == 0 else "000000"
        for c in cells:
            set_cell_bg(c, bg)
            for para in c.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(10)
                    run.font.bold = (i == 0)
                    run.font.color.rgb = RGBColor(
                        int(fc[0:2],16), int(fc[2:4],16), int(fc[4:6],16))

    doc.add_page_break()

    # ── TABLE OF CONTENTS ────────────────────────────────────────
    h = doc.add_heading("Table of Contents", level=1)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
        run.font.size = Pt(18)

    toc = [
        ("1.", "System Context & Architecture Overview"),
        ("2.", "Section 1 — Class Diagrams"),
        ("    2.1", "CD-01: Backend Database Models"),
        ("    2.2", "CD-02: Backend Core & Services"),
        ("    2.3", "CD-03: Backend API Routers"),
        ("    2.4", "CD-04: Frontend State Management & API"),
        ("    2.5", "CD-05: Frontend Pages & Components"),
        ("3.", "Section 2 — Sequence Diagrams"),
        ("    3.1", "SD-01: User Registration Flow"),
        ("    3.2", "SD-02: Activity Submission & AI Grading"),
        ("    3.3", "SD-03: Speech Transcription (Whisper STT)"),
        ("    3.4", "SD-04: Admin Create Pair & Server Startup"),
        ("4.", "Section 3 — Activity Diagrams"),
        ("    4.1", "AD-01: User Registration & Login"),
        ("    4.2", "AD-02: Dashboard Load & Render"),
        ("    4.3", "AD-03: Activity Execution General Flow"),
        ("    4.4", "AD-04: STT Recording Flow"),
        ("    4.5", "AD-05: Progress Advancement & XP Unlock"),
        ("5.", "Section 4 — State Diagrams"),
        ("    5.1", "SM-01: User Account Lifecycle"),
        ("    5.2", "SM-02: JWT Token Lifecycle"),
        ("    5.3", "SM-03: UserLanguageProgress Curriculum"),
        ("    5.4", "SM-04: ActivityCompletion & Activity Page"),
        ("    5.5", "SM-05: Service Layer State Machines"),
    ]
    for num, title in toc:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(f"{num}  ")
        r1.bold = True; r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(0x1F,0x38,0x64)
        r2 = p.add_run(title)
        r2.font.size = Pt(10)

    doc.add_page_break()

    # ── SYSTEM CONTEXT ────────────────────────────────────────────
    h = doc.add_heading("1. System Context & Architecture Overview", level=1)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0x1F,0x38,0x64)
        run.font.size = Pt(18)

    p = doc.add_paragraph()
    r = p.add_run(
        "LearnWise is a full-stack AI-powered language learning platform. Learners progress "
        "through a hierarchical curriculum: Language Pair → Month → Block → Activity. Each block "
        "contains 8 distinct activity types. Open-ended activities (writing, speaking, "
        "pronunciation, reading, vocabulary, lesson) are graded in real-time by the Groq "
        "LLaMA-3 API. Multiple-choice activities use a deterministic local scoring engine. "
        "Audio activities are transcribed using an on-premise OpenAI Whisper model. All "
        "progression data is persisted to PostgreSQL, with XP accumulation and social "
        "leaderboards driving engagement."
    )
    r.font.size = Pt(11)

    doc.add_paragraph()

    p = doc.add_paragraph()
    r = p.add_run("Architecture Overview"); r.bold = True; r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(0x1F,0x38,0x64)

    arch_lines = [
        "Browser  (React 18 + Redux Toolkit + Axios + Vite)",
        "         ↕   HTTPS / REST JSON API",
        "FastAPI Backend  (Uvicorn · Python 3.10)",
        "   ├── Routers:  Auth · Users · Progress · Validate · Speech",
        "   │             Leaderboard · Friends · Admin · Content",
        "   ├── Services: GroqService · WhisperService · ScoringService · ContentService",
        "   └── Core:     Security (JWT+bcrypt) · Database (SQLAlchemy) · Config · Dependencies",
        "         ↕   SQLAlchemy ORM",
        "PostgreSQL Database",
        "         ↕   External HTTP / Local Process",
        "Groq Cloud API (LLaMA-3-8B-8192)     OpenAI Whisper (on-premise small model)",
    ]
    for line in arch_lines:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.space_after = Pt(1)
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto')
        shd.set(qn('w:fill'),'F2F2F2'); pPr.append(shd)
        r = p.add_run(line)
        r.font.name = 'Courier New'; r.font.size = Pt(9)

    doc.add_paragraph()
    p = doc.add_paragraph()
    r = p.add_run("Curriculum Hierarchy:  ")
    r.bold = True; r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(0x1F,0x38,0x64)
    r2 = p.add_run(
        "Language Pair (e.g. hi-ja)  →  Month (1–3)  →  Block (1–6)  "
        "→  Activity (8 types per block).  "
        "Total per pair: 3 × 6 × 8 = 144 activities, each addressed by a unique "
        "activity_seq_id (1–144)."
    )
    r2.font.size = Pt(11)

    doc.add_page_break()

    # ── SECTION BANNER helper ─────────────────────────────────────
    def section_banner(text, color="1F3864"):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after  = Pt(6)
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto')
        shd.set(qn('w:fill'), color); pPr.append(shd)
        r = p.add_run(f"  {text}")
        r.bold = True; r.font.size = Pt(16)
        r.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
        return p

    def diagram_caption(diagram_id, title, description):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after  = Pt(2)
        r1 = p.add_run(f"{diagram_id}  —  ")
        r1.bold = True; r1.font.size = Pt(12)
        r1.font.color.rgb = RGBColor(0x1F,0x38,0x64)
        r2 = p.add_run(title)
        r2.bold = True; r2.font.size = Pt(12)
        r2.font.color.rgb = RGBColor(0x1F,0x38,0x64)
        if description:
            p2 = doc.add_paragraph()
            p2.paragraph_format.space_after = Pt(6)
            r = p2.add_run(description)
            r.italic = True; r.font.size = Pt(9)
            r.font.color.rgb = RGBColor(0x55,0x55,0x55)

    def insert_diagram(key, width_inches=6.5):
        path = diagram_paths.get(key)
        if path and Path(path).exists():
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(path, width=Inches(width_inches))
        else:
            p = doc.add_paragraph()
            r = p.add_run(f"[Diagram {key} — render failed, check internet connection]")
            r.italic = True; r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(0xCC,0x00,0x00)

    # ── SECTION 2: CLASS DIAGRAMS ─────────────────────────────────
    section_banner("Section 1  —  Class Diagrams")
    doc.add_paragraph().add_run(
        "Class diagrams document the static structure of the LearnWise platform following "
        "UML 2.5 notation. Each diagram shows classes with their attributes (typed and "
        "constrained), methods, stereotypes, and inter-class associations with multiplicities. "
        "Layers are organized from database models through to frontend components."
    ).font.size = Pt(10)
    doc.add_paragraph()

    diagram_caption("CD-01", "Backend Database Models Layer",
        "SQLAlchemy ORM classes mapped to PostgreSQL tables: users, user_language_progress, "
        "activity_completions, friend_requests. Shows all foreign key relationships, "
        "cascade rules, and unique constraints.")
    insert_diagram("CD-01_DB_Models")
    doc.add_page_break()

    diagram_caption("CD-02", "Backend Core & Services Layer",
        "Configuration singleton (Settings), database session factory (Database), "
        "authentication utilities (Security, Dependencies), and all four service classes "
        "(ScoringService, GroqService, WhisperService, ContentService) with their dependencies.")
    insert_diagram("CD-02_Core_Services")
    doc.add_page_break()

    diagram_caption("CD-03", "Backend API Routers Layer",
        "All eight FastAPI routers registered under the /api prefix. Each router shows "
        "its URL prefix, authentication dependencies, and complete endpoint signatures "
        "with parameter and return types.")
    insert_diagram("CD-03_API_Routers")
    doc.add_page_break()

    diagram_caption("CD-04", "Frontend State Management & API Client Layer",
        "Redux Toolkit slices (authSlice, progressSlice, UISlice) with their state shapes, "
        "synchronous reducers, and async thunks. Axios client instance with request/response "
        "interceptors and all four API module classes.")
    insert_diagram("CD-04_Frontend_State")
    doc.add_page_break()

    diagram_caption("CD-05", "Frontend Pages & Components Layer",
        "React component hierarchy from App router through ProtectedRoute/AdminRoute guards, "
        "DashboardPage, ActivityRouter, all eight activity pages, and shared UI components "
        "(ScoreModal, AudioRecorder, AudioPlayer).")
    insert_diagram("CD-05_Frontend_Pages")
    doc.add_page_break()

    # ── SECTION 3: SEQUENCE DIAGRAMS ─────────────────────────────
    section_banner("Section 2  —  Sequence Diagrams", "2E6EBF")
    doc.add_paragraph().add_run(
        "Sequence diagrams document time-ordered message exchanges between actors and system "
        "components. Each diagram specifies all participants (lifelines), synchronous and "
        "asynchronous messages, return values, alt/else conditional frames, opt optional "
        "frames, par parallel frames, and loop frames."
    ).font.size = Pt(10)
    doc.add_paragraph()

    diagram_caption("SD-01", "User Registration Flow",
        "Complete message sequence from form submission through Pydantic schema validation, "
        "duplicate detection, bcrypt hashing, database insertion, JWT issuance, and "
        "Redux state hydration ending with navigation to /dashboard.")
    insert_diagram("SD-01_User_Registration")
    doc.add_page_break()

    diagram_caption("SD-02", "Activity Submission, AI Grading & Progress Recording",
        "Full pipeline from Submit click through MCQ/Groq branching, LLaMA-3 API call, "
        "ScoringService calculation, feedback tier determination, optional second Groq call, "
        "SCORE_THRESHOLD_OVERRIDE application, and completion recording with XP and "
        "activity unlock logic.")
    insert_diagram("SD-02_Activity_Submission", width_inches=6.8)
    doc.add_page_break()

    diagram_caption("SD-03", "Speech Transcription — Whisper STT Pipeline",
        "Complete audio-to-text sequence: MediaRecorder capture, blob assembly, "
        "multipart POST, MIME and size validation in SpeechRouter, lazy Whisper model "
        "loading, ffmpeg transcoding to 16kHz WAV, Whisper inference, and the "
        "is_mock=True fallback path for graceful degradation.")
    insert_diagram("SD-03_STT_Transcription")
    doc.add_page_break()

    diagram_caption("SD-04", "Admin: Create Language Pair & Server Startup Initialization",
        "Two flows: (1) Admin scaffolding a complete language pair curriculum (144 JSON files) "
        "via ContentService. (2) Uvicorn lifespan startup sequence: table creation, admin "
        "seeding, upload directory, CORS middleware, static mounts, and router registration.")
    insert_diagram("SD-04_Admin_Create_Pair", width_inches=6.8)
    doc.add_page_break()

    # ── SECTION 4: ACTIVITY DIAGRAMS ─────────────────────────────
    section_banner("Section 3  —  Activity Diagrams", "1A6B3E")
    doc.add_paragraph().add_run(
        "Activity diagrams use swimlanes to show which actor or system component is responsible "
        "for each action. Decision nodes (diamonds) show guard conditions. Fork/join nodes show "
        "parallel execution. Each diagram covers a complete user journey from start to end node."
    ).font.size = Pt(10)
    doc.add_paragraph()

    diagram_caption("AD-01", "User Registration & Login Activity Flow",
        "Swimlanes: User · Frontend · Backend · Database. Full flow including client-side "
        "validation, Pydantic schema validation, email/username uniqueness checks, bcrypt "
        "hashing, JWT issuance and localStorage persistence.")
    insert_diagram("AD-01_Registration")
    doc.add_page_break()

    diagram_caption("AD-02", "Dashboard Load & Activity Roadmap Render",
        "Swimlanes: User · DashboardPage · Redux Store · Backend · File System. "
        "Parallel fetch of progress and pairs, followed by sequential meta and completions "
        "fetches, roadmap construction, and node state determination (unlocked/locked/completed).")
    insert_diagram("AD-02_Dashboard_Load")
    doc.add_page_break()

    diagram_caption("AD-03", "Activity Execution — General Flow (All Activity Types)",
        "Swimlanes: User · Activity Page · Backend Validate · Groq Service · Scoring Service · "
        "Backend Progress · Database. MCQ vs Groq branching, feedback tier logic, threshold "
        "override, XP delta calculation, and progression unlock mechanism.")
    insert_diagram("AD-03_Activity_Execution")
    doc.add_page_break()

    diagram_caption("AD-04", "STT Recording Flow — Speaking & Pronunciation Activities",
        "Swimlanes: User · AudioRecorder Component · Browser API · Backend Speech Router · "
        "Whisper Service. Full MediaRecorder lifecycle, audio blob handling, MIME/size "
        "validation, ffmpeg transcoding, Whisper inference, and is_mock fallback path.")
    insert_diagram("AD-04_STT_Recording")
    doc.add_page_break()

    diagram_caption("AD-05", "Progress Advancement & XP Unlock Logic",
        "Swimlanes: Progress Router · Database. Detailed internal flow of the "
        "complete_activity endpoint: SCORE_THRESHOLD_OVERRIDE application, month/block "
        "derivation formula, first-vs-retry branching, XP delta calculation, "
        "current_activity_id increment, and commit cycle.")
    insert_diagram("AD-05_Progress_Unlock")
    doc.add_page_break()

    # ── SECTION 5: STATE DIAGRAMS ─────────────────────────────────
    section_banner("Section 4  —  State Diagrams", "7B2D8B")
    doc.add_paragraph().add_run(
        "State diagrams document every stateful entity in the platform. Each machine "
        "specifies all discrete states, entry/exit actions, transition events with guard "
        "conditions and actions, composite (nested) states, and initial/final pseudostates."
    ).font.size = Pt(10)
    doc.add_paragraph()

    diagram_caption("SM-01", "User Account Lifecycle",
        "Entity: User database record. States: UNREGISTERED → REGISTERED_ACTIVE ↔ "
        "LOGGED_IN ↔ LOGGED_OUT ↔ DEACTIVATED. Covers admin activate/deactivate, "
        "JWT-based session management, and ADMIN_ROLE composite sub-state.")
    insert_diagram("SM-01_User_Account")
    doc.add_page_break()

    diagram_caption("SM-02", "JWT Token Lifecycle",
        "Entity: Bearer Token (security.py and src/api/client.js). Complete lifecycle "
        "from DOES_NOT_EXIST through ACTIVE decode states (VALID/INVALID/EXPIRED) to "
        "CLEARED with role-based redirect logic (admin → /admin/login, user → /login).")
    insert_diagram("SM-02_JWT_Token")
    doc.add_page_break()

    diagram_caption("SM-03", "UserLanguageProgress — Curriculum Progression Machine",
        "Entity: UserLanguageProgress database record. Composite states: ACTIVITY_POSITION "
        "(AT_ACTIVITY_N advancing 1→144) and XP_LEVEL (BEGINNER→INTERMEDIATE→ADVANCED). "
        "Month/block derivation formula documented in state notes.")
    insert_diagram("SM-03_Language_Progress")
    doc.add_page_break()

    diagram_caption("SM-04", "ActivityCompletion Record & Activity Page States",
        "Two machines on one diagram: (1) ActivityCompletion DB record "
        "(NEVER_ATTEMPTED → ATTEMPTED → FAILED/PASSED). (2) ActivityPage React component "
        "(LOADING → CONTENT_READY → ANSWERING/RECORDING → SUBMITTING → PASSED/FAILED).")
    insert_diagram("SM-04_Activity_Completion", width_inches=6.8)
    doc.add_page_break()

    diagram_caption("SM-05", "Service Layer State Machines",
        "Three machines: (1) WhisperService Python module (UNINITIALIZED → AVAILABLE/"
        "UNAVAILABLE → TRANSCRIBING). (2) GroqService single API call (IDLE → BUILDING_PROMPT "
        "→ CALLING_GROQ → RESULT/ERROR). (3) Redux authSlice frontend "
        "(UNAUTHENTICATED → LOADING → AUTHENTICATED/ERROR).")
    insert_diagram("SM-05_Services", width_inches=6.8)
    doc.add_page_break()

    # ── FINAL PAGE ────────────────────────────────────────────────
    for _ in range(6):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("End of LearnWise Software Design Document  —  Version 1.0")
    r.bold = True; r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0x1F,0x38,0x64)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("IEEE Std 1016  ·  Stakeholder Presentation  ·  April 2026")
    r.italic = True; r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(0x55,0x55,0x55)

    return doc


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    DOCS_DIR = Path(__file__).parent
    IMG_DIR  = DOCS_DIR / "_diagram_images"
    IMG_DIR.mkdir(exist_ok=True)

    print("═" * 60)
    print("  LearnWise — Design Document Generator")
    print("  Rendering diagrams via PlantUML web service …")
    print("═" * 60)

    diagram_paths = {}
    failed = []

    for name, puml in DIAGRAMS.items():
        out = str(IMG_DIR / f"{name}.png")
        ok  = render_diagram(puml, out)
        if ok:
            diagram_paths[name] = out
        else:
            failed.append(name)

    print()
    print(f"  Rendered: {len(diagram_paths)}/{len(DIAGRAMS)} diagrams")
    if failed:
        print(f"  Failed:   {failed}")

    print()
    print("  Building DESIGN_DOCUMENT.docx …")
    doc = build_document(diagram_paths)

    out_path = str(DOCS_DIR / "DESIGN_DOCUMENT.docx")
    doc.save(out_path)
    print(f"  ✓ Saved → {out_path}")
    print()
    print("═" * 60)
    print("  DONE. Open docs/DESIGN_DOCUMENT.docx to review.")
    print("═" * 60)
