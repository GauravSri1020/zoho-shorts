# Script: UAE E-Invoicing in Zoho Books: Everything to Do Before 1 January 2027

Length ~456 s (7.6 min), 16:9. Voice: Kokoro am_michael (placeholder until Gaurav's cloned voice). Facts: docs/longform/research/uae-einvoicing.md.

Spoken forms ("A S P", "five thousand dirhams") are for the TTS; captions show ASP, AED 5,000.


## 0:00  s01  HOOK - hook  (36 s)

- On the first of January 2027, big businesses in the UAE can no longer just email a PDF invoice to their business customers.
- From that day, every B to B invoice has to travel as a structured e-invoice, through an accredited provider, and the tax authority gets the data in near real time.
- If your company is smaller, your date is later. But the clock has already started.
- In the next few minutes, I'll show you what changes, who goes live when, what the fines are, and how to set it all up in Zoho Books.

## 0:36  s02  CHAPTER - Chapter 1: What is changing  (4 s)

- Let's start with what is actually changing.

## 0:40  s03  CARTOON - old_way  (24 s)

- Today, most invoices work like this. Your accountant makes the invoice, saves it as a PDF, and emails it to the client.
- The client types it into their own system. And the tax authority only sees the numbers much later, in your VAT return.
- Under the new rules, a PDF, a Word file, a scan, or an email is not an e-invoice.

## 1:04  s04  CARTOON - five_corner  (35 s)

- Instead, the UAE uses what it calls a five corner model, built on the Peppol network.
- Corner one is you, the supplier. Your invoice data goes to corner two, your accredited service provider, or A S P.
- Your A S P checks the invoice and delivers it to corner three, your buyer's A S P, which passes it to corner four, the buyer.
- At the same time, your A S P reports the tax data to corner five, the Federal Tax Authority.
- So nobody retypes anything, and the F T A sees it in near real time.

## 1:39  s05  BOARD - compare  (23 s)

- So which invoices are covered? Business to business, and business to government.
- Government to business, and government to government, are covered too.
- Sales to ordinary consumers, B to C, are out of scope, along with a few special cases like airline passenger tickets.
- And e-credit notes go through the same system as your invoices.

## 2:02  s06  CHAPTER - Chapter 2: Who goes live when  (4 s)

- Now, the most important part. Who goes live when?

## 2:06  s07  BOARD - timeline  (43 s)

- The system opened for a pilot, and for voluntary use, on the first of July 2026.
- If your annual revenue is fifty million dirhams or more, you had to appoint your A S P by the thirtieth of October 2026. And you go live on the first of January 2027.
- If your revenue is under fifty million dirhams, appoint your A S P by the thirty first of March 2027, and go live on the first of July 2027.
- Government entities also appoint by the thirty first of March 2027, and go live on the first of October 2027.

## 2:49  s08  CARTOON - fourteen_days  (17 s)

- One more date matters every single day after you go live.
- Each e-invoice and e-credit note has to be issued and sent within fourteen business days of the transaction.
- So a pile of invoices waiting for month end is no longer a safe habit.

## 3:07  s09  CHAPTER - Chapter 3: What it costs if you miss it  (3 s)

- So what happens if you miss these dates?

## 3:10  s10  CARTOON - penalty  (34 s)

- The fines are set by Cabinet Decision 173 of 2026.
- If you have no e-invoicing system, or no A S P, when you should, the fine is five thousand dirhams for every month, capped at fifty thousand dirhams in twelve months.
- Every e-invoice you fail to issue or send costs one hundred dirhams, up to five thousand dirhams a month. The same applies to e-credit notes.
- Small amounts per invoice, but for a busy business they add up fast.

## 3:43  s11  CHAPTER - Chapter 4: Setting it up in Zoho Books  (3 s)

- Now let's set it up in Zoho Books.

## 3:47  s12  BOARD - badge  (20 s)

- First, some good news if you already use Zoho Books.
- Zoho is on the Ministry of Finance list of accredited e-invoicing service providers, as Zoho Software Trading L L C.
- So Zoho can be your A S P, and the invoices you already make in Books can go out over Peppol.

## 4:06  s13  PODCAST  (19 s)

Screen: books/invoices_list, books/settings_home | path: Settings > Taxes & Compliance > E-Invoicing | corner: point_up

- In Zoho Books, click the gear icon to open Settings.
- Under Taxes and Compliance, open E-Invoicing.
- Check that your business name, your T R N and T I N, and your address match what the F T A has. And use the email that is registered with the F T A.

## 4:25  s14  BOARD - flow  (21 s)

- Next, sign in to Emara Tax, open the E-Invoicing service, and choose Zoho Software Trading L L C as your service provider.
- Submit the declaration there.
- Then come back to Zoho Books and click Verify and Complete Setup. When the connection shows as active, you're done with the setup.

## 4:46  s15  BOARD - formula  (23 s)

- A quick note on your Peppol I D, because it confuses a lot of people.
- It is zero two three five, followed by your ten digit T I N. And your T I N is simply the first ten digits of your fifteen digit T R N.
- Your A S P creates this I D for you. Your job is to keep your T R N correct everywhere.

## 5:09  s16  BOARD - record  (23 s)

- Now clean up your customers. Open each business customer, and go to the Other Details tab.
- Fill in the T I N, the legal name, and the electronic address, and check the Peppol status.
- Then do the basics for your items too: mark each one as goods or service, and set the unit.
- Clean data now means fewer failed e-invoices later.

## 5:32  s17  PODCAST  (17 s)

Screen: books/invoices_list | path: Sales > Invoices > + New | corner: open_hands

- Creating an e-invoice feels just like before. Go to Sales, then Invoices, and click New.
- Pick the customer, add your items, and check the tax treatment.
- When you send it, Zoho Books pushes it over Peppol, with Zoho acting as your A S P.

## 5:49  s18  PODCAST  (21 s)

Screen: books/invoices_list | path: Invoice > E-Invoice status | corner: point_you

- Every invoice then shows an e-invoice status, separate from draft or sent.
- Yet to be pushed. Push initiated. And then pushed, with a unique U U I D. If it says failed, open it, fix the error, and push it again.
- Once it's pushed, the invoice is locked, so corrections go through a credit note.

## 6:09  s19  PODCAST  (13 s)

Screen: books/bills_list | path: Purchases > Bills | corner: wow

- It works the other way too. E-invoices your suppliers send you arrive in Purchases, under Bills, as drafts.
- So you review them, instead of typing supplier invoices in by hand.

## 6:22  s20  CHAPTER - Chapter 5: Your checklist  (4 s)

- Finally, here's your checklist for the next few weeks.

## 6:26  s21  BOARD - checklist  (44 s)

- One. Know your revenue band, so you know whether your date is January or July 2027.
- Two. Appoint your A S P in Emara Tax. With Zoho Books, that means choosing Zoho Software Trading L L C.
- Three. Make sure you have a T I N, and that every business customer has the right T R N and legal name.
- Four. Clean up your items and units.
- Five. Test the whole flow before you go live: a normal sale, an export, a credit note, and receiving a supplier invoice.
- Six. Keep your A S P updated whenever your registration details change, because late updates carry their own fine.

## 7:10  s22  CARTOON - celebrate  (6 s)

- Do these six things, and the deadline becomes just another date in your calendar.

## 7:16  s23  OUTRO - outro  (20 s)

- If this helped, subscribe to G S X Automation. Next up on the channel: Saudi Arabia's ZATCA Phase 2 in Zoho Books.
- Rules can still change, so always check the latest notices from the Ministry of Finance and the F T A. See you in the next one.

## YouTube description (draft)

```
UAE e-invoicing starts on 1 January 2027 for businesses with revenue of AED 50 million or more, and on 1 July 2027 for smaller businesses. In this video: what changes (the 5-corner Peppol model), who goes live when, the penalties under Cabinet Decision 173 of 2026, and how to set up e-invoicing in Zoho Books step by step.

Chapters
{chapters}

Sources (checked {date})
- UAE Ministry of Finance, e-invoicing: https://mof.gov.ae/en/about-us/initiatives/einvoicing/
- MoF list of accredited service providers: https://mof.gov.ae/en/about-us/initiatives/einvoicing/pre-approved-einvoicing-service-providers/
- FTA notice on deadlines (25 Oct 2026): https://tax.gov.ae/en/media.centre/news/federal.tax.authority.calls.on.persons.subject.to.einvoicing.to.comply.wit.the.prescribed.legal.deadlines.and.avoid.administrative.penalties.aspx
- Zoho Books UAE e-invoicing: https://www.zoho.com/ae/books/e-invoicing/

This is general information, not tax or legal advice. Rules can change - always check the latest MoF / FTA notices.
Voice-over and animations were made with AI tools; facts were checked against the official sources above.

#UAEeInvoicing #ZohoBooks #Peppol #UAEVAT #GSXAutomation
```
