# Research: Zoho Books automation - recurring invoices, payment reminders, workflow rules (checked 20 Nov 2026)

Why: evergreen how-to with real screens we already have (books/*); Gulf + India SMB search terms
("zoho books recurring invoice", "zoho books payment reminder", "zoho books workflow rules"). Not in topics-used (30 days).
Structure `before-after-demo`, hook `result-first` (last 4 long: deadline-countdown, step-by-step x2, news-impact-action).

| Fact | Value | Source | Type |
|---|---|---|---|
| Recurring invoice = recurring profile | profile contains all invoices generated / to be generated | Zoho Books help - Create & Send Recurring Invoices | official |
| Create | Sales > Recurring Invoices > + New; Customer Name, Profile Name, Repeat Every; customer notes, T&C; Save | same + KB "How do I create a recurring invoice?" | official |
| Child invoices | saved as Draft or sent to customers right away | Zoho Books help (ri-createsend) | official |
| Back-dated profile | child invoices generated only after the current date | Zoho Books help (ri-createsend) | official |
| Shortcuts | Invoices list "New Recurring Invoice"; invoice form "Make Recurring" | our real screens books/invoices_list, books/invoice_new | screen |
| Reminders location | Settings > Reminders (Reminders & Notifications) > Invoices tab | Zoho Books help - Reminders | official |
| Manual reminders | Reminder for Overdue Invoices / Sent Invoices; edit + Insert Placeholders; send: invoice > Reminders > Send Now | Zoho Books help - Reminders, KB manual-rem-invoice | official |
| Automated reminders | 3 by default; before or after due date; toggle; From address; Enable this reminder; Save | Zoho Books help - Reminders, KB rem-addnew | official |
| More reminders | add new reminders; customer and own users (KB: up to 30) | KB rem-addnew, KB invoice-reminders | official |
| Expected payment date | reminders based on expected payment date | Zoho Books help - Reminders | official |
| Stop | invoice > Reminders > Stop Reminders | Zoho Books help - Reminders | official |
| Workflow rules | Settings > Workflow Rules (Automation) > + New Workflow Rule; Name, Description, Module; Next | Zoho Books help - Workflow Rules | official |
| Triggers | Event based: Created, Edited, Created or Edited, Deleted, Submitted, Approved, Rejected; Date based: days before/after a date field, execution time, cycle Once/Daily/Weekly/Monthly/Yearly | same | official |
| Criteria / actions | up to 10 criteria; immediate or time-based actions; email alerts, field updates, webhooks, functions | same | official |
| Example | thank-you email after a customer payment (Zoho's own scenario) | same | official |
| Usage + logs | daily counts of functions / webhooks / email alerts; View Logs | same | official |

Not verified -> not used: hours saved, % faster payment, plan limits per edition.

Sources
- https://www.zoho.com/books/help/recurring-invoice/ri-createsend.html
- https://www.zoho.com/books/kb/invoices/new-rec-inv.html
- https://www.zoho.com/books/help/settings/reminders.html
- https://www.zoho.com/en-fr/books/kb/reminders/rem-addnew.html
- https://www.zoho.com/en-ng/books/help/settings/automation/workflow-rules.html
