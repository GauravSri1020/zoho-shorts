# 17 Nov 2026 (raat) - brain token missing, queue haath se bhari

## Gaurav ne kya maanga
- Repo ki summary; phir "aage ki videos bana ke aage karo"; "ye khaali kyun hai, brain agent chala ki nahi check karo".

## Kya mila
- daily-robot ke runs green the, par brain job har baar skip: secret CLAUDE_CODE_OAUTH_TOKEN nahi hai (issue #177).
  Queue 0 -> keeper ke paas kuch nahi -> 16 Nov 21:30 IST ke baad channel pe kuch scheduled nahi tha.

## Kya kiya
- Backups: backup-2026-11-17-before-queue-refill (main), backup-2026-11-17-long-videos-before-queue-refill.
- 6 Shorts likhe, local render + QA + contact sheet, push -> shorts-daily #5 ne sab schedule kiye:
  18 Nov 07:30 Autoscan (Ga4U_UkddJ8), 13:30 UAE tax group (29xVMeskuog), 21:30 Purchase Approval (UJ4w_U0ZFDE);
  19 Nov 07:30 Recurring Invoices (OR2dny795eU), 13:30 Zoho Desk Blended Agents (n0N5Z1lMJxc), 21:30 CRM MCP (8ZF5N60ChjI).
- Long video zoho-crm-mcp-claude (7.3 min) -> longform-daily #3, publish 18 Nov 18:30 IST (render 1-2 h).
- Fix: longform/vshort.py ab Shorts captions pe caption_fix lagata hai.

## Faisle
- Sab 6 Shorts seedha docs/longform/shorts/ mein (queue nahi), kyunki 0 scheduled the.
- Long video topic: Zoho CRM MCP + Claude (evergreen, 3 real CRM screens).

## Open
1. Gaurav: CLAUDE_CODE_OAUTH_TOKEN secret daalo (claude setup-token). Iske bina brain kabhi nahi chalega.
2. longform-daily #3 ka result: docs/longform/uploaded/zoho-crm-mcp-claude.json (ya failed/).
3. Queue khaali: docs/longform/queue/shorts (>= 6) + queue/long (>= 3) bharni hai. 20 Nov se aage kuch scheduled nahi.
4. Gemini robot duplicates: #185 (Desk Blended Agents) aur #184 (Hotelogix, 12 Nov ko already gaya) - skip karna hai ya nahi.

## Agla step (exact)
Token check (daily-robot run ke brain job ka log). Na ho to agli chat: longform-daily #3 result dekho, phir queue bharo
(ideas: Zoho Books Oct 2026 updates, Zoho MCP for Bigin, UAE e-invoicing fines, Zoho partner tiers, Zoho Analytics
trusted BI layer long video, ZATCA follow-up).
