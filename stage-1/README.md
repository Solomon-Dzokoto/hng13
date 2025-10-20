# Stage 1 - String Analyzer Service

Simple FastAPI service that analyzes strings and stores computed properties in an in-memory store.


Run the app (from inside the `stage-1` folder):

Install dependencies into a virtualenv, cd to `stage-1`, then:

python -m uvicorn app:app --reload --port 8000

Run tests:

pytest -q
