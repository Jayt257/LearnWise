# LearnWise — Windows Quick Start Guide

## What your friend needs to do (5 steps)

---

### Step 1 — Install Docker Desktop

1. Download from: **https://www.docker.com/products/docker-desktop/**
2. Install it (next → next → finish)
3. Open Docker Desktop and wait for it to say **"Engine running"** (green icon in taskbar)

---

### Step 2 — Clone the project

Open **PowerShell** or **Command Prompt** and run:

```powershell
git clone https://github.com/jeel00dev/application.git learnwise
cd learnwise
```

If git is not installed: https://git-scm.com/download/win

---

### Step 3 — Get the secrets file

You will receive a file called **`test.env`** from your friend (via WhatsApp / email / USB).

Place it in the project root folder:
```
learnwise\
    test.env        ← put it here
    docker-compose.yml
    Dockerfile.frontend
    ...
```

---

### Step 4 — Run it

Double-click **`start_windows.bat`** in the project folder.

OR run in PowerShell:
```powershell
docker compose --env-file test.env up --build
```

Wait 2–5 minutes for the first build (downloads Python, Node, installs dependencies).

---

### Step 5 — Open the app

Once you see:
```
frontend_1  | nginx: [notice] start worker processes
backend_1   | INFO: Application startup complete.
```

Open your browser and go to:

| Page | URL |
|---|---|
| **App (Frontend)** | http://localhost:3000 |
| **API Health Check** | http://localhost:8000/api/health |
| **API Docs** | http://localhost:8000/docs |

---

## Stopping the app

In PowerShell:
```powershell
docker compose down
```

Or press `Ctrl+C` in the terminal where it's running.

## Restarting (no rebuild needed)

```powershell
docker compose --env-file test.env up
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `docker: command not found` | Docker Desktop is not running — open it from Start menu |
| Port 3000 already in use | Close whatever is using port 3000 and retry |
| Port 8000 already in use | Close whatever is using port 8000 and retry |
| Build fails with "no space left" | Open Docker Desktop → Settings → Clean / Purge data |
| Blank white page in browser | Wait 30 more seconds, then refresh |
| Backend keeps restarting | Check that `test.env` has GROQ_API_KEY filled in |
