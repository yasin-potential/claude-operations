---
name: qa-guard
description: "Audit auth & security — role guards, route protection, permission gaps, token handling, SQL injection, XSS, rate limiting"
user-invocable: true
argument-hint: "[module] [--check N]"
---

# QA Guard — Auth & Security Auditor

Verify authentication, authorization, and security across the full stack. Merges checks from qa-auth and qa-security.

## Execution Mode

- **Standalone** (`/qa-guard [module]`): Diagnose-only. Scans the codebase, applies checks below, outputs a report. Does NOT modify files.
- **Via qa-scan** (`/qa-scan --check guard`): qa-scan uses these checks for the guard layer.

Shared conventions (scoring, framework detection, output format): see `qa-shared/reference.md`.

## Tier 1: Checklist

### Authentication & Authorization

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| G-01 | Unprotected endpoint | **Critical** | | Controller method has no auth guard and is not marked as public |
| G-02 | Missing role guard | **High** | | Endpoint should restrict by role but has no role decorator |
| G-03 | Unprotected frontend route | **High** | | Frontend page accessible without auth redirect |
| G-04 | Role mismatch frontend<>backend | **High** | | Frontend shows action for role that backend doesn't allow |
| G-05 | Missing current-user validation | **Medium** | | Endpoint uses user data but doesn't verify ownership |
| G-06 | Token exposure | **Critical** | | JWT stored in localStorage instead of HTTP-only cookie |
| G-07 | Missing CORS config | **Medium** | | Backend allows all origins or missing CORS |
| G-08 | Sensitive data in response | **Medium** | | API returns password hash, tokens, or secrets |
| G-09 | Missing rate limiting | **Medium** | | Login/register without rate limiter |
| G-10 | Frontend role-based UI gap | **Medium** | | Backend has role restriction but frontend doesn't hide UI |
| G-11 | Permission check inconsistency | **Medium** | | Different permission check utilities used inconsistently across components (hooks vs HOCs vs inline) |
| G-12 | Permission name mismatch | **High** | | Frontend role/permission names don't match backend definitions (casing, format, enum vs string) |
| G-13 | Missing visibility matrix | **Medium** | | UI elements not conditionally rendered based on role when backend restricts access |
| G-14 | Rate limiter infrastructure inactive | **Critical** | has_backend | Rate limiting decorators exist but the guard/middleware is not registered globally — all rate limits are dead code |
| G-15 | Missing brute-force protection | **High** | | OTP/token verification endpoint has no attempt counter or lockout mechanism |
| G-16 | Session timeout warning missing | **High** | | JWT/session expires and user is silently redirected to login with no advance warning. Should show countdown dialog (e.g., "Session expires in 5 minutes") with option to extend, preventing data loss on forms |
| G-17 | Role-based field editability gap | **High** | | For entities with update endpoints accessible by multiple roles (e.g., admin update vs user self-update): (1) Admin-only fields (`role`, `isActive`, `coachId`, `adminNotes`) present in user self-update DTO = privilege escalation risk, (2) User-editable fields (`fullName`, `phone`) missing from admin update DTO = admin capability gap. **Scan**: Find all `Update*Dto` classes, group by entity, compare field lists between admin and user DTOs. Admin DTO should be a superset of user DTO for editable fields. Cross-references `qa-form` BQ2 results in `QA_BUSINESS_DECISIONS.md` if available |
| G-18 | Response field filtering by role | **Medium** | | Admin-only fields (`adminNotes`, `withdrawalDate`, `internalNotes`, `coachStatus`) appear in user-facing GET API responses. Check if role-specific serialization or response transformation exists. If the same endpoint serves all roles with identical response shape, sensitive fields are leaked to unauthorized roles |

### Security

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| GS-01 | SQL/NoSQL injection | **Critical** | | Raw user input interpolated into queries without parameterization |
| GS-02 | Insecure randomness | **High** | | `Math.random()`, `random.random()`, or similar non-cryptographic RNG used for security-sensitive values (OTP, tokens, secrets) |
| GS-03 | Unsanitized file upload | **Medium** | | User-controlled filename used in storage path without sanitization (path traversal risk) |
| GS-04 | Sensitive data in logs | **High** | | `console.log`, `logger.debug`, or equivalent outputs JWT tokens, passwords, OTP codes, cookies, or API keys |
| GS-05 | Debug/test routes in production | **Medium** | | Static file serving, debug endpoints, or test fixtures accessible without environment guard |
| GS-06 | XSS via unsafe URL handling | **High** | | `window.open()`, `href`, `src`, or `location` set from user-controlled data without scheme validation (`javascript:` protocol injection) |
| GS-07 | Infrastructure secrets | **Medium** | | Hardcoded secrets, missing auth on Redis/DB, default credentials, `process.env` used at module evaluation time instead of ConfigService |
| GS-08 | Missing input sanitization at boundaries | **Medium** | | User input from request body/params/query not validated before use in business logic (beyond DTO validation — raw SQL, file ops, external API calls) |
| GS-09 | Unsafe deserialization | **High** | | `JSON.parse()` on untrusted input without try-catch, `eval()`, `new Function()`, or `child_process.exec` with user input |
| GS-10 | Side-effect logic bugs in auth flows | **Medium** | | Password change/reset setting unintended flags (e.g., `isVerified: false`), token refresh not invalidating old token, session not cleared on password change |
| GS-11 | IME/i18n input compatibility | **Medium** | cjk_ime | `onKeyPress` used instead of `onKeyDown` with `isComposing` check (breaks CJK input), or Enter key handling without IME composition guard |
| GS-12 | Missing request size limits | **Low** | | No body size limit on file upload or JSON endpoints, no array length limit on batch endpoints, enabling resource exhaustion |
| GS-13 | WebView accepts all SSL certificates | **Critical** | has_native_wrapper | WebView `onReceivedServerTrustAuthRequest` or equivalent always returns PROCEED/allow, accepting any certificate including self-signed/expired. Production apps must validate certificates to prevent MITM attacks. **Scan**: Search for `onReceivedServerTrustAuthRequest`, `ServerTrustChallenge`, `PROCEED` in mobile/native wrapper code |
| GS-14 | Missing App Transport Security config | **High** | platform_ios | iOS `Info.plist` lacks `NSAppTransportSecurity` configuration. Default ATS blocks HTTP but may need explicit domain exceptions. Misconfigured ATS causes silent network failures or App Store rejection. **Scan**: Read `Info.plist` for `NSAppTransportSecurity` key |

## Tier 2: Reasoning Patterns

- **RP-05: Permission Boundary Tracing** — For each role-restricted endpoint/UI, trace enforcement at every layer (guard -> service -> query -> frontend route -> component -> button). Flag gaps where restriction is not enforced.
- **RP-10: Error Path Completeness** — For auth-specific errors (401/403), verify the frontend handles them distinctly with meaningful messages and appropriate redirects (e.g., 401 -> login page, 403 -> access denied page).

Document findings as R-prefixed items.

## Cross-Skill Triggers

| Condition found by qa-guard | Trigger | Reason |
|-----------------------------|---------|--------|
| New role-restricted endpoint discovered | -> `qa-inputs` BQ2 (Role-Based Editability) | Verify the endpoint's fields match role expectations |
| Role mismatch frontend<>backend (G-04) | -> `qa-inputs` #57 (Immutable Field) | If mismatch involves identity/system fields, check immutability |
| Missing ownership check (G-05) | -> `qa-crud` #9 (Missing ownership check) | Cross-validate ownership enforcement |

## Skill-Specific Patterns

### Auth Library Detection

| Signal | Library |
|--------|---------|
| `next-auth` / `@auth/core` in package.json | NextAuth / Auth.js |
| `@casl/ability` / `@casl/react` / `@casl/vue` | CASL |
| `firebase/auth` in package.json | Firebase Auth |
| `@clerk/nextjs` / `@clerk/clerk-react` | Clerk |
| `@supabase/supabase-js` + `.auth` usage | Supabase Auth |
| `@auth0/auth0-react` / `@auth0/nextjs-auth0` | Auth0 |
| Custom: `useAuth()`, `usePermission()`, `AuthContext` | Custom auth hook/context |

### Framework Auth Patterns

| Framework | Auth Guard | Public Route | Role Decorator | Current User |
|-----------|-----------|--------------|----------------|-------------|
| NestJS | APP_GUARD/JwtAuthGuard | @Public() | @Roles() | @CurrentUser() |
| Express | passport.authenticate | - | custom middleware | req.user |
| Spring Boot | @PreAuthorize | @PermitAll | @Secured/@RolesAllowed | @AuthenticationPrincipal |
| Django | @login_required | @permission_classes([AllowAny]) | @permission_required | request.user |
| Laravel | ->middleware('auth') | - | ->middleware('role:admin') | auth()->user() |
| Next.js | middleware.ts | matcher config | custom | getServerSession() |
