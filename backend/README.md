# TrojanClaw Backend (FastAPI + Supabase)

This is the Python backend for **TrojanClaw**, built with **FastAPI** and configured to use **Supabase**.

## Project Structure

```/dev/null/tree.txt#L1-9
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── supabase_client.py
├── .env.example
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.10+ (recommended: 3.11)
- A Supabase project (URL + anon/service role key)

## 1) Create and activate a virtual environment

From this directory (`TrojanClaw/backend`):

```/dev/null/setup.sh#L1-2
python3 -m venv .venv
source .venv/bin/activate
```

On Windows (PowerShell):

```/dev/null/setup.ps1#L1-2
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 2) Install dependencies

```/dev/null/install.sh#L1-1
pip install -r requirements.txt
```

## 3) Configure environment variables

Copy `.env.example` to `.env` and fill in your Supabase credentials.

```/dev/null/env-setup.sh#L1-2
cp .env.example .env
# then edit .env
```

Required variables:

- `SUPABASE_URL`
- `SUPABASE_KEY`

Example:

```/dev/null/env.example#L1-2
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-key
```

## 4) Run the API

```/dev/null/run.sh#L1-1
uvicorn app.main:app --reload
```

Server will start at:

- `http://127.0.0.1:8000`

## 5) Verify healthcheck endpoint

Open:

- `http://127.0.0.1:8000/healthcheck`

Expected response:

```/dev/null/health.json#L1-3
{
  "status": "ok"
}
```

## API Docs

FastAPI auto-generates interactive docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Notes on Supabase

- Keep keys in `.env` and never commit secrets to version control.
- Use the **anon key** for client-safe operations; use **service role key** only on trusted backend paths.
- If Supabase client initialization fails, verify `SUPABASE_URL` and `SUPABASE_KEY`.

## Development Tips

- Add formatting/linting as the project grows (e.g., `black`, `ruff`).
- Add tests with `pytest` for endpoint and integration coverage.
- Consider environment-specific `.env` files for local/staging/production.