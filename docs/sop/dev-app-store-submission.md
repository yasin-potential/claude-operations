# App Store Submission — Developer SOP

> **Audience**: Developer
> **Scope**: Step-by-step technical process for submitting a webview app to Google Play & Apple App Store
> **Automation**: Each section has a Claude Code shortcut (in toggle sections) that automates most of the work.

This document outlines the step-by-step process for uploading an application to the Google Play Store and Apple App Store. It covers the required assets, build process, and submission steps.

> **Tip**: To ensure app submission before completing MVP, decide with the team which complex features can be removed to make the app ready for initial submission.

---

## 1. Prerequisites

Before starting, make sure you have:

### For Both Stores
- [ ] Node.js installed
- [ ] Project source code (web app)
- [ ] App information ready (name, description, icon)

### For Apple App Store
- [ ] Apple Developer Account ($99/year)
- [ ] Mac system with Xcode installed
- [ ] Valid Apple distribution certificate
- [ ] Provisioning profile for App Store distribution

### For Google Play
- [ ] Google Play Developer Account ($25 one-time)
- [ ] Java/Android SDK installed (for Capacitor builds)
- [ ] Release keystore generated

<details>
<summary>🤖 <b>Automate with Claude Code</b></summary>

```
/store-prep
```

Analyzes the project and generates all required documents (listing text, privacy policy, terms of service, technical checklist). PM answers 3 multiple-choice questions; the rest is auto-generated.

</details>

---

## 2. Native App Setup (Capacitor)

### 2.1 Initialize Capacitor

```bash
npm install @capacitor/core @capacitor/cli
npx cap init [appName] [appId]
```

### 2.2 Add Platforms

```bash
npx cap add android
npx cap add ios
```

### 2.3 Configure `capacitor.config.ts`
- Set `appId` (e.g., `com.company.appname`)
- Set `appName`
- Set `webDir` to your build output folder (e.g., `dist`, `build`, `.output/public`)

### 2.4 Required Native Features

| Feature | Required? | Why |
|---------|-----------|-----|
| Push Notifications | Strongly recommended | Apple rejects WebView-only apps (Guideline 4.2) |
| Sign in with Apple | **Mandatory** if social login exists | Apple Guideline 4.8 |
| Account Deletion | **Mandatory** (both stores) | Store policy |
| App Tracking Transparency | **Mandatory** if tracking SDKs | iOS 14.5+ |
| Deep Links | If needed | For opening specific pages from external links |

### 2.5 Sync Web Assets

After every frontend build:
```bash
npx cap sync
```

<details>
<summary>🤖 <b>Automate with Claude Code</b></summary>

```
/store-native
```

Auto-detects the framework (React, Vue, Angular, Next.js, etc.), sets up Capacitor, and implements all required native features (push, deep links, Sign in with Apple, account deletion, ATT).

Sub-commands available:
- `/store-native init` — Capacitor + platform setup
- `/store-native push` — Push notifications
- `/store-native apple-login` — Sign in with Apple
- `/store-native account-deletion` — Account deletion
- `/store-native att` — App Tracking Transparency

</details>

---

## 3. Production Deployment

Before submission, the app must be served from a production server with HTTPS.

### Checklist
- [ ] Production environment variables set (no test keys, no localhost URLs)
- [ ] HTTPS configured with valid SSL certificate
- [ ] CORS configured for the production domain
- [ ] Debug/dev code removed
- [ ] Server is stable and accessible

<details>
<summary>🤖 <b>Automate with Claude Code</b></summary>

```
/store-deploy
```

- `/store-deploy check` — Scans for security vulnerabilities (test keys, debug code, hardcoded URLs)
- `/store-deploy env` — Production environment variable guide
- `/store-deploy docker` — Docker production config
- `/store-deploy ssl` — SSL/HTTPS setup guide

</details>

---

## 4. App Store (iOS) — Build & Upload

### 4.1 Apple Developer Portal Setup

1. Go to https://developer.apple.com/account
2. **Create App ID**:
   - Certificates, IDs & Profiles → Identifiers → +
   - Choose "App IDs" → "App"
   - Enter description (app name) and Bundle ID (must match `capacitor.config.ts`)
   - Enable required capabilities (Push Notifications, Sign In with Apple, etc.)
   - Register

3. **Create Distribution Certificate**:
   - Open Keychain Access → Certificate Assistant → Request a Certificate From a Certificate Authority
   - Save the `.certSigningRequest` file
   - Go to Certificates → + → "Apple Distribution"
   - Upload the CSR file → Download and install the certificate

4. **Create Provisioning Profile**:
   - Go to Profiles → +
   - Choose "App Store Distribution"
   - Select your App ID and certificate
   - Download the `.mobileprovision` file and double-click to install

### 4.2 Configure Xcode

1. Open `ios/App/App.xcworkspace` in Xcode
2. Go to App target → Signing & Capabilities
3. Set Team, Bundle Identifier, and Provisioning Profile
4. Set Deployment Target (recommended: iOS 15.0+)

### 4.3 Build & Archive

```bash
# Build frontend
npm run build
npx cap sync ios

# In Xcode:
# Product → Archive
# Wait for build to complete
```

### 4.4 Validate & Upload

1. In Xcode Organizer, click **Validate App**
   - Fix any issues (bundle ID mismatch, missing icons, etc.)
2. Click **Distribute App** → App Store Connect → Upload
3. Sign with distribution certificate
4. Wait for "Upload Complete" message

### 4.5 App Store Connect Setup

1. Go to https://appstoreconnect.apple.com
2. My Apps → + → New App
   - Platform: iOS
   - Name: App name
   - Bundle ID: Must match Xcode
   - SKU: Any unique string (e.g., `appname2026`)
3. Fill in:
   - App Information (category, content rights)
   - Pricing and Availability
   - Version Information (screenshots, description, keywords)
   - App Review Information (test account, contact info)

### 4.6 Privacy & Compliance

- **App Privacy Labels**: Declare data collection types and usage
- **Export Compliance**: Answer encryption questions (usually "No" for standard HTTPS)
- **Age Rating**: Complete the questionnaire

### 4.7 Submit for Review

Attach the build, complete all sections, and click **Add for Review**.

<details>
<summary>🤖 <b>Automate with Claude Code</b></summary>

```
/store-build    # Signing + release build
/store-submit   # Step-by-step console guide + auto-drafted data safety & age rating
```

</details>

---

## 5. Google Play — Build & Upload

### 5.1 Generate Release Keystore

```bash
keytool -genkey -v -keystore release.keystore -alias my-key-alias \
  -keyalg RSA -keysize 2048 -validity 10000
```

> **Keep this keystore safe** — you need it for all future updates.

### 5.2 Configure Signing

In `android/app/build.gradle`:
- Add signing config with keystore path, alias, and passwords
- Set `targetSdkVersion` to current minimum (API 34+)

### 5.3 Build AAB

```bash
# Build frontend
npm run build
npx cap sync android

# Build release
cd android
./gradlew bundleRelease
```

Output: `android/app/build/outputs/bundle/release/app-release.aab`

### 5.4 Google Play Console Setup

1. Go to https://play.google.com/console
2. Create app → Enter app name, language, free/paid
3. Fill in:
   - **Store listing**: Title, descriptions, icon (512×512), feature graphic (1024×500), screenshots
   - **Content rating**: Complete IARC questionnaire
   - **Data Safety**: Declare data collection and sharing practices
   - **App pricing**: Set country availability and pricing

### 5.5 Internal Testing (Recommended Before Production)

1. Go to Testing → Internal testing → Create new release
2. Upload the AAB file
3. Add testers (PM email)
4. PM completes smoke test → approves

### 5.6 Production Release

1. Go to Production → Create new release
2. Upload AAB (or promote from internal testing)
3. Add release notes
4. Submit for review

<details>
<summary>🤖 <b>Automate with Claude Code</b></summary>

```
/store-build    # Keystore generation + build
/store-submit   # Console guide + auto-drafted data safety
```

</details>

---

## 6. Review & Rejection Handling

### Common Rejection Reasons

| Reason | Store | Fix |
|--------|-------|-----|
| App crashes | Both | Check server status, test account data |
| WebView-only (no native features) | Apple (4.2) | Add push notifications, biometric, or offline features |
| Missing Sign in with Apple | Apple (4.8) | Implement if any social login exists |
| Missing privacy policy | Both | Host at public URL, add to store listing |
| Incomplete data safety | Google | Re-analyze code for data collection |
| Screenshots don't match | Both | Re-capture from current build |
| `targetSdkVersion` too old | Google | Update to API 34+ |
| Missing account deletion | Both | Implement in-app account deletion |

### After Rejection

1. Read the rejection email carefully — note the guideline number
2. Fix the issue
3. Re-build and re-upload
4. Add resolution notes explaining what was fixed
5. Re-submit

<details>
<summary>🤖 <b>Automate with Claude Code</b></summary>

```
/store-review
```

Paste the rejection email. Claude will identify the exact guideline, propose fixes with code examples, draft a resolution response, and guide resubmission.

</details>

---

## 7. Version Updates

For subsequent releases:

1. Increment version in `package.json` and native configs
2. Build frontend → `npx cap sync`
3. Build release (AAB / Archive)
4. Upload new build to store console
5. Add release notes
6. Submit for review

<details>
<summary>🤖 <b>Automate with Claude Code</b></summary>

```
/store-ship update
```

Runs a reduced pipeline — skips prep/assets/native/deploy if unchanged. Focuses on version increment, build, and submission.

</details>

---

## Quick Reference: Claude Commands

| Command | What It Does |
|---------|-------------|
| `/store-ship start` | Full pipeline — all phases sequentially |
| `/store-ship status` | Progress dashboard |
| `/store-ship from native` | Start from a specific phase |
| `/store-native` | Capacitor setup + native features |
| `/store-deploy` | Production deployment + security scan |
| `/store-build` | Signing + release build |
| `/store-submit` | Console submission guide |
| `/store-review` | Rejection analysis + fix guide |
| `/store-ship update` | Version update workflow |
| `/store-ship checklist` | Auto-checked full checklist |
| `/store-ship blockers` | PM vs Developer blocker analysis |

---

## Common Pitfalls Checklist

- [ ] Test account has **pre-populated content** (not empty)
- [ ] All permissions include **clear reason text** in Info.plist / AndroidManifest
- [ ] iPad screenshots match **actual iPad display** (Xcode simulator, not Chrome DevTools)
- [ ] Privacy policy URL is **publicly accessible** (not behind login)
- [ ] Production server is **running and reachable** during the entire review period
- [ ] `targetSdkVersion` ≥ API 34 (Google Play)
- [ ] Personal info fields (phone, gender) are **not required** unless functionally necessary
- [ ] App icon includes **no alpha channel** (App Store rejects transparent icons)
