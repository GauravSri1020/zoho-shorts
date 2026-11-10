"""Research input for the scout.

1. Feeds (channel.yaml -> sources.feeds): Zoho questions, AI news, automation questions, region news, Google Trends.
   Each item gets a "trend" score = how many OTHER items (from other sources) talk about the same key terms,
   so a topic that is everywhere this week ranks first.
   10 Nov 2026: sources.trending_only = only fresh news is a topic (see fetch); community feeds = context only.
2. Problem bank (research/problem_bank.yaml): real problems + Gaurav's own Zoho experience. Never-used ones are
   added as candidates every day, so the scout always has strong material even when the feeds are quiet.
"""
import calendar
import re
import time
from collections import Counter
from html import unescape

import feedparser
import yaml

from .config import (FEEDS, KEYWORDS, LOOKBACK_DAYS, PROBLEM_BANK, IS_ZOHO, COMMUNITY_FEEDS, TRENDING_ONLY,
                     NEWS_MAX_AGE_HOURS)

_KW = [k.strip() for k in KEYWORDS if k.strip()]
MATCH = re.compile(r"\b(" + "|".join(re.escape(k) for k in _KW) + r")\b", re.I) if _KW else None
_STOP = set("""a an the and or of to in on for with from by at is are was were be been this that these those it its
as how what why when who new now your you our we they their about into over after more most just than not no can
will has have had do does did vs via using use how-to get gets make makes 2025 2026 2027""".split())


def _clean(html):
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _norm_title(t):
    return re.sub(r"[^a-z0-9 ]", "", t.lower())[:80]


def _terms(text):
    words = [w for w in re.findall(r"[a-z][a-z0-9\-]{2,}", text.lower()) if w not in _STOP]
    return set(words) | {f"{a} {b}" for a, b in zip(words, words[1:])}


def _trend_scores(items):
    """Terms that appear in several sources this week = trending. Score = sum of their spread."""
    by_source = {}
    for it in items:
        by_source.setdefault(it["source"], set()).update(_terms(it["title"]))
    spread = Counter(t for terms in by_source.values() for t in terms)
    for it in items:
        it["trend"] = sum(spread[t] - 1 for t in _terms(it["title"]) if spread[t] > 1)


def _bank(already_covered):
    """Problem bank entries not made yet, as candidates (source = 'GSX problem bank')."""
    try:
        data = yaml.safe_load(PROBLEM_BANK.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"[research] problem bank unreadable: {e}")
        return []
    out = []
    for p in data.get("problems") or []:
        link = f"bank:{_norm_title(p.get('problem', ''))[:60]}"
        if not p.get("problem") or link in already_covered:
            continue
        summary = " | ".join(f"{k}: {p[k]}" for k in ("pillar", "region", "product", "fix", "facts", "wow") if p.get(k))
        if not IS_ZOHO:  # niche switch: the Claude-wealth bank also carries steps, the catch and its source
            extra = " | ".join(f"{k}: {p[k]}" for k in ("kind", "steps", "catch", "source") if p.get(k))
            summary = (summary + " | " + extra if extra else summary)[:1600]
        out.append({"title": p["problem"], "link": link, "summary": summary[:900] if IS_ZOHO else summary,
                    "source": "GSX problem bank", "ts": time.time(), "trend": 0, "pillar": p.get("pillar", "")})
        if not IS_ZOHO:
            out[-1] |= {"kind": p.get("kind") or ("problems" if p.get("pillar") == "problems" else "wealth"),
                        "order": p.get("order")}
    # round-robin over pillars, so the scout always sees a mix (AI agents, lead flow, API, regional, ...)
    if not IS_ZOHO:  # Claude-wealth bank: the hand-ordered first Shorts ("order: 1..5") come first
        out.sort(key=lambda it: (it.get("order") is None, it.get("order") or 0))
        return out
    groups = {}
    for it in out:
        groups.setdefault(it["pillar"], []).append(it)
    mixed = []
    while any(groups.values()):
        for g in list(groups.values()):
            if g:
                mixed.append(g.pop(0))
    return mixed


def _read(urls, cutoff, covered, seen_titles, kind):
    items = []
    for url in urls:
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
            if kind == "news" and not ts and TRENDING_ONLY:  # news without a date cannot prove it is fresh
                continue
            title = _clean(e.get("title", ""))
            link = e.get("link", "")
            summary = _clean(e.get("summary", ""))[:900]
            if not title or link in covered:
                continue
            if MATCH and not MATCH.search(title + " " + summary):
                continue
            src = source
            m = re.match(r"(.+?)\s+-\s+([^-]{2,60})$", title) if "news.google" in url else None
            if m:  # Google News: "Headline - Publisher" -> the publisher is the real source
                title, src = m.group(1).strip(), m.group(2).strip()
            key = _norm_title(title)
            if key in seen_titles:
                continue
            seen_titles.add(key)
            items.append({"title": title, "link": link, "summary": summary, "source": src,
                          "ts": ts or time.time(), "type": kind})
    return items


def _hours_old(it):
    return max(0, int((time.time() - it["ts"]) / 3600))


def fetch(already_covered, lookback_days=LOOKBACK_DAYS):
    covered = set(already_covered)
    seen_titles = set()
    if TRENDING_ONLY:
        # 10 Nov 2026 (Gaurav): ONLY trending news. News = fresh (news_max_age_hours) and ranked by how many
        # different publishers / sources carry the same story + how new it is. Community questions are kept
        # separately, only as proof that people feel the pain. No problem bank, no evergreen topics.
        news = _read(FEEDS, time.time() - NEWS_MAX_AGE_HOURS * 3600, covered, seen_titles, "news")
        community = _read(COMMUNITY_FEEDS, time.time() - lookback_days * 86400, covered, seen_titles, "question")
        _trend_scores(news + community)
        for it in news:
            h = _hours_old(it)
            it["age_hours"] = h
            it["score"] = it["trend"] * 2 + (4 if h <= 24 else 2 if h <= 48 else 1 if h <= 72 else 0)
        news.sort(key=lambda x: (x["score"], x["ts"]), reverse=True)
        community.sort(key=lambda x: (x["trend"], x["ts"]), reverse=True)
        news, community = news[:40], community[:12]
        print(f"[research] TRENDING ONLY: {len(news)} fresh news items (top score {news[0]['score'] if news else 0}), "
              f"{len(community)} community questions as context")
        for it in news[:8]:
            print(f"[research]   score {it['score']:>2} | {it['age_hours']:>3}h | {it['title'][:90]} ({it['source']})")
        return news + community
    cutoff = time.time() - lookback_days * 86400
    items = _read(FEEDS, cutoff, covered, seen_titles, "news") + _read(COMMUNITY_FEEDS, cutoff, covered,
                                                                     seen_titles, "question")
    _trend_scores(items)
    # trending first, then newest
    items.sort(key=lambda x: (x["trend"], x["ts"]), reverse=True)
    items = items[:45]
    bank = _bank(covered)
    print(f"[research] {len(items)} feed items (top trend score {items[0]['trend'] if items else 0}), "
          f"{len(bank)} unused problem-bank entries")
    return items + bank[:25]
