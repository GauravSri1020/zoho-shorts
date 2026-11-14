# Research: ZATCA Phase 2 (Wave 25) in Zoho Books - verified 15 Nov 2026 (Claude, night run)

Rule: every number / date / menu label in the script is in this table. Anything else is NOT in the script.

| # | Fact | Value | Source | Type |
|---|---|---|---|---|
| 1 | Wave 25 announced | 24 July 2026 | ZATCA news https://zatca.gov.sa/en/MediaCenter/News/Pages/Wave25-E-invoicing.aspx | official |
| 2 | Wave 25 who | taxpayers whose revenues subject to VAT exceeded SAR 187,500 during 2022, 2023, 2024 or 2025 | same | official |
| 3 | Wave 25 deadline | integrate "by no later than February 1, 2027" | same | official |
| 4 | Notice | ZATCA informs following waves directly at least six months before their integration date | same | official |
| 5 | Phase 1 start | 4 December 2021 (Generation Phase) | same page ("introduced on December 4, 2021") | official |
| 6 | Wave 24 | taxable turnover above SAR 375,000 in 2022, 2023 or 2024; integrate between 1 Apr and 30 Jun 2026 | EY Tax News https://taxnews.ey.com/news/2025-2023-saudi-arabia-announces-24th-wave-of-phase-2-e-invoicing-integration | secondary (Big-4, cites ZATCA 26 Sep 2025) |
| 7 | Phase 2 start | 1 January 2023, in groups (waves), >= 6 months notice | ZATCA Detailed Guidelines v2 (May 2023) p.6 https://zatca.gov.sa/en/e-invoicing/introduction/guidelines/documents/e-invoicing_detailed__guideline.pdf ; Zoho Academy (wave 1 = 1 Jan 2023) | official |
| 8 | Clearance | standard tax invoices "must be cleared by the Authority as a prerequisite for sharing them with the buyers" | Guidelines p.31 | official |
| 9 | Reporting | simplified tax invoices transmitted to FATOORA "within (24) hours from its issuance" | Guidelines p.12 | official |
| 10 | Scanned paper | a paper invoice converted to electronic format by copying / scanning is NOT an electronic invoice | Guidelines p.8 | official |
| 11 | Cryptographic stamp / CSID | stamp verifies origin + integrity; CSID = unique identifier linking the e-invoice solution unit | Guidelines p.10 | official |
| 12 | QR | Phase 2 QR code with 9 tags (simplified invoices) | Guidelines p.18 | official |
| 13 | OTP | Fatoora portal > Onboard New Solution Unit/Device > number of devices (Zoho Books only: 1) > OTP valid one hour | Zoho Books help https://www.zoho.com/sa/books/help/e-invoicing/phase-2.html | Zoho |
| 14 | CSID in Zoho | enter OTP in Zoho Books within one hour to generate CSID; check in Fatoora "View List Of Solutions and Devices" | same | Zoho |
| 15 | Renew | Fatoora "Renew Existing Cryptographic Stamp Identifier"; Zoho Books Settings > Taxes & Compliance > e-Invoicing > Renew CSID | same | Zoho |
| 16 | Permission | Settings > Roles > e-Invoicing section > Push Transactions | same | Zoho |
| 17 | Mandatory fields | Org: building number, street, additional number, district, city, state, postal code. Customer: billing address in Arabic etc. Invoice: item name + customer name in Arabic. B2B standard: customer's National ID + full address | same | Zoho |
| 18 | Push | Sales > Invoices > select invoice > Push to Fatoora; standard pushed before sending; simplified within 24 h of sending; failed -> fix + retry | same | Zoho |
| 19 | Statuses | Yet-to-be Pushed, Push Initiated, Pushed, Failed | same | Zoho |
| 20 | Recurring | preference "Create, Push, and Send Invoices" | same | Zoho |
| 21 | Zoho Books + Fatoora | Zoho says Zoho Books integrates with the Fatoora portal | Zoho Academy https://www.zoho.com/sa/books/academy/taxes-and-compliance/zatca-e-invoicing-phase-2.html | Zoho |

## Not verified -> NOT used
- Penalty amounts for Phase 2 (no official page read tonight).
- "Approved by ZATCA" wording for any software (ZATCA does not certify vendors in the sources read).
- Exact Zoho Books screen where the OTP is typed (help page gives no path) -> shown as steps, not a screen.
- Real-screen note: the Books screens are from the sample India org; only the generic menus (Settings gear, Taxes, Invoices) are shown.
