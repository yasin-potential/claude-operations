# DUNS iUpdate — PM Operator Playbook

PM-driven flow. Client's only effort: fill the intake form once, and forward any SMS they receive from D&B via KakaoTalk (rare for DUNS — usually just email).

## Before starting

- Intake form complete — 1Password vault `<Client Slug> - Platforms` has `DUNS Registration` item populated.
- Client's business registration certificate PDF available at the path stored in the 1Password item's `business_cert_path` field.
- `.env.1password.<client-slug>` exists and points to the client's vault item.
- 1Password CLI signed in (`op whoami`).

Run sanity:

```bash
./scripts/run-flow.sh --client=<slug> --project=duns-iupdate -- --list
```

## Portal quirks (verified during research)

- Start URL is the D&B DUNS landing: `https://www.dnb.com/en-us/smb/duns/get-a-duns.html`. Clicking through enters the iUpdate flow.
- Classic ASP.NET `__VIEWSTATE` once inside iUpdate — do NOT open extra tabs on the same session. One tab only.
- Email verification link expires in ~24h. If the link is expired, re-run the flow; the search step de-duplicates.
- Document upload is inside an iframe — the `uploadDocument` fixture already handles `frameLocator`.
- Success toast is `role="alert"`, disappears in ~3s. Don't rely on URL change.

## PM-operator HITL checkpoints

### 1. CAPTCHA (if present)

Portal may show hCaptcha or reCAPTCHA after the initial submission. Solve it as PM. Zero client involvement.

### 2. `post-email` — Verify email link

Browser pauses with message *"Verify email link from D&B"*.

1. Open the shared inbox or the address the client set as their DUNS contact email.
2. Find the D&B email (from `noreply@dnb.com` or similar), click the verification link.
3. The link opens in your default browser; copy the URL and paste into the Playwright-controlled browser, or let it redirect and continue there.
4. In the Playwright Inspector, click **Resume**. Flow auto-saves the `post-email` checkpoint.

If email hasn't arrived after 2 minutes, check spam. If still missing, close browser and re-run — the search step won't duplicate entries.

### 3. `post-details` — Auto-saved after detailed form fill

No human action. Checkpoint is snapshot of the fully-filled form before upload.

### 4. `post-upload` — Auto-saved after cert upload

No human action. Checkpoint confirms the business registration certificate upload succeeded.

### 5. `pre-submit` — Sanity check before submit

Browser pauses with message *"Review the summary page. Click Resume to submit."*

1. Scroll through the summary page.
2. Quick-check every field against the intake form — especially tax ID (사업자등록번호) and English address.
3. If any field is wrong: **do not submit.** Close the browser. The intake form's data is wrong — contact client, correct the 1Password item, re-run with `--resume=post-email` to skip back to the right step.
4. If everything is correct: in the Inspector, click **Resume**. Skill clicks Submit on the D&B page.

Note: this checkpoint is a PM sanity check only. The intake form's data-accuracy certification means client is responsible for providing correct data, not PM for catching every typo. This pause exists to catch auto-fill selector drift (wrong field matched), not client-supplied errors.

### 6. Result capture

Skill reads the DUNS number from the confirmation page (9-digit number) and writes:

- `artifacts/<client>/duns-iupdate/<run-id>/result.json` — DUNS number + timestamp
- `artifacts/<client>/duns-iupdate/<run-id>/handoff.md` — client delivery doc

## After the run

1. Open `handoff.md`, paste into an email to the client contact:
   - DUNS number
   - Registration date
   - Attach the confirmation screenshot (`pre-submit.png` or D&B confirmation email)
2. Update 1Password item with the new DUNS number (field: `duns_number`).
3. Delete any local copy of the business registration certificate (`DUNS_BUSINESS_CERT_PATH`) from PM's laptop.
4. `artifacts/<client>/duns-iupdate/<run-id>/` retained locally for 1 year — evidence of what was submitted.

## Recovering from failure

| Symptom | Fix |
|---|---|
| CAPTCHA keeps failing | D&B flagged the IP. Wait 30 min, retry; or run from a different network. |
| "Company already exists" | Client has an existing DUNS. Switch to the "Claim existing DUNS" flow (not currently built). Pause and consult. |
| Upload fails silently | The iframe sometimes doesn't mount on first load. `--resume=post-email` and retry. |
| Email link expired (>24h) | Re-run — the `companySearch` step de-duplicates; D&B sends a new email. |
| Summary page shows wrong data | Intake form has wrong data. Stop, fix the 1Password item, re-run from `--resume=post-email`. |
