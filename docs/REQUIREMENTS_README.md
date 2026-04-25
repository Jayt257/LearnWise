# LearnWise — Requirements, Use Cases & User Stories Reference

> **Purpose:** Exhaustive reference for all Functional Requirements (FRs), Non-Functional Requirements (NFRs), User Stories, and Use Cases across the LearnWise platform.  
> **Scope:** Full-stack coverage (FastAPI Backend + React Frontend + Groq AI + Whisper STT + Content System).

---

## TABLE OF CONTENTS

1. [Functional Requirements (FR)](#1-functional-requirements-fr)
    - 1.1 Authentication & User Management
    - 1.2 Curriculum Content & Delivery
    - 1.3 Activity Execution & Evaluation
    - 1.4 Progress Tracking & Gamification
    - 1.5 Social Features & Leaderboard
    - 1.6 Administrator Features
2. [Non-Functional Requirements (NFR)](#2-non-functional-requirements-nfr)
    - 2.1 Security & Compliance
    - 2.2 Performance & Scalability
    - 2.3 Usability & UI/UX
    - 2.4 Reliability & Resilience
3. [User Stories](#3-user-stories)
    - Learner Stories
    - Administrator Stories
4. [Use Case Scenarios](#4-use-case-scenarios)
    - UC-01: User Registration
    - UC-02: Executing a Curriculum Activity
    - UC-03: AI-Graded Open-Ended Evaluation
    - UC-04: Audio Transcription (STT)

---

## 1. FUNCTIONAL REQUIREMENTS (FR)

### 1.1 Authentication & User Management
* **FR-AUTH-01:** The system shall allow users to register with a username (3-50 alphanumeric characters + underscores), a valid email address, and a secure password (min 8 characters).
* **FR-AUTH-02:** The system shall reject duplicate registrations for the same username or email.
* **FR-AUTH-03:** The system shall authenticate users via email and password, issuing a JWT (JSON Web Token) valid for 7 days upon success.
* **FR-AUTH-04:** The system shall provide distinct roles (`user`, `admin`) to enforce access control.
* **FR-AUTH-05:** The system shall allow users to view and update their public profile (display name, chosen native language, avatar URL).
* **FR-AUTH-06:** The system shall support soft deactivation of accounts, where a deactivated user cannot log in but their data remains intact.

### 1.2 Curriculum Content & Delivery
* **FR-CONT-01:** The system shall organize curriculum hierarchically into Language Pairs (e.g., Hindi → Japanese) > Months (1-3) > Blocks (1-6) > Activities (8 distinct types per block).
* **FR-CONT-02:** The system shall assign a globally unique, sequential ID (`activity_seq_id` from 1 to 144) to every activity to govern curriculum progression mathematically.
* **FR-CONT-03:** The frontend shall sequentially read the structured curriculum defined in `meta.json` and render a visual roadmap (Dashboard) consisting of unlockable nodes.
* **FR-CONT-04:** The system shall support 8 specific activity formats: `lesson`, `vocabulary`, `pronunciation`, `reading`, `writing`, `listening`, `speaking`, and `test`.

### 1.3 Activity Execution & Evaluation
* **FR-EVAL-01:** The system shall provide a local, deterministic scoring engine for Multiple Choice Questions (MCQ) used in `test` and `listening` activities based on exact string matching.
* **FR-EVAL-02:** The system shall dynamically route open-ended text inputs (`speaking`, `writing`, `reading` short answers) to the Groq AI service for generative evaluation.
* **FR-EVAL-03:** The AI evaluation engine shall output JSON containing per-question scores, an overall feedback string, and a suggestion for improvement.
* **FR-EVAL-04:** The AI engine shall adjust its evaluation prompt dynamically based on the Activity Type (e.g. allowing paraphrasing for lessons, strict phonetic checking for pronunciation).
* **FR-EVAL-05:** The system shall categorize AI feedback into tiers ("hint", "lesson", "praise") based on the percentage score and the number of prior attempts.
* **FR-EVAL-06 (STT):** The system shall process audio recordings (WAV, WEBM from browsers) using an on-premise Whisper model to transcribe speech-to-text.
* **FR-EVAL-07 (STT Fallback):** If the Whisper model is unavailable or crashing, the system shall return an `is_mock: True` signal, putting the frontend into a graceful "Demo Mode" that blocks submission rather than crashing.

### 1.4 Progress Tracking & Gamification
* **FR-PROG-01:** The system shall track a user's progress per language pair, storing total XP, current month, current block, and the current locked/unlocked `activity_seq_id`.
* **FR-PROG-02:** The system shall unlock the next sequential activity ONLY if the user achieves a passing score (default ≥ 20%) on their currently locked activity.
* **FR-PROG-03:** The system must support a global override (`SCORE_THRESHOLD_OVERRIDE`) to alter the passing threshold without changing business logic code.
* **FR-PROG-04:** The system shall record every completion attempt, tracking the number of attempts and updating the maximum `score_earned`.
* **FR-PROG-05:** The system shall only award Delta XP (the difference between a previous high score and a new higher score). Retrying an activity for a lower score shall not deduct or add XP.

### 1.5 Social Features & Leaderboard
* **FR-SOC-01:** The system shall feature a global leaderboard ranked in descending order by `total_xp` across a specific language pair.
* **FR-SOC-02:** The system shall allow users to search for others by username substring.
* **FR-SOC-03:** The system shall implement a mutual Friend Request system (Pending, Accepted, Declined states).
* **FR-SOC-04:** The system shall enforce constraints preventing self-requests, duplicate pending requests, and duplicate friendships.
* **FR-SOC-05:** The system shall provide a secondary, filtered Leaderboard containing only the user and their accepted friends.

### 1.6 Administrator Features
* **FR-ADM-01:** The system shall provide a secure, Role-Based Access Control (RBAC) portal exclusively for `admin` users.
* **FR-ADM-02:** Administrators shall view aggregate platform metrics, including total users, active pairs, and completion velocity.
* **FR-ADM-03:** Administrators shall be able to activate, deactivate, or elevate users to Admin status (excluding themselves).
* **FR-ADM-04 (Content CRUD):** Administrators shall be able to create new language pairs, which automatically scaffolds physical directories and 144 placeholder JSON activity templates.
* **FR-ADM-05:** Administrators shall be able to dynamically add or delete Curriculum Blocks and Months within an existing pair.
* **FR-ADM-06:** Administrators shall utilize a UI form/JSON editor to physically modify the contents of curriculum files on the backend disk in real-time.

---

## 2. NON-FUNCTIONAL REQUIREMENTS (NFR)

### 2.1 Security & Compliance
* **NFR-SEC-01 (Authentication):** All state-modifying and PII-accessing API endpoints MUST require an HTTP `Bearer` Authorization header with a valid JWT.
* **NFR-SEC-02 (Data Protection):** Passwords must be hashed using `bcrypt` prior to database insertion; raw passwords must never be logged.
* **NFR-SEC-03 (Path Traversal):** File-reading and file-writing content endpoints must strictly validate file paths to prevent traversal (e.g., `../.env`).
* **NFR-SEC-04 (Input Sanitization):** The backend must validate maximum lengths on user inputs (e.g., 2000 characters for answers) to prevent payload bloat.

### 2.2 Performance & Scalability
* **NFR-PERF-01 (Audio Process):** Audio uploads for STT MUST NOT exceed 25MB. Real-time transcription latency should aim for under 3 seconds using `fp16=False` models.
* **NFR-PERF-02 (AI Generation):** Calls to the Groq API (Llama3) must utilize aggressive timeouts and temperature controls (`temp=0.1`) to ensure deterministic boundaries.
* **NFR-PERF-03 (File I/O):** Curriculum data delivery relies heavily on JSON file reads; the file system implementation must handle concurrent read operations without locking.

### 2.3 Usability & UI/UX
* **NFR-UI-01:** The frontend interface MUST employ modern "glassmorphism" aesthetic principles, utilizing layered blur (`backdrop-blur`), translucent cards, and smooth gradient transitions.
* **NFR-UI-02:** The Activity progression map must visually distinguish between Unlocked (clickable, bold color), Locked (greyed out, lock icon), and Completed (green checkmark indicator) node states.
* **NFR-UI-03:** Interactive nodes must feature micro-animations on hover to encourage user engagement.
* **NFR-UI-04 (Responsive):** The dashboard and activity panels must adapt to mobile, tablet, and desktop viewports seamlessly using Tailwind's responsive prefixes.

### 2.4 Reliability & Resilience
* **NFR-REL-01 (AI Fallback):** If the Groq API fails or times out, the validation router MUST catch the exception and return a structured fallback response ("AI unavailable") rather than HTTP 500.
* **NFR-REL-02 (Silent File Cleanup):** When `tempfile` cleanup throws an `OSError` (common in certain environments), the error must be logged and swallowed so it does not interrupt the STT payload delivery.
* **NFR-REL-03 (Database State):** Database operations inside complex router endpoints (like `complete_activity`) must employ transaction blocks (`db.commit()`) logically grouped at the end of the procedure to prevent partial state integrity loss.

---

## 3. USER STORIES

### Learner Stories
1. **AS A LEARNER**, I want to register for a new account with my email, **SO THAT** I can securely save my language learning progress.
2. **AS A LEARNER**, I want to view a visual roadmap of my curriculum (Dashboard), **SO THAT** I know exactly which activities I have finished and what is coming next.
3. **AS A LEARNER**, I want to be forced to complete activities sequentially, **SO THAT** I learn foundational concepts before advancing to harder material.
4. **AS A LEARNER**, I want immediate AI feedback on my written answers, **SO THAT** I understand my grammatical mistakes contextually rather than relying on a strict pass/fail key.
5. **AS A LEARNER**, I want to record my own voice using my browser microphone, **SO THAT** the system can evaluate my pronunciation.
6. **AS A LEARNER**, I want to earn Experience Points (XP) for completing activities, **SO THAT** I feel a sense of progression and reward.
7. **AS A LEARNER**, I want to retry previously completed activities to improve my low scores, **SO THAT** I can earn the remaining XP delta and improve my ranking.
8. **AS A LEARNER**, I want to seamlessly search for, send requests to, and add friends, **SO THAT** I can view a targeted Leaderboard comparing my XP to my friends.
9. **AS A LEARNER**, I want my session to gracefully redirect me to the login page when my token expires, **SO THAT** I am not confused by silent API errors.

### Administrator Stories
1. **AS AN ADMIN**, I want access to a secure, separate dashboard, **SO THAT** I can monitor and manage the platform without impacting frontend consumer workflows.
2. **AS AN ADMIN**, I want to quickly create a scaffolding for a new Language Pair (e.g. Hindi to Korean), **SO THAT** I do not have to manually create 144 JSON files with complex schemas.
3. **AS AN ADMIN**, I want to edit activity JSON content via a UI interface, **SO THAT** I can fix curriculum typos or add new questions in real-time without executing a backend server restart.
4. **AS AN ADMIN**, I want to be able to deactivate toxic or spam users, **SO THAT** they can no longer log in or appear on active leaderboards.
5. **AS AN ADMIN**, I want to view platform-level aggregates (completion velocities, user counts), **SO THAT** I can report KPIs back to the business.

---

## 4. USE CASE SCENARIOS

### UC-01: User Registration
**Primary Actor:** New Learner
**Preconditions:** User does not have an account.
**Main Flow:**
1. Learner navigates to Landing Page and clicks "Sign Up".
2. System presents registration form (username, email, password).
3. Learner submits valid details.
4. Frontend performs client-side validation then dispatches Redux action.
5. Backend validates the schema, checks uniqueness constraints in DB.
6. Backend encrypts password via `bcrypt`.
7. Backend inserts User into the database and generates HS256 JWT.
8. System logs Learner in and redirects them to `/onboarding`.

### UC-02: Executing a Curriculum Activity
**Primary Actor:** Authenticated Learner
**Preconditions:** User is on the Dashboard. Activity ID `4` is unlocked.
**Main Flow:**
1. Learner clicks on the Activity node (e.g., Block 1, Activity 4 - "Writing").
2. Frontend queries Backend for content: `GET /api/content/{pair}/activity?file={path}`.
3. System parses JSON content and renders the ActivityPage component.
4. Learner views the lesson material and inputs their text answers into textareas.
5. Learner clicks "Submit".
6. Frontend ensures no fields are empty before compiling the submission array.
7. System transitions to Evaluation Use Case (UC-03).
8. System renders a glassmorphic `ScoreModal` detailing score percentage, XP earned, and exact feedback.

### UC-03: AI-Graded Open-Ended Evaluation
**Primary Actor:** System (Backend Router)
**Preconditions:** Validate Endpoint (`POST /api/validate`) receives non-MCQ payload.
**Main Flow:**
1. System receives `ValidateRequest` containing Learner's raw text inputs.
2. System identifies the activity type triggers the `GroqService`.
3. System dynamically builds an LLM prompt incorporating the specific rubric (e.g., "accept romanization", "be lenient").
4. System executes HTTP call to Groq infrastructure requesting deterministic JSON format.
5. Content is received, parsed, and scores are clamped between bounds.
6. System evaluates aggregate percentage against the `PASS_THRESHOLD` (normally 20%).
7. System queries a secondary prompt to determine the feedback "tier" (Praise vs Lesson vs Hint).
8. Validation payload is marshaled and returned to frontend.
**Exception Flow:** Groq API timeouts. System catches exception and returns `{ passed: False, min_score, overall_feedback: "AI unavailable, try again." }`. 

### UC-04: Audio Transcription (STT)
**Primary Actor:** Learner
**Preconditions:** User is on an activity requiring Voice Input. System microphone permission granted.
**Main Flow:**
1. Learner clicks "Record", speaks phrase into microphone.
2. Learner clicks "Stop".
3. Browser generates a Blob (`audio/webm`) containing Opus chunks.
4. Frontend POSTs multipart data to `/api/speech/transcribe`.
5. Backend loads on-premise Whisper model.
6. System uses `ffmpeg` subsystem to transcode `webm` to `16kHz WAV` in a temporary directory.
7. Whisper evaluates tensor data and returns detected `text`, `language`, and `confidence`.
8. System deletes temporary files safely.
9. Transcript is propagated into frontend textarea, ready for Step 5 of UC-02.
