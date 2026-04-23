# 🎓 LearnWise — AI-Powered Language Learning Platform

LearnWise is a full-stack language learning platform with AI-powered evaluation, interactive roadmaps, leaderboards, and speech recognition.

---

## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Local Development (without Docker)](#-local-development-without-docker)
- [Local Testing with Docker](#-local-testing-with-docker)
- [Deploy to Render (Production)](#-deploy-to-render-production)
- [Environment Variables Reference](#-environment-variables-reference)
- [Admin Portal](#-admin-portal)
- [Updating the App](#-updating-the-app)
- [Troubleshooting](#-troubleshooting)

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + Nginx |
| Backend | FastAPI + Uvicorn (Python 3.10) |
| Database | PostgreSQL |
| AI Evaluation | Groq API (llama-3.1-8b-instant) |
| Speech Recognition | OpenAI Whisper |
| Containerization | Docker + Docker Compose |

---

## 📁 Project Structure

```
learnwise-react/
├── src/                        # React frontend source
├── backend/
│   ├── app/                    # FastAPI application
│   │   ├── routers/            # API endpoints
│   │   ├── models/             # SQLAlchemy models
│   │   ├── services/           # AI / Groq / Whisper services
│   │   └── core/               # Config, DB, Auth
│   ├── data/                   # Curriculum JSON files (single source of truth)
│   │   ├── language_pairs.json
│   │   └── languages/
│   ├── Dockerfile              # Backend Docker image
│   ├── .env.example            # Env vars template
│   └── requirements.txt
├── Dockerfile.frontend          # Frontend Docker image (multi-stage)
├── docker-compose.yml           # Local full-stack testing
├── nginx.conf                   # Nginx SPA routing config
├── start_windows.bat            # One-click start for Windows testers
└── QUICKSTART_WINDOWS.md        # Windows setup guide
```

---

## 💻 Local Development (without Docker)

### Prerequisites
- Python 3.10
- Node.js 18+
- PostgreSQL running locally

### 1. Backend

```bash
cd backend
python3.10 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit .env with your values
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
# From project root
npm install
npm run dev
```

Open **http://localhost:5173**

---

## 🐳 Local Testing with Docker

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Sign in to Docker Hub inside Docker Desktop

### Steps

**1. Clone the repo**
```bash
git clone https://github.com/jeel00dev/application.git learnwise
cd learnwise
```

**2. Create `test.env`** in the project root (get this file from the project owner):
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
WHISPER_MODEL=small
ADMIN_EMAIL=admin@learnwise.app
ADMIN_PASSWORD=Admin@Test2026
ADMIN_USERNAME=admin
SCORE_THRESHOLD_OVERRIDE=-1
```

**3. Start everything**

- **Windows:** Double-click **`start_windows.bat`**
- **Linux / Mac:**
  ```bash
  docker compose --env-file test.env up --build
  ```

First build takes 3–5 minutes (downloads Python, Node, installs deps).

**4. Open the app**

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/health |
| API Docs (Swagger) | http://localhost:8000/docs |

**5. Stop**
```bash
docker compose down
```

> ⚠️ **Windows Docker issue — `no such host` error?**
> Open Docker Desktop → sign in to Docker Hub → retry.
> Or: Settings → Docker Engine → add `"dns": ["8.8.8.8", "8.8.4.4"]` → Apply & Restart.

---

## 🚀 Deploy to Render (Production)

**Estimated cost: ~$25/month**
- Backend: Render Standard ($25/mo) — needed for Whisper RAM
- Frontend: Render Free ($0)
- PostgreSQL: Render Free ($0)

### Step 1 — Push code to GitHub

```bash
git push origin main
```

### Step 2 — Create PostgreSQL Database

1. [dashboard.render.com](https://dashboard.render.com) → **New → PostgreSQL**
2. Name: `learnwise-db` | Plan: **Free**
3. After creation, copy the **Internal Database URL** (starts with `postgresql://`)

### Step 3 — Deploy Backend

1. **New → Web Service**
2. Connect GitHub repo → select `jeel00dev/application`
3. Settings:

| Field | Value |
|---|---|
| Name | `learnwise-backend` |
| Root Directory | `backend` |
| Environment | `Docker` |
| Dockerfile Path | `./Dockerfile` |
| Plan | **Standard** ($25/mo) |

4. Add **Environment Variables:**

| Variable | Value |
|---|---|
| `DATABASE_URL` | Internal Database URL from Step 2 |
| `SECRET_KEY` | Output of `openssl rand -hex 32` |
| `GROQ_API_KEY` | From [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | `llama-3.1-8b-instant` |
| `WHISPER_MODEL` | `small` |
| `ALLOWED_ORIGINS` | `https://learnwise-frontend.onrender.com` |
| `ADMIN_EMAIL` | `admin@learnwise.app` |
| `ADMIN_PASSWORD` | A strong password of your choice |
| `ADMIN_USERNAME` | `admin` |
| `SCORE_THRESHOLD_OVERRIDE` | `-1` |
| `DATA_DIR` | `data` |

5. Add **Persistent Disk** (for admin curriculum changes to survive restarts):
   - Scroll to **Disks** → **Add Disk**
   - Name: `learnwise-data` | Mount Path: `/app/data` | Size: `1 GB`

6. Click **Create Web Service** — wait ~5 min for first deploy

7. ✅ Test: `https://learnwise-backend.onrender.com/api/health` → `{"status":"ok"}`

### Step 4 — Deploy Frontend

1. **New → Web Service**
2. Same GitHub repo
3. Settings:

| Field | Value |
|---|---|
| Name | `learnwise-frontend` |
| Root Directory | *(leave blank / `.`)* |
| Environment | `Docker` |
| Dockerfile Path | `./Dockerfile.frontend` |
| Plan | **Free** |

4. Add **Environment Variables:**

| Variable | Value |
|---|---|
| `VITE_API_BASE_URL` | `https://learnwise-backend.onrender.com` |

5. Click **Create Web Service**

6. ✅ Open: `https://learnwise-frontend.onrender.com`

### Step 5 — Update Backend CORS

1. Go to backend service → **Environment**
2. Update `ALLOWED_ORIGINS` to your real frontend URL:
   ```
   https://learnwise-frontend.onrender.com
   ```
3. **Save Changes** → Render auto-redeploys

### Final Checks

| What to verify | Where |
|---|---|
| Frontend loads | `https://learnwise-frontend.onrender.com` |
| API is healthy | `https://learnwise-backend.onrender.com/api/health` |
| API docs accessible | `https://learnwise-backend.onrender.com/docs` |
| Admin login works | `https://learnwise-frontend.onrender.com/admin/login` |

---

## 🔑 Environment Variables Reference

### Backend

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | JWT signing secret (64 chars) — `openssl rand -hex 32` |
| `GROQ_API_KEY` | ✅ | From [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | ✅ | `llama-3.1-8b-instant` (recommended) |
| `WHISPER_MODEL` | ✅ | `small` on Standard, `tiny` on Starter |
| `ALLOWED_ORIGINS` | ✅ | Comma-separated frontend URLs |
| `ADMIN_EMAIL` | ✅ | Admin account email |
| `ADMIN_PASSWORD` | ✅ | Admin account password |
| `ADMIN_USERNAME` | ✅ | Admin username |
| `SCORE_THRESHOLD_OVERRIDE` | ✅ | Always set to `-1` in production |
| `DATA_DIR` | ✅ | Always `data` |

### Frontend (build-time)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_BASE_URL` | ✅ | Full URL of your backend service |

---

## 🔧 Admin Portal

Access at `/admin/login` using `ADMIN_EMAIL` + `ADMIN_PASSWORD`.

**Capabilities:**
- Create / edit language pairs
- Add months and blocks to curriculum
- Upload activity content (lesson, vocab, reading, writing, listening, speaking, test)
- View registered users

> **Important:** On Render, the **Persistent Disk** mounted at `/app/data` is required for admin changes to survive container restarts. Without it, curriculum edits are lost on every deploy.

---

## 🔄 Updating the App

Push to GitHub — Render auto-redeploys both services:

```bash
git add .
git commit -m "your changes"
git push origin main
```

No manual steps needed on Render.

---

## 🐛 Troubleshooting

| Symptom | Fix |
|---|---|
| Frontend shows blank white page | Check `VITE_API_BASE_URL` is set and correct |
| Backend returns 500 on startup | Check `DATABASE_URL` uses the **Internal** URL, not External |
| Login always fails | Check `SECRET_KEY` is set and not empty |
| AI evaluation errors | Check `GROQ_API_KEY` is valid and has quota |
| Admin curriculum changes disappear | Add Persistent Disk at `/app/data` on backend service |
| Docker build fails (`no such host`) | Sign in to Docker Hub in Docker Desktop |
| Port already in use locally | Change ports in `docker-compose.yml` or stop conflicting app |
