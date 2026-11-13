# RECORDING TODO - UAE E-Invoicing in Zoho Books (sample video 1)

What Gaurav opens, so Claude can screen-record the real steps later (his Chrome, "Share this tab" click is his).
Rules: Zoho **demo / trial org with sample data only** (no real customers, no real TRN, no keys). Claude never logs in or types passwords.
Org must be a **UAE** organisation (VAT / e-invoicing menus only exist there) - the current screenshots are from the India org "Helios"
(GST menus, "Delivery Challans") and are only placeholders.

Menu paths below come from a setup guide that cites Zoho's help page https://www.zoho.com/ae/books/help/e-invoicing/ (Zoho's page itself
could not be opened by the night run). **First job when recording: confirm every label on screen; anything different -> fix the
script line before upload** (CLAUDE.md rule 3).

| # | Fills scene | Open / do (in the demo UAE org) | Record | Placeholder now |
|---|---|---|---|---|
| R1 | s13 (0:00-0:25 of chapter 4) | Gear icon (Settings) -> **Taxes & Compliance -> E-Invoicing** | Click gear, scroll to Taxes & Compliance, open E-Invoicing; pause 3 s on the page showing business name, TIN, TRN, address, FTA email fields | books/invoices_list + books/settings_home (India org) + checklist overlay |
| R2 | s14 | Same E-Invoicing page: the step that links to **EmaraTax** + the **"Verify & Complete Setup"** button | Only the Zoho side (we never open EmaraTax / never log in). Hover the button, do not click if it would change a real setup | whiteboard flow |
| R3 | s16 | **Sales -> Customers -> (sample customer) -> Edit -> Other Details** tab | Show fields TIN Number, Buyer ID, Legal Name, Electronic Address, PEPPOL Status (type sample values: TIN 1001234567, "Sample Trading LLC") | illustrated record card |
| R4 | s16 | **Items -> (sample item) -> Edit** | Goods / Service choice and Unit field | illustrated item card |
| R5 | s17 | **Sales -> Invoices -> + New** | Pick sample customer, add 1 item, show tax treatment, scroll to Save / Send buttons (do NOT send to a real Peppol ID) | books/invoices_list + overlays |
| R6 | s18 | An existing invoice in the demo org | E-invoice status label (Yet To Be Pushed / Push Initiated / Pushed + UUID / Failed) - whatever the demo org shows | status diagram overlay |
| R7 | s19 | **Purchases -> Bills** | List view; if any received e-invoice drafts exist show one | books/bills_list + inbox overlay |
| R8 | optional | **Sales -> Credit Notes -> + New** | for the "corrections go through a credit note" line | none |

After recording: save clips to `assets/recordings/books-uae/R<n>.mp4` (1080p or higher, 30 fps), then the PODCAST scenes use the
recording instead of the animated screenshot (todo in longform/scenes: `video` source for PODCAST).
