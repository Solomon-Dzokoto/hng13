(The file `/Users/brasolo/Desktop/hgn13internship/stage-0/README.md` is being created with the following content)
# Stage 0 - Profile API

Simple FastAPI app exposing GET /me which returns profile information and a dynamic cat fact from https://catfact.ninja/fact

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

Or use `pip install .` if you prefer installing via the project package metadata.

Run locally

Start the app with uvicorn:

```bash
uvicorn main:app --reload --port 8000
```

Open http://127.0.0.1:8000/me to see the JSON response.



Notes
- The endpoint returns JSON with Content-Type application/json and the following fields: status, user (email/name/stack), timestamp (UTC ISO 8601), and fact.
- If the Cat Facts API is unreachable, the response will still return status success but with a fallback fact message.
