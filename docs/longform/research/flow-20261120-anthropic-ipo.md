# Research: Anthropic IPO - Nasdaq debut 19 Nov 2026 (checked 20 Nov 2026 ~11:00 IST)

Why today: biggest business story of the week; carried by CNBC, CNN, NPR, Washington Post, AP/PBS, ABC News (US),
ABC (Australia), Zee Business (>= 3 outlets = trend). Search terms: "anthropic ipo", "anthropic stock", "ANT stock".

## Fact table (only these may be used in the script)
| Fact | Value | Source |
|---|---|---|
| Ticker / exchange | "ANT", Nasdaq Global Select Market | Anthropic (official), PBS/AP, ABC News |
| IPO price | $83.00 per share (range had been $70-$78) | Anthropic (official), PBS/AP, ABC News |
| Shares offered | 980,000,000 Class A (956,351,354 by Anthropic, 23,648,646 by selling holders); greenshoe up to 147,000,000 | Anthropic (official) |
| SEC effective | registration statement declared effective 18 Nov 2026 | Anthropic on X (official) |
| Amount raised | about $81 billion (980M x $83 = $81.34B) | PBS/AP ("Proceeds totaling $81 billion"), ABC Australia ($81.3B) |
| Record | ahead of SpaceX's ~$75 billion (June 2026); ABC AU: "largest fundraiser in stock market history" | PBS/AP, ABC Australia |
| Valuation at IPO price | about $1.5 trillion | PBS/AP, ABC News |
| Debut | first trade 19 Nov 2026; opened at ~$111.50, about 34% above the IPO price | ABC Australia; Zee Business headline ("34% jump on Nasdaq debut") |
| Intraday | market value briefly above US$2 trillion | ABC Australia |
| First-day close | NOT verified (CNN headline: "valued at $1.76 trillion after first day"; CNBC headline: "$1.8 trillion market cap") -> do NOT say a closing number | search headlines only |
| CEO | Dario Amodei rang the Nasdaq opening bell (lower-third only) | ABC Australia |

Not used (single source / unclear): revenue by year from prospectus, losses, insider sales, 20 Nov trading.
Failed to load: CNBC, NPR, CNN, Washington Post, CBC, Zee Business pages (robots / client error).

Note: the channel's tools include Claude (an Anthropic product) - script stays neutral news, "Not investment advice".

## Script plan
Structure `news-impact-action` (fresh 24-h news; last 2 Shorts used teardown-explained + deadline-countdown).
Hook type `news` (yesterday's news Short used `number`).
Titles: (1) "Anthropic IPO: $81 Billion Raised, Biggest Listing Ever #Shorts" (2) "Anthropic Stock (ANT) Debuts: Up 34% on Day One #Shorts"
(3) "Anthropic Goes Public at $1.5 Trillion: What Just Happened #Shorts" -> pick (1): keyword first, record = tension.

## Sources
- https://www.anthropic.com/news/anthropic-prices-initial-public-offering
- https://www.pbs.org/newshour/economy/anthropic-prices-its-ipo-at-83-per-share-valuing-the-ai-giant-at-1-5-trillion
- https://abcnews.com/Business/anthropic-announces-price-83-share-ipo/story?id=138245320
- https://abc.net.au/news/2026-11-20/asx-markets-business-live-news-nov-20/107403768
- https://www.zeebiz.com/markets/global-markets/news-anthropic-ipo-record-fundraise-34-jump-on-nasdaq-debut-how-it-happened-10-things-to-know-405797 (headline only)
