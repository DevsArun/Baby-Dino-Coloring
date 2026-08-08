# Baby Dino Coloring 🦖

**Tap, color, roar! Easy coloring for toddlers.**

- Package: `com.itschool.babydinocoloring` · Version: `1.0.1+2`
- 520 unique dino coloring pages, 10 categories, **104 free**
- One-time IAP `full_library_unlock` ($3.99) unlocks everything
- Fully offline · zero permissions · no ads · no analytics · COPPA-friendly
- **Devices:** ALL Amazon devices eligible — har Fire tablet (Fire OS 5+,
  minSdk 22) + Fire TV (touchscreen optional, leanback banner included)
- **Languages:** app UI device ki language me khud ba khud —
  English, Deutsch, Français, Español, Italiano, 日本語, Português
  (tier-1 countries: US, CA, UK, DE, FR, ES, IT, JP, BR...)

## Setup (ek baar, 5 minute)

1. **Repo banao** — GitHub par `baby-dino-coloring` naam ka repo banao aur is
   zip ka SARA content drag-and-drop karke upload karo (folders ke saath).
2. **4 GitHub Secrets add karo** — Repo → Settings → Secrets and variables →
   Actions → New repository secret. Values signing kit ke `SECRETS.txt` me hain:
   - `SIGNING_KEYSTORE_BASE64`
   - `SIGNING_STORE_PASSWORD`
   - `SIGNING_KEY_PASSWORD`
   - `SIGNING_KEY_ALIAS`
3. **Amazon pem file** — Amazon Developer Console me app entry banane ke baad:
   *Upcoming Version → Upload Your App File → Additional information → View
   public key* se `AppstoreAuthenticationKey.pem` download karo aur repo ke
   **root** me upload karo. (Ye nahi hoga to build FAIL hogi — yehi #1
   rejection reason hai.)
4. **Build** — koi bhi commit push karo ya Actions tab me *Build Baby Dino
   Coloring APKs* → *Run workflow* chalao.

## Artifacts (Actions run ke neeche)

| Artifact | Kaam |
|---|---|
| `AMAZON-UPLOAD-signed-release` | **Sirf yehi** Amazon Console me upload karo |
| `APPETIZE-ONLY-debug` | Appetize.io / tablet testing ke liye. Amazon par **kabhi nahi** |

## IAP testing

- Appetize/emulator par Amazon IAP **test nahi hota** (NOT_SUPPORTED aayega) —
  ye normal hai.
- Real test: Fire tablet + **Amazon App Tester** app + `store/amazon.sdktester.json`
  ko tablet ke `/sdcard/` me copy karo. Ya Live App Testing use karo.
- Console me IAP item `full_library_unlock` **app ke saath SUBMIT** hona
  chahiye (Draft nahi).

## Structure

- `lib/` — Flutter app (coloring engine, IAP bridge, parental gate, 7-language UI)
- `assets/pages/pages.json` — 520 generated coloring pages (proper names on every page)
- `android-overlay/` — CI me generated android/ shell ke upar copy hota hai
- `ci/` — android prep + signature verification scripts
- `.github/workflows/build.yml` — CI pipeline
- `store/` — sdktester json, listing icons, `store_listing.md` (7 languages)
- `docs/index.html` — privacy policy (GitHub Pages me host karo)
- `tools/` — page/icon generators (repo me sirf reference ke liye)

## Privacy policy hosting

Repo → Settings → Pages → *Deploy from a branch* → `main` + `/docs` folder.
URL hoga: `https://<username>.github.io/baby-dino-coloring/`
