
from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Dict, List

import os
import requests


def try_fetch_nse_announcements(run_day: datetime, cfg: Dict) -> List[Dict]:
    """Best-effort query to NSE corporate announcements.

    NOTE:
      - NSE often blocks automated clients (403) without proper session cookies, headers and pacing.
      - This Phase 1 helper returns [] if the call fails; enable gradually.
    """
    from_days = cfg.get("from_days_back", 0)
    to_days = cfg.get("to_days_back", 0)

    start = (run_day - timedelta(days=from_days)).date().isoformat()
    end = (run_day - timedelta(days=to_days)).date().isoformat()

    endpoint = cfg.get("endpoint_template") or (
        "https://www.nseindia.com/api/corporate-announcements?index=equities&from_date={from_date}&to_date={to_date}"
    )
    url = endpoint.format(from_date=start, to_date=end)

    headers = {
        "User-Agent": os.environ.get("HTTP_USER_AGENT", "Mozilla/5.0"),
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        s = requests.Session()
        # Warm-up GET to set cookies
        s.get("https://www.nseindia.com/", headers=headers, timeout=15)
        r = s.get(url, headers=headers, timeout=30)
        if r.status_code != 200:
            return []
        data = r.json()
    except Exception:
        return []

    out: List[Dict] = []
    for item in data if isinstance(data, list) else data.get("data", []):
        out.append(
            {
                "source": "nse_corporate",
                "title": item.get("sm_ann_desc", ""),
                "summary": item.get("subject", ""),
                "url": item.get("pdfUrl") or item.get("attchmntFile") or "",
                "published_at": item.get("ann_date") or item.get("dissemDT") or None,
                "company_symbols": [item.get("symbol")] if item.get("symbol") else [],
                "raw": item,
            }
        )
    return out
