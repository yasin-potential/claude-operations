# Intake Form — Platform Registration Engagement

One-time data collection for a client engagement. Every field here gets stored in the client's 1Password vault and is reused across every platform flow (DUNS, Apple, Google, Meta, etc.) without re-asking. Complete once per client.

**Instructions for PM**: create a 1Password vault named `<Client Slug> - Platforms`, share it with the client contact, ask them to fill in each field. PM verifies completeness before running any flow.

---

## 1. Legal Entity

| Field | 1Password field | Value (client fills) |
|---|---|---|
| Legal name (Korean) | `company_name_ko` | |
| Legal name (English, as registered with 사업자등록증) | `company_name_en` | |
| Business registration number (사업자등록번호) | `business_registration_number` | |
| Date of establishment | `established_date` | |
| Business type (업종) | `business_type` | |
| Primary industry code (업태) | `industry_code` | |
| Website (must match legal entity) | `website` | |

## 2. Representative / Signatory

The person with legal authority to bind the entity. Required for DUNS submission name, Apple Developer Account Holder, etc.

| Field | 1Password field | Value |
|---|---|---|
| CEO / 대표 name (Korean) | `representative_ko` | |
| CEO / 대표 name (English, romanized, must match passport/ID) | `representative_en` | |
| Title | `representative_title` | |
| Email (business, reachable) | `representative_email` | |
| Mobile phone (for SMS verification) | `representative_phone` | |

## 3. Business Address

Must match the address on the 사업자등록증. Apple and Google cross-check this against DUNS.

| Field | 1Password field | Value |
|---|---|---|
| Street address (Korean) | `address_ko` | |
| Street address (English romanization) | `address_en` | |
| City / Province (English) | `address_city_en` | |
| Postal code | `address_postal_code` | |
| Country | `address_country` | `KR` |

## 4. Documents

Upload PDFs to the 1Password item as attachments, and paste the local path (on PM's laptop after download) for automation.

| Document | 1Password field | Status |
|---|---|---|
| 사업자등록증 (business registration certificate) PDF | `business_cert_attachment` + `business_cert_path` | [ ] uploaded |
| 법인등기부등본 (corporate register extract, if needed) | `corp_register_attachment` | [ ] uploaded |
| 대표자 신분증 (ID, if Apple or Google requests) | `representative_id_attachment` | [ ] uploaded |

## 5. Payment Method

Required for Apple Developer ($99/year) and any platform with paid tiers. Credit card in the legal entity's name.

| Field | 1Password field | Value |
|---|---|---|
| Card number | `card_number` | |
| Cardholder name | `card_name` | |
| Expiry (MM/YY) | `card_expiry` | |
| CVC | `card_cvc` | |
| Billing address (match entity address unless different) | `card_billing_address` | |

## 6. Platform-Specific

### DUNS
- Existing DUNS number (if claiming, not registering new): `duns_number` = __________
- Preferred SIC code (if known): `duns_sic_code` = __________

### Apple Developer
- Apple ID email (create new one with business email if none) — `apple_id_email`: _________
- Apple ID password (client creates; stored in 1Password): `apple_id_password`
- Apple ID TOTP secret (generated during 2FA enrollment; stored in 1Password as OTP field)
- Signatory title (e.g., CEO, Managing Director): `apple_signatory_title` = __________

### Google Play
- Play Console developer name (public-facing): `google_developer_name` = __________
- Tax classification for Payments profile (usually "Corporation" for 주식회사): `google_tax_classification` = `Corporation`
- W-8BEN-E fields — ask at enrollment time, stable once set.

### Meta Business
- Facebook Business Manager admin email: `meta_admin_email` = __________
- Domain you'll verify: `meta_domain` = __________

## 7. Communication Preferences

| Question | Answer |
|---|---|
| Preferred channel for ongoing comms | [ ] Email  [ ] KakaoTalk  [ ] Slack |
| Client contact for engagement | _________ |
| Client contact for emergencies (e.g., Apple calling) | _________ |
| SMS forwarding acknowledgment | [ ] I will forward any SMS from Apple / Google / D&B to Potential Inc. via KakaoTalk within 10 minutes of receipt. |
| Phone number strategy for Apple | [ ] Use my real mobile — I'll forward SMS  [ ] Set up dedicated 070 VoIP (Potential assists) |

## 8. Deliverables Checklist

To be filled by PM at engagement end. Evidence of what was registered.

| Deliverable | Value | Date |
|---|---|---|
| DUNS Number | __________ | __________ |
| Apple Developer Team ID | __________ | __________ |
| Apple Developer Account Holder email | __________ | __________ |
| Google Play Console developer account URL | __________ | __________ |
| Meta Business Manager ID | __________ | __________ |

## 9. Signature

Client confirms the data above is accurate as of the date below, and authorizes Potential Inc. to submit this data to the platforms specified above without per-submission approval.

**Date**: _______________________

**Client signatory**: _______________________ (name, title)

**Signature / seal**: _______________________

---

## For PM — data completeness check before running any flow

Run this mental checklist:

- [ ] All Section 1 fields complete (legal entity)
- [ ] All Section 2 fields complete (representative)
- [ ] Section 3 address is the exact address on the 사업자등록증 (PM verifies by cross-reading the attached PDF)
- [ ] Section 4 business cert PDF attached to 1Password item AND saved locally at `business_cert_path`
- [ ] Section 5 card fields complete if running Apple or Google (not needed for DUNS)
- [ ] Section 7 SMS forwarding acknowledgment checked
- [ ] Intake form Section 9 signed by client and filed in the project folder

If any of the above are missing: ask client. Do NOT run a flow with gaps.
