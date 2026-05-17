---
name: testing-content-generator
description: Test the AI Social Content Generator end-to-end. Use when verifying dashboard UI, API, or content generation changes.
---

# Testing AI Social Content Generator

## Prerequisites

- Python 3.11+ with virtualenv at `backend/.venv/`
- Node.js 18+ with npm (frontend uses Vite + React)
- No OpenAI API key required (app falls back to template-based generation)

## Devin Secrets Needed

- `GITHUB_PAT_PORTFOLIO` — GitHub token for adrianherediaportfolio (for PR operations)
- No other secrets required for local testing

## Starting the Servers

### Backend (FastAPI)
```bash
cd /home/ubuntu/ai-social-content-generator/backend
source .venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Verify: `curl -s http://localhost:8000/health`
Expected: `{"status":"healthy","service":"ai-social-content-generator","version":"X.Y.Z"}`

### Frontend (React/Vite)
```bash
cd /home/ubuntu/ai-social-content-generator/frontend
npm run dev -- --port 3000 --host 0.0.0.0
```

Verify: `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/`
Expected: `200`

**Important**: Backend MUST run on port 8000 — the Vite proxy in `vite.config.js` forwards `/api/v1/` requests to `http://localhost:8000`. If backend is on a different port, the frontend won't be able to fetch data.

## Key Test Flows

### 1. Dashboard Load Test
- Navigate to `http://localhost:3000`
- Verify: heading "AI Social Content Generator", stats bar (Total/Drafts/Scheduled/Published), Generate Content form, Posts section
- Stats bar should reflect existing data in SQLite DB

### 2. Content Generation
- Enter a topic (e.g., "Cloud computing trends") in the Topic field
- All 3 platform buttons (Twitter, Linkedin, Instagram) are selected by default
- Click "Generate Content"
- Verify: "Generated 3 posts!" message appears, stats Total/Drafts increase by 3
- New posts appear in the Posts list with platform badges, hashtags, and timestamps

### 3. Post Filtering
- Use the "All platforms" dropdown to filter by Twitter/LinkedIn/Instagram
- Use the "All status" dropdown to filter by Draft/Scheduled/Published
- Verify filtered results match selection

### 4. Post Deletion
- Click "Delete" on any post card
- Verify: post disappears, stats update accordingly

### 5. Backend Swagger Docs
- Navigate to `http://localhost:8000/docs`
- Verify: Swagger UI loads with endpoints for generate, posts CRUD, health

### 6. Version Verification
- Check `/health` endpoint for correct version string
- Check `frontend/package.json` version field matches backend

## Known Issues

- Without OpenAI API key, generated content uses templates (generic but functional)
- SQLite database persists between restarts at `backend/data/app.db`
- Port conflicts: use `fuser -k 8000/tcp` and `fuser -k 3000/tcp` to free ports
- Frontend dev server may die if the shell session is interrupted; restart with `npm run dev`

## CI

GitHub Actions runs `backend-test` and `frontend-build` jobs on push/PR. Both must pass before merging.
