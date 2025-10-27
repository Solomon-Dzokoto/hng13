# Country Currency & Exchange API (FastAPI)

REST API that fetches countries from RestCountries, matches currency exchange rates from Open ER-API (base USD), computes an estimated GDP, caches everything in a database, and serves endpoints.

## Features

- POST `/countries/refresh`: Fetch countries + rates, transactional cache update, generate summary image
- GET `/countries`: List with filters `?region=`, `?currency=` and sorting `?sort=gdp_desc`
- GET `/countries/{name}`: Get one (case-insensitive)
- DELETE `/countries/{name}`: Delete one
- GET `/status`: Total countries and last refresh timestamp
- GET `/countries/image`: Serve generated summary image (`cache/summary.png`)

## Tech

- Python FastAPI, SQLAlchemy 2
- HTTPX for async HTTP
- Pillow for image generation
- MySQL (Railway) or SQLite (local default)

## Setup (Local)

1. Python 3.10+

```bash
cd /Users/brasolo/Desktop/hgn13internship/stage-2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

1. Copy and edit env vars. By default it uses SQLite at `stage-2/app.db` if no MySQL vars are provided.
To use MySQL locally or on Railway, you can either:

- Set a full URL:
 
```env
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:PORT/DATABASE
```
 
- Or set individual variables (URL takes precedence if both are provided):
 
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=changeme
MYSQL_DB=hng13
```

1. Run API
 
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

Open <http://localhost:8080/docs>

## Refresh and Test with curl

- Refresh (fetch external APIs, cache to DB, build image)
 
```bash
curl -X POST http://localhost:8080/countries/refresh
```

- List countries (optionally filter/sort)
 
```bash
curl "http://localhost:8080/countries?region=Africa"
curl "http://localhost:8080/countries?currency=NGN"
curl "http://localhost:8080/countries?sort=gdp_desc"
```

- Get one country (case-insensitive on name)
 
```bash
curl http://localhost:8080/countries/Nigeria
```

- Delete a country
 
```bash
curl -X DELETE http://localhost:8080/countries/Ghana
```

- Status
 
```bash
curl http://localhost:8080/status
```

- Download summary image
 
```bash
curl -o summary.png http://localhost:8080/countries/image
```

## Error Responses

- 404 → `{ "error": "Country not found" }`
- 400 → `{ "error": "Validation failed" }`
- 503 → `{ "error": "External data source unavailable", "details": "Could not fetch data from <API>" }`
- 500 → `{ "error": "Internal server error" }`

## Deployment (Railway)

1. Create a new Railway project, add a MySQL service.
1. Add a service from Git repo or upload the `stage-2` directory.
1. Set env var `DATABASE_URL` in Railway to the MySQL URL, or provide the `MYSQL_*` variables shown above.
1. `Procfile` is included:

```bash
web: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
```

1. Deploy; Railway injects `PORT`.

## Notes

- Cache updates only on `/countries/refresh`.
- If a country has no currencies, we store it with `currency_code=null`, `exchange_rate=null`, `estimated_gdp=0`.
- If `currency_code` not present in rates, `exchange_rate=null`, `estimated_gdp=null` and the record is still stored.

