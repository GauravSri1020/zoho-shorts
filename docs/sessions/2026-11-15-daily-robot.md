# 15 Nov 2026 (night) - daily robot (Shorts + long videos without Flow / laptop / Claude chat)

## What Gaurav asked
- Thumbnail + keywords on long video -JyVV7LA4pA -> DONE (workflow longform-fix).
- Everything automatic: 2 Shorts + 1 long video daily, researched, uploaded, scheduled; >= 2 days (better a week) buffer;
  fresh news first; topics: Zoho ecosystem news x trends (AI, Claude, MCP, licensing, partners) > tax/compliance updates
  (UAE, ZATCA, India, EU) > Zoho tutorials > general trending news LAST. "Jhatka" = ZATCA (next long video).
- NO Claude scheduler / artifacts / chat history: it must run on GitHub. Flow only when he opens the laptop (scripts ready).

## What was built (branch long-videos, + one new file on main)
- longform/scenes/generic.js: generic scene kinds (hook2, story, stat, headline, dates, flow2, celebrate2) + props.
- longform/validate.py (strict script check), longform/thumb.py + thumb/template.html (generic thumbnail),
  longform/vshort.py (9:16 Shorts from the same engine, no Flow/Gemini), qa.py --short, keeper.py (queue -> production).
- Workflows on long-videos: shorts-daily, longform-daily (validate -> voice -> render -> QA -> meta -> thumb -> 4K ->
  upload -> result files), longform-fix. On main: .github/workflows/daily-robot.yml = cron brain 05:17 IST (Claude Code
  action, needs secret CLAUDE_CODE_OAUTH_TOKEN) + keeper 05:53 / 15:07 IST (no AI).
- docs/longform/DAILY.md = the brain's full instructions (priorities, fact rules, formats, buffer, report issue).

## Content made tonight
- Short s20261115-uae-pdf -> ac2VsB7cqqU, public 15 Nov 07:30 IST.
- Short s20261115-zoho-campaigns-mcp (news, 13:30 slot), queue Shorts books-payment-reminders + zatca-wave25 (moved by
  keeper -> 21:30 / next 07:30). Check docs/longform/shorts-uploaded/.
- Long zatca-phase2-zoho-books (7.1 min, publish 15 Nov 18:30 IST) - longform-daily run 43634326603 was rendering.
  If docs/longform/failed/zatca-phase2-zoho-books.json appears: read the log, fix, re-dispatch.
- UAE test run failed QA only because the UAE script is now 5.9 min (< 7 min rule) - expected, nothing uploaded.

## Open items / exact next step
1. Gaurav: add repo secret CLAUDE_CODE_OAUTH_TOKEN (`claude setup-token` on his laptop -> GitHub Settings -> Secrets
   -> Actions). Without it only the keeper runs (publishes from the queue) - the queue is almost empty.
2. Next chat: check ZATCA long video result + the 3 Shorts; fill docs/longform/queue (>= 6 Shorts, >= 3 long) - ideas:
   Zoho Books October 2026 updates (Netting, line-item subtotals, public PO link), Zoho CRM built-in MCP,
   Zoho MCP for Bigin, Zoho Campaigns long video, UAE e-invoicing fines, Zoho partner tiers.
3. Gemini Shorts robot on main still runs at 07:17 (may add its own Shorts; slots are shared via YouTube schedule).
