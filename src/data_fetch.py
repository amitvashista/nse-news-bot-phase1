
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import List, Dict

import yaml

from src.utils.logger import get_logger
from src.sources.rss_feeds import fetch_from_all_feeds
from src.sources.nse_announcements import try_fetch_nse_announcements
from src.storage.db import NewsDB


def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dirs(paths: List[str]) -> None:
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def to_ist_midnight(date_str: str | None, tz_name: str) -> datetime:
    tz = ZoneInfo(tz_name)
    if date_str in (None, "today"):
        dt = datetime.now(tz)
    else:
        dt = datetime.fromisoformat(date_str).replace(tzinfo=tz)
    # normalize to local day window
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def dedupe(items: List[Dict]) -> List[Dict]:
    seen = set()
    unique = []
    for it in items:
        key = (it.get("url") or "").strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(it)
    return unique


def main():
    parser = argparse.ArgumentParser(description="Phase 1: fetch daily NSE news")
    parser.add_argument("--date", type=str, default="today", help="YYYY-MM-DD (IST) or 'today'")
    args = parser.parse_args()

    cfg = load_config()
    tz_name = cfg.get("timezone", "Asia/Kolkata")
    run_day = to_ist_midnight(args.date, tz_name)
    iso_day = run_day.date().isoformat()

    logger = get_logger(__name__)
    logger.info(f"Starting Phase 1 fetch for {iso_day} ({tz_name})")

    # Prepare storage
    out_dir = Path(cfg["storage"]["json_out_dir"])
    db_path = cfg["storage"]["sqlite_path"]
    ensure_dirs([str(out_dir), "db"])
    db = NewsDB(db_path)
    db.create_tables()

    # Collect from RSS feeds
    feeds = cfg.get("feeds", [])
    rss_items = fetch_from_all_feeds(feeds, tz_name=tz_name)
    logger.info(f"RSS items collected: {len(rss_items)}")

    # Optionally collect NSE corporate announcements (disabled by default)
    ann_cfg = cfg.get("nse_corporate_announcements", {})
    ann_items = []
    if ann_cfg.get("enabled"):
        ann_items = try_fetch_nse_announcements(run_day, ann_cfg)
        logger.info(f"NSE announcements collected: {len(ann_items)}")

    all_items = dedupe(rss_items + ann_items)
    logger.info(f"Total unique items: {len(all_items)}")

    # Persist to JSON (daily file)
    out_file = out_dir / f"{iso_day}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    # Persist to SQLite
    inserted = db.insert_many(all_items)
    logger.info(f"Inserted into DB: {inserted} rows")

    logger.info(f"Done. JSON: {out_file} | DB: {db_path}")


if __name__ == "__main__":
    main()
