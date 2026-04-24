# 🚀 LearnWise — Hostinger KVM2 VPS Deployment Guide

Complete guide to deploy LearnWise on a production VPS so anyone in the world can access it via a real domain name.

---

## 📋 About the Domain Question

> **Do you get a `.cloud` domain for free?**
>
> **No.** Hostinger does NOT give a free `.cloud` domain, but **they DO give a free domain for 1 year** if you pick a **12-month or 24-month VPS plan** (NOT the 1-month plan). The free domains are usually `.com`, `.net`, or `.xyz`. You would name yours `learnwise.xyz` or `getlearnwise.com` — not `.cloud`.
>
> `.cloud` domains cost about ₹300–₹500/year extra and must be purchased separately.

---

## 🛒 Step 1: Purchase & Setup on Hostinger

### 1.1 Choose the Right Plan
1. Go to `hostinger.com/in/vps-hosting`
2. Select **KVM 2 plan** (₹799/mo)
3. Choose **12 or 24 months** billing (you get a free domain!)
4. Skip the Daily Auto-Backup (code is safe on GitHub)
5. Server Location: **India - Mumbai 2** (32ms latency - already selected)
6. Operating System: Click "Select operating system" → pick **Ubuntu 24.04 LTS**
7. Click **Continue** and complete payment.

### 1.2 Get Your Free Domain (if on 12+ month plan)
1. In the Hostinger dashboard → **Domains** → **Claim Free Domain**
2. Search for `learnwise` — pick a free option like:
   - `learnwise.xyz` (usually free for 1 year)
   - `getlearnwise.com` (check availability)
3. Claim it. We'll point it to your server in Step 3.

---

## 🔑 Step 2: Connect to Your VPS (SSH)

Once Hostinger sends you the VPS details email (usually 5–10 minutes):

### On Windows:
Use Windows Terminal or download [PuTTY](https://putty.org):
```
ssh root@YOUR_VPS_IP_ADDRESS
```
*(Replace `YOUR_VPS_IP_ADDRESS` with the IP Hostinger gives you e.g. `194.23.45.67`)*

Enter the root password Hostinger emailed you.

---

## 🌐 Step 3: Point Your Domain to the VPS

1. In Hostinger dashboard → **Domains** → click your domain → **DNS / Nameservers**
2. Find the `A` record. **Edit it** to your VPS IP:
   - **Type:** `A` | **Name:** `@` | **Points to:** `YOUR_VPS_IP_ADDRESS` | **TTL:** 300
3. Add another record for `www`:
   - **Type:** `A` | **Name:** `www` | **Points to:** `YOUR_VPS_IP_ADDRESS` | **TTL:** 300
4. Save. DNS takes **5–15 minutes** to propagate.

---

## ⚙️ Step 4: Prepare the VPS Server

Run these commands in your SSH terminal:

### 4.1 Update the server
```bash
apt update && apt upgrade -y
```

### 4.2 Install Docker & Docker Compose
```bash
curl -fsSL https://get.docker.com | sh
usermod -aG docker $USER
docker --version && docker compose version
```

### 4.3 Install Git & Certbot (for free SSL)
```bash
apt install -y git certbot
```

### 4.4 Create a deploy user (security best practice)
```bash
adduser learnwise
usermod -aG sudo learnwise
usermod -aG docker learnwise
su - learnwise
```

---

## 📥 Step 5: Clone Your Code

```bash
git clone https://github.com/jeel00dev/application.git /home/learnwise/app
cd /home/learnwise/app
```

---

## 🔐 Step 6: Create Your Production .env File

```bash
cp backend/.env.production.example backend/.env
nano backend/.env
```

**Fill in EVERY value. Critical ones:**

```env
POSTGRES_PASSWORD=SomeVeryStrongPassword123!

# Run this in your terminal to generate: openssl rand -hex 32
SECRET_KEY=paste_the_64_char_output_here

GROQ_API_KEY=gsk_your_real_groq_key_from_console.groq.com

# REPLACE with your actual domain
ALLOWED_ORIGINS=https://learnwise.xyz,https://www.learnwise.xyz
VITE_API_BASE_URL=https://learnwise.xyz

ADMIN_EMAIL=admin@learnwise.xyz
ADMIN_PASSWORD=YourStrongAdminPassword!
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

## 🔧 Step 7: Configure Nginx with Your Domain

```bash
nano nginx.prod.conf
```

**Find and replace ALL 4 occurrences of `YOUR_DOMAIN.com`** with your actual domain (e.g., `learnwise.xyz`). Save and exit.

---

## 🔒 Step 8: Get a Free SSL Certificate (HTTPS)

Run this **BEFORE** starting Docker (Certbot needs port 80 free):

```bash
certbot certonly --standalone \
  -d learnwise.xyz \
  -d www.learnwise.xyz \
  --email admin@learnwise.xyz \
  --agree-tos \
  --non-interactive
```

Success message: `Certificate is saved at: /etc/letsencrypt/live/learnwise.xyz/fullchain.pem`

**Set up auto-renewal so HTTPS never expires:**
```bash
echo "0 12 * * * /usr/bin/certbot renew --quiet && docker compose -f /home/learnwise/app/docker-compose.prod.yml restart frontend" | crontab -
```

---

## 🐳 Step 9: Start Your Application

```bash
cd /home/learnwise/app
docker compose -f docker-compose.prod.yml up -d --build
```

Wait 3–5 minutes for the first build (compiling React + downloading Whisper model).

**Verify all 3 containers are running:**
```bash
docker compose -f docker-compose.prod.yml ps
```

Expected output — all three should be `Up`:
```
NAME                    STATUS
learnwise-db-1          Up (healthy)
learnwise-backend-1     Up
learnwise-frontend-1    Up
```

---

## ✅ Step 10: Verify Your Live Site

Open your browser:
- `https://learnwise.xyz` → Your app loads ✅
- `https://learnwise.xyz/api/health` → `{"status": "ok"}` ✅
- `https://learnwise.xyz/api/docs` → API docs ✅

**Anyone in the world can now access your site!** 🌍

---

## 📊 Daily Management Commands

```bash
# View live logs (Ctrl+C to exit)
docker compose -f docker-compose.prod.yml logs -f

# Restart after config change
docker compose -f docker-compose.prod.yml restart

# Pull latest code from GitHub and redeploy
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build

# Stop everything
docker compose -f docker-compose.prod.yml down
```

---

## 🔥 Firewall (Security)

```bash
ufw allow ssh
ufw allow 80
ufw allow 443
ufw enable
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---|---|
| Website doesn't load | Check DNS: `nslookup learnwise.xyz` — should show your VPS IP |
| SSL error in browser | Run `certbot renew --force-renewal` then restart frontend |
| 502 Bad Gateway | Backend crashed: `docker compose -f docker-compose.prod.yml logs backend` |
| Database error | Check: `docker compose -f docker-compose.prod.yml logs db` |
| Out of memory / slow AI | Whisper is loading — wait 2 min. Consider KVM 4 if persistent |

---

## 💡 Cost Summary

| Item | Cost |
|---|---|
| Hostinger KVM 2 (12 months) | ₹799/mo |
| Free domain (12+ month plan) | ₹0 for 1 year |
| SSL Certificate (Let's Encrypt) | ₹0 (free forever) |
| Groq AI API | ₹0 (free tier) |
| **Total** | **₹799/mo** |

---

## 📁 New Files Added for This Deployment

| File | Purpose |
|---|---|
| `docker-compose.prod.yml` | Production Docker config (locked down DB, uses domain URLs) |
| `nginx.prod.conf` | Production Nginx with SSL, HTTPS redirect, API reverse proxy |
| `backend/.env.production.example` | Template for your production secrets |
| `VPS_DEPLOYMENT.md` | This guide |
