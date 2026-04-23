# browser-signup 스킬 사용 가이드 — PM용 (한국어)

Eddy님 안녕하세요. 이 문서는 `browser-signup` 스킬을 처음 사용하시는 PM 분들을 위한 온보딩 가이드입니다. 끝까지 따라 하시면 실제 고객을 위한 DUNS / Apple Developer / Google Play 계정 등록을 수행하실 수 있습니다.

**읽는 데 약 15분, 최초 세팅에 약 20분이 걸립니다.**

---

## 1. 이 스킬이 하는 일

간단히 말해: **고객사의 해외 플랫폼 계정 등록을 우리가 대신 처리하는 자동화 툴**입니다.

### 왜 만들었나요?

한국 중소기업·스타트업 고객이 가장 힘들어하는 작업 중 하나가 아래입니다:

- DUNS Number 등록 (영어 포털, 서류 요구)
- Apple Developer Program 등록 (연 $99, DUNS 선행 필요, 영어 전화 인증)
- Google Play Console 등록 (조직 인증, 세금 양식)
- Meta Business Manager 인증

이걸 고객이 직접 하면 며칠씩 헤매거나 포기합니다. 우리가 대행하면 **고객은 15분만 투자**하고, 나머지는 PM이 포텐셜 내부 도구로 처리합니다.

### 고객의 부담 vs PM의 부담

| | 고객 | PM |
|---|---|---|
| Intake Form 작성 | 10분 (1회) | — |
| 데이터 제공 (1Password) | 포함 | — |
| 플랫폼 양식 작성 · 제출 | 0 | 자동화로 수행 |
| CAPTCHA · 이메일 인증 · 서류 업로드 | 0 | PM이 처리 |
| SMS 인증 (Apple만) | 30초 × 1~2회 KakaoTalk 포워딩 | SMS 받은 뒤 코드 입력 |
| 결과 확인 | 이메일 수신 (0분) | 전달 이메일 발송 |

**고객은 진짜 SMS 포워딩 몇 번만 해주시면 됩니다.** 그게 전부입니다.

---

## 2. 용어 정리

가이드에서 자주 나오는 단어들:

| 용어 | 뜻 |
|---|---|
| **Flow** | 하나의 플랫폼 등록 과정 (예: `duns-iupdate`, `apple-developer-enroll`) |
| **Checkpoint** | 중간 저장점. 문제 생기면 여기서부터 재실행 가능 |
| **HITL** | Human-In-The-Loop. 사람 개입이 필요한 순간 (CAPTCHA, 이메일 클릭 등) |
| **1Password Vault** | 고객사 한 군데마다 만드는 전용 보관소 (`<고객사명> - Platforms`) |
| **Intake Form** | 고객사 데이터 + 데이터 정확성 확인 서명이 담긴 최초 1회 입력 양식 |
| **op run** | 1Password에서 비밀값을 실시간으로 불러와 명령어 실행 |
| **Playwright** | 브라우저를 자동화해 주는 라이브러리 (우리가 쓰는 엔진) |
| **Inspector** | Playwright 실행 중 열리는 디버거 창 (여기서 "Resume" 누름) |

---

## 3. 최초 세팅 — 한 번만 하면 됩니다 (약 20분)

### 3.1 1Password 접근 권한

우리 팀 1Password 계정 (`team-potentialai.1password.com`) 의 `Shared` 볼트에 접근 권한을 받으세요. 관리자에게 부탁하시면 됩니다.

- 1Password 데스크톱 앱 설치 → 로그인
- 앱 설정 → Security → **Touch ID** 켜기
- 앱 설정 → Developer → **"Integrate with 1Password CLI"** 체크

### 3.2 명령줄 도구 설치 (Mac 기준)

터미널을 열고:

```bash
# 1Password CLI
brew install 1password-cli

# Node.js 18 이상 (이미 있으시면 생략)
brew install node

# 스킬 폴더로 이동
cd ~/Documents/Potential/projects/claude-team-workspace/.claude/operation/skills/automation/browser-signup

# 의존성 설치
npm install
npx playwright install chromium
```

`npx playwright install chromium` 은 약 150MB 다운로드됩니다. 1~2분 걸려요.

### 3.3 1Password CLI 로그인

```bash
op signin
op whoami
```

`op whoami` 결과에 본인 이메일과 `team-potentialai.1password.com` 이 뜨면 OK.

### 3.4 설치 확인

```bash
npm run smoke
```

이게 통과하면 Playwright + fixtures 가 제대로 설치된 겁니다. 이때는 아직 1Password 접근 없이도 돌아가는 테스트예요.

출력 예시:
```
✓ framework smoke › checkpoint saves storageState + screenshot + meta
✓ framework smoke › fillForm + validateValue works on a real form
2 passed
```

여기까지 되면 **최초 세팅 완료**입니다. 🎉

---

## 4. 고객 한 명 온보딩 (고객사마다 1회)

새 고객을 맡으면 아래 순서대로 진행하세요.

### 4.1 Intake Form 서명 받기

1. [resources/intake-form-template.md](intake-form-template.md) 을 복사해서 고객사에 전달합니다.
2. 고객 담당자에게 Section 1~7 을 채우고, 마지막 Section 9 (데이터 정확성 확인 + 제출 권한 위임) 에 서명하도록 요청합니다.
3. 서명된 Intake Form 을 프로젝트 폴더에 보관합니다.

**중요**: 서명된 Intake Form 없으면 실행하지 마세요. 데이터 정확성 책임과 제출 권한의 근거가 이 서명입니다.

### 4.2 고객사 전용 1Password Vault 만들기

[resources/1password-vault-setup.md](1password-vault-setup.md) 전체 참고하시고, 요약하면:

1. 1Password 데스크톱 앱에서 **New Vault** → 이름: `<고객사명> - Platforms` (예: `Acme Corp - Platforms`).
2. 해당 볼트에 고객 담당자를 "Can Edit" 권한으로 초대.
3. 볼트 안에 아래 Item 들을 만듭니다 (각 Item의 필드명은 vault-setup.md 참고):
   - `Entity Data` (법인 정보)
   - `Payment` (신용카드, Credit Card 카테고리)
   - `DUNS Registration` (DUNS 등록용)
   - 필요 시 `Apple Developer`, `Google Play Console`, `Meta Business Manager`

4. 고객이 Intake Form 내용을 볼트 Item 에 채우도록 안내합니다. **Intake Form 과 볼트 Item의 필드는 1:1 대응**되니 고객이 헷갈리지 않습니다.

5. 고객이 사업자등록증 PDF 를 `Entity Data` Item 에 첨부하도록 안내합니다.

### 4.3 고객사 전용 env-file 만들기

스킬 폴더 (`browser-signup/`) 에서:

```bash
# 내부용 env-file 을 복사해서 고객사용으로 사용
cp .env.1password.test .env.1password.acme    # acme = 고객사 슬러그, 짧은 영문
```

`.env.1password.acme` 를 편집해서, 모든 `op://` 경로를 고객사 볼트 경로로 바꿉니다.

변경 예시:
```bash
# 변경 전 (내부용 Potential Inc.)
DUNS_COMPANY_NAME_EN=op://Shared/DUNS Registration/test_company_name_en

# 변경 후 (Acme Corp 고객사용)
DUNS_COMPANY_NAME_EN=op://Acme Corp - Platforms/Entity Data/company_name_en
```

그리고 파일 맨 위에 클라이언트 슬러그를 추가:

```bash
CLIENT_SLUG=acme
```

**이 파일은 Git에 커밋되지 않습니다** (`.gitignore` 에 등록됨). 고객사 이름 노출 방지 목적.

### 4.4 환경 확인

```bash
./scripts/run-flow.sh --client=acme --project=duns-iupdate -- --list
```

오류 없이 테스트 목록이 출력되면 성공. `permission denied` 나오면 고객사 볼트 접근 권한이 없는 겁니다.

---

## 5. 첫 실행 — DUNS Number 등록

### 5.1 사전 체크리스트

실행 전에 아래가 모두 OK인지 확인:

- [ ] 서명된 Intake Form 프로젝트 폴더에 있음
- [ ] 1Password 볼트 `<고객사> - Platforms` 생성 완료
- [ ] 볼트 Item `Entity Data` 의 모든 필드 채워짐 (company_name_ko, business_registration_number, representative_en, address_en, representative_phone, representative_email)
- [ ] 사업자등록증 PDF 첨부됨
- [ ] 로컬 경로 `business_cert_path` 에 해당 PDF 복사됨 (자동화가 업로드용으로 읽음)
- [ ] `.env.1password.<고객사슬러그>` 파일 생성 및 경로 수정 완료
- [ ] 1Password CLI 로그인 상태 (`op whoami` 통과)
- [ ] DUNS Registration 담당 이메일 받은 편지함을 열어둘 수 있는 상태

### 5.2 실행

```bash
./scripts/run-flow.sh --client=acme --project=duns-iupdate
```

실행되면:

1. **Chromium 창이 뜹니다.** D&B DUNS 등록 페이지가 로드됩니다.
2. **Playwright Inspector 창도 함께 뜹니다.** (옆에 작은 디버거 창)
3. 스킬이 자동으로 입력란을 채우고 검색 페이지로 넘어갑니다.
4. **첫 번째 HITL 일시정지: 이메일 인증**
   - 알림음과 함께 Mac 데스크톱 알림: *"Verify email link from D&B"*
   - 받은 편지함에서 D&B 이메일 (from `noreply@dnb.com`) 을 찾아 인증 링크 클릭
   - 링크가 기본 브라우저에서 열리면, URL을 복사해서 Playwright Chromium 에 붙여넣기 (또는 리다이렉트 따라가기)
   - Inspector 창에서 **Resume** 클릭
5. 스킬이 상세 양식을 자동 입력합니다.
6. 스킬이 사업자등록증 PDF 를 업로드합니다.
7. **두 번째 HITL 일시정지: 제출 전 확인**
   - 알림: *"Review the summary page. Click Resume to submit."*
   - 요약 페이지가 화면에 보입니다. **영문 주소, 사업자등록번호를 한 번만 훑으세요**
   - 이상 없으면 Inspector 에서 **Resume** 클릭 → 스킬이 Submit 버튼을 누릅니다
   - 이상 있으면: **절대 Submit 하지 말고**, Chromium 창 닫고, 1Password 에서 데이터 수정한 후 재실행
8. 성공 페이지에서 DUNS Number (9자리) 가 캡처됩니다.

### 5.3 결과 확인

실행이 끝나면 `artifacts/acme/duns-iupdate/<실행ID>/` 폴더에 다음 파일들이 생깁니다:

| 파일 | 용도 |
|---|---|
| `post-email.png` | 이메일 인증 직후 화면 |
| `post-details.png` | 상세 양식 입력 직후 |
| `post-upload.png` | 사업자등록증 업로드 직후 |
| `pre-submit.png` | 제출 직전 요약 페이지 (가장 중요한 증거) |
| `result.json` | DUNS Number + 등록 시각 |
| `handoff.md` | 고객 전달용 이메일 초안 |

### 5.4 고객 전달

1. `handoff.md` 를 열어 (자동 생성됨) 복사합니다.
2. [resources/delivery-duns.md](delivery-duns.md) 의 한국어 이메일 템플릿에 붙여넣어 고객 담당자에게 발송.
3. 1Password 의 `DUNS Registration` Item 에 DUNS Number 필드를 업데이트.
4. 로컬 사업자등록증 PDF 파일 삭제.

---

## 6. 문제 해결 (자주 묻는 질문)

### Q. 실행하자마자 `permission denied reading op://...` 오류

→ 1Password 볼트 접근 권한이 없는 겁니다. 관리자에게 요청하거나, 고객 볼트 공유가 본인 계정에 수락되었는지 확인.

### Q. `account is not signed in`

→ `op signin` 실행. Touch ID 요청이 뜨면 승인.

### Q. 이메일 인증 링크가 만료됐어요 (24시간 지남)

→ 그냥 다시 실행하면 됩니다. 같은 이메일로 재전송되고 DUNS 는 중복 등록되지 않습니다.

### Q. CAPTCHA 가 여러 번 실패해요

→ D&B 가 해당 IP 를 잠시 막은 겁니다. 30분 기다리고 재시도. 또는 다른 네트워크 (핫스팟 등) 에서.

### Q. 업로드 iframe 이 안 뜨는 것 같아요

→ 페이지 새로고침 후 `--resume=post-email` 로 재실행. 예: `./scripts/run-flow.sh --client=acme --project=duns-iupdate --run-id=<기존실행ID> --resume=post-email`

### Q. 중간에 Chromium 창을 닫았어요. 처음부터 다시 해야 하나요?

→ 아니요. 마지막 checkpoint 부터 재시작 가능.

```bash
# artifacts/<고객슬러그>/duns-iupdate/ 아래 있는 폴더 중 최근 실행ID 확인
ls artifacts/acme/duns-iupdate/

# 가장 최근 checkpoint 확인
ls artifacts/acme/duns-iupdate/<실행ID>/

# 거기서부터 재개 (예: post-email 이후부터)
./scripts/run-flow.sh --client=acme --project=duns-iupdate \
  --run-id=<실행ID> --resume=post-email
```

### Q. 요약 페이지 필드가 잘못됐어요

→ **절대 Submit 하지 마세요.** Chromium 닫고, 1Password Intake 필드 수정, 재실행. Intake 에 원본 데이터가 잘못 들어간 거라면 고객에게 확인.

### Q. 스킬이 한참 멈춰 있어요

→ Playwright 는 기본 10분 대기합니다. 그 안에 Resume 누르면 계속 진행. 대기 시간 초과하면 오류로 종료되는데, 그때도 checkpoint 는 저장되어 있어서 재개 가능.

---

## 7. 하지 말아야 할 것들

- ❌ **서명된 Intake Form 없이 실행** — 데이터 정확성 책임이 불분명해집니다
- ❌ **고객 CC 정보를 채팅/이메일로 받기** — 반드시 1Password 로만
- ❌ **사업자등록증을 영원히 내 랩탑에 저장** — 실행 후 삭제
- ❌ **여러 고객사 데이터를 한 볼트에 섞기** — 고객사마다 별도 볼트
- ❌ **artifacts 폴더를 Git 에 커밋하거나 Slack 에 공유** — 고객 화면 스크린샷이 들어있음
- ❌ **CAPTCHA 자동 해결 서비스 사용** — 모든 플랫폼의 ToS 위반, 계정 영구 정지 위험
- ❌ **PM 전화번호를 고객사 등록에 사용 후 나중에 변경하는 우회** — Apple 의심 플래그. 고객 실번호 + KakaoTalk SMS 포워딩 방식으로만 진행

---

## 8. 전체 파일 위치 요약

| 용도 | 파일 경로 |
|---|---|
| 스킬 전체 설명 | [../SKILL.md](../SKILL.md) |
| Intake Form 템플릿 | [intake-form-template.md](intake-form-template.md) |
| 고객용 Apple FAQ (한글) | [client-faq-apple.md](client-faq-apple.md) |
| 1Password 볼트 구조 | [1password-vault-setup.md](1password-vault-setup.md) |
| DUNS 전달 이메일 템플릿 | [delivery-duns.md](delivery-duns.md) |
| DUNS 실행 상세 플레이북 | [../flows/duns-iupdate/playbook.md](../flows/duns-iupdate/playbook.md) |

---

## 9. 지원

실행 중 막히거나 이해 안 되는 부분 있으면:

- **기술 문제** (스크립트 에러, 1Password 연결 안 됨 등): 팀 Slack `#dev-automation` 채널 질문
- **법적/계약 문제** (고객이 데이터 정확성 서명 거부, 약관 이의제기 등): 팀 리드에게 에스컬레이션
- **스킬 자체에 버그 / 개선 아이디어**: GitHub 이슈 또는 Claude Code 에 "browser-signup 스킬에 XX 추가" 로 요청

---

## 10. 첫 고객 전 자가 점검 (체크리스트)

정말 준비됐는지 셀프 체크:

- [ ] 이 문서 끝까지 읽었다
- [ ] `npm run smoke` 통과 확인
- [ ] `op whoami` 팀 계정 확인
- [ ] Potential 내부 데이터로 `./scripts/run-flow.sh --client=potential --project=duns-iupdate --list` 실행해 봄 (실제 제출은 하지 마세요)
- [ ] [intake-form-template.md](intake-form-template.md) 의 Section 9 서명 조항 읽어봄
- [ ] 1Password 볼트 만들기 연습 1회 해봄 (`Eddy Test - Platforms` 같은 더미 볼트)
- [ ] 첫 고객 engagement 일정 정해짐

여기까지 되면 실전 투입 가능합니다. 💪

화이팅 Eddy님!

— 주식회사 포텐셜 개발팀
