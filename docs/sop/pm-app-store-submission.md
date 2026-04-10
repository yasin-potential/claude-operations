# App Store Submission — PM SOP

> **Audience**: Project Manager
> **Scope**: Webview app → Google Play & Apple App Store submission

---

## Before You Start: Environment Setup

<details>
<summary><b>First time setup</b> (click to expand)</summary>

### 1. Install Claude Code

Follow the official installation guide: https://docs.anthropic.com/en/docs/claude-code/overview

### 2. Download the operations repo

```bash
cd ~/Desktop/potential/projects
git clone https://github.com/potentialInc/claude-operations.git
```

### 3. Sync store skills

```bash
cd ~/Desktop/potential/projects/pipeline/claude-operations
bash scripts/sync-store-skills.sh
```

After this, all `/store-xxx` commands will be available in Claude Code for any project.

</details>

<details>
<summary><b>Already have the operations repo?</b></summary>

```bash
cd ~/Desktop/potential/projects/pipeline/claude-operations
git pull
bash scripts/sync-store-skills.sh
```

</details>

> Restart Claude Code after syncing for the new skills to take effect.

---

## Step 1. Inform the Development Team

As soon as a project needs a webview app, **inform the dev team before any deadline**.

Share the following:
- [ ] **Submission deadline** — When the app needs to be live
- [ ] **Feature list** — Push notifications, payment, social login, camera/location, etc.
- [ ] **Target stores** — Google Play, App Store, or both

> The dev team needs lead time for native setup (1-3 days) and the build process (1-2 days).

<details>
<summary>🤖 <b>Automate with Claude Code</b></summary>

Open Claude Code in the project folder and run:

```
/store-prep
```

Claude analyzes the codebase and PRD, then asks you 3 simple questions (target stores, pricing, countries). It generates: store listing text, privacy policy, terms of service, client guide, and technical checklist — all automatically.

</details>

---

## Step 2. Check Client's Developer Account

### Google Play
- **Personal account**: $25 one-time fee
- **Organization account**: $25 + identity verification (3-7 business days)

### Apple App Store
- **Personal account**: $99/year
- **Organization account**: $99/year + requires a **D-U-N-S number** (can take **2-4 weeks**)

> **Start this immediately** — account verification is often the longest blocker. Don't wait until the app is ready.

- [ ] Client's account type confirmed (Personal or Organization)
- [ ] Developer account created and verified
- [ ] If Organization: D-U-N-S number obtained (Apple only)

---

## Step 3. Prepare Store Listing Text

### Google Play (Required fields)
- **App name** (max 30 characters)
- **Short description** (max 80 characters)
- **Full description** (max 4000 characters)

### App Store (Required fields)
- **App name** (max 30 characters)
- **Description** (max 4000 characters)
- **Keywords** (max 100 characters, comma-separated)
- **Support URL**
- **Copyright** (e.g., "2026 Company Name")

> Check your project's admin/account page — there may already be description fields you can use as a starting point.

<details>
<summary>🤖 <b>Automate with Claude Code</b></summary>

`/store-prep` generates store listing text for both Google Play and App Store by analyzing the PRD and i18n files. You review and edit.

</details>

---

## Step 4. Prepare Visual Assets

### App Icon
- Provide the original logo/icon file (**minimum 1024×1024px**)
- The developer resizes it to all required dimensions

### Screenshots — How much design do I need?

**Simple screenshots are sufficient for most apps.**

Even [ChatGPT](https://apps.apple.com/us/app/chatgpt/id6448311069) (500M+ downloads) uses plain app screen captures with short captions. **The app experience itself matters far more than screenshot polish.**

**Standard level (most apps):**
- Real app screen inside a device frame
- Short feature description caption at the top
- Clean gradient background

> [IMAGE: Copy the 3 banner example images from the original SOP]

**When you need custom design (social apps, content platforms, etc.):**
- Run `/store-assets screenshot` → Claude generates a list of key pages + a designer brief → Forward the brief to your designer

**Pricing screenshot**: If the app has pricing or subscription plans, include a screenshot of the pricing page.

> [IMAGE: Copy the pricing screenshot from the original SOP]

### Asset Specifications

| Asset | Google Play | App Store |
|-------|------------|-----------|
| App Icon | 512×512 | 1024×1024 |
| Phone Screenshots | 1080×1920, min 2 | 1242×2688 (6.5"), min 3, max 10 |
| iPad Screenshots | — | 2048×2732 (required) |
| Feature Graphic | 1024×500 | — |

> **iPad screenshots**: Since iPad support is enabled in Xcode, iPad screenshots are required. Capture them on a real iPad or Xcode Simulator — Chrome DevTools responsive mode is not accurate enough.

- [ ] App icon source provided (1024×1024+)
- [ ] Phone screenshots created with device mockups
- [ ] iPad screenshots created
- [ ] Feature graphic created (Google Play, 1024×500)
- [ ] Pricing screenshot included (if applicable)

<details>
<summary>🤖 <b>Automate with Claude Code</b></summary>

```
/store-assets
```

Claude will:
1. **Auto-resize** your icon to all required dimensions
2. **Capture screenshots** via Playwright (you provide login credentials + which screens to capture)
3. **Open a screenshot designer** — an HTML editor where you add device frames, captions, and backgrounds
4. **Generate feature graphic** (Google Play)

Prerequisites: App must be running (dev server or production URL) + login credentials.

</details>

---

## Step 5. Prepare Legal Documents

Both stores require:
- [ ] **Privacy Policy** — Must be hosted at a publicly accessible URL
- [ ] **Terms of Service** — Recommended

<details>
<summary>🤖 <b>Automate with Claude Code</b></summary>

`/store-prep` generates both documents by analyzing which data the app collects (Entity/DTO fields, SDKs, permissions).

</details>

---

## Step 6. Prepare a Test Account

Store reviewers need a working test account.

- [ ] **Login credentials** — Working username/password
- [ ] **Pre-populated content** — The account must already have data. **Do NOT provide an empty account.**
- [ ] **No unnecessary required fields** — Phone number, gender, etc. should not be required unless functionally necessary
- [ ] **Special instructions** — If anything specific is needed to test the app, write it down

> **Common rejection reason**: Providing an empty test account. Reviewers need to see the app with real content.

### Multi-user / interaction apps (chat, matching, social, etc.)

If the app requires another person to demonstrate core functionality (e.g., messaging, video calls, matching), a single test account is not enough.

- [ ] **Two test accounts** — Provide credentials for both (e.g., Account A and Account B)
- [ ] **Demo video** — Record a short video showing the full interaction flow using both accounts
  - Show: login → find/match the other user → interact (chat, call, etc.)
  - Keep it under 1–2 minutes
  - Upload to a publicly accessible URL (unlisted YouTube, cloud storage link, etc.)
  - Reference the video URL in the **App Review Notes** field
- [ ] **Review notes** — Explain the two-account setup clearly (e.g., "Log in with Account A on one device, Account B on another, then start a chat")

> **Why a demo video?** Reviewers use a single device. Without a video, they cannot verify features that require real-time interaction with another user — this is a common rejection reason for social/chat apps.

---

## Step 7–9. Developer Phases

> These steps are handled by the development team.
> Refer to **[App Store Submission — Developer SOP](https://www.notion.so/potentialinc/App-Store-Submission-Developer-SOP-328b6d88d2cf80d09572db36bab4e26b)** for details.

| Phase | What Happens | PM Action |
|-------|-------------|-----------|
| **7. Native Setup** | Web app → native app conversion + required features (push, Apple login, account deletion) | Confirm required features with dev |
| **8. Deployment** | Production server with HTTPS | Verify production URL opens in browser |
| **9. Build & Test** | Release build → internal testing / TestFlight | **Smoke test** the build (see checklist below) |

### Smoke Test (Step 9)
When the developer shares a test build, verify:
- [ ] App opens without crash
- [ ] Login/signup works
- [ ] Core features function correctly
- [ ] Push notifications arrive
- [ ] All pages load properly
- [ ] No placeholder text or broken images
- [ ] Permission popups explain why they're needed
- [ ] **iPad**: Layout displays correctly (no stretched/broken UI)

---

## Step 10. Store Submission

### What PM enters in the store console:
- [ ] Store listing text (title, descriptions)
- [ ] Screenshots and icon uploaded
- [ ] Content rating questionnaire answered
- [ ] Data safety / privacy labels completed
- [ ] Privacy policy URL entered
- [ ] Test account credentials and review notes entered
- [ ] **Submit for review**

> Build file (AAB/IPA) upload is done by the developer. PM handles metadata and submission.

<details>
<summary>🤖 <b>Automate with Claude Code</b></summary>

```
/store-submit
```

Claude auto-drafts data safety responses and age rating answers by analyzing the code. You review and enter them into the store console.

</details>

---

## Checklist (Copy this to your project page)

> Copy this checklist to your Notion project page and track progress as you go.

### Preparation (PM)
- [ ] Dev team informed with deadline and feature list
- [ ] Client's developer account confirmed and verified
- [ ] Store listing text prepared and reviewed
- [ ] App icon source provided (1024×1024+)
- [ ] Phone screenshots created with device mockups
- [ ] iPad screenshots created
- [ ] Feature graphic created (Google Play)
- [ ] Privacy policy hosted at public URL
- [ ] Terms of service prepared
- [ ] Test account ready with pre-populated content

### Developer Phases
- [ ] Native features implemented (push, Apple login, account deletion)
- [ ] Production server deployed with HTTPS
- [ ] Release build → internal testing / TestFlight
- [ ] PM smoke test passed (including iPad)

### Submission (PM)
- [ ] Store listing text entered
- [ ] Screenshots and icon uploaded
- [ ] Content rating questionnaire completed
- [ ] Data safety / privacy labels completed
- [ ] Test account credentials and review notes entered
- [ ] Submitted for review

### Post-Submission
- [ ] Review result received
- [ ] If rejected: forwarded to dev → fixed → re-submitted
- [ ] App is live on the store

---

## Client Communication Template (Slack)

> Copy-paste the message below into the client Slack channel at the start of the project.

```
We need the following items to prepare [APP NAME] for store submission:

1. App name — Official name to display on the store
2. Google Play Developer account — Email / password
   • If you don't have one, create it here: https://play.google.com/console ($25)
3. Apple Developer account — Apple ID / password
   • If you don't have one, enroll here: https://developer.apple.com ($99/year)
4. App icon (logo) — Original file, 1024×1024px or larger
5. Domain — Purchase a domain and share the registrar credentials
6. AWS account — Sign up and share the credentials

⚠️ Items 1–3 directly impact the release timeline — please prioritize these.
(Apple Organization accounts require a D-U-N-S number, which can take 2–4 weeks)
```
