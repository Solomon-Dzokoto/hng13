(The file `/Users/brasolo/Desktop/hgn13internship/stage-0/README.md` is being created with the following content)
# Stage 0 - Profile API

Simple FastAPI app exposing GET /me which returns profile information and a dynamic cat fact from https://catfact.ninja/fact

Requirements
# hng13 — Internship workspace

This repository contains multiple stage folders for progressive exercises. Below are quick start instructions for Stage 0 and Stage 3 (current work).

## Stage 0 — Profile API

Simple FastAPI app exposing GET `/me` which returns profile information and a dynamic cat fact from https://catfact.ninja/fact.

Requirements
- Python 3.10+

Install

1. Create a virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Run locally

Start the app with uvicorn:

```bash
uvicorn main:app --reload --port 8000
```

Open http://127.0.0.1:8000/me to see the JSON response.

Notes
- The endpoint returns JSON with fields: `status`, `user` (email/name/stack), `timestamp` (UTC ISO 8601), and `fact`.
- If the Cat Facts API is unreachable, the response will return a fallback fact message.

## Stage 3 — Code Review Assistant (Telex.im A2A)

This stage implements a Code Review Assistant agent using FastAPI and Google Gemini (via `google-generativeai`). It exposes an A2A endpoint compatible with Telex.im and includes local tests and a Postman collection.

Key files (stage-3/):
- `main.py` — FastAPI application (endpoints: `/health`, `/info`, `/a2a/agent/codeReviewAssistant`, `/chat`).
- `agent.py` — Agent implementation that talks to Gemini and processes messages.
- `config.py` — Settings and environment-loading (GEMINI_API_KEY, GEMINI_MODEL).
- `test_gemini_setup.py` — Small script to validate Gemini API key and list available models.
- `test_agent.py`, `test_a2a_diagnostic.py` — Local endpoint tests.
- `postman_collection.json` — Importable Postman collection for quick testing.
- `workflow.json` — Telex workflow pointing to your deployed A2A URL.

Environment variables (in `stage-3/.env`):
- `GEMINI_API_KEY` — your Google Gemini API key (from https://aistudio.google.com/app/apikey)
- `GEMINI_MODEL` — model id (e.g. `models/gemini-2.5-flash`)

Quick local test & run (stage-3):

```bash
# from repo root
cd stage-3
source venv/bin/activate   # or create a venv with python -m venv venv
pip install -r requirements.txt



# Start the server
python -m uvicorn main:app --reload --port 8000






If you'd like the top-level README to include additional stage sections or deployment instructions, tell me which stage to add next and I'll update it.
