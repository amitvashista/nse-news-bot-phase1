
# NSE News Bot – Phase 1 (Project Setup & Data Pipeline)

This repo is the **Phase 1** scaffold for your AI agent that ingests daily market news for NSE-listed companies.

## What’s inside
- RSS + NSE corporate announcements collectors
- SQLite storage
- Config-driven feeds
- GitHub Actions workflow (09:07 IST on weekdays)
- Basic logging & smoke tests

## Quickstart (local)
```bash
python -V  # ensure Python 3.10+
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # optional keys, headers
python src/data_fetch.py --date today  # or YYYY-MM-DD
```

Outputs land in `data/raw/<YYYY-MM-DD>.json` and `db/news.db`.

## GitHub Actions
The workflow runs at **09:07 IST** (03:37 UTC) on weekdays and also supports **manual runs**.
Edit `.github/workflows/daily.yml` to change schedule.

## Next
- Phase 2 will add NLP cleaning, sentiment & event tags.
