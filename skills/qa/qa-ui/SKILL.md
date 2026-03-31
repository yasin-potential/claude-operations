---
name: qa-ui
description: "Audit UI/UX layer — states, buttons, modals, lists, navigation, accessibility, layout, performance, and i18n with subcategory filtering"
user-invocable: true
argument-hint: "[module] [--sub states|buttons|modals|lists|nav|a11y|layout|perf|i18n] [--check N]"
---

# QA UI — UI/UX Layer Auditor

Comprehensive UI/UX audit covering all frontend interaction patterns. Consolidates 8 specialized skills into subcategories.

## Execution Mode

- **Standalone** (`/qa-ui [module]`): Run all subcategories. Use `--sub` to filter.
- **Via qa-scan** (`/qa-scan --check ui`): qa-scan uses these checks for the UI layer.

### Subcategory Filtering

```bash
/qa-ui                          # All subcategories
/qa-ui --sub states             # Only loading/error/empty states
/qa-ui --sub lists,modals       # Multiple subcategories
/qa-ui --sub nav                # Only navigation checks
```

Shared conventions: see `qa-shared/reference.md`.

## Tier 1: Checklist

### States (from qa-states)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| S-01 | Missing initial load indicator | **High** | | Data fetch has no skeleton/spinner shown during `isLoading`/`isPending` |
| S-02 | Missing refetch indicator | **Low** | | `isFetching` while data exists shows no subtle refresh indicator |
| S-03 | Missing mutation loading | **High** | | Mutation `isPending` not disabling/showing spinner on submit button |
| S-04 | Missing pagination loading | **Medium** | | No loading indicator during page change in paginated list |
| S-05 | Missing loading timeout | **Medium** | | Spinner spins forever with no timeout message or retry guidance |
| S-06 | Layout shift on load | **Low** | | Spinner causes content jump — skeleton not matching content dimensions (verify via qa-screen CLS check) |
| S-07 | Content disappears on refetch | **High** | | Data disappears during refetch instead of showing stale content with refresh indicator |
| S-08 | Missing Error Boundary | **Critical** | | No Error Boundary wrapping the component tree |
| S-09 | Missing per-fetch error UI | **High** | | `isError` state has no rendered error message |
| S-10 | Generic error message | **Medium** | | Error shows "Something went wrong" instead of specific API message |
| S-11 | Missing retry button | **Medium** | | Error state has no button to call `refetch()` / re-trigger fetch |
| S-12 | No network error handling | **Medium** | | No offline detection, timeout handling, or network-specific error UI |
| S-13 | Missing mutation error feedback | **High** | | Mutation failure shows no toast/alert/inline error message |
| S-14 | No empty state | **High** | | `data.map(...)` with no empty check — nothing rendered when list is empty |
| S-15 | Same message for no-data and no-results | **Medium** | | Single "No data" for both initial empty and filtered-empty states |
| S-16 | Empty state shown during loading | **High** | | `data.length === 0` checked before `isLoading` — flash of empty state |
| S-17 | Missing CTA in empty state | **Low** | | Empty state has text but no "Create your first item" action button |
| S-18 | Infinite loading loop | **Critical** | | Missing dependency array, fetch in render body, or watcher modifying its own dependency |
| S-19 | Missing optimistic rollback | **High** | | `onMutate` updates cache but `onError` does not revert to previous value |
| S-20 | Stale cache after mutation | **High** | | No `invalidateQueries()` / `refresh()` after mutation success |
| S-20a | Invalidation key mismatch | **High** | | Mutation's `invalidateQueries`/`setQueryData` key doesn't match the `useQuery` queryKey on the same page/module — cache appears refreshed but wrong query is invalidated |
| S-21 | Real-time cache inconsistency | **Critical** | has_realtime | Socket event updates item cache but parent list cache not invalidated |
| S-22 | Stale closure / race condition | **Medium** | | `useEffect` + `setState` without cleanup or AbortController |
| S-23 | Missing abort on unmount | **Medium** | | No `return () => controller.abort()` in useEffect cleanup |
| S-24 | Loading indicator type inconsistent | **Low** | | Same data type (e.g., user list) uses skeleton loader on one page but spinner on another — inconsistent loading UX across the app |
| S-25 | Optimistic update feedback missing | **Medium** | | Mutation uses optimistic update (`onMutate` sets cache) but UI doesn't immediately reflect the change — list/count only updates after server response, defeating the purpose of optimistic update |
| S-26 | No offline state handling | **High** | is_mobile_target | App has no `navigator.onLine` or `online`/`offline` event listeners. When mobile network drops (common on cellular), users see no feedback — requests silently fail or hang indefinitely. **Scan**: Search for `navigator.onLine`, `addEventListener('online'`, `addEventListener('offline'` |
| S-27 | No network error recovery UI | **High** | is_mobile_target | Network errors show generic error or nothing. Mobile apps must show retry-able error states with clear "retry" action when requests fail due to connectivity. **Scan**: Check error boundary components and React Query `onError` handlers for user-facing retry UI |

### Buttons (from qa-buttons)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| B-01 | Dead button | **Critical** | | Button with no onClick handler and no form submission role |
| B-02 | Broken route link | **High** | | Link to route not defined in router config |
| B-03 | Missing loading state | **High** | | Async action button with no loading/disabled state during operation |
| B-04 | Missing confirmation | **Medium** | | Delete/destructive button with no confirmation dialog |
| B-05 | Missing disabled state | **Medium** | | Submit button not disabled when form is invalid |
| B-06 | Empty href | **High** | | Anchor with href="#" or empty/javascript href |
| B-07 | Missing aria-label | **Medium** | | Icon-only button with no accessible name |
| B-08 | Non-button clickable | **Medium** | | div/span with onClick but no role="button" or keyboard support |
| B-09 | Button hover/active state missing | **Medium** | | Interactive button has no visual change on hover (`hover:`) or active (`active:`) — user cannot tell it's clickable. Check for `hover:bg-*`, `hover:opacity-*`, or `active:scale-*` classes |
| B-10 | Touch target too small | **High** | | Button/link click area < 44×44px (WCAG 2.2 minimum). Threshold: `elderly_ux ? 48px : 44px`. Check `min-h-*`, `min-w-*`, `p-*` classes on small icon buttons |
| B-11 | Missing tap highlight removal | **High** | is_mobile_target | No `-webkit-tap-highlight-color: transparent` in global CSS. iOS Safari/WebView shows blue flash overlay on every tap of buttons and links. **Scan**: Check global CSS files for `-webkit-tap-highlight-color` declaration |
| B-12 | Interactive element text selectable | **Medium** | is_mobile_target | Buttons, nav items, and other interactive elements lack `user-select: none`. Tapping on mobile triggers text selection instead of action. **Scan**: Check global CSS for `user-select: none` on `button`, `a`, `nav`, `[role="button"]` selectors |

### Modals (from qa-modal)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| M-01 | Missing close path | **Critical** | | Modal open trigger has no matching close path (X button, overlay, ESC, cancel) |
| M-02 | Missing focus trap | **High** | | Custom modal with no focus trap — Tab key moves focus outside modal |
| M-03 | Missing focus return | **Medium** | | Focus does not return to trigger element when modal closes |
| M-04 | Missing scroll lock | **High** | | Body scroll not disabled when modal is open — background scrolls behind overlay |
| M-05 | Missing iOS scroll fix | **Medium** | platform_ios | No `position: fixed` + scroll offset pattern for iOS body scroll lock |
| M-06 | ESC key not handled | **High** | | Custom modal has no ESC key close handler |
| M-07 | Nested ESC order wrong | **Medium** | | ESC closes parent modal instead of topmost nested modal |
| M-08 | Overlay close without dirty check | **High** | | Form modal closes on overlay/backdrop click without "Unsaved changes?" confirmation |
| M-09 | Missing dirty check on close | **High** | | Closing modal with modified form shows no unsaved changes confirmation |
| M-10 | Premature close on submit | **High** | | Modal closes before API response — error display lost |
| M-11 | Missing double-submit prevention | **Medium** | | Submit button not disabled during API call in modal form |
| M-12 | State not reset on close | **High** | | Form values, errors, or loading states not cleared when modal closes and reopens |
| M-13 | Missing role="dialog" | **Medium** | | Custom modal container missing `role="dialog"` attribute |
| M-14 | Missing aria-modal | **Medium** | | Modal missing `aria-modal="true"` attribute |
| M-15 | Missing aria-labelledby | **Medium** | | Modal not linked to its title via `aria-labelledby` |
| M-17 | No mobile adaptation | **Medium** | is_mobile_target | Desktop-sized dialog on mobile viewport — may be cut off or hard to dismiss |
| M-18 | Nested modal z-index issue | **Medium** | | Nested modals not stacking correctly — child modal behind parent overlay |
| M-19 | Modal header not sticky on scroll | **Medium** | | Modal with scrollable content — title and close button scroll away when user scrolls down. Header should use `sticky top-0` to remain visible |
| M-20 | Confirmation button order incorrect | **Medium** | | Destructive confirmation dialog has cancel/destructive buttons in wrong order. Convention: cancel (secondary, left) → destructive action (primary, right). Reversed order increases accidental destructive clicks |

#### Radix / Headless UI Guard

Before flagging checks M-02, M-03, M-04, M-06, M-13, M-14, determine if the modal is built on a managed primitive (Radix Dialog/AlertDialog/Sheet, Headless UI Dialog, Ark UI Dialog). These primitives auto-handle focus trap, focus return, scroll lock, ESC dismiss, `role="dialog"`, and `aria-modal="true"`. **SKIP those checks for primitive-based modals.** Only flag custom `div`/`Portal`-based modals that implement their own open/close logic.

### Lists (from qa-list)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| L-01 | Missing default sort | **High** | | List renders in arbitrary order — no default sort column specified |
| L-02 | Sort UI disconnected | **High** | | Sortable header exists but missing sort direction/onClick props |
| L-03 | Missing search | **Medium** | | List page has no search input for filtering |
| L-04 | Missing search debounce | **High** | | Search input has no debounce — breaks Korean/CJK IME composition |
| L-05 | Missing column resize | **Low** | | Table has no column resize support — columns are fixed width |
| L-06 | Missing loading state | **High** | | No loading indicator while data is being fetched |
| L-07 | Missing empty state | **Medium** | | No message shown when list has zero results |
| L-08 | Missing filter reset | **Medium** | | Filters exist but no way to reset/clear them |
| L-09 | Single-select filter only | **Low** | | Filter that should support multi-select only allows single selection (SKIP — design decision) |
| L-10 | Sorted data not used | **High** | | Sort hook called but template still maps over unsorted array |
| L-11 | Missing result count | **Medium** | | No "showing X of Y" count display |
| L-12 | Multi-line toolbar | **Low** | | Search, tabs, and filters on separate lines — wastes vertical space |
| L-13 | Unfillable table column | **High** | | Table displays a data field that cannot be entered in any create/edit form — column is always empty |
| L-14 | List-detail status mismatch | **High** | | Status/badge in list row uses different logic or styling than detail page |
| L-14a | List-detail count mismatch | **Critical** | | Aggregated count in list row (e.g., "3명") uses different filter conditions than the detail page query for the same data. **Scan**: Find columns displaying counts derived from related entities. Trace the list API's count logic and the detail API's query logic — compare WHERE/filter clauses (especially `isActive`, `status`, `deletedAt`, role filters). If one includes inactive/soft-deleted records and the other excludes them, the count will not match the detail view. |
| L-15 | Filter component type mismatch | **High** | | Status filter uses Select dropdown instead of inline button group — inconsistent with other list pages |
| L-16 | Filter state not in URL | **High** | frontend_spa | Filter/sub-tab state stored in local state only — lost on browser back navigation |
| L-17 | Missing full-stack tracing | **High** | | Frontend pagination/sort/filter params don't match backend query API |
| L-18 | URL state not synced | **Medium** | frontend_spa | Pagination/sort/filter state lost on page refresh (not in URL params) |
| L-18a | URL param default-setter mismatch | **High** | frontend_spa | Setter deletes a URL param to "reset" it, but the fallback value (`param || default`) is conditional (e.g., differs per tab/context), causing the action to silently revert to an unintended state |
| L-19 | Missing data freshness strategy | **Medium** | | No refetch/revalidation after mutations, stale data shown |
| L-20 | Inline edit issues | **Medium** | | Inline edit mode lacks save/cancel, dirty check, or optimistic update |
| L-21 | Missing export functionality | **Low** | | List page with >50 items has no CSV/Excel export option |
| L-22 | Expanded row index vs entity field | **High** | | Expandable sub-table uses `index + 1` for row numbering instead of entity's actual field |
| L-23 | Hardcoded fake list items | **High** | | List contains items fabricated in frontend code — fake entries mixed with real data |
| L-24 | Scroll position not restored | **Medium** | | Navigate to detail page → browser back to list: scroll resets to top instead of previous position. Check for `scrollRestoration`, `useScrollPosition`, or manual scroll save/restore |
| L-25 | Batch action affordance missing | **Medium** | | Batch delete/action endpoint exists but list has no row selection checkboxes, no select-all, or no indeterminate state on partial selection |
| L-26 | Infinite scroll vs pagination inconsistent | **Low** | | Similar list pages within the same app use different pagination strategies (infinite scroll vs numbered pagination) — confusing UX pattern |

### Navigation (from qa-back-nav)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| N-01 | Replace vs push classification | **High** | | All `router.replace()` calls reviewed — replace should only be used for auth guards, post-delete, logout. Flagged if used in normal navigation |
| N-02 | Back button handler quality | **Critical** | | Back/return buttons must use `router.back()` / `navigate(-1)`, not hardcoded paths. `window.location.href` in back button is Critical |
| N-03 | Auth guard redirect method | **High** | | Auth guards that redirect unauthenticated users must use `replace` (not `push`) so login page does not appear in back history |
| N-04 | After-action redirect correctness | **High** | | Post-delete must use `replace` (back to deleted resource = 404). Post-logout must use `replace`. Post-create can use `push` |
| N-05 | Redirect chain detection | **Medium** | | Sequential redirects > 2 hops corrupt the history stack. Flag redirect-inside-redirect patterns |
| N-06 | Mobile back key coverage | **High** | is_mobile_target | React Native `BackHandler`, Capacitor `App.addListener('backButton')`, Flutter InAppWebView `canGoBack()`/`goBack()`, Cordova `backbutton` event, or web `popstate` listener present for modals/drawers |
| N-07 | Modal back-close pattern | **Medium** | is_mobile_target | Modals/drawers should push a history entry on open and close on `popstate`, so back key closes modal instead of navigating away |
| N-09 | Deep link back behavior | **Medium** | | Pages accessed via deep link (no prior history) must have a meaningful back destination, not an empty history stack |
| N-10 | Unsaved changes warning on navigation | **High** | | Page with dirty form (edited fields) allows browser back / link click without confirmation dialog — user loses data silently. Check for `useBlocker`, `beforeunload`, or `Prompt` component |
| N-11 | Query params lost on back | **Medium** | frontend_spa | Search/filter/sort state stored in component state only, not in URL params — browser back resets all filters to default. State should be persisted in URL via `useSearchParams` |
| N-12 | Scroll position not saved before navigation | **Medium** | | User's scroll position in list not stored before navigating to detail — returning via back shows top of page instead of previous scroll position |
| N-13 | WebView wrapper back-button deduplication | **Critical** | has_native_wrapper | Flutter/native WebView apps must not handle back button in multiple layers simultaneously (e.g., PopScope + GoRouter onExit + WillPopScope). Only one layer should own the exit dialog logic — duplicate handlers cause double dialogs where the first confirm appears to do nothing |
| N-14 | App exit uses platform API | **Critical** | has_native_wrapper | Root-level WebView screen must use `SystemNavigator.pop()` (Android) or `exit(0)` (iOS) to exit — not `Navigator.of(context).pop()` which leaves a black screen when no parent route exists |
| N-15 | WebView onJsBeforeUnload suppression | **High** | has_native_wrapper | InAppWebView must handle `onJsBeforeUnload` to suppress the default English browser dialog. Back navigation should be controlled by the native wrapper, not browser-level beforeunload (Vite dev server sets beforeunload for HMR) |
| N-16 | WebView session boundary on re-login | **Critical** | has_native_wrapper | In WebView-wrapped SPAs, logout→login creates a new session but the WebView back history still contains previous user's pages. The back button handler must inspect history via `getCopyBackForwardList()` and block navigation past login/auth page boundaries. Without this, pressing back after re-login exposes previous user's data |
| N-17 | WebView history clear on auth transition | **High** | has_native_wrapper | After successful login in a WebView-wrapped app, the native layer should detect the auth-page→home transition (via `onUpdateVisitedHistory`) and clear or fence the navigation history (e.g., `replaceState`) to prevent stale session pages from being reachable |

#### Navigation Framework Detection

| Signal | Framework |
|--------|-----------|
| `import { useNavigate } from 'react-router-dom'` or `useHistory` | React Router v5/v6 |
| `import { useRouter } from 'next/router'` | Next.js Pages Router |
| `import { useRouter } from 'next/navigation'` | Next.js App Router |
| `import { useRouter } from 'vue-router'` | Vue Router |
| `import { Router, ActivatedRoute } from '@angular/router'` | Angular Router |
| `navigateTo()` or `import { useRouter } from '#app'` | Nuxt 3 |
| `import { goto } from '$app/navigation'` | SvelteKit |
| `import { useRouter } from '@tanstack/react-router'` | TanStack Router |
| `flutter_inappwebview` or `InAppWebView` | Flutter WebView wrapper |
| `PopScope` or `WillPopScope` | Flutter back-button handling |

#### After-Action Redirect Rules

| Scenario | Expected Method | Wrong Method → Issue |
|----------|----------------|---------------------|
| After create (POST) | `push` | — |
| After delete | `replace` | `push` → back leads to deleted resource (404) |
| After logout | `replace` | `push` → back returns to authenticated state |
| After form cancel | `back()` | `push('/list')` → user loses back history |

### Accessibility (from qa-a11y)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| A-01 | Heading hierarchy | **High** | | Heading levels must not skip (h1→h3 without h2). Each page should have exactly one `<h1>` |
| A-02 | Landmark regions | **High** | | Page must have `<main>`, `<nav>`, `<header>`, `<footer>` landmarks. No content outside landmarks |
| A-03 | Semantic elements vs div-soup | **Medium** | | Interactive elements must use semantic HTML (`<button>`, `<a>`, `<input>`) not `<div onClick>` or `<span onClick>` |
| A-04 | Image alt text | **High** | | All `<img>` must have `alt` attribute. Decorative images use `alt=""`. Informative images have descriptive alt text |
| A-05 | ARIA role correctness | **Medium** | | No redundant roles on semantic HTML (e.g., `<button role="button">`). ARIA roles match widget patterns (tabs, accordion, dialog) |
| A-06 | ARIA states and properties | **Medium** | | Interactive widgets have required ARIA states (`aria-expanded`, `aria-selected`, `aria-checked`). `aria-describedby`/`aria-labelledby` reference existing IDs |
| A-07 | Live regions | **High** | | Dynamic status messages use `aria-live="polite"` or `aria-live="assertive"`. Toast notifications are announced to screen readers |
| A-08 | Tab order | **High** | | No positive `tabIndex` values (> 0). Interactive elements are reachable via Tab. Logical reading order matches visual order |
| A-09 | Focus management | **Critical** | | Modal open must trap focus. Modal close must return focus to trigger. Route changes must move focus to new content |
| A-10 | Keyboard traps | **Critical** | | No element traps keyboard focus without an escape mechanism. All interactive elements are keyboard-operable |
| A-11 | Skip links | **Medium** | | Skip-to-content link present for pages with navigation before main content |
| A-12 | Form label association | **High** | | Every `<input>`, `<select>`, `<textarea>` has a visible label via `<label htmlFor>`, `aria-label`, or `aria-labelledby` |
| A-13 | Form error messaging | **High** | | Invalid fields use `aria-invalid="true"` + `aria-describedby` linking to error message element |
| A-14 | Required field indication | **Medium** | | Required fields indicated visually and via `aria-required="true"` or `required` attribute |
| A-15 | Fieldset and legend grouping | **Low** | | Related form controls (radio groups, checkbox groups) wrapped in `<fieldset>` with `<legend>` |
| A-16 | Color contrast indicators | **High** | | Information not conveyed by color alone. Focus indicators visible (`:focus-visible` styles present) |
| A-17 | Text sizing | **Medium** | | Text resizable to 200% without loss of content. No fixed `px` font sizes that prevent scaling |
| A-18 | Motion preferences | **Medium** | | Animations respect `prefers-reduced-motion`. CSS includes `@media (prefers-reduced-motion: reduce)` |
| A-19 | Route change announcements | **High** | frontend_spa | SPA route changes announced to screen readers via `aria-live` region or document title update |
| A-20 | Touch target size | **Medium** | | Interactive touch targets minimum 24x24px (WCAG 2.2 Level AA). Threshold: `elderly_ux ? 48px : 44px`. Adequate spacing between targets |

#### Accessibility Library Detection

| Signal | Library |
|--------|---------|
| `@axe-core/react` in package.json | axe-core React integration |
| `react-aria` or `@react-aria/*` | React Aria (Adobe) |
| `@radix-ui/*` | Radix UI primitives |
| `@headlessui/react` or `@headlessui/vue` | Headless UI (Tailwind) |
| `ark-ui` or `@ark-ui/*` | Ark UI |

#### WCAG 2.2 Level Mapping

| Check | Level A | Level AA | Level AAA |
|-------|---------|----------|-----------|
| Heading hierarchy | Required | Required | Required |
| Image alt text | Required | Required | Required |
| Keyboard operability | Required | Required | Required |
| Focus management | Required | Required | Required |
| Color contrast (4.5:1 text) | — | Required | Required |
| Color contrast (7:1 text) | — | — | Required |
| Touch target 24x24 | — | Required | Required |
| Touch target 44x44 | — | — | Required |

### Layout (from qa-layout)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| Y-01 | Title placement inconsistency | **High** | | Page title (`<h1>`) is inside a sub-panel instead of spanning full width like sibling pages |
| Y-02 | Layout padding mismatch | **High** | | Same-level pages use different padding negation patterns (`-m-6` vs none) |
| Y-03 | Border style inconsistency | **Medium** | | Panel separators differ across pages (`border-t` vs `border` vs `border rounded-*`) |
| Y-04 | Rounded corner inconsistency | **Medium** | | Same-role containers have `rounded-*` on some pages but not others |
| Y-05 | Sidebar gap inconsistency | **High** | | Shared sidebar component has different spacing/gap from the app sidebar across pages |
| Y-06 | Shared component wrapper mismatch | **Medium** | | Same component used across pages but parent wrapper classes differ significantly |
| Y-07 | Content area structure mismatch | **Medium** | | Pages with same layout type (sidebar+content) use different flex/grid structures |
| Y-08 | Header action alignment inconsistency | **Low** | | Title-row action buttons (export, refresh) positioned differently across pages |
| Y-09 | Toolbar gap inconsistency | **High** | | Same-type pages use different gap values on the filter/search toolbar (e.g., `gap-2` vs `gap-4`) |
| Y-10 | Count display placement inconsistency | **Medium** | | Result count text (`Showing X of Y`) positioned differently or uses inconsistent margins |
| Y-11 | Search input width inconsistency | **Low** | | Search inputs use different widths across same-type pages (e.g., `w-64` vs `w-80`) |
| Y-12 | Label-value typography hierarchy | **Medium** | | Detail/form pages have insufficient visual distinction between labels and values (font-size, font-weight, color) |
| Y-13 | Filter component type inconsistency | **High** | | Same-type pages use different filter UI patterns — Select dropdown on one page vs inline button group on another |
| Y-14 | Scroll container missing | **High** | | Content area inside overflow-hidden layout lacks `overflow-y-auto`, making long content unscrollable |
| Y-15 | Cross-role page structure divergence | **High** | | Same-function pages across roles use different layout patterns (fixed footer vs scroll-inline CTA, different padding) |
| Y-16 | Minimum font size violation | **High** | | Text elements use font sizes below 12px. 12px is the industry-standard minimum for readability |
| Y-17 | Arbitrary font size values | **Medium** | | Custom pixel-based font sizes (e.g., `text-[13px]`) used instead of the framework's standard scale (`text-xs`/`text-sm`/`text-base`) |
| Y-18 | Page heading size inconsistency | **High** | | Same-level page headings use different font sizes across the app |
| Y-19 | Font size variety overload | **Medium** | | App uses more than 6 unique font size values. A well-structured typography system should use 4-6 sizes maximum |
| Y-20 | Form label font size inconsistency | **Medium** | | Form labels across different pages use different font sizes |
| Y-21 | Arbitrary color values bypassing design tokens | **High** | | Hardcoded hex/rgb color values used instead of design tokens when the project defines a color palette |
| Y-22 | Z-index hierarchy inconsistency | **High** | | Z-index values do not follow a consistent hierarchy. Expected: base(0) → content(10) → sticky(20) → dropdown(30) → modal(40) → toast(50) |
| Y-23 | Fixed spacing on fullscreen mobile pages | **High** | is_mobile_target | Fullscreen pages use fixed px spacing instead of viewport-relative units (`vh`). On small screens content overflows; on large screens excessive empty space |
| Y-24 | Overflow text not truncated | **Low** | | Long text in table cells, card titles, or list items overflows its container instead of being truncated with ellipsis |
| Y-25 | Responsive breakpoint missing | **High** | | Page has no mobile layout adaptation — sidebar/3-panel doesn't collapse on small screens. Check for `sm:`/`md:`/`lg:` responsive classes or media queries |
| Y-26 | Spacing not grid-aligned | **Low** | | Padding/margin uses arbitrary values (e.g., `p-[13px]`, `mt-[7px]`) outside 4/8px grid system. Prefer standard Tailwind spacing scale |
| Y-27 | Icon size inconsistent | **Low** | | Same-context icons use different sizes (e.g., 16px in one action button, 24px in adjacent action button). Icon size should be consistent within the same UI context |
| Y-28 | Missing viewport-fit=cover | **CRITICAL** | webview_checks | Viewport meta tag lacks `viewport-fit=cover`. Required for iOS WebView/Safari to expose safe area insets. Without it, `env(safe-area-inset-*)` always returns 0 and fixed elements overlap the home indicator |
| Y-29 | Fixed bottom element missing safe-area padding | **CRITICAL** | safe_area | Fixed-position elements at screen bottom (`fixed bottom-0`, BottomNav, footer buttons) lack `env(safe-area-inset-bottom)` padding. On notched iPhones and Android devices with system nav bars, these get clipped |
| Y-30 | Fixed top element missing safe-area padding | **High** | safe_area | Fixed-position elements at screen top lack `env(safe-area-inset-top)` padding. On notched iPhones, content overlaps the status bar/notch area |
| Y-31 | Missing overscroll-behavior | **High** | webview_checks | Root element and scrollable containers lack `overscroll-behavior: none/contain`. In WebView apps, overscroll triggers pull-to-refresh or rubber-band bounce that conflicts with app navigation |
| Y-32 | Missing theme-color meta tag | **Medium** | webview_checks | No `<meta name="theme-color">` tag. Browser/WebView status bar area has no defined color, breaking native app appearance |
| Y-33 | Missing apple-mobile-web-app meta tags | **Medium** | platform_ios | Missing `apple-mobile-web-app-capable` and `apple-mobile-web-app-status-bar-style` meta tags. iOS WebView/Safari won't render app in fullscreen native style |
| Y-34 | Layout bottom padding ignores safe-area variable | **High** | safe_area | Layout container uses fixed padding-bottom (e.g., `pb-28`) to reserve space for a fixed BottomNav. On devices without safe area (desktop, Android), this creates a visible gap between content and nav. Use `calc(<nav-height> + var(--safe-area-bottom))` so padding adapts: exact fit on desktop, safe-area-aware on iOS |
| Y-35 | Bottom offset doesn't match navigation height | **CRITICAL** | safe_area | A component uses a hardcoded `bottom` px value (inline style `bottom: 'Npx'` or Tailwind `bottom-[Npx]`) to avoid overlapping a fixed BottomNav, but the value doesn't use the same calculation as the nav's actual height. **Detection procedure:** (1) Find the fixed bottom navigation element (`fixed bottom-0` persistent nav bar — not modals/overlays). (2) Extract its height formula (explicit height class, or sum of padding + content height + safe-area variable). (3) Search all other components for hardcoded `bottom` values in inline styles or Tailwind classes. (4) Flag any hardcoded value that doesn't reference the same CSS variable or `calc()` formula as the nav height. Auto-fix: replace hardcoded px with `calc(<nav-height> + var(--safe-area-bottom))` matching the layout's pattern |
| Y-36 | Flex-pushed bottom content missing safe-area padding | **High** | safe_area | Fullscreen flex layouts (`flex-col flex-1`, `h-screen`) that push footer content to the bottom via `mt-auto` or `justify-between` use fixed padding-bottom (e.g., `pb-6`) without `env(safe-area-inset-bottom)`. On devices with system navigation bars (Galaxy Z Flip, iPhones with home indicator), the bottom content gets clipped. **Detection:** Find containers with `flex-col` + (`flex-1` or `h-screen`) where a child uses `mt-auto` or parent uses `justify-between`. Check if padding-bottom includes `var(--safe-area-bottom)` or `env(safe-area-inset-bottom)`. **Fix:** Replace fixed `pb-*` with `pb-[calc(<value>+var(--safe-area-bottom))]` |
| Y-37 | Fixed-width children overflow flex/grid parent | **High** | is_mobile_target | Child elements use fixed pixel widths (`w-[Npx]`, `min-w-[Npx]`) inside a flexible container (`flex`, `grid`, `grid-cols-*`) without `min-w-0` or `shrink`. On narrow mobile viewports, total child width exceeds container, causing clipping. **Detection:** Find elements with `w-[*px]` or `w-[*rem]` classes whose parent (or grandparent within same component) uses `flex`, `grid`, or `grid-cols-*`. Sum all sibling fixed widths + gap values. Flag when total exceeds ~160px (half of 360px mobile viewport minus typical padding). **Fix:** Replace fixed widths with `flex-1 min-w-0`, or use `max-w-` + `shrink` |
| Y-38 | Native wrapper SafeArea not applied | **CRITICAL** | has_native_wrapper | Mobile wrapper exists but SafeArea is not properly applied to the WebView container. **Flutter:** No `SafeArea` widget wrapping the WebView, or `SafeArea(bottom: false)` disabling bottom protection. **Capacitor:** `StatusBar` or `SafeArea` plugin not configured. **React Native:** No `SafeAreaView` wrapping the WebView component. **Detection:** Read the native wrapper's main screen/widget file and check for SafeArea usage. Without this, CSS `env(safe-area-inset-*)` may return 0 on Android even when the system nav bar overlaps content |

### Performance (from qa-performance)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| P-01 | Heavy dependency detection | **High** | | Full imports of heavy libraries (`lodash`, `moment`, `date-fns`) instead of tree-shakeable imports (e.g., `import get from 'lodash/get'`) |
| P-02 | Barrel import bloat | **High** | | Importing from barrel `index.ts` files that re-export entire modules, defeating tree-shaking |
| P-03 | Duplicate dependencies | **Medium** | | Multiple versions of the same library in the bundle (e.g., two versions of `lodash`) |
| P-04 | Missing memoization | **Medium** | | Components re-rendering on every parent render without `React.memo`, `useMemo`, or `useCallback` where beneficial |
| P-05 | Inline object/array in JSX props | **Medium** | | Object literals or array literals created inline in JSX props (e.g., `style={{ color: 'red' }}`) causing unnecessary re-renders |
| P-06 | Expensive computation in render | **High** | | Heavy computations (sort, filter, map over large arrays) inside render without `useMemo` |
| P-07 | Image missing dimensions | **High** | | `<img>` without explicit `width`/`height` attributes causes CLS (Cumulative Layout Shift) |
| P-08 | Image lazy loading | **Medium** | | Below-the-fold images without `loading="lazy"`. LCP image should NOT be lazy-loaded |
| P-09 | Unoptimized image format | **Medium** | | Using PNG/JPG when WebP/AVIF would be smaller. Not using framework image components (`next/image`, `nuxt-img`) |
| P-10 | Missing route-level code splitting | **High** | | Route components imported synchronously instead of using `React.lazy()`, `defineAsyncComponent()`, or dynamic `import()` |
| P-11 | Heavy component not lazy-loaded | **Medium** | | Large components (modals, charts, rich editors) imported statically instead of dynamically |
| P-12 | Font loading CLS | **Medium** | | Web fonts loaded without `font-display: swap` or `font-display: optional`, causing invisible text or layout shift |
| P-13 | Dynamic content without reserved space | **High** | | Content injected dynamically (ads, embeds, async data) without placeholder/skeleton causing CLS |
| P-14 | Render-blocking resources | **High** | | CSS/JS in `<head>` without `async`/`defer` blocking first paint |
| P-15 | Third-party script impact | **Medium** | | Third-party scripts (analytics, ads, chat widgets) loaded synchronously in the critical path |
| P-16 | Data fetching waterfall | **High** | | Sequential API calls that could be parallelized (`await a; await b` instead of `Promise.all`) |
| P-17 | Missing data prefetch/cache | **Medium** | | Pages that always fetch on mount without cache strategy (SWR, React Query, Apollo cache) |
| P-18 | Over-fetching | **Medium** | | API responses returning significantly more data than the component needs, without field selection |

### i18n

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| I-01 | Hardcoded user-facing string | **Warning** | always | User-visible text not using i18n function/constant |
| I-02 | Wrong language in UI text | **Critical** | always | UI text in different language than project's configured language |
| I-03 | Missing locale formatting | **Warning** | i18n_multi_locale | Date/number not formatted with locale-aware function |
| I-04 | Missing RTL support | **Medium** | i18n_multi_locale | No RTL layout handling for Arabic/Hebrew locales |
| I-05 | Hardcoded currency symbol | **Warning** | i18n_multi_locale | Currency symbol not locale-aware |
| I-06 | Inconsistent date format | **Warning** | always | Same date formatted differently across pages |
| I-07 | Missing pluralization | **Low** | i18n_multi_locale | Count display without plural forms |
| I-08 | String concatenation for i18n | **Warning** | i18n_multi_locale | Building sentences by concatenating translated fragments |
| I-09 | Missing language selector | **Low** | i18n_multi_locale | Multi-locale app with no way to switch language |

## Tier 2: Reasoning Patterns

After Tier 1, apply:

- **RP-02: State Lifecycle Completeness** — For each status/state displayed in UI (badges, labels, progress indicators), verify ALL possible states are handled with appropriate visual treatment.
- **RP-06: Temporal Consistency** — For date/time displays, verify timezone handling, format consistency across pages, and expired item treatment.
- **RP-09: Concurrency & Race Conditions** — For real-time features, verify socket event updates match REST state, cache invalidation is correct, and optimistic updates have rollback.
- **RP-10: Error Path Completeness** — For each user action that calls an API, verify all error types (network, 4xx, 5xx) are handled with meaningful UI feedback.
- **RP-11: Cross-App Consistency** — For features in multiple apps, verify consistent UX patterns (search, pagination, empty states).

Document findings as R-prefixed items.
