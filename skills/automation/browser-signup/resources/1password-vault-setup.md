# 1Password Vault Setup per Client

How to structure 1Password for a managed-signup engagement. Done once per client, then reused across all platform flows (DUNS, Apple, Google, Meta).

## Vault naming

**One vault per client, not per flow.** Vault name format:

```
<Client Slug> - Platforms
```

Examples: `Acme Corp - Platforms`, `Bluewave - Platforms`.

Why one vault for all platforms: the client data (legal name, tax ID, address, card) is shared across every flow. One vault = one place to revoke access when the engagement ends.

## Vault access

Create the vault inside the Potential team account (`team-potentialai.1password.com`).

| Role | Members |
|---|---|
| Owner | Potential PM running the engagement |
| Admin | Potential engagement lead |
| Can Edit | Client designated contact |
| Can View | (none unless specifically needed) |

**Revocation**: at engagement end, change client role to "Can View" (they still have read access to their own credentials) and remove Potential members if the relationship closes fully.

## Items per vault

Create one 1Password item per flow. Client fills values according to the intake form once; they're reused forever across flows.

### Item: `Entity Data` (shared across all flows)

Category: **Secure Note** (or custom "Entity" category if preferred).

Fields — all from Section 1-4 of the intake form:

```
company_name_ko               (text)
company_name_en               (text)
business_registration_number  (text)
established_date              (date)
representative_ko             (text)
representative_en             (text)
representative_title          (text)
representative_email          (email)
representative_phone          (phone)
address_ko                    (text)
address_en                    (text)
address_city_en               (text)
address_postal_code           (text)
address_country               (text, default "KR")
website                       (url)
business_cert_attachment      (file attachment — 사업자등록증 PDF)
business_cert_path            (text — local path on PM's laptop after download)
```

### Item: `Payment` (shared across paid-tier flows)

Category: **Credit Card** (native 1Password category).

Fields: card number, cardholder name, expiry, CVC, billing address. 1Password's built-in Credit Card category has the right field types — use it, don't make custom fields.

### Item: `DUNS Registration`

Category: **Secure Note**.

Fields:
```
duns_number                   (text — filled by PM at engagement end)
duns_submitted_at             (date)
duns_email                    (email — the contact email on the DUNS application)
sic_code                      (text, optional)
```

### Item: `Apple Developer`

Category: **Login**.

Fields:
```
apple_id_email                (username / email)
apple_id_password             (password)
                              (one-time password — the TOTP field, enabled and populated during enrollment)
team_id                       (text — captured at engagement end)
account_holder_name           (text)
account_holder_title          (text)
enrolled_at                   (date)
next_renewal                  (date — 1 year after enrollment; set 1Password reminder)
```

Attachments: Apple Developer Program Agreement PDF (saved at enrollment).

### Item: `Google Play Console`

Category: **Login**.

```
google_account_email          (username)
google_account_password       (password)
                              (one-time password — TOTP)
developer_account_url         (url — after creation)
payments_profile_id           (text)
tax_form_type                 (text — e.g., "W-8BEN-E")
```

### Item: `Meta Business Manager`

Similar structure. Create when engagement scope includes Meta.

## Env-file references

Each flow's `.env.1password.<slug>` points into this vault:

```
# .env.1password.acme
CLIENT_SLUG=acme

# Entity Data (shared across flows)
DUNS_COMPANY_NAME_EN=op://Acme Corp - Platforms/Entity Data/company_name_en
DUNS_COMPANY_NAME_KO=op://Acme Corp - Platforms/Entity Data/company_name_ko
DUNS_REPRESENTATIVE=op://Acme Corp - Platforms/Entity Data/representative_en
DUNS_BUSINESS_REGISTRATION_NUMBER=op://Acme Corp - Platforms/Entity Data/business_registration_number
DUNS_ADDRESS_EN=op://Acme Corp - Platforms/Entity Data/address_en
DUNS_PHONE=op://Acme Corp - Platforms/Entity Data/representative_phone
DUNS_EMAIL=op://Acme Corp - Platforms/Entity Data/representative_email
DUNS_BUSINESS_CERT_PATH=op://Acme Corp - Platforms/Entity Data/business_cert_path

# Apple-specific (when Apple flow runs)
APPLE_DEV_EMAIL=op://Acme Corp - Platforms/Apple Developer/username
APPLE_DEV_PASSWORD=op://Acme Corp - Platforms/Apple Developer/password
APPLE_DEV_TOTP=op://Acme Corp - Platforms/Apple Developer/one-time password

# Payment
CC_NUMBER=op://Acme Corp - Platforms/Payment/number
CC_EXPIRY=op://Acme Corp - Platforms/Payment/expiry
CC_CVC=op://Acme Corp - Platforms/Payment/verification number
```

## Client onboarding — 15-minute walkthrough

Schedule a short call or async setup with the client:

1. **PM creates empty vault + empty items** (5 min, async).
2. **Share vault with client's 1Password** (client must have a 1Password account; free Family plan works if they don't).
3. **Client fills Entity Data + Payment item** (10 min, async — they do it when convenient).
4. **Client attaches business cert PDF** to the Entity Data item.
5. **PM runs `npm run check --client=<slug>`** — verifies all op:// pointers resolve. Any failures surface missing fields.

If client doesn't have 1Password: they can install the free version at 1password.com/downloads/, create a free individual account with their business email, accept the vault share. No cost to them.

## At engagement end

- Export the vault to a 1PUX backup file, save to project folder.
- Change client role to "Can View" only.
- Remove Potential members if full handoff.
- Delete local copies of any attached PDFs.
- Update the Entity Data item with engagement end date in the notes field.

## Security notes

- **Never copy vault items between clients.** Each client's data lives in their own vault.
- **Business cert PDFs** are sensitive. They live as 1Password attachments, not on PM's laptop. The `business_cert_path` field is a temporary local path for the automation — delete after each run.
- **TOTP fields** in 1Password generate 6-digit codes every 30 seconds. The `op run` mechanism reads them in real-time, so codes passed to Playwright are always fresh.
- **Revocation is immediate.** Changing vault permissions in 1Password takes effect within seconds across all signed-in devices.
