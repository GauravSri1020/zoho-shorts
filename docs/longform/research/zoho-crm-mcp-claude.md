# Research: Zoho CRM MCP servers + Claude Desktop - verified 17 Nov 2026 (Claude, live chat run)

Rule: every number / date / menu label in the script is in this table. Anything else is NOT in the script.

| # | Fact | Value | Source | Type |
|---|---|---|---|---|
| 1 | Built-in MCP | Zoho CRM provides built-in MCP support; pre-built servers, nothing to build, host or maintain | https://www.zoho.com/crm/developer/docs/mcp/overview.html | Zoho |
| 2 | Four servers | Data Insights, Data Operations, Module Customization, Workflow & Process Automation | same + https://help.zoho.com/portal/en/community/topic/zoho-crm-with-built-in-mcp-support | Zoho |
| 3 | Data Insights | read-only: query records (COQL), module list, field schemas; search records, monitor pipelines | same | Zoho |
| 4 | Data Operations | create, read, update, delete records, bulk operations, lead conversion, duplicate detection | same | Zoho |
| 5 | Module Customization | custom modules, fields, page layouts, global picklists | same | Zoho |
| 6 | Workflow & Process Automation | create, update, list workflow rules and task actions, reorder rules | overview | Zoho |
| 7 | Clients | Cursor, Claude Desktop, VS Code, Windsurf + any MCP tool; Zoho has a setup guide per client | overview | Zoho |
| 8 | Auth | first use starts an OAuth flow in the browser (Zoho sign-in) | overview | Zoho |
| 9 | Permissions | actions limited to the user's CRM role permissions; cannot exceed them; HTTPS | overview + FAQ https://www.zoho.com/crm/developer/docs/mcp/faqs.html | Zoho |
| 10 | API credits | MCP calls consume API credits like standard API calls, same limits | overview | Zoho |
| 11 | Multiple servers | install as many as needed; the agent picks the server by the action described | FAQ | Zoho |
| 12 | Switch org | disconnect the server in the AI tool, re-authenticate | FAQ | Zoho |
| 13 | Deleted records | go to the recycle bin, restorable before permanent removal; "Always review prompts carefully" | FAQ | Zoho |
| 14 | Rollout | rolling out in phases, all data centres "soon" | community post | Zoho |
| 15 | Claude Desktop steps | Customize > Connector; Add icon > Add Custom Connector; name + paste URL in Remote MCP Server URL; Add; select server > Connect to authenticate | https://www.zoho.com/crm/developer/docs/mcp/setup/claude.html | Zoho |
| 16 | CRM screen path | Setup > Developer Hub > MCP for AI Agents; Install menu VS Code / Cursor / Other IDEs; link icon copies server link | real screenshot crm/mcp_for_ai_agents (Gaurav's org) | screen |
| 17 | CRM sidebar | "MCP Server" item in the CRM left menu, cards Data Insights / Data Operations with Install + View Detail | real screenshots crm/leads_list, crm/mcp_server | screen |
| 18 | API credit dashboard | Setup > Developer Hub > APIs and SDKs, Dashboard tab = API credit usage | real screenshot crm/api_names | screen |
| 19 | Zoho's claimed benefits | faster configuration through conversation, smaller learning curve, no API handling | community post | Zoho |
| 20 | MCP origin | Anthropic released MCP 25 Nov 2024 as an open standard for connecting AI assistants to systems where data lives | https://www.anthropic.com/news/model-context-protocol ; InfoWorld 26 Nov 2024 | official + secondary |
| 21 | Zoho Campaigns MCP | rebuilt Campaigns supports MCP for compatible AI agents, user reviews/approves (13 Nov 2026) | Zoho press release via Malay Mail; allAfrica (see s20261115-zoho-campaigns-mcp) | Zoho |
| 22 | Zoho Desk Blended Agents | launched 16 Nov 2026, AI agents hand hard cases to humans | Business Wire via Yahoo Finance; ANI/The Tribune | Zoho + secondary |

## Example prompts (chapter 4)
Written by us as illustrations of documented capabilities (query records, convert leads, duplicate detection,
picklist fields, workflow rules, create records). The video says "things you could ask"; the description says results
depend on data, permissions and rollout.

## Not verified -> NOT used
- Which Zoho CRM editions / plans include MCP (not stated in Zoho's docs).
- Whether admin rights are needed to install (not stated).
- The "five servers" mention in the community post (it lists only four) -> we say four, as the developer docs do.
- The server URLs printed in the Claude guide (they are org-specific, India DC) -> not shown; we say "copy the server link".
- "Windsurf (now Devin Desktop)" rename (single secondary blog) -> not used.
