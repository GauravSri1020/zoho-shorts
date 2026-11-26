# Research: Zoho Books Credit Notes (evergreen how-to) - checked 26 Nov 2026
Sources are Zoho's own help pages (WebFetch, opened 26 Nov 2026). Anything not in this table is NOT used.

| # | Fact | Value | Source | Type |
|---|---|---|---|---|
| 1 | Create a credit note | Sales > Credit Notes > + New (top right). Fields: Customer Name, Invoice# (optional; only invoices in Sent status of that customer), Credit Note# (auto from default series, or manual via gear icon), Credit Note Date. Enter items, then Save as Draft or Save as Open | https://www.zoho.com/us/books/help/credit-note/ | Zoho |
| 2 | Create from an invoice | Sales > Invoices > open invoice > More icon > Create Credit Note; New Credit Note page opens with invoice details filled in; review and save | same | Zoho |
| 3 | Unpaid invoice + returned goods | Invoices > open invoice > More > Create Credit Note > enter the exact returned quantity under Item Details > create. Stock goes back to inventory; invoice becomes Paid or Partially Paid depending on value returned; credit note status becomes Closed | https://www.zoho.com/us/books/kb/credits/issue-refund.html | Zoho |
| 4 | Paid invoice + returned goods | Create the credit note as in #3, then Sales > Credit Notes > select it > More > Refund > enter refund amount and select the cash or bank account to refund from > Save | same | Zoho |
| 5 | Apply from Credit Note page | Sales > Credit Notes > select the note > Apply to Invoice (top) > popup lists credit notes of same customer across all locations > enter Credits to Apply per invoice > Save | https://www.zoho.com/us/books/help/credit-note/apply-credits.html | Zoho |
| 6 | Apply from Invoice page | Sales > Invoices > select invoice > arrow next to Credits Available > enter Credits to Apply > Apply Credits. Credits Available shows only when the customer has an outstanding invoice and an open credit note | same | Zoho |
| 7 | Statuses | Credits left after applying: note stays Open. All applied: note becomes Closed | same | Zoho |
| 8 | Partial / multiple | A credit note can be applied fully or partially, to one or more outstanding invoices. Only to invoices of the same customer | same | Zoho |
| 9 | See / undo applied credits | Credit Notes > select note > Credit Applied Invoices tab; hover over the invoice > Remove icon; amount becomes available again | same | Zoho |
| 10 | Refund | Sales > Credit Notes > select note > More > Refund > enter amount (full or partial) > Save | https://www.zoho.com/us/books/help/credit-note/refund-credits.html | Zoho |
| 11 | Refund history | Credit Notes > select note > Refund History tab (top right); icons to Edit or Delete a refund | same | Zoho |
| 12 | Import refunds | Credit Notes > More icon (top right) > Import Refunds > Choose File (CSV, TSV, XLS; samples downloadable) > Next > Map Fields > Next > Import | same | Zoho |
| 13 | Vendor Credits | Separate section in the Zoho Books navigation (the page does not explain more) - mention only as "the purchase side has its own Vendor Credits" | credit-note help page | Zoho |

## Not verified -> NOT used
- Refund modes / Paid Through / Refund Date fields, status of a note after a refund, Void status, emailing / PDF of credit notes,
  tax / VAT / GST treatment, e-invoicing credit notes (UAE / ZATCA), any plan limits, currency rules.
- No amounts of money are given by Zoho; examples in the script must be labelled "example", round numbers, no tax.

## Screens (assets/screens/index.yaml)
books/creditnote_new (targets: Customer Name, Credit Note#, Save as Draft, Save as Open), books/invoices_list, books/invoice_new.
Everything else (Apply to Invoice popup, Refund dialog, tabs) = board (flow2 / checklist), never an invented screen.
Screens are a sample India org; show no tax settings.

## Related channel videos (for OUTRO "next")
zoho-books-automation (recurring invoices, payment reminders, workflow rules) - uploaded 21 Nov.

## Script plan
Structure: mistakes-to-avoid (not used by the last 4 longs). Why: a how-to people get wrong (paid vs unpaid, wrong customer, no undo). Hook: mistake (last long was question).
Title: Zoho Books Credit Note: Refund vs Apply to Invoice (5 Mistakes); thumb: CREDIT NOTE / REFUND? / OR APPLY.
