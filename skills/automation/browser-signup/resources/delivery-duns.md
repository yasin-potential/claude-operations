# DUNS 등록 완료 전달 이메일 템플릿 / DUNS Registration Delivery Email Template

Auto-generated at end of DUNS flow via the `writeHandoff` fixture — lands at `artifacts/<client>/duns-iupdate/<run-id>/handoff.md`. PM fills the `{{placeholders}}`, copies into email, sends to client.

---

## Korean version

**제목**: [포텐셜] `{{client_legal_name}}` DUNS Number 등록 완료

`{{client_contact_name}}`님, 안녕하세요.

포텐셜에서 의뢰하신 `{{client_legal_name}}`의 DUNS Number 등록을 완료하여 결과를 공유드립니다.

### 등록 결과

| 항목 | 내용 |
|---|---|
| DUNS Number | **`{{duns_number}}`** |
| 등록일자 | `{{registration_date}}` |
| 등록된 법인명 (영문) | `{{legal_entity_name_en}}` |
| 등록된 주소 (영문) | `{{address_en}}` |

### 확인 및 보관 방법

- D&B의 공식 확인 이메일이 `{{registration_email}}`로 1~3 영업일 내에 발송됩니다.
- 발송 시 원본을 그대로 보관해 주세요 (향후 Apple Developer 등록 시 참조 자료로 사용).
- DUNS 정보는 1Password `{{client_slug}} - Platforms` 보관소의 `DUNS Registration` 항목에도 저장하였습니다.

### 다음 단계 (선택)

본 DUNS Number를 다음 플랫폼 등록에 활용하실 수 있습니다:
- [ ] Apple Developer Program 등록 (연 $99)
- [ ] Google Play Console 등록 (1회 $25)
- [ ] Meta Business Manager 인증

관심 있으시면 회신 주시면 견적 안내드리겠습니다.

감사합니다.

---
주식회사 포텐셜
`{{pm_name}}`
`{{pm_email}}`

---

## English version (if client prefers)

**Subject**: [Potential] `{{client_legal_name}}` DUNS Number Registered

Hi `{{client_contact_name}}`,

We've completed the DUNS Number registration for `{{client_legal_name}}`. Here's the summary.

### Result

| Item | Value |
|---|---|
| DUNS Number | **`{{duns_number}}`** |
| Registration Date | `{{registration_date}}` |
| Registered Entity (EN) | `{{legal_entity_name_en}}` |
| Registered Address (EN) | `{{address_en}}` |

### What to keep

- Dun & Bradstreet will send a confirmation email to `{{registration_email}}` within 1-3 business days. Please keep the original — it's useful for Apple Developer and other platform registrations later.
- We've also stored the DUNS data in 1Password vault `{{client_slug}} - Platforms`, in the `DUNS Registration` item.

### Next steps (optional)

You can use this DUNS Number for:
- [ ] Apple Developer Program enrollment ($99/year)
- [ ] Google Play Console registration ($25 one-time)
- [ ] Meta Business Manager verification

Let me know if you'd like a quote for any of these.

Best regards,
Potential Inc.
`{{pm_name}}`
`{{pm_email}}`

---

## PM checklist before sending

- [ ] `{{duns_number}}` is a real 9-digit number (not empty, not placeholder)
- [ ] Registration date set to today
- [ ] Legal entity name exactly matches 사업자등록증 (English)
- [ ] 1Password `DUNS Registration` item updated with the DUNS number
- [ ] Local copy of business cert PDF deleted from PM's laptop
- [ ] Pre-submit screenshot (`pre-submit.png`) archived in project folder (evidence of what was submitted)
