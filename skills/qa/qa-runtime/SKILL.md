---
name: qa-runtime
description: "Run Playwright-based browser QA — actionability, console errors, modals, a11y, CLS, user flows, form smoke, responsive"
user-invocable: true
argument-hint: "[--frontend|--dashboard] [--layer=actionability|console|modal|accessibility|performance|flows|forms|responsive] [--critical] [--viewport=mobile|multi-device]"
---

# QA Runtime — Browser-Based Runtime Testing

## Purpose

Unlike code-level QA skills that analyze source statically, this skill **runs Playwright in a real browser** to catch visual/interaction bugs:
- Buttons covered by overlapping elements (z-index, overflow)
- Forms that can't be submitted (submit button off-screen)
- Modals that won't close (ESC broken, no close button)
- JS runtime errors during page navigation
- Layout shift (CLS) causing click-miss issues
- Keyboard navigation gaps (unreachable elements)
- Form validation gaps (empty submit accepted)
- Text overflow/wrapping issues (unintended line breaks, truncation, container overflow)
- Responsive layout breakage across real device viewports (Galaxy, iPhone, Pixel)

## Usage

```
/qa-runtime                              # Full 7-layer audit, both apps
/qa-runtime --frontend                   # Primary frontend app only
/qa-runtime --dashboard                  # Admin dashboard only
/qa-runtime --layer=actionability        # Specific layer only
/qa-runtime --layer=flows                # User flow scenarios only
/qa-runtime --critical                   # Only pages tagged 'critical'
/qa-runtime --viewport=mobile            # Mobile viewport only (single generic viewport)
/qa-runtime --viewport=multi-device      # Test across 6 real device viewports (Galaxy, iPhone, Pixel)
/qa-runtime --layer=responsive           # Responsive-only audit across all device viewports
/qa-runtime --layer=responsive --frontend # Responsive audit on frontend app only
```

## Prerequisites

1. Backend must be running (auto-detect port from project config)
2. Frontend dev servers must be running (auto-detect ports from project config)
3. Test users must exist in database (check CLAUDE.md or .env.test for credentials)
4. Optional: Install axe-core for Layer 4 (use detected package manager: `npm install -D @axe-core/playwright` / `yarn add -D` / `pnpm add -D` / `bun add -D`)
5. **Reference:** `qa-shared/reference.md` for standardized scoring, framework detection tables, and output formatting

## Execution Mode

This skill performs **runtime browser testing**. For static code analysis, use `/qa-scan` instead.

## 8 Layers

| # | Layer | What It Catches | Severity | Gate |
|---|-------|----------------|----------|------|
| L1 | **Actionability** | Covered/hidden/disabled/zero-size interactive elements, dead clicks, truncated text, **text overflow/wrapping** | Critical | |
| L2 | **Console Errors** | JS errors, unhandled rejections, failed/slow network requests | Critical | |
| L3 | **Modal Lifecycle** | Modals that won't open/close, broken ESC, focus trap failures | High | |
| L4 | **Accessibility** | WCAG 2.0 AA violations (axe-core), keyboard navigation gaps | Medium | |
| L5 | **CLS & Performance** | Layout shifts > 0.25, LCP > 4000ms | Medium | |
| L6 | **User Flows** | Broken user journeys (login→navigate→interact→verify) | High | |
| L7 | **Form Smoke** | Form detection, smart-fill JS errors, validation gaps | High | |
| L8 | **Responsive (Multi-Device)** | Layout breakage, overflow, touch target sizing, text wrapping across real device viewports | High | is_mobile_target |

## Execution Steps

### Step 1: Check server status
```bash
# Verify ports are listening (auto-detect ports from project config / package.json scripts)
# Example:
curl -s -o /dev/null -w "%{http_code}" http://localhost:{backend-port}/api || echo "Backend not running"
curl -s -o /dev/null -w "%{http_code}" http://localhost:{frontend-port} || echo "Frontend not running"
# Check all frontend apps as detected from project structure
```

### Step 2: Parse arguments and determine scope

| Argument | Effect |
|----------|--------|
| `--frontend` | Only run in the primary frontend app |
| `--dashboard` | Only run in the admin/dashboard app |
| `--layer=X` | Only run `X.spec.ts` (actionability, console, modal, accessibility, performance, flows, forms, **responsive**) |
| `--critical` | Pass `--grep "critical"` to Playwright |
| `--viewport=mobile` | Pass `--project=mobile-chrome` (single generic mobile viewport) |
| `--viewport=multi-device` | Run all layers across 6 real device viewports (see Device Matrix below) |
| No args | Run all layers in both apps with desktop viewport |

### Step 3: Run Playwright tests

For each target app (frontend and/or dashboard):

```bash
cd <app-dir>

# Build the test command based on arguments
npx playwright test test/tests/screen-qa/ \
  --reporter=list \
  --reporter=./test/utils/screen-qa/reporter.ts \
  [layer filter] [grep filter] [project filter]
```

Layer filter examples:
- `--layer=actionability` → `test/tests/screen-qa/actionability.spec.ts`
- `--layer=console` → `test/tests/screen-qa/console-errors.spec.ts`
- `--layer=modal` → `test/tests/screen-qa/modal-lifecycle.spec.ts`
- `--layer=accessibility` → `test/tests/screen-qa/accessibility.spec.ts`
- `--layer=performance` → `test/tests/screen-qa/performance.spec.ts`
- `--layer=flows` → `test/tests/screen-qa/user-flows.spec.ts`
- `--layer=forms` → `test/tests/screen-qa/form-smoke.spec.ts`
- `--layer=responsive` → `test/tests/screen-qa/responsive.spec.ts`

#### L1 Text Overflow/Wrapping Detection

Within L1 Actionability, check every visible text element for unintended overflow or wrapping:

```javascript
// For each page, evaluate all visible text elements
const textIssues = await page.evaluate(() => {
  const issues = [];
  const elements = document.querySelectorAll(
    'button, a, label, th, td, h1, h2, h3, h4, h5, h6, span, p, li, [role="tab"], [role="menuitem"]'
  );

  for (const el of elements) {
    const rect = el.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) continue;

    // Check 1: scrollWidth > clientWidth (horizontal overflow)
    if (el.scrollWidth > el.clientWidth + 1) {
      issues.push({
        type: 'horizontal-overflow',
        text: el.textContent?.trim().slice(0, 50),
        tag: el.tagName,
        selector: el.closest('[class]')?.className?.split(' ').slice(0, 3).join('.'),
        scrollWidth: el.scrollWidth,
        clientWidth: el.clientWidth,
      });
    }

    // Check 2: scrollHeight > clientHeight (vertical overflow / unintended wrapping)
    if (el.scrollHeight > el.clientHeight + 1) {
      issues.push({
        type: 'vertical-overflow',
        text: el.textContent?.trim().slice(0, 50),
        tag: el.tagName,
        selector: el.closest('[class]')?.className?.split(' ').slice(0, 3).join('.'),
        scrollHeight: el.scrollHeight,
        clientHeight: el.clientHeight,
      });
    }

    // Check 3: Single-line elements that wrapped to multi-line
    const style = getComputedStyle(el);
    const lineHeight = parseFloat(style.lineHeight) || parseFloat(style.fontSize) * 1.2;
    if (
      ['button', 'a', 'th', 'label'].includes(el.tagName.toLowerCase()) ||
      el.getAttribute('role') === 'tab' ||
      el.getAttribute('role') === 'menuitem'
    ) {
      if (rect.height > lineHeight * 1.8) {
        issues.push({
          type: 'unintended-wrap',
          text: el.textContent?.trim().slice(0, 50),
          tag: el.tagName,
          actualHeight: rect.height,
          expectedMaxHeight: lineHeight * 1.5,
        });
      }
    }
  }
  return issues;
});
```

**Severity rules for text overflow:**
| Issue Type | Severity | Rationale |
|-----------|----------|-----------|
| Button/tab/menu text wrapping to 2+ lines | **Critical** | Breaks layout, may hide text |
| Table header text overflowing | **High** | Column misalignment, unreadable headers |
| Label text overflowing its container | **High** | Form usability degraded |
| Paragraph/body text horizontal overflow | **Medium** | Content unreadable without scroll |
| Text truncated without ellipsis or tooltip | **Medium** | Information loss with no affordance |

**Allowlist:** Elements with explicit `truncate`, `line-clamp-*`, `overflow-hidden`, `text-ellipsis`, or `whitespace-nowrap` classes are intentional — skip these unless their container is too narrow to show meaningful content (< 3 characters visible).

#### L8 Responsive (Multi-Device) Detection

This layer runs the same page across multiple real device viewports to catch responsive layout issues.

**Device Matrix:**

| # | Device | Viewport (px) | DPR | Category | Playwright Device |
|---|--------|--------------|-----|----------|-------------------|
| 1 | Galaxy S9+ | 320 x 658 | 4.0 | Android Small | `Galaxy S9+` |
| 2 | Galaxy S24 | 360 x 780 | 3.0 | Android Standard | `Galaxy S24` (custom) |
| 3 | iPhone SE | 375 x 667 | 2.0 | iOS Small | `iPhone SE` |
| 4 | iPhone 14 | 390 x 844 | 3.0 | iOS Standard | `iPhone 14` |
| 5 | iPhone 14 Pro Max | 430 x 932 | 3.0 | iOS Large | `iPhone 14 Pro Max` |
| 6 | Pixel 7 | 412 x 915 | 2.625 | Android Large | `Pixel 7` |

**Custom device definition** (for devices not in Playwright's built-in list):
```javascript
const customDevices = {
  'Galaxy S24': {
    userAgent: 'Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    viewport: { width: 360, height: 780 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  },
};
```

**Per-device checks:**

1. **Horizontal overflow** — `document.documentElement.scrollWidth > document.documentElement.clientWidth`
   - Any page that scrolls horizontally on mobile is a Critical issue
2. **Touch target size** — All interactive elements must be >= 44x44px (WCAG 2.5.8)
   - Buttons, links, inputs smaller than 44px on any device → High
3. **Text wrapping** — Reuse L1 text overflow checks at each viewport size
   - Text that fits on desktop but wraps/overflows on a specific device → High
4. **Content clipping** — Elements with `overflow: hidden` that clip visible content
   - Important content invisible on smaller screens → Critical
5. **Fixed position overlap** — Fixed headers/footers/FABs that overlap main content
   - Especially BottomNav covering content on short viewports (iPhone SE) → Critical
6. **Font readability** — Text below 11px rendered size at device DPR
   - `computedFontSize * deviceScaleFactor` check → Medium
7. **Viewport-specific screenshots** — Capture full-page screenshot per device for visual review
   - Saved to `test/reports/screen-qa/screenshots/{device-name}/{page-name}.png`

**Execution flow for `--viewport=multi-device` or `--layer=responsive`:**

```bash
# For each device in the matrix:
npx playwright test test/tests/screen-qa/responsive.spec.ts \
  --project="{device-name}" \
  --reporter=list \
  --reporter=./test/utils/screen-qa/reporter.ts
```

**Output format for responsive results:**

```
### L8 Responsive (Multi-Device) Results

| Page | Galaxy S9+ | Galaxy S24 | iPhone SE | iPhone 14 | iPhone 14 Pro Max | Pixel 7 |
|------|-----------|-----------|-----------|-----------|-------------------|---------|
| Login | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Dashboard | ✅ | ✅ | ⚠️ wrap | ✅ | ✅ | ✅ |
| Exercise List | ❌ h-scroll | ❌ h-scroll | ❌ h-scroll | ✅ | ✅ | ⚠️ wrap |
| Chat | ✅ | ✅ | ⚠️ overlap | ✅ | ✅ | ✅ |

Legend: ✅ Pass | ⚠️ Warning | ❌ Critical

#### Device-Specific Issues
1. **[Galaxy S9+] Exercise List** — Page scrolls horizontally (scrollWidth: 412, clientWidth: 320)
2. **[iPhone SE] Chat** — BottomNav overlaps last message (fixed position conflict)
3. **[iPhone SE] Dashboard** — "운동 처방 관리" button text wraps to 2 lines

#### Screenshots
- Galaxy S9+: `test/reports/screen-qa/screenshots/galaxy-s9-plus/`
- iPhone SE: `test/reports/screen-qa/screenshots/iphone-se/`
- [... all devices ...]
```

### Step 4: Read and summarize results

After tests complete:
1. Read the HTML report at `test/reports/screen-qa/index.html`
2. Read JSON results at `test/reports/screen-qa/results.json`
3. Present a summary table to the user:
   - Layer-by-layer pass/fail counts
   - List of all failed tests with error messages
   - Suggest fixes for common issues

### Step 5: Output format

```
## QA Runtime Results

### Summary
| Layer | Pass | Fail | Skip |
|-------|------|------|------|
| Actionability | 20/22 | 2 | 0 |
| Console Errors | 22/22 | 0 | 0 |
| ...

### Critical Issues (fix first)
1. **[Actionability] Item Detail Page** — "Submit" button covered by toast container
2. **[CLS] Admin Dashboard** — CLS 0.32 exceeds 0.25 threshold

### Warnings (review)
- ...

### Reports
- HTML: `{app-dir}/test/reports/screen-qa/index.html`
- JSON: `{app-dir}/test/reports/screen-qa/results.json`
```

## File Locations

### Frontend App
```
{frontend-dir}/test/
├── utils/screen-qa/
│   ├── config.ts                  # Allowlists, thresholds
│   ├── route-registry.ts          # All routes + metadata
│   ├── flow-registry.ts           # User flow scenarios
│   ├── actionability-checker.ts   # DOM audit engine (includes text overflow detection)
│   ├── console-monitor.ts         # Console/network monitor
│   ├── cls-measurer.ts            # CLS + LCP measurement
│   ├── form-detector.ts           # Form auto-detection
│   ├── keyboard-auditor.ts        # Tab order + focus check
│   ├── device-matrix.ts           # Device viewport definitions for multi-device testing
│   └── reporter.ts                # Custom HTML reporter
└── tests/screen-qa/
    ├── actionability.spec.ts      # L1 (includes text overflow/wrapping checks)
    ├── console-errors.spec.ts     # L2
    ├── modal-lifecycle.spec.ts    # L3
    ├── accessibility.spec.ts      # L4
    ├── performance.spec.ts        # L5
    ├── user-flows.spec.ts         # L6
    ├── form-smoke.spec.ts         # L7
    └── responsive.spec.ts         # L8 (multi-device responsive audit)
```

### Additional Frontend Apps — same structure in each app's `test/` directory

## Maintenance

### Adding new routes
Edit `route-registry.ts` in the relevant app. Add:
- `path`, `name`, `auth`
- `navigationSteps` if dynamic route
- `hasModal` if page has modals
- `hasForms` if page has forms
- `tags` for filtering

### Adding new user flows
Edit `flow-registry.ts`. Follow existing step patterns.

### Adjusting thresholds
Edit `config.ts`:
- `consoleAllowlist` — patterns to ignore in console monitoring
- `performanceThresholds` — CLS/LCP limits
- `actionabilityConfig` — touch target size, selectors

### Adding/updating devices
Edit `device-matrix.ts` in the relevant app. Each device entry needs:
- `name` — display name for reports
- `viewport` — `{ width, height }`
- `deviceScaleFactor` — pixel density
- `isMobile`, `hasTouch` — capability flags
- `userAgent` — realistic UA string for the device

When a new popular device launches (e.g., Galaxy S25, iPhone 16), add it and remove obsolete entries to keep the matrix at 6-8 devices.

### Skipping individual elements
Add `data-screen-qa-ignore` attribute to any element that should be excluded from actionability audit.
