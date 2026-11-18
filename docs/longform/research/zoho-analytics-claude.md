# Research: Zoho Analytics 7.0 (Ask Zia agents) + Claude connector - verified 18 Nov 2026 (daily robot)

| # | Fact | Value | Source | Type |
|---|---|---|---|---|
| 1 | Announcement | Zoho Analytics evolves into an agentic analytics platform, announced 10 Nov 2026 (Singapore dateline, Media OutReach) | https://vir.com.vn/zoho-upgrades-analytics-platform-with-agentic-artificial-intelligence-capabilities-164929.html ; Malay Mail/AsiaNews carry the same release (could not open, 403) | Zoho press release, republished |
| 2 | Release name | "Zoho Analytics 7.0 (Release 2026)", rolling out gradually | https://www.zoho.com/analytics/whats-new.html | Zoho |
| 3 | Ask Zia | super agent routing to six specialist agents: Data Analysis, Visualization, Data Prep, Formula, SQL, Coding (press release lists data modeling instead of formula -> script names the what's-new list and says "six") | whats-new page ; press release | Zoho |
| 4 | Coordination | central agent plans/coordinates sub-agents; shared semantic layer, ontology and conversation context; keeps history and memory | press release | Zoho |
| 5 | Model | Zia's own LLM or bring your own frontier model | press release | Zoho |
| 6 | Semantic layer / ontology | business glossary (descriptions, synonyms, instructions, metrics), no-code editing; ontology models entities and relations; Apache Ossie compatible | press release | Zoho |
| 7 | Custom agents | built on own data; support MCP servers, web search; gallery of pre-built agents (whats-new); trigger actions/workflows, workflow builder | press release + whats-new | Zoho |
| 8 | Embed | agents embeddable in own apps/portals with white labeling; permissions apply | press release | Zoho |
| 9 | Connectors | 30+ new, 500+ existing; new Zoho: ERP, Spend, FSM, Shifts, Voice; others SAP, PayPal, Adobe Commerce, Twilio, Notion, Intercom, Supabase, DocumentDB, AlloyDB | press release | Zoho |
| 10 | Governance | Data Catalog (lineage), AI Observability (who ran, accessed, answered; usage and cost by team), sandbox/publish/rollback | press release | Zoho |
| 11 | 50+ new capabilities | 10+ visualizations, custom visuals, pixel-perfect reports, scenario analysis, correlation matrix, VARX, data science studio (Jupyter), Ask Zia mobile | press release | Zoho |
| 12 | Pricing | unchanged; Zoho LLM credits included in each plan. Price figure NOT used (not checked on Zoho pricing page) | press release | Zoho |
| 13 | Availability | cloud now; previews (pixel-perfect reporting, ontology, semantic model) globally in 4-8 weeks; on-premise Q1 2027 | press release; whats-new (on-prem Q1 2027) | Zoho |
| 14 | Roadmap | dynamic business context, decision intelligence, openness, unified data platform; no dates | press release | Zoho |
| 15 | MCP server | remote (Zoho-managed or self-hosted) and local (Docker, Claude Connector, NPM); consumes API units; data aggregated for a request is shared with the LLM; project in development, tools may change; CLI exists | https://www.zoho.com/analytics/api/v2/zoho-analytics-mcp-server.html ; whats-new | Zoho |
| 16 | Claude connector | Claude Desktop app (not web), macOS + Windows only; Settings > Integrations > Add Integration / Claude Marketplace > Zoho Analytics MCP Server > Add to Claude > enter credentials > Install; verify active in Settings > Integrations | https://www.zoho.com/analytics/api/v2/zoho-analytics-mcp-server/local-mcp/claude-connector.html | Zoho |
| 17 | Credentials | client ID, secret, refresh token, org ID, Accounts server URL, Analytics server URL by data centre (US, EU, IN, AU, JP, CA); made via Developer Console > Self Client > Analytics scope > refresh token | same | Zoho |
| 18 | Claude CLI plug-in | "Zoho Analytics Plugin" for the Claude CLI | whats-new | Zoho |

Not verified -> not used: Basic plan price (US$24/month, press release only), "100,000 businesses" claim, list of MCP tools by category, whether MCP can delete rows, exact Analytics menu paths (no Analytics screens in assets, so only boards are used).
