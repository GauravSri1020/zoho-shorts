# GSX Automation Shorts: setup guide (step by step)

**Poora automatic. Tujhe kuch record, padhna ya review nahi karna.** Setup sirf ek baar karna hai, ~30 min.

Roz kya hota hai (GitHub pe, free):

1. **10:00 AM IST:**
   - Research agent Zoho ki asli problems dhoondhta hai (Reddit, Stack Overflow, Google News). Feeds khaali hon to common Zoho problems se kaam chalata hai.
   - Script agent 2 Shorts likhta hai, saath mein zaroori Deluge / widget / HTML code.
   - **QA agent** har script pass/fail karta hai (galat feature, vague step, buggy code), aur fail ho to 3 baar tak theek karwata hai.
2. Video banti hai:
   - **AI awaaz** (Gemini TTS, backup edge-tts)
   - **tera AI avatar**, har video mein alag photo se, lip-sync ke saath (SadTalker, free). Wo fail ho to tera photo halki camera movement ke saath lagta hai.
   - Tu poori screen pe dikhta hai, apne asli background ke saath (lights wagairah). Camera har video mein alag tarah se dheere-dheere move karta hai. Screen pe sirf bole hue words captions mein aate hain. Na split screen hai, na cards, na badge. Code description mein jaata hai.
   - **Photo agent** (har Sunday): tere photos dekh ke naye scenes mein tere naye photos banata hai, jaise raat ki lights wali street, rooftop, office ya cafe. Ek QA agent check karta hai ki photo bilkul tere jaisa aur real lage, tabhi wo rotation mein jaata hai.
3. **QA agent final video dekhta hai:** captions, awaaz, chehra glitch to nahi. Fail ho to upload nahi hota.
4. YouTube pe **schedule** hoti hai, roz alag random time pe:
   - **subah 7:00-8:00**
   - **raat 8:00-9:00**
   - pichhle din ka time kabhi repeat nahi hota
5. Har 3 ghante comments ke reply apne aap jaate hain. Spam aur risky comments skip hote hain.
6. **Telegram pe sirf problem aati hai**, jaise "aaj 2 mein se 1 hi Short upload hua, ye wajah hai". Sab theek ho to koi message nahi.

**AI label:** video mein AI avatar aur AI awaaz hai, isliye har upload pe YouTube ka "altered or synthetic content" label ON rehta hai. Description mein bhi ek line hai: "Is video mein AI avatar aur AI voice hai".
**Isko kabhi band mat karna.** Label chhupane pe hi strike ya ban ka risk hai.

---

## Step 1: Accounts (ek baar)

1. **YouTube channel**
   - Apna existing channel use kar, naam **GSX Automation** rakh. Naam ya logo mein "Zoho" mat daalna, wo trademark hai.
   - Settings > Channel > Feature eligibility mein jaake phone verify kar.
2. **Google Cloud** (https://console.cloud.google.com)
   - Naya project bana aur APIs & Services > Library mein **YouTube Data API v3** ko **Enable** kar.
   - **OAuth consent screen** setup kar:
     - type External rakh, test user mein apna Gmail daal
     - phir **Publish app / In production** kar de
     - ⚠️ Testing mode mein token 7 din mein expire ho jata hai.
   - Credentials > Create credentials > OAuth client ID banao:
     - type **Web application** rakh
     - Authorized redirect URI mein `https://developers.google.com/oauthplayground` daal
     - Client ID aur Client secret copy kar le
3. **Refresh token** (sirf browser se, kuch install nahi karna)
   - https://developers.google.com/oauthplayground kholo.
   - Upar right mein ⚙️ dabao, "Use your own OAuth credentials" tick karo, aur apna Client ID / Secret daal do.
   - Left mein scope box mein ye do daalo, dono ek ke baad ek:
     - `https://www.googleapis.com/auth/youtube.upload`
     - `https://www.googleapis.com/auth/youtube.force-ssl`
   - **Authorize APIs** dabao aur channel wale account se login karo.
     - "Google hasn't verified this app" aaye to Advanced > Go to … pe click karo, phir Allow.
   - **Exchange authorization code for tokens** dabao, phir **Refresh token** copy karo.
   - (Python aata ho to `python tools/get_refresh_token.py` bhi kaam karta hai.)
4. **Gemini API key** (free): https://aistudio.google.com/apikey
5. **Telegram** (problem alerts ke liye):
   - @BotFather pe `/newbot` karke token le.
   - Apne bot ko ek message bhej.
   - @userinfobot se apna chat id le.

## Step 2: GitHub repo

1. github.com > New repository banao, **Public** rakh.
   - Lip-sync CPU pe chalta hai aur roz 1-2 ghante leta hai. Public repo ke minutes free aur unlimited hain, private repo ki 2000 min/mahina ki limit isme khatam ho jayegi.
   - Repo mein koi secret nahi hota, aur tere photos encrypted rehte hain.
2. Ye poora folder upload kar de, `.github/workflows/autopilot.yml` bhi.
3. Settings > Secrets and variables > Actions > **New repository secret** mein ye daal:

| Secret | Kya hai |
|---|---|
| `GEMINI_API_KEY` | Step 1.4 |
| `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` | Step 1.3 ki 3 values |
| `AVATAR_KEY` | `AVATAR_KEY.txt` ka text (maine alag file di hai). Isse tere encrypted photos khulte hain |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Step 1.5 |

Tere 3 photos har video mein baari-baari se lagte hain: brown jacket, office standing aur office desk. Repo mein ye sirf encrypted rehte hain. Naye ya HD photos lagane hon to project mein bhej de, main naya bundle bana dunga.

## Step 3: Pehla test (upload ke bina)

1. Actions > "GSX Automation Shorts" > **Run workflow** chala. Inputs: task `daily`, count `1`, upload `no`.
   - Pehli baar lip-sync engine install hota hai (~20 min), uske baad cache se chalta hai.
2. Run khatam hone pe **Artifacts** download kar aur `short.mp4` dekh.
3. Theek lage to kuch mat kar. Kal 10 baje se apne aap chalega.
   - Pehli asli video ke baad YouTube Studio mein check kar ki wo "Scheduled" dikh rahi hai.
   - ⚠️ "Locked (private)" dikhe to naye Google Cloud project ka **API audit** chahiye. Ye free hai, form yahan hai: https://support.google.com/youtube/contact/yt_api_form

## Settings (`channel.yaml`)

- `scripts.per_day`: roz kitne Shorts.
- `schedule.windows`: kis time pe public ho (IST).
- `avatar.engine`:
  - `sadtalker` = lip-sync
  - `photo` = sirf photo motion, tez aur safe
- `avatar.gemini_voice`: awaaz badalni ho to.

## Risk rules (already built in)

- AI label hamesha ON, aur description mein disclosure line.
- "Not affiliated with Zoho" line har description mein.
- Paise, tax ya legal advice nahi, aur asli customer data nahi.
- Comment replies mein risky comments skip hote hain.
- YouTube quota: ek upload ~1,600 units ka hai aur roz 10,000 milte hain, to 2-4 Shorts/din theek hai.
