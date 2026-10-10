"""Research input: recent questions / stories about Zoho from the RSS feeds listed in channel.yaml."""
import calendar
import re
import time
from html import unescape

import feedparser

from .config import FEEDS, KEYWORDS, LOOKBACK_DAYS

_KW = [k.strip() for k in KEYWORDS if k.strip()]
MATCH = re.compile(r"\b(" + "|".join(re.escape(k) for k in _KW) + r")\b", re.I) if _KW else None


def _clean(html):
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _norm_title(t):
    return re.sub(r"[^a-z0-9 ]", "", t.lower())[:80]


def fetch(already_covered, lookback_days=LOOKBACK_DAYS):
    cutoff = time.time() - lookback_days * 86400
    covered = set(already_covered)
    items, seen_titles = [], set()
    for url in FEEDS:
        try:
            feed = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0 (shorts-research-bot)"})
        except Exception as e:  # one bad feed must not stop the run
            print(f"[research] feed failed {url}: {e}")
            continue
        if not feed.entries:
            print(f"[research] no entries from {url} (status {feed.get('status')})")
        source = feed.feed.get("title", url)
        for e in feed.entries[:40]:
            t = e.get("published_parsed") or e.get("updated_parsed")
            ts = calendar.timegm(t) if t else None
            if ts and ts < cutoff:
                continue
            title = _clean(e.get("title", ""))
            link = e.get("link", "")
            summary = _clean(e.get("summary", ""))[:900]
            if not title or link in covered:
                continue
            if MATCH and not MATCH.search(title + " " + summary):
                continue
            key = _norm_title(title)
            if key in seen_titles:
                continue
            seen_titles.add(key)
            items.append({"title": title, "link": link, "summary": summary,
                          "source": source, "ts": ts or time.time()})
    items.sort(key=lambda x: x["ts"], reverse=True)
    print(f"[research] {len(items)} candidate questions/stories")
    return items[:60]
