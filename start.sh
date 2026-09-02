#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  echo "Missing .env. Run ./setup.sh first, then add GROQ_API_KEY."
  exit 1
fi

set -a
source .env
set +a

python -m uvicorn app:app --host 0.0.0.0 --port 8000
