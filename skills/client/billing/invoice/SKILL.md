---
name: generate-invoice
description: "Generate a client Invoice as single-page A4 HTML/PDF with Potential Inc branding. Supports monthly-subscription and project-based invoice types, domestic (VAT) and international (--no-vat). Invoke when the user asks to create/issue an invoice or 견적서."
argument-hint: "[--client 'company'] [--contact 'name'] [--no-vat]"
---

# Generate Invoice Command

Generate a branded single-page client Invoice (title: `Invoice`, Korean-context 견적서) in HTML and PDF matching the Potential Inc template.

All arguments are optional. Any missing required field is collected interactively via AskUserQuestion.

> **Single-Page Constraint** — the rendered PDF MUST be exactly one A4 page. The template is tuned for up to ~10 line items. If the verification step reports >1 page, apply the shrink ladder in [Step 4.4](#44-verify-single-page-output-required) and regenerate until it fits. Clipped content is a bug, not a fix.

---

## Usage

```bash
# Fully specified
/generate-invoice --client "오누이" --contact "노대원 CRO님"

# Minimal (fully interactive)
/generate-invoice

# International client, no VAT
/generate-invoice --client "Global Corp" --contact "John Smith CEO" --no-vat
```

---

## Workflow

1. Parse `$ARGUMENTS` and collect missing required fields
2. Collect invoice type + line items
3. Generate HTML from `templates/invoice.html` with variable substitution
4. Convert HTML → PDF via Chrome headless, verify single-page
5. Append record to `invoice-records.json`
6. Report result

---

## Design System

Source: `ui-ux-pro-max --design-system` for "B2B invoice / corporate print document".
Selected pattern: **Swiss Modernism 2.0** — strict grid, mathematical spacing, Inter typography, single accent, high contrast. Fits corporate trust-and-authority tone while keeping print complexity low.

To recommend a new variant (e.g., a distinct accent for international invoices), re-run:

```bash
python3 .claude/third-party/skills/ui-ux-pro-max/scripts/search.py \
  "b2b invoice corporate print" --design-system
```

### Brand Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--accent-primary` | `#624DFF` | Table header band, bottom-bar left |
| `--accent-dark` | `#4834CC` | Bottom-bar right |
| `--heading` | `#050042` | Invoice title, client name, TOTAL |
| `--text-body` | `#333333` | Default body text, item titles |
| `--text-muted` | `#666666` | Item detail dash, summary labels, signature labels |
| `--text-label` | `#555555` | Small-caps labels (INVOICE TO, COMPANY) |
| `--divider` | `#dddddd` | Summary divider only |
| `--bg` | `#ffffff` | Page background |
| `--font-primary` | `Inter` | Latin + numerics |
| `--font-fallback-ko` | `Apple SD Gothic Neo`, `Malgun Gothic` | Korean characters |
| `--base-unit` | `8px` | Spacing rhythm (padding / margin multiples) |
| `--line-height-body` | `1.5`–`1.6` | Body and detail lines |

### Contrast Ledger (WCAG AA target ≥4.5:1)

| Pair | Ratio | Verdict |
|------|-------|---------|
| `#050042` on `#ffffff` | 18.1:1 | ✓ AAA |
| `#333333` on `#ffffff` | 12.6:1 | ✓ AAA |
| `#555555` on `#ffffff` | 7.5:1 | ✓ AAA |
| `#666666` on `#ffffff` | 5.7:1 | ✓ AA |
| `#ffffff` on `#624DFF` | 5.4:1 | ✓ AA (table header) |
| `#050042` on `#ffffff` (large) | 18.1:1 | ✓ AAA |

Prior versions used `#999` for labels and decorative dashes (2.85:1) — fails AA. Do not reintroduce.

---

## Step 1: Parse Arguments & Collect Missing Info

Extract from `$ARGUMENTS`:
- `--client` — client company name
- `--contact` — contact person + title
- `--no-vat` — flag, excludes VAT

If `--client` or `--contact` is missing, ask via AskUserQuestion. Use multi-question mode to batch:

- "What is the client company name? (고객사명)"
- "Who is the contact person and their title? (담당자명 + 직함, e.g., 노대원 CRO님)"

Do not proceed to Step 2 until both are collected.

---

## Step 2: Collect Invoice Type & Line Items

### 2.1 Select type

Ask: "What type of invoice is this?"

| Type | Required fields | Example |
|------|-----------------|---------|
| **Monthly Subscription** (월 결제 구독) | Developer composition, monthly amount (만원), contract start date, billing day | Backend 20h/wk + Frontend 20h/wk, 320만원, 11.18 start, 매월 18일 결제 |
| **Project-Based** (프로젝트 단위) | Line items (`Item name: Amount 만원`), optional sub-details | 기획 200, Frontend 500, Backend 400 |
| **Custom** (직접 입력) | Free-form items and amounts — parse into (title, amount) pairs | — |

Collect required fields via AskUserQuestion (multi-question).

### 2.2 Amount input format

Users enter amounts in **만원** (10,000 KRW) for convenience. The invoice MUST display full 원 (KRW) with comma formatting.

| User input | Invoice display |
|------------|-----------------|
| 33만원 | 330,000원 |
| 320만원 | 3,200,000원 |
| 1200만원 | 12,000,000원 |

Conversion: `value_manwon × 10,000`, then format with commas and append `원`. Use the character `원`, not `₩` or `KRW`.

---

## Step 3: Generate HTML

### 3.1 Invoice number

Format: `YYYYMMDD-N` where `N` is a **global continuous counter** (not daily-reset). Seed value = **15** — the company issued 14 invoices outside this system before adoption, so the first invoice produced here is `YYYYMMDD-15`.

1. Read `.claude-project/billing/invoice-records.json`
2. Scan **all** records, extract the numeric suffix `N` from each `invoiceNo`
3. If the file is empty or no records exist → `N = 15`
4. Otherwise → `N = max(existing N) + 1`

Example: if latest record is `20260320-18` → next issued today is `20260421-19`, then `20260421-20`, and so on.

### 3.2 Compute amounts

- **`SUB TOTAL`** — sum of item amounts, **excluding VAT** (pre-tax)
- **`Vat Tax (10%)`** — `SUB TOTAL × 0.10` (row omitted if `--no-vat`)
- **`TOTAL`** — `SUB TOTAL + Vat Tax`, **including VAT** (final amount the client pays). If `--no-vat`, `TOTAL = SUB TOTAL`.

> Never add VAT into `SUB TOTAL`. Never strip VAT from `TOTAL` (except `--no-vat`). The gap between the two rows IS the VAT amount.

### 3.3 Template file

Template: `templates/invoice.html` — single-file HTML + inlined CSS, designed against the Brand Tokens above.

Load the template, substitute placeholders, write to:

- **Directory**: `.claude-project/billing/invoice/` (create if missing)
- **Filename**: `[Invoice] {ClientName}.html`

### 3.4 Placeholder map

| Placeholder | Value | Example |
|-------------|-------|---------|
| `[CLIENT_NAME]` | Client company name | `오누이` |
| `[CONTACT_NAME]` | Contact + title | `노대원 CRO님` |
| `[INVOICE_NO]` | `YYYYMMDD-N` | `20260421-1` |
| `[INVOICE_ITEMS]` | HTML for line items (see 3.5) | — |
| `[SUB_TOTAL]` | Sum in 원, comma-formatted | `3,300,000` |
| `[VAT_ROW]` | VAT row HTML, or empty string if `--no-vat` | See 3.6 |
| `[TOTAL]` | Final total in 원, comma-formatted | `3,630,000` |
| `[DATE_FORMATTED]` | `YYYY. MM. DD` | `2026. 04. 21` |
| `[SEAL_BASE64]` | Seal image Base64 | See 3.8 |
| `<!-- LOGO_SVG -->` | Inline SVG contents | See 3.7 |

### 3.5 `[INVOICE_ITEMS]` HTML

**Monthly subscription — single composite block:**

```html
<div class="table-item">
    <span class="item-title">세부내역</span>
</div>
<div style="display: flex; justify-content: space-between;">
    <div class="item-details">
        <div class="item-detail"><span>월 결제 구독</span></div>
        <div class="item-details" style="margin-left: 48px;">
            <div class="item-detail">백엔드 개발자 주 20시간</div>
            <div class="item-detail">프론트엔드 개발자 주 20시간</div>
        </div>
        <div class="item-detail"><span>계약 시작일 11.18</span></div>
        <div class="item-details" style="margin-left: 48px;">
            <div class="item-detail">매월 18일 결제</div>
        </div>
    </div>
    <div class="item-price" style="padding-top: 4px;">[PRICE]원</div>
</div>
```

**Project-based — one block per line item:**

```html
<div class="table-item">
    <span class="item-title">[Item Name]</span>
    <span class="item-price">[Amount]원</span>
</div>
```

### 3.6 `[VAT_ROW]`

With VAT (default):

```html
<div class="summary-row">
    <span class="summary-label">Vat Tax (10%)</span>
    <span class="summary-value">[VAT_AMOUNT]원</span>
</div>
```

With `--no-vat`: empty string.

### 3.7 Logo SVG — fallback chain

Primary asset ships **skill-local** at `templates/logo.svg` (Potential Inc logo, copied from brand Tier 1). Resolve in order:

1. `templates/logo.svg` (skill-local, Tier 3) — **default, always present**
2. `../../../../resources/brand/logo/logo.svg` (Tier 1) — recovery if local missing
3. Render without logo (silent fallback)

Inline the SVG contents at `<!-- LOGO_SVG -->`.

### 3.8 Seal image — fallback chain

Primary asset ships **skill-local** at `templates/seal.png` (Potential Inc seal, copied from brand Tier 1). Resolve in order:

1. `templates/seal.png` (skill-local, Tier 3) — **default, always present**
2. `../../../../resources/brand/logo/seal.png` (Tier 1) — recovery if local missing
3. `../../../../operation/resources/stamp.png` (Tier 2) — secondary recovery
4. Omit the `<img class="signature-seal">` element

Base64-encode the resolved file and use as `src="data:image/png;base64,{encoded}"`.

> **Global-sync note** — skill-local assets in `templates/` sync cleanly to `~/.claude/skills/invoice/templates/`. Tier 1/2 fallbacks break after sync and exist only for repo-context recovery. Keep `templates/logo.svg` + `templates/seal.png` checked in to avoid global-sync issues. See `operation/CLAUDE.md` → Shared Asset Tiers → Global-sync caveat.

---

## Step 4: Convert to PDF

### 4.1 Chrome headless

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless \
  --disable-gpu \
  --print-to-pdf="[OUTPUT_PDF_PATH]" \
  --no-margins \
  "file://[ABSOLUTE_HTML_PATH]"
```

### 4.2 Output

`.claude-project/billing/invoice/[Invoice] {ClientName}.pdf`

### 4.3 Error: conversion fails

Report:

```
Error: PDF conversion failed. Verify Google Chrome is installed.
HTML saved at: [HTML_PATH]
```

### 4.4 Verify single-page output (REQUIRED)

```bash
python3 -c "from pypdf import PdfReader; print(len(PdfReader('[PDF_PATH]').pages))"
```

If result > 1, apply this shrink ladder and regenerate until page count == 1:

1. `.page` padding-top: `28px → 20px → 16px`
2. `.table-item` margin-bottom: `7px → 5px → 4px`
3. `.info-section` / `.header` margin-bottom: `22px → 16px → 12px`
4. Scale all font-sizes by `0.9×` (e.g., `14 → 13`, `15 → 14`, `20 → 18`)

Do not report success until page count == 1. `overflow: hidden` on `.page` clips overflow but is not a fix — content must genuinely fit.

---

## Step 5: Save to Invoice Records

Append a record to `.claude-project/billing/invoice-records.json` (JSON array; create `[]` if file missing).

### Record schema

```json
{
  "invoiceNo": "YYYYMMDD-N",
  "client": "Client company name",
  "contact": "Contact person name",
  "type": "월결제 | 프로젝트 | 유지보수 | ...",
  "items": [
    { "title": "Item description", "amount": 33 }
  ],
  "subTotal": 33,
  "vat": 3.3,
  "total": 36.3,
  "vatIncluded": true,
  "date": "YYYY-MM-DD",
  "files": {
    "html": ".claude-project/billing/invoice/[Invoice] ClientName.html",
    "pdf":  ".claude-project/billing/invoice/[Invoice] ClientName.pdf"
  }
}
```

Amounts stored in **만원** (same unit the user enters), to match how subsequent analytics aggregate.

Write back pretty-printed (2-space indent).

---

## Step 6: Report Result

```
Invoice generated successfully.

HTML: .claude-project/billing/invoice/[Invoice] {ClientName}.html
PDF:  .claude-project/billing/invoice/[Invoice] {ClientName}.pdf

Client: [CLIENT_NAME]
Contact: [CONTACT_NAME]
Total: [TOTAL]원 (VAT included/excluded)

Preview by opening the HTML file in a browser.
```

---

## Print Pre-Delivery Checklist

Verify before reporting success:

- [ ] PDF page count == 1 (Step 4.4)
- [ ] No overflow clipping — content fits naturally, not hidden by `overflow: hidden`
- [ ] All text meets WCAG AA (≥4.5:1) — see Contrast Ledger; no `#999` on white for meaningful text
- [ ] Brand tokens match — spot-check `#624DFF` table header, `#050042` title, `#4834CC` bottom-bar right
- [ ] Inter loaded; Apple SD Gothic Neo / Malgun Gothic fallback present for Korean glyphs
- [ ] Logo and seal resolved through the documented fallback chain, or gracefully omitted
- [ ] Currency format — `원` suffix, comma thousands, 만원→원 conversion applied
- [ ] `SUB TOTAL` = pre-VAT, `TOTAL` = post-VAT (never swap)
- [ ] Invoice number = `max(existing N) + 1`, seeded at 15 on empty records
- [ ] `invoice-records.json` appended with the new record
- [ ] Header title renders as `Invoice` (not `견적서`)
- [ ] Company block shows Seoul address, `070-4578-8349`, `contact@potentialai.com`

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Client / contact / type / items missing | Ask via AskUserQuestion |
| Logo not found (Tiers 1+3) | Render without logo |
| Seal not found (Tiers 2+3) | Omit seal image |
| PDF conversion fails | Report error, provide HTML path |
| PDF > 1 page | Apply Step 4.4 shrink ladder, regenerate |

---

## Examples

### Monthly Subscription

```bash
/generate-invoice --client "오누이" --contact "노대원 CRO님"
```

→ Type: Monthly Subscription → 월 결제 구독 320만원 (Backend 20h/wk + Frontend 20h/wk)
→ Output: `.claude-project/billing/invoice/[Invoice] 오누이.pdf`

### Project-Based

```bash
/generate-invoice --client "테스트회사" --contact "홍길동 PM님"
```

→ Type: Project-Based → 기획 200만원, Frontend 500만원, Backend 400만원
→ Output: `.claude-project/billing/invoice/[Invoice] 테스트회사.pdf`

### Fully Interactive

```bash
/generate-invoice
```

→ Asks for: client, contact, type, items, amounts

### International (No VAT)

```bash
/generate-invoice --client "Global Corp" --contact "John Smith CEO" --no-vat
```

→ VAT row omitted, `TOTAL = SUB TOTAL`
→ Output: `.claude-project/billing/invoice/[Invoice] Global Corp.pdf`
