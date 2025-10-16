from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from datetime import datetime, timezone
import logging

app = FastAPI(title="Stage 0 - Profile API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stage0")

# Configuration via environment variables with sensible defaults.
EMAIL = os.getenv("PROFILE_EMAIL", "dzokotosolomon85@gmail.com")
NAME = os.getenv("PROFILE_NAME", "Solomon Dzokoto")
STACK = os.getenv("PROFILE_STACK", "Python/FastAPI")
CATFACT_URL = os.getenv("CATFACT_URL", "https://catfact.ninja/fact")
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "5.0"))


def utc_iso_now():
    """Return the current UTC time in ISO 8601 format with milliseconds and 'Z' suffix."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


@app.get("/me")
async def me():
    """Return profile information plus a dynamic cat fact fetched from an external API."""
    fact = "Cat fact could not be retrieved at this time."
    try:
        timeout = httpx.Timeout(HTTP_TIMEOUT)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(CATFACT_URL)
            if resp.status_code == 200:
                data = resp.json()
                logger.info("Cat Facts API response: %s", data)
                fact = data.get("fact", fact)
            else:
                logger.warning("Cat Facts API returned status %s", resp.status_code)
    except Exception as exc:
        logger.exception("Failed to fetch cat fact: %s", exc)

    payload = {
        "status": "success",
        "user": {
            "email": EMAIL,
            "name": NAME,
            "stack": STACK,
        },
        "timestamp": utc_iso_now(),
        "fact": fact,
    }

    return JSONResponse(content=payload, status_code=200, media_type="application/json")


if __name__ == "__main__":

    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
