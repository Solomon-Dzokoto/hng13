#!/usr/bin/env bash
set -euo pipefail

: "${PORT:=8080}"

echo "Starting app on 0.0.0.0:${PORT}"
exec python -m uvicorn main:app --host 0.0.0.0 --port "${PORT}"
