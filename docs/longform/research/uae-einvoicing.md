# Research: UAE E-Invoicing in Zoho Books (verified 13 Nov 2026, scheduled run)

Rule: every number in the script must be in this table. "official" = MoF / FTA / decision text; "Zoho" = Zoho's own page;
"secondary" = adviser / news (used only where noted). Anything not verified is listed at the bottom and NOT used in the script.

## IMPORTANT changes vs. HISTORY (12 Nov)
- Large-business (revenue >= AED 50M) ASP deadline is now **30 Oct 2026** (Ministerial Decision 66/2026; was 31 Jul 2026). Go-live still **1 Jan 2027**.
- Penalties: **Cabinet Decision 173 of 2026** replaced Cabinet Decision 106/2025 (MoF announcement 30 Oct 2026). New caps.
- The "report a system failure within 2 days" rule was repealed (MD 197/2026) - do not mention it.

## Facts used in the script

| # | Fact | Value | Source | Type |
|---|---|---|---|---|
| 1 | Legal base | MD 243/2025 (system) + MD 244/2025 (timeline); amended by MD 66/2026, MD 197/2026 | https://mof.gov.ae/en/about-us/initiatives/einvoicing/ (updated 12 Nov 2026) | official |
| 2 | Pilot / voluntary | From 1 Jul 2026 (pilot for volunteers; voluntary adoption open, no penalties before your mandatory date) | MoF Guidelines v2.0 (26 Oct 2026) https://mof.gov.ae/wp-content/uploads/2026/10/UAE-Electronic-Invoicing-Guidelines_En.pdf ; https://mof.gov.ae/en/news/ministry-of-finance-announces-pilot-phase-of-the-electronic-invoicing-system/ | official |
| 3 | Revenue >= AED 50M | Appoint ASP by **30 Oct 2026**, go live **1 Jan 2027** | MD 66/2026 https://mof.gov.ae/wp-content/uploads/2026/05/Ministerial-Resolution-No.-66-of-2026-Amending-Certain-Provisions-of-Ministerial-Resolution-No.-244-of-2025-Regarding-the-Implementation-of-the-Electronic-Invoicing-System-En-20260514.pdf ; FTA news 25 Oct 2026 https://tax.gov.ae/en/media.centre/news/federal.tax.authority.calls.on.persons.subject.to.einvoicing.to.comply.wit.the.prescribed.legal.deadlines.and.avoid.administrative.penalties.aspx | official (Guidelines table says 31 Oct - decision text + FTA say 30 Oct, we use 30 Oct) |
| 4 | Revenue < AED 50M | Appoint ASP by **31 Mar 2027**, go live **1 Jul 2027** | FTA news 25 Oct 2026; Guidelines v2.0 | official |
| 5 | Government entities | ASP by 31 Mar 2027, go live **1 Oct 2027** | Guidelines v2.0 | official |
| 6 | Model | DCTCE 5-corner: C1 supplier -> C2 supplier's ASP (validates, delivers, reports to FTA) -> C3 buyer's ASP -> C4 buyer; C5 = FTA | MoF e-invoicing page; Guidelines v2.0 | official |
| 7 | Standard | Peppol, PINT AE; "near real-time" exchange (no seconds/hours rule stated) | Guidelines v2.0 | official |
| 8 | Peppol ID | "0235" + 10-digit TIN; TIN = first 10 digits of the 15-digit TRN | Guidelines v2.0; Zoho Academy (17 Sep 2026) https://www.zoho.com/ae/books/academy/taxes-and-compliance/uae-einvoicing-readiness-implementation-guide.html | official + Zoho |
| 9 | Issue deadline | e-invoice / e-credit note issued + transmitted within **14 business days** (in force 1 Oct 2026) | MD 197/2026 https://mof.gov.ae/wp-content/uploads/2026/10/Ministerial-Decision-No.-197-of-2026-%E2%80%93-Amending-Certain-Provisions-of-Ministerial-Decision-No.-243-of-2025-on-the-Electronic-Invoicing-System_En.pdf | official |
| 10 | Scope | In: B2B, B2G (also G2B, G2G). Out: B2C (+ some exclusions: airline tickets, certain financial services, VAT group internal supplies for 24 months) | Guidelines v2.0; MD 197/2026 | official |
| 11 | PDF is not an e-invoice | "PDFs, Word documents, images, scans, and emails are not eInvoices" | MoF e-invoicing page | official |
| 12 | E-credit notes | Go through the same system | Guidelines v2.0 | official |
| 13 | Penalty: no ASP / no system | AED 5,000 per month (FTA); under CD 173/2026 capped at AED 50,000 per 12 months | FTA news 25 Oct 2026 (official, 5,000/month); cap: Sovos https://sovos.com/regulatory-updates/global-vat/uae-issues-new-e-invoicing-penalties-under-cabinet-decision-no-173-of-2026/ + Crowe https://www.crowe.com/ae/news/new-violations-and-administrative-penalties | official + 2 secondary |
| 14 | Penalty: e-invoice not issued / sent | AED 100 per invoice, max AED 5,000 per month (same for e-credit notes) | Sovos + Crowe (CD 173/2026 summaries); MoF announcement https://mof.gov.ae/en/news/ministry-of-finance-announces-the-issuance-of-cabinet-resolution-on-administrative-fines-related-to-electronic-invoicing-system/ | secondary x2 - official PDF could not be fetched; RE-CHECK before upload |
| 15 | Zoho = accredited ASP | "Zoho Software Trading LLC" on MoF list of accredited providers | https://mof.gov.ae/en/about-us/initiatives/einvoicing/pre-approved-einvoicing-service-providers/ (updated 13 Nov 2026) | official |
| 16 | Zoho Books features | PINT-AE, UUID, send/receive over Peppol, e-credit notes; you select Zoho Software Trading LLC in EmaraTax | https://www.zoho.com/ae/books/e-invoicing/ | Zoho |

## Zoho Books steps (for script + RECORDING_TODO)
Source: SAIF Audit setup guide 28 Sep 2026 (cites Zoho help https://www.zoho.com/ae/books/help/e-invoicing/) https://www.saifaudit.com/blog/2026/09/28/zoho-books-uae-e-invoicing-setup/ + Zoho product page above.
Zoho's own help page could not be fetched by the scheduled run -> **every menu label must be confirmed on screen in the demo org before upload** (CLAUDE.md rule 3).
1. Settings > Taxes & Compliance > E-Invoicing: check business name, TIN, TRN, address; FTA-registered email.
2. EmaraTax > E-Invoicing service > select ASP "Zoho Software Trading LLC" > submit declaration.
3. Zoho Books: "Verify & Complete Setup" -> connection active.
4. Customers: Other Details tab - TIN, Buyer ID, Legal Name, Electronic Address, PEPPOL Status.
5. Items: Goods/Service, unit / unit code.
6. Sales > Invoices > + New > ... > Send -> pushed over Peppol.
7. E-invoice status on invoice: Yet To Be Pushed -> Push Initiated -> Pushed (UUID) / Failed.
8. Purchases > Bills: e-invoices received from suppliers arrive as drafts.
9. Corrections after push: credit note (menu steps not verified).

## Not verified -> NOT in the script
- Exact CD 173/2026 text from the official PDF (amounts in #13/#14 come from two advisers; FTA confirms 5,000/month).
- How "annual revenue" for the AED 50M line is measured.
- E-credit-note screens in Zoho Books; E-invoice report path.
- Any "seconds / hours" real-time reporting limit.
