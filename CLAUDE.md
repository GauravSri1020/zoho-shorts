# Rules for Claude in this repo

1. BACKUP FIRST. Before changing anything Gaurav asks for: create branch `backup-YYYY-MM-DD-<what-changes>` from main
   (and, for video work, download the latest Short artifact). Only then touch code. Say which backup was made.
2. Read docs/HISTORY.md first (status + what was tried), update it at the end of every session.
3. Quality over speed: a Short with a black frame, a voice change (while Gemini quota is available), broken lip sync
   or wrong Zoho steps must never be uploaded. The editor (flow.py / composer.py / editor.py) and QA (benchmark.py)
   must stay strict.
4. END OF CHAT = BACKUP + HANDOFF. When Gaurav says the chat is ending (or before a long break): create branch
   `backup-YYYY-MM-DD-end-of-<topic>` from main, write docs/sessions/YYYY-MM-DD-<topic>.md (what he asked, what was
   done, decisions, open items, exact next step), commit it, and paste the same summary in the chat so he can start the
   next chat with it. A new chat starts by reading CLAUDE.md, docs/HISTORY.md and the newest docs/sessions/ file.
5. Real Zoho screenshots: Gaurav opens the app (sample data only, never real customers / keys); Claude never logs in or
   types passwords. Saved under assets/screens/<app>/ + click targets in assets/screens/index.yaml.
