# Piston Code Execution Engine — Setup Guide

> **Piston** is a free, open-source, sandboxed code execution engine. It runs inside Docker and exposes a simple REST API. No API keys or billing required.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Docker Desktop | 4.x+ | Must be running |
| Docker Compose | v2+ | Bundled with Docker Desktop |

---

## Step-by-step Setup

### 1 — Start the Piston container

From your project root (`Programming/`):

```bash
docker compose up -d piston
```

This downloads the image (~250 MB on first run) and starts the container on **port 2000**.

### 2 — Verify it's running

```bash
curl http://localhost:2000/api/v2/runtimes
```

Expected response: `[]` (empty list, no runtimes installed yet — that's fine).

### 3 — Install language runtimes (one time only)

```bash
docker compose run --rm piston-install
```

This helper service installs **Python, JavaScript, C++, C, and Java** into the shared Docker volume. Takes ~2–5 minutes depending on internet speed. Runtimes persist in the `piston_packages` Docker volume across restarts.

### 4 — Verify runtimes are installed

```bash
curl http://localhost:2000/api/v2/runtimes
```

You should now see a JSON array listing the installed languages and their versions.

### 5 — Check the `.env` is configured

Open `backend/.env` and confirm:

```env
PISTON_URL=http://localhost:2000/api/v2/execute
```

---

## Quick Test

Test code execution directly via the API:

```bash
curl.exe -X POST http://localhost:2000/api/v2/execute `
  -H "Content-Type: application/json" `
  -d '{"language":"python","version":"*","files":[{"content":"print(\"Hello from Piston!\")"}],"stdin":""}'
```

Expected response:
```json
{
  "run": { "stdout": "Hello from Piston!\n", "stderr": "", "code": 0, "signal": null, "output": "Hello from Piston!\n" }
}
```

---

## Container Management

| Command | Description |
|---------|-------------|
| `docker compose up -d piston` | Start in background |
| `docker compose stop piston` | Stop the container |
| `docker compose logs piston` | View logs |
| `docker ps` | Verify container is running |

---

## Supported Languages

After running `piston-install`, these languages are available in the editor:

| Language | Identifier |
|----------|-----------|
| Python 3 | `python` |
| JavaScript | `javascript` |
| C++ | `cpp` |
| C | `c` |
| Java | `java` |

To add more languages, check the available packages:

```bash
curl http://localhost:2000/api/v2/packages
```

Then install with:

```bash
curl.exe -X POST http://localhost:2000/api/v2/packages `
  -H "Content-Type: application/json" `
  -d '{"language":"go","version":"1.16.2"}'
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Cannot reach Piston container` banner in app | Run `docker compose up -d piston` |
| Container exits immediately | Ensure Docker Desktop is running with **WSL2 backend** enabled |
| Runtimes not showing after install | Wait 30s and retry the runtimes endpoint |
| `privileged: true` error | Enable WSL2 backend in Docker Desktop settings |

---

## Architecture

```
Browser (Monaco Editor)
    │  POST /api/code/run  { code, language, stdin }
    ▼
Flask Backend (backend/app.py)
    │  execute_code_api()  →  POST http://localhost:2000/api/v2/execute
    ▼
Piston Docker Container (port 2000)
    │  Runs code in sandboxed subprocess
    ▼
Output returned as JSON  →  Backend  →  Frontend Console
```
