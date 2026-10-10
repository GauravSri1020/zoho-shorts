"""Zoho Books style screens for the STEP parts of a Short (illustrations, rendered by headless Chromium).

The script writer gives every step a small "screen" spec, e.g.
  {"path": ["Sales", "Sales Orders"], "view": "list", "heading": "Sales Orders",
   "columns": ["Date", "SO#", "Customer", "Status"], "rows": [["10 Oct", "SO-0012", "Sharma Traders", "Paid"]],
   "fields": [["Customer Name", "Sharma Traders"]], "toggles": [["Auto-convert to invoice", true]],
   "click": "Convert to Invoice", "tip": "Paid orders ko ek click mein invoice banao"}
Each step becomes two PNGs (plain + target highlighted) and the bounding box of the highlighted target,
so the editor can zoom the "camera" onto it.
"""
import html
import json
from pathlib import Path

W, H, SCALE = 1000, 1100, 2          # panel size in the video; rendered at 2x so zooming stays sharp

MODULES = [("Home", "⌂"), ("Items", "▦"), ("Banking", "₹"), ("Sales", "↗"), ("Purchases", "↘"),
           ("Time Tracking", "◷"), ("Accountant", "⚖"), ("Reports", "▤"), ("Documents", "▢"), ("Settings", "⚙")]
SUB = {"Sales": ["Customers", "Quotes", "Sales Orders", "Invoices", "Payments Received", "Credit Notes"],
       "Purchases": ["Vendors", "Expenses", "Purchase Orders", "Bills", "Payments Made"],
       "Items": ["Items", "Price Lists", "Inventory Adjustments"],
       "Banking": ["Banking", "Bank Rules"],
       "Accountant": ["Manual Journals", "Chart of Accounts", "Transaction Locking"],
       "Settings": ["Organization Profile", "Preferences", "Taxes", "Automation", "Customization"]}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:%(W)dpx;height:%(H)dpx;font-family:'Noto Sans','Inter','DejaVu Sans',sans-serif;background:#f5f7fb;
     color:#1f2937;overflow:hidden;display:flex;flex-direction:column}
.top{height:74px;background:#fff;border-bottom:1px solid #e3e7ef;display:flex;align-items:center;padding:0 26px;gap:16px}
.logo{font-weight:800;font-size:28px;color:#1f2937}.logo b{color:#408dfb}
.search{flex:1;height:44px;border-radius:10px;background:#f1f3f8;color:#9aa3b2;font-size:20px;display:flex;
        align-items:center;padding:0 16px}
.org{font-size:19px;color:#4b5563}
.main{flex:1;display:flex;min-height:0}
.side{width:250px;background:#21263c;color:#c9cfdd;padding:16px 0;font-size:21px}
.side .m{padding:12px 22px;display:flex;gap:14px;align-items:center}
.side .m.on{background:#408dfb;color:#fff;font-weight:700}
.side .s{padding:9px 22px 9px 60px;font-size:19px;color:#9aa3b8}
.side .s.on{color:#fff;font-weight:700;background:#2d3450}
.content{flex:1;padding:26px 28px;min-width:0;display:flex;flex-direction:column;gap:18px}
.crumb{font-size:19px;color:#6b7280}
.head{display:flex;align-items:center;justify-content:space-between;gap:12px}
h1{font-size:33px;font-weight:800;color:#111827;line-height:1.15}
.btn{border-radius:10px;padding:13px 20px;font-size:21px;font-weight:700;border:2px solid #d5dbe6;background:#fff;
     color:#1f2937;white-space:nowrap}
.btn.primary{background:#408dfb;border-color:#408dfb;color:#fff}
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
"""


def _esc(x):
    return html.escape(str(x if x is not None else ""))


def _pill(v):
    t = str(v)
    low = t.lower()
    cls = "g" if any(k in low for k in ("paid", "closed", "active", "approved", "sent", "done", "yes")) else \
          "o" if any(k in low for k in ("draft", "pending", "open", "partial")) else \
          "r" if any(k in low for k in ("overdue", "void", "error", "missing", "unpaid")) else ""
    return f'<span class="pill {cls}">{_esc(t)}</span>'


def normalize(spec, card="", beat=""):
    """Makes any (even missing / half) spec renderable. "card" like 'Sales > Sales Orders' is the fallback."""
    spec = dict(spec or {})
    path = spec.get("path") or [p.strip() for p in str(card or "").replace("→", ">").split(">") if p.strip()]
    if isinstance(path, str):
        path = [p.strip() for p in path.split(">") if p.strip()]
    path = [str(p) for p in path][:4] or ["Home"]
    spec["path"] = path
    spec.setdefault("heading", path[-1])
    v = str(spec.get("view") or "").lower()
    if v not in ("list", "form", "settings"):
        v = "list" if spec.get("rows") else "settings" if spec.get("toggles") else "form" if spec.get("fields") else \
            ("settings" if path[0].lower() in ("settings", "preferences") else "list")
    spec["view"] = v
    spec.setdefault("click", "")
    spec.setdefault("tip", "")
    spec["beat"] = beat
    return spec


def _module_of(path):
    names = [m for m, _ in MODULES]
    for p in path:
        for n in names:
            if p.lower() == n.lower():
                return n
    for p in path:
        for mod, subs in SUB.items():
            if any(p.lower() == s.lower() for s in subs):
                return mod
    return "Settings" if any("setting" in p.lower() or "preference" in p.lower() for p in path) else "Home"


def build_html(spec):
    path, click = spec["path"], spec.get("click") or ""
    mod = _module_of(path)
    side = []
    for name, icon in MODULES:
        side.append(f'<div class="m {"on" if name == mod else ""}"><span>{icon}</span>{_esc(name)}</div>')
        if name == mod:
            subs = list(SUB.get(mod, []))
            here = next((p for p in path if p.lower() not in (mod.lower(),)), None)
            if here and not any(here.lower() == s.lower() for s in subs) and len(path) > 1:
                subs = subs[:4] + [here]
            for s in subs[:6]:
                on = here and s.lower() == here.lower()
                tgt = 'data-target=1' if click and s.lower() == click.lower() else ""
                side.append(f'<div class="s {"on" if on else ""}" {tgt}>{_esc(s)}</div>')

    v = spec["view"]
    body = ""
    if v == "list":
        cols = spec.get("columns") or ["Date", "Number", "Customer", "Amount", "Status"]
        rows = spec.get("rows") or [["10 Oct 2026", "SO-00012", "Sharma Traders", "₹12,500", "Paid"],
                                     ["09 Oct 2026", "SO-00011", "Gupta & Sons", "₹8,200", "Draft"],
                                     ["08 Oct 2026", "SO-00010", "Mehta Foods", "₹21,000", "Open"]]
        th = "".join(f"<th>{_esc(c)}</th>" for c in cols[:5])
        trs = []
        for r in rows[:5]:
            cells = list(r)[:len(cols[:5])]
            tds = []
            for j, c in enumerate(cells):
                col = str(cols[j]).lower() if j < len(cols) else ""
                txt = _pill(c) if "status" in col else _esc(c)
                tgt = 'data-target=1' if click and str(c).lower() == click.lower() else ""
                tds.append(f"<td {tgt}>{txt}</td>")
            trs.append("<tr>" + "".join(tds) + "</tr>")
        body = f'<div class="card"><table><tr>{th}</tr>{"".join(trs)}</table></div>'
    elif v == "form":
        fs = spec.get("fields") or [["Customer Name", "Sharma Traders"], ["Date", "10 Oct 2026"]]
        items = []
        for f in fs[:6]:
            lab, val = (list(f) + [""])[:2] if isinstance(f, (list, tuple)) else (f.get("label"), f.get("value"))
            tgt = 'data-target=1' if click and str(lab).lower() == click.lower() else ""
            items.append(f'<div class="field" {tgt}><label>{_esc(lab)}</label><div class="inp">{_esc(val) or "&nbsp;"}</div></div>')
        body = f'<div class="card">{"".join(items)}</div>'
    else:
        ts = spec.get("toggles") or [["Enable this option", True]]
        items = []
        for t in ts[:6]:
            lab, on = (list(t) + [True])[:2] if isinstance(t, (list, tuple)) else (t.get("label"), t.get("on", True))
            tgt = 'data-target=1' if click and str(lab).lower() == click.lower() else ""
            items.append(f'<div class="tog" {tgt}><span>{_esc(lab)}</span><span class="sw {"on" if on else ""}"></span></div>')
        body = f'<div class="card">{"".join(items)}</div>'

    acts = []
    primary_label = click if click else ("Save" if v != "list" else "+ New")
    in_body = click and ("data-target=1" in body or "data-target=1" in "".join(side))
    if v == "list":
        btns = ["+ New"] if in_body or click == "+ New" else [primary_label, "+ New"] if click else ["+ New"]
    else:
        btns = ["Save", "Cancel"] if in_body or not click else [click, "Cancel"]
    for k, b in enumerate(dict.fromkeys(btns)):
        tgt = 'data-target=1' if click and b.lower() == click.lower() and not in_body else ""
        acts.append(f'<span class="btn {"primary" if k == 0 else ""}" {tgt}>{_esc(b)}</span>')
    top_btn = acts[0] if v == "list" else ""
    bottom = "" if v == "list" else f'<div class="actions">{"".join(acts)}</div>'
    tip = f'<div class="tip">Tip: {_esc(spec["tip"])}</div>' if spec.get("tip") else ""
    crumb = " › ".join(_esc(p) for p in path)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS % {'W': W, 'H': H}}</style></head>
<body><div class="top"><div class="logo">Zoho <b>Books</b></div><div class="search">Search in {_esc(spec['heading'])}</div>
<div class="org">My Business ▾</div></div>
<div class="main"><div class="side">{''.join(side)}</div>
<div class="content"><div class="crumb">{crumb}</div><div class="head"><h1>{_esc(spec['heading'])}</h1>{top_btn}</div>
{body}{bottom}{tip}</div></div><div class="illu">illustration</div></body></html>"""


CURSOR = ('<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M3 2l7.5 19 2.6-7.6L21 11z" '
          'fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>')

JS_HL = """() => {
  let el = document.querySelector('[data-target]');
  if (!el) el = document.querySelector('.btn.primary') || document.querySelector('h1');
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
        b = p.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        for i, spec in enumerate(specs):
            pg.set_content(build_html(spec), wait_until="load")
            plain, hl = outdir / f"screen{i:02d}_a.png", outdir / f"screen{i:02d}_b.png"
            pg.screenshot(path=str(plain))
            box = pg.evaluate(JS_HL)
            pg.screenshot(path=str(hl))
            res.append({"plain": plain, "hl": hl, "box": box})
        b.close()
    return res
