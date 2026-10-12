"""Screens for the FIX / STEP parts of a Short (rendered by headless Chromium).

Two sources, in this order:
1. REAL screenshots from the creator's own Zoho account: assets/screens/index.yaml lists them
   (key -> file, about, targets {label: [x, y, w, h] in image pixels}). A spec with "real": "<key>" uses one.
2. Illustrations drawn here, for any Zoho app (CRM, Books, Desk, Creator, Social, Flow, Analytics, Sign, Catalyst,
   SalesIQ, Inventory, ...) and for the "AI" parts: an AI chat connected to Zoho (Claude / ChatGPT via MCP),
   an API call (request + response), a code editor (Deluge / widget JS), and a Zoho Flow chain.

A spec, e.g.
  {"app": "crm", "view": "list", "path": ["Leads"], "heading": "Leads", "columns": [...], "rows": [[...]],
   "click": "Create Lead", "tip": "..."}
  {"app": "claude", "view": "chat", "messages": [["user", "..."], ["assistant", "..."]], "tool": "Zoho CRM - Data Insights",
   "click": "Zoho CRM - Data Insights"}
  {"app": "api", "view": "api", "method": "POST", "url": "https://www.zohoapis.com/crm/v8/Leads/upsert",
   "headers": [["Authorization", "Zoho-oauthtoken ****"]], "body": "{...}", "response": "{...}", "click": "upsert"}
Each step becomes two PNGs (plain + target highlighted) and the bounding box of the highlighted target,
so the editor can zoom the "camera" onto it.
"""
import html
import json
from pathlib import Path

import yaml

W, H, SCALE = 1000, 1100, 2  # panel size in the video; rendered at 2x so zooming stays sharp
ROOT = Path(__file__).resolve().parent.parent
REAL_DIR = ROOT / "assets" / "screens"

# ------------------------------------------------------------------ app "chrome" (logo, colours, menu)
APPS = {
    "books": {"name": "Books", "accent": "#408dfb", "side": "#21263c",
              "modules": [("Home", "⌂"), ("Items", "▦"), ("Banking", "◫"), ("Sales", "↗"), ("Purchases", "↘"),
                          ("Time Tracking", "◷"), ("Accountant", "⚖"), ("Reports", "▤"), ("Documents", "▢"),
                          ("Settings", "⚙")],
              "sub": {"Sales": ["Customers", "Quotes", "Sales Orders", "Invoices", "Payments Received", "Credit Notes"],
                      "Purchases": ["Vendors", "Expenses", "Purchase Orders", "Bills", "Payments Made"],
                      "Items": ["Items", "Price Lists", "Inventory Adjustments"],
                      "Banking": ["Banking", "Bank Rules"],
                      "Accountant": ["Manual Journals", "Chart of Accounts", "Transaction Locking"],
                      "Settings": ["Organization Profile", "Preferences", "Taxes & Compliance", "Automation",
                                   "Customization"]}},
    "crm": {"name": "CRM", "accent": "#1a73e8", "side": "#1b2437",
            "modules": [("Home", "⌂"), ("Leads", "☆"), ("Contacts", "☺"), ("Accounts", "▣"), ("Deals", "◎"),
                        ("Tasks", "✓"), ("Meetings", "◷"), ("Calls", "☏"), ("Reports", "▤"), ("Analytics", "◔"),
                        ("Setup", "⚙")],
            "sub": {"Setup": ["Users and Control", "Channels", "Automation", "Customization", "Developer Hub",
                              "Data Administration"],
                    "Leads": ["All Leads", "My Leads", "Today's Leads", "Unread Leads"],
                    "Deals": ["All Deals", "My Deals", "Closing This Month"]}},
    "desk": {"name": "Desk", "accent": "#2b9348", "side": "#1d2a24",
             "modules": [("Tickets", "✉"), ("Customers", "☺"), ("Activities", "✓"), ("Knowledge Base", "▤"),
                         ("Reports", "◔"), ("Setup", "⚙")],
             "sub": {"Setup": ["Automation", "Assignment Rules", "Workflows", "Blueprints", "SLAs", "Channels"]}},
    "creator": {"name": "Creator", "accent": "#e8590c", "side": "#2b2118",
                "modules": [("Dashboard", "⌂"), ("Forms", "▦"), ("Reports", "▤"), ("Pages", "▢"),
                            ("Workflows", "↻"), ("Settings", "⚙")],
                "sub": {"Workflows": ["Form Workflows", "Schedules", "Functions", "Approvals"]}},
    "social": {"name": "Social", "accent": "#d6336c", "side": "#2a1a22",
               "modules": [("Home", "⌂"), ("Publishing", "✎"), ("Messages", "✉"), ("Monitor", "◉"),
                           ("Reports", "◔"), ("Lead Forms", "☆"), ("Settings", "⚙")],
               "sub": {"Lead Forms": ["Facebook Lead Ads", "Field Mapping", "Assignment Rule"]}},
    "flow": {"name": "Flow", "accent": "#7048e8", "side": "#1f1a33",
             "modules": [("My Flows", "↻"), ("Templates", "▦"), ("History", "◷"), ("Connections", "⇄"),
                         ("Settings", "⚙")], "sub": {}},
    "analytics": {"name": "Analytics", "accent": "#f08c00", "side": "#2b2416",
                  "modules": [("Home", "⌂"), ("Workspaces", "▦"), ("Ask Zia", "✦"), ("Reports", "◔"),
                              ("Settings", "⚙")], "sub": {}},
    "sign": {"name": "Sign", "accent": "#1971c2", "side": "#16222e",
             "modules": [("Home", "⌂"), ("Documents", "▢"), ("Templates", "▦"), ("Reports", "◔"),
                         ("Settings", "⚙")], "sub": {}},
    "catalyst": {"name": "Catalyst", "accent": "#0ca678", "side": "#14261f",
                 "modules": [("Projects", "▦"), ("Functions", "ƒ"), ("Data Store", "▤"), ("Cron", "◷"),
                             ("QuickML", "✦"), ("Settings", "⚙")], "sub": {}},
    "salesiq": {"name": "SalesIQ", "accent": "#fa5252", "side": "#2b1717",
                "modules": [("Visitors", "◉"), ("Conversations", "✉"), ("Bots", "✦"), ("Leads", "☆"),
                            ("Reports", "◔"), ("Settings", "⚙")], "sub": {}},
    "inventory": {"name": "Inventory", "accent": "#408dfb", "side": "#21263c",
                  "modules": [("Home", "⌂"), ("Items", "▦"), ("Sales Orders", "↗"), ("Purchase Orders", "↘"),
                              ("Packages", "▢"), ("Reports", "▤"), ("Settings", "⚙")], "sub": {}},
}
GENERIC = {"name": "", "accent": "#408dfb", "side": "#21263c",
           "modules": [("Home", "⌂"), ("Records", "▦"), ("Reports", "▤"), ("Settings", "⚙")], "sub": {}}
ALIASES = {"zoho crm": "crm", "zoho books": "books", "zoho desk": "desk", "zoho creator": "creator",
           "zoho social": "social", "zoho flow": "flow", "zoho analytics": "analytics", "zoho sign": "sign",
           "zoho catalyst": "catalyst", "zoho salesiq": "salesiq", "zoho inventory": "inventory",
           "chatgpt": "chatgpt", "openai": "chatgpt", "claude": "claude", "anthropic": "claude",
           "deluge": "code", "widget": "code", "javascript": "code", "postman": "api", "rest": "api"}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:%(W)dpx;height:%(H)dpx;font-family:'Noto Sans','Inter','DejaVu Sans',sans-serif;background:#f5f7fb;
     color:#1f2937;overflow:hidden;display:flex;flex-direction:column;position:relative}
.top{height:74px;background:#fff;border-bottom:1px solid #e3e7ef;display:flex;align-items:center;padding:0 26px;gap:16px}
.logo{font-weight:800;font-size:28px;color:#1f2937;white-space:nowrap}.logo b{color:var(--ac)}
.search{flex:1;height:44px;border-radius:10px;background:#f1f3f8;color:#9aa3b2;font-size:20px;display:flex;
        align-items:center;padding:0 16px;overflow:hidden;white-space:nowrap}
.org{font-size:19px;color:#4b5563;white-space:nowrap}
.main{flex:1;display:flex;min-height:0}
.side{width:250px;background:var(--sd);color:#c9cfdd;padding:16px 0;font-size:21px}
.side .m{padding:12px 22px;display:flex;gap:14px;align-items:center}
.side .m.on{background:var(--ac);color:#fff;font-weight:700}
.side .s{padding:9px 22px 9px 60px;font-size:19px;color:#9aa3b8}
.side .s.on{color:#fff;font-weight:700;background:rgba(255,255,255,.08)}
.content{flex:1;padding:26px 28px;min-width:0;display:flex;flex-direction:column;gap:18px}
.crumb{font-size:19px;color:#6b7280}
.head{display:flex;align-items:center;justify-content:space-between;gap:12px}
h1{font-size:33px;font-weight:800;color:#111827;line-height:1.15}
.btn{border-radius:10px;padding:13px 20px;font-size:21px;font-weight:700;border:2px solid #d5dbe6;background:#fff;
     color:#1f2937;white-space:nowrap}
.btn.primary{background:var(--ac);border-color:var(--ac);color:#fff}
.card{background:#fff;border:1px solid #e3e7ef;border-radius:14px;padding:6px 0;box-shadow:0 2px 6px rgba(20,30,60,.05)}
table{width:100%%;border-collapse:collapse;font-size:20px}
th{text-align:left;color:#6b7280;font-weight:700;font-size:17px;text-transform:uppercase;padding:14px 16px;
   border-bottom:1px solid #eef1f6}
td{padding:16px;border-bottom:1px solid #f0f2f7}
.pill{display:inline-block;padding:4px 12px;border-radius:20px;font-size:17px;font-weight:700;background:#e8f1ff;color:#2563eb}
.pill.g{background:#e6f7ee;color:#0f8a4b}.pill.o{background:#fff3e0;color:#c26a00}.pill.r{background:#fdecec;color:#c62828}
.field{padding:14px 22px;display:flex;flex-direction:column;gap:8px}
.field label{font-size:18px;color:#6b7280;font-weight:600}
.field .inp{border:2px solid #d5dbe6;border-radius:10px;padding:13px 16px;font-size:22px;color:#111827;background:#fff}
.tog{display:flex;justify-content:space-between;align-items:center;padding:18px 22px;border-bottom:1px solid #f0f2f7;font-size:22px}
.sw{width:64px;height:36px;border-radius:20px;background:#cfd6e2;position:relative;flex:none}
.sw:after{content:'';position:absolute;top:4px;left:4px;width:28px;height:28px;border-radius:50%%;background:#fff}
.sw.on{background:#22a35a}.sw.on:after{left:32px}
.actions{display:flex;gap:14px;flex-wrap:wrap}
.tip{margin-top:auto;background:#fff8db;border:2px solid #f4d35e;border-radius:14px;padding:16px 20px;font-size:22px;
     font-weight:700;color:#5b4500}
.illu{position:absolute;right:12px;bottom:8px;font-size:13px;color:#a0a7b4}
.hl{outline:6px solid #ff3b30;outline-offset:6px;border-radius:12px;position:relative;z-index:5;
    box-shadow:0 0 0 9999px rgba(15,20,35,.28)}
.cursor{position:absolute;width:56px;height:56px;z-index:9;pointer-events:none}
/* AI chat */
.chat{flex:1;display:flex;flex-direction:column;background:#faf9f6}
.chat .bar{height:74px;display:flex;align-items:center;gap:14px;padding:0 26px;border-bottom:1px solid #e7e3da;
           font-size:24px;font-weight:800;background:#fff}
.chat .dot{width:34px;height:34px;border-radius:50%%;background:var(--ac)}
.chat .conn{margin-left:auto;font-size:17px;font-weight:700;color:#0f8a4b;background:#e6f7ee;padding:6px 14px;border-radius:20px}
.chat .msgs{flex:1;padding:28px;display:flex;flex-direction:column;gap:22px}
.chat .u{align-self:flex-end;max-width:82%%;background:#ece8df;border-radius:22px;padding:18px 22px;font-size:24px;line-height:1.35}
.chat .a{max-width:92%%;font-size:24px;line-height:1.4;color:#1f2937}
.chat .tool{display:inline-flex;gap:10px;align-items:center;border:2px solid #d9d4c7;border-radius:12px;padding:10px 16px;
            font-size:19px;font-weight:700;color:#4b5563;background:#fff;margin-bottom:12px}
.chat .box{margin:22px 28px;border:2px solid #d9d4c7;border-radius:20px;padding:18px 22px;font-size:22px;color:#9aa3b2;background:#fff}
/* API */
.api{flex:1;display:flex;flex-direction:column;gap:16px;padding:26px;background:#f7f8fa}
.req{display:flex;gap:12px;align-items:center}
.meth{font-weight:800;font-size:22px;padding:12px 16px;border-radius:10px;background:#fff3e0;color:#c26a00}
.meth.GET{background:#e6f7ee;color:#0f8a4b}.meth.DELETE{background:#fdecec;color:#c62828}
.url{flex:1;font-family:'DejaVu Sans Mono',monospace;font-size:19px;background:#fff;border:2px solid #d5dbe6;
     border-radius:10px;padding:12px 14px;word-break:break-all}
.lbl{font-size:17px;font-weight:800;color:#6b7280;text-transform:uppercase;letter-spacing:.5px}
pre{font-family:'DejaVu Sans Mono',monospace;font-size:19px;line-height:1.45;white-space:pre-wrap;word-break:break-word;
    background:#1e2433;color:#e6e9f0;border-radius:12px;padding:16px 18px;margin:0}
pre.resp{background:#0f2a1d;color:#c7f0d8}
.kv{display:flex;gap:10px;font-family:'DejaVu Sans Mono',monospace;font-size:18px;background:#fff;border:1px solid #e3e7ef;
    border-radius:8px;padding:8px 12px}
.kv b{color:#6b7280}
/* code */
.code{flex:1;background:#1e2433;color:#e6e9f0;display:flex;flex-direction:column}
.code .tab{height:60px;display:flex;align-items:center;padding:0 22px;font-size:19px;background:#161b27;color:#9aa3b8;gap:12px}
.code .tab b{color:#fff;background:#1e2433;padding:18px 18px}
.code .ln{display:flex;font-family:'DejaVu Sans Mono',monospace;font-size:21px;line-height:1.6;padding:0 18px}
.code .ln i{width:44px;color:#5c6680;font-style:normal;flex:none}
.code .ln span{white-space:pre-wrap;word-break:break-word}
.code .hlline{background:rgba(255,201,60,.14)}
/* flow chain */
.chain{flex:1;display:flex;flex-direction:column;align-items:center;gap:0;padding:30px 40px;background:#f6f4fb}
.node{width:100%%;background:#fff;border:2px solid #ddd6f3;border-radius:16px;padding:20px 24px;font-size:24px;font-weight:700;
      display:flex;gap:16px;align-items:center}
.node em{font-style:normal;font-size:16px;font-weight:800;color:#fff;background:var(--ac);border-radius:8px;padding:5px 10px}
.arrow{height:44px;width:4px;background:#c5bdea;position:relative}
.arrow:after{content:'';position:absolute;bottom:-6px;left:-8px;border:10px solid transparent;border-top-color:#c5bdea}
/* real screenshot */
.real{flex:1;display:flex;align-items:center;justify-content:center;background:#e9edf3;position:relative}
.real .wrap{position:relative}
.real img{display:block;max-width:%(W)dpx;max-height:%(H)dpx}
.real .t{position:absolute}
"""


def _esc(x):
    return html.escape(str(x if x is not None else ""))


def _pill(v):
    t = str(v)
    low = t.lower()
    cls = "g" if any(k in low for k in ("paid", "closed", "active", "approved", "sent", "done", "yes", "won", "signed")) else \
          "o" if any(k in low for k in ("draft", "pending", "open", "partial", "new", "hot")) else \
          "r" if any(k in low for k in ("overdue", "void", "error", "missing", "unpaid", "lost", "failed")) else ""
    return f'<span class="pill {cls}">{_esc(t)}</span>'


def _tgt(click, text):
    return 'data-target=1' if click and str(text).strip().lower() == str(click).strip().lower() else ""


def _tgt_in(click, text):
    """Target when the click text is contained in this element (code lines, URLs, chat bubbles)."""
    return 'data-target=1' if click and str(click).strip().lower() in str(text).lower() else ""


# ------------------------------------------------------------------ real screenshots
def library():
    """assets/screens/index.yaml -> {key: {"file", "about", "targets": {label: [x, y, w, h]}}}"""
    f = REAL_DIR / "index.yaml"
    if not f.exists():
        return {}
    try:
        data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    except Exception as e:
        print(f"[screens] index.yaml unreadable: {e}")
        return {}
    lib = {}
    for k, v in (data.get("screens") or {}).items():
        if isinstance(v, dict) and v.get("file") and (REAL_DIR / v["file"]).exists():
            lib[str(k)] = v
    return lib


def normalize(spec, card="", beat=""):
    """Makes any (even missing / half) spec renderable. "card" like 'Sales > Sales Orders' is the fallback."""
    spec = dict(spec or {})
    path = spec.get("path") or [p.strip() for p in str(card or "").replace("→", ">").split(">") if p.strip()]
    if isinstance(path, str):
        path = [p.strip() for p in path.split(">") if p.strip()]
    path = [str(p) for p in path][:4] or ["Home"]
    spec["path"] = path
    spec.setdefault("heading", path[-1])
    app = str(spec.get("app") or "").strip().lower()
    app = ALIASES.get(app, app.replace("zoho ", ""))
    v = str(spec.get("view") or "").lower()
    if app in ("claude", "chatgpt") or spec.get("messages"):
        v = "chat"
    elif app == "api" or (spec.get("url") and spec.get("method")):
        v, app = "api", "api"
    elif app == "code" or (spec.get("code") and v not in ("list", "form", "settings")):
        v, app = "code", "code"
    elif v == "flow" or (app == "flow" and spec.get("nodes")):
        v = "flow"
    if v not in ("list", "form", "settings", "chat", "api", "code", "flow"):
        v = "list" if spec.get("rows") else "settings" if spec.get("toggles") else "form" if spec.get("fields") else \
            ("settings" if path[0].lower() in ("settings", "preferences", "setup") else "list")
    if v in ("list", "form", "settings") and app not in APPS:
        app = "books" if not app else app
    spec["app"], spec["view"] = app, v
    if v in ("api", "code", "flow", "chat") and spec.get("heading") == path[-1] and path == ["Home"]:
        spec["heading"] = ""  # no fake "Home" title on API / code / flow / chat screens
    real = spec.get("real")
    spec["real"] = real if real and real in library() else None
    spec.setdefault("click", "")
    spec.setdefault("tip", "")
    spec["beat"] = beat
    return spec


def _module_of(path, conf):
    names = [m for m, _ in conf["modules"]]
    for p in path:
        for n in names:
            if p.lower() == n.lower():
                return n
    for p in path:
        for mod, subs in conf["sub"].items():
            if any(p.lower() == s.lower() for s in subs):
                return mod
    for p in path:
        if any(w in p.lower() for w in ("setting", "setup", "preference")):
            return next((n for n in names if n.lower() in ("settings", "setup")), names[0])
    return names[0]


def _page(inner, ac="#408dfb", sd="#21263c", illu=True):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS % {"W": W, "H": H}}</style></head>'
            f'<body style="--ac:{ac};--sd:{sd}">{inner}'
            + ('<div class="illu">illustration</div>' if illu else "") + "</body></html>")


def _app_page(spec):
    conf = APPS.get(spec["app"], GENERIC)
    path, click = spec["path"], spec.get("click") or ""
    mod = _module_of(path, conf)
    side = []
    for name, icon in conf["modules"]:
        side.append(f'<div class="m {"on" if name == mod else ""}" {_tgt(click, name)}><span>{icon}</span>{_esc(name)}</div>')
        if name == mod:
            subs = list(conf["sub"].get(mod, []))
            here = next((p for p in path if p.lower() != mod.lower()), None)
            if here and not any(here.lower() == s.lower() for s in subs) and len(path) > 1:
                subs = subs[:4] + [here]
            for s in subs[:6]:
                on = here and s.lower() == here.lower()
                side.append(f'<div class="s {"on" if on else ""}" {_tgt(click, s)}>{_esc(s)}</div>')

    v = spec["view"]
    if v == "list":
        cols = spec.get("columns") or ["Name", "Company", "Source", "Owner", "Status"]
        rows = spec.get("rows") or [["Omar Haddad", "Al Noor Trading", "Facebook", "Sara", "New"],
                                    ["Lena Fischer", "Berlin Logistics GmbH", "Website", "Arjun", "Contacted"],
                                    ["Ravi Sharma", "Sharma Exports", "WhatsApp", "Sara", "Qualified"]]
        th = "".join(f"<th {_tgt(click, c)}>{_esc(c)}</th>" for c in cols[:5])
        trs = []
        for r in rows[:5]:
            cells = list(r)[:len(cols[:5])]
            tds = []
            for j, c in enumerate(cells):
                col = str(cols[j]).lower() if j < len(cols) else ""
                txt = _pill(c) if ("status" in col or "stage" in col) else _esc(c)
                tds.append(f"<td {_tgt(click, c)}>{txt}</td>")
            trs.append("<tr>" + "".join(tds) + "</tr>")
        body = f'<div class="card"><table><tr>{th}</tr>{"".join(trs)}</table></div>'
    elif v == "form":
        fs = spec.get("fields") or [["Name", "Al Noor Trading"], ["Email", "info@alnoor.example"]]
        items = []
        for f in fs[:6]:
            lab, val = (list(f) + [""])[:2] if isinstance(f, (list, tuple)) else (f.get("label"), f.get("value"))
            items.append(f'<div class="field" {_tgt(click, lab) or _tgt(click, val)}><label>{_esc(lab)}</label>'
                         f'<div class="inp">{_esc(val) or "&nbsp;"}</div></div>')
        body = f'<div class="card">{"".join(items)}</div>'
    else:
        ts = spec.get("toggles") or [["Enable this option", True]]
        items = []
        for t in ts[:6]:
            lab, on = (list(t) + [True])[:2] if isinstance(t, (list, tuple)) else (t.get("label"), t.get("on", True))
            items.append(f'<div class="tog" {_tgt(click, lab)}><span>{_esc(lab)}</span>'
                         f'<span class="sw {"on" if on else ""}"></span></div>')
        body = f'<div class="card">{"".join(items)}</div>'

    acts = []
    primary_label = click if click else ("Save" if v != "list" else "+ New")
    in_body = click and ("data-target=1" in body or "data-target=1" in "".join(side))
    if v == "list":
        btns = ["+ New"] if in_body or click == "+ New" else [primary_label, "+ New"] if click else ["+ New"]
    else:
        btns = ["Save", "Cancel"] if in_body or not click else [click, "Cancel"]
    for k, b in enumerate(dict.fromkeys(btns)):
        tgt = _tgt(click, b) if not in_body else ""
        acts.append(f'<span class="btn {"primary" if k == 0 else ""}" {tgt}>{_esc(b)}</span>')
    top_btn = acts[0] if v == "list" else ""
    bottom = "" if v == "list" else f'<div class="actions">{"".join(acts)}</div>'
    tip = f'<div class="tip">Tip: {_esc(spec["tip"])}</div>' if spec.get("tip") else ""
    crumb = " › ".join(_esc(p) for p in path)
    logo = f'Zoho <b>{_esc(conf["name"])}</b>' if conf["name"] else "<b>Zoho</b>"
    inner = (f'<div class="top"><div class="logo">{logo}</div><div class="search">Search in {_esc(spec["heading"])}</div>'
             f'<div class="org">My Business ▾</div></div>'
             f'<div class="main"><div class="side">{"".join(side)}</div>'
             f'<div class="content"><div class="crumb">{crumb}</div><div class="head"><h1>{_esc(spec["heading"])}</h1>'
             f'{top_btn}</div>{body}{bottom}{tip}</div></div>')
    return _page(inner, conf["accent"], conf["side"])


def _chat_page(spec):
    click = spec.get("click") or ""
    who = "ChatGPT" if spec["app"] == "chatgpt" else "Claude"
    ac = "#10a37f" if who == "ChatGPT" else "#c96442"
    tool = spec.get("tool") or "Zoho CRM (MCP)"
    msgs = spec.get("messages") or [["user", "Which deals over $10k have had no activity for 14 days?"],
                                    ["assistant", "Found 6 deals. Biggest: Al Noor Trading - $48,000, last touch 19 days ago."]]
    out = []
    for m in msgs[:4]:
        role, text = (list(m) + [""])[:2] if isinstance(m, (list, tuple)) else (m.get("role"), m.get("text"))
        if str(role).lower().startswith("u"):
            out.append(f'<div class="u" {_tgt_in(click, text)}>{_esc(text)}</div>')
        else:
            out.append(f'<div class="a"><div class="tool" {_tgt_in(click, tool)}>⚙ {_esc(tool)}</div>'
                       f'<div {_tgt_in(click, text) if not _tgt_in(click, tool) else ""}>{_esc(text)}</div></div>')
    tip = f'<div class="tip" style="margin:0 28px 20px">Tip: {_esc(spec["tip"])}</div>' if spec.get("tip") else ""
    inner = (f'<div class="chat"><div class="bar"><span class="dot"></span>{who}'
             f'<span class="conn" {_tgt_in(click, "connected")}>● Zoho connected</span></div>'
             f'<div class="msgs">{"".join(out)}</div>{tip}<div class="box">Reply...</div></div>')
    return _page(inner, ac, "#222")


def _kv(rows, click):
    return "".join(f'<div class="kv" {_tgt_in(click, a)}><b>{_esc(a)}:</b> {_esc(b)}</div>'
                   for a, b in [(list(r) + [""])[:2] for r in (rows or [])][:4])


def _api_page(spec):
    click = spec.get("click") or ""
    method = str(spec.get("method") or "GET").upper()
    url = spec.get("url") or "https://www.zohoapis.com/crm/v8/Leads"
    body = spec.get("body") or ""
    resp = spec.get("response") or '{"data": [{"code": "SUCCESS", "status": "success"}]}'
    if not isinstance(body, str):
        body = json.dumps(body, indent=1)
    if not isinstance(resp, str):
        resp = json.dumps(resp, indent=1)
    parts = [f'<div class="lbl">Request</div><div class="req"><span class="meth {method}" {_tgt(click, method)}>{method}</span>'
             f'<div class="url" {_tgt_in(click, url)}>{_esc(url)}</div></div>']
    if spec.get("headers"):
        parts.append(f'<div class="lbl">Headers</div>{_kv(spec["headers"], click)}')
    if body:
        parts.append(f'<div class="lbl">Body</div><pre {_tgt_in(click, body) if not _tgt_in(click, url) else ""}>'
                     f'{_esc(body[:600])}</pre>')
    parts.append(f'<div class="lbl">Response</div><pre class="resp">{_esc(resp[:500])}</pre>')
    if spec.get("tip"):
        parts.append(f'<div class="tip">Tip: {_esc(spec["tip"])}</div>')
    inner = (f'<div class="top"><div class="logo">API <b>call</b></div><div class="search">{_esc(spec.get("heading") or url)}</div></div>'
             f'<div class="api">{"".join(parts)}</div>')
    return _page(inner)


def _code_page(spec):
    click = spec.get("click") or ""
    code = spec.get("code") or "// your code here"
    if isinstance(code, dict):
        code = code.get("content", "")
    lines = str(code).splitlines()[:18]
    hit = next((i for i, l in enumerate(lines) if click and click.lower() in l.lower()), None)
    rows = "".join(f'<div class="ln {"hlline" if i == hit else ""}" {"data-target=1" if i == hit else ""}>'
                   f'<i>{i + 1}</i><span>{_esc(l)}</span></div>' for i, l in enumerate(lines))
    lang = spec.get("language") or "deluge"
    fname = spec.get("heading") or {"deluge": "function.dg", "javascript": "widget.js", "html": "index.html"}.get(lang, "code")
    tip = f'<div class="tip" style="margin:16px">Tip: {_esc(spec["tip"])}</div>' if spec.get("tip") else ""
    inner = (f'<div class="code"><div class="tab"><b>{_esc(fname)}</b>{_esc(lang)}</div>'
             f'<div style="padding:16px 0;flex:1">{rows}</div>{tip}</div>')
    return _page(inner)


def _flow_page(spec):
    click = spec.get("click") or ""
    nodes = spec.get("nodes") or ["Trigger: New Facebook lead", "AI: score the lead", "Action: Create lead in Zoho CRM"]
    out = []
    for i, n in enumerate(nodes[:5]):
        kind, _, text = str(n).partition(":")
        if not text:
            kind, text = ("Trigger" if i == 0 else "Action"), kind
        if i:
            out.append('<div class="arrow"></div>')
        out.append(f'<div class="node" {_tgt_in(click, n)}><em>{_esc(kind.strip().upper())}</em>{_esc(text.strip())}</div>')
    tip = f'<div class="tip" style="margin-top:30px;width:100%">Tip: {_esc(spec["tip"])}</div>' if spec.get("tip") else ""
    inner = (f'<div class="top"><div class="logo">Zoho <b>Flow</b></div><div class="search">{_esc(spec.get("heading") or "My Flows")}</div></div>'
             f'<div class="chain">{"".join(out)}{tip}</div>')
    return _page(inner, APPS["flow"]["accent"], APPS["flow"]["side"])


def _real_page(spec):
    item = library()[spec["real"]]
    img = (REAL_DIR / item["file"]).resolve()
    tg = item.get("targets") or {}
    click = (spec.get("click") or "").lower()
    box = next((b for k, b in tg.items() if k.lower() == click), None) or \
        next((b for k, b in tg.items() if click and click in k.lower()), None)
    t = ""
    if box:
        x, y, w, h = box
        # positions are in image pixels; the <img> is scaled by CSS -> use percentages of the natural size
        nat = item.get("size") or [None, None]
        if nat[0] and nat[1]:
            t = (f'<div class="t" data-target=1 style="left:{x / nat[0] * 100:.3f}%;top:{y / nat[1] * 100:.3f}%;'
                 f'width:{w / nat[0] * 100:.3f}%;height:{h / nat[1] * 100:.3f}%"></div>')
    tip = f'<div class="tip" style="position:absolute;left:20px;right:20px;bottom:20px">Tip: {_esc(spec["tip"])}</div>' \
        if spec.get("tip") else ""
    inner = f'<div class="real"><div class="wrap"><img src="{img.as_uri()}">{t}</div>{tip}</div>'
    return _page(inner, illu=False)


def build_html(spec):
    if spec.get("real"):
        return _real_page(spec)
    return {"chat": _chat_page, "api": _api_page, "code": _code_page, "flow": _flow_page}.get(
        spec["view"], _app_page)(spec)


CURSOR = ('<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M3 2l7.5 19 2.6-7.6L21 11z" '
          'fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>')

JS_HL = """() => {
  let el = document.querySelector('[data-target]');
  if (!el) el = document.querySelector('.btn.primary') || document.querySelector('h1') || document.querySelector('.node')
            || document.querySelector('.url') || document.querySelector('.u') || document.body.firstElementChild;
  el.classList.add('hl');
  const r = el.getBoundingClientRect();
  const c = document.createElement('div'); c.className = 'cursor'; c.innerHTML = %s;
  c.style.left = (r.left + r.width * 0.6) + 'px'; c.style.top = (r.top + r.height * 0.55) + 'px';
  document.body.appendChild(c);
  return [r.left, r.top, r.width, r.height];
}""" % json.dumps(CURSOR)


def render(specs, outdir: Path):
    """specs: list of normalized specs. Returns list of {"plain": png, "hl": png, "box": [x,y,w,h] (1x px)}."""
    from playwright.sync_api import sync_playwright
    outdir.mkdir(parents=True, exist_ok=True)
    res = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        for i, spec in enumerate(specs):
            page = build_html(spec)
            f = outdir / f"screen{i:02d}.html"  # a file URL so real screenshots (file://) load
            f.write_text(page, encoding="utf-8")
            pg.goto(f.resolve().as_uri(), wait_until="load")
            plain, hl = outdir / f"screen{i:02d}_a.png", outdir / f"screen{i:02d}_b.png"
            pg.screenshot(path=str(plain))
            box = pg.evaluate(JS_HL)
            pg.screenshot(path=str(hl))
            res.append({"plain": plain, "hl": hl, "box": box})
        b.close()
    return res
