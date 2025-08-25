
from __future__ import annotations

from datetime import datetime
from typing import Dict, List
from zoneinfo import ZoneInfo

import feedparser


def parse_entry(entry, tz) -> Dict:
    # Robust extraction with fallbacks
    title = getattr(entry, "title", "") or ""
    summary = getattr(entry, "summary", "") or ""
    link = getattr(entry, "link", "") or ""

    # published parsing
    published = None
    if getattr(entry, "published_parsed", None):
        published = datetime(*entry.published_parsed[:6], tzinfo=tz).isoformat()
    elif getattr(entry, "updated_parsed", None):
        published = datetime(*entry.updated_parsed[:6], tzinfo=tz).isoformat()

    return {
        "source": "rss",
        "title": title,
        "summary": summary,
        "url": link,
        "published_at": published,
        "company_symbols": [],  # Phase 2 will populate
        "raw": {
            "id": getattr(entry, "id", None),
        },
    }


def fetch_from_feed(url: str, tz_name: str = "Asia/Kolkata") -> List[Dict]:
    tz = ZoneInfo(tz_name)
    parsed = feedparser.parse(url)
    items = []
    for entry in parsed.entries:
        try:
            items.append(parse_entry(entry, tz))
        except Exception as e:
            # Skip malformed entries; logging handled by caller if desired
            continue
    return items


def fetch_from_all_feeds(urls: List[str], tz_name: str = "Asia/Kolkata") -> List[Dict]:
    all_items: List[Dict] = []
    for u in urls:
        try:
            all_items.extend(fetch_from_feed(u, tz_name))
        except Exception:
            # Ignore feed errors for robustness in Phase 1
            pass
    return all_items
