---
name: generate-korean-prd
description: "Generate a Korean PRD document with company logo watermark as PDF. Invoke when user needs a Korean-language PRD deliverable for clients."
argument-hint: "<project-content-file> [--client <company>] [--contact <name>] [--analysis]"
---

# Korean PRD PDF Generator

프로젝트 요구사항 파일을 기반으로 한글 PRD PDF 문서를 자동 생성합니다. 회사 로고를 워터마크로 포함하여 복제 방지 효과를 제공합니다.

---

## Quick Start

```bash
# 기본 사용
/generate-korean-prd /path/to/project-content.txt

# 고객사 정보 포함
/generate-korean-prd /path/to/project.txt --client "인스티드컴퍼니" --contact "김정수"

# 난이도/리스크 분석 포함
/generate-korean-prd /path/to/project.txt --client "테스트회사" --contact "홍길동" --analysis
```

---

## Workflow Overview

```
┌─────────────────┐
│  Step 1         │
│  입력 검증       │
└────────┬────────┘
         │
┌────────▼────────┐
│  Step 2         │
│  프로젝트 분석   │
└────────┬────────┘
         │
┌────────▼────────┐
│  Step 3         │
│  HTML 생성      │
└────────┬────────┘
         │
┌────────▼────────┐
│  Step 4         │
│  PDF 변환       │
└────────┬────────┘
         │
┌────────▼────────┐
│  Step 5         │
│  결과 보고      │
└─────────────────┘
```

---

## Step 1: 입력 검증

### 1.1 인자 파싱

`$ARGUMENTS`에서 다음을 추출:
- **파일 경로** (필수): 프로젝트 내용이 담긴 파일
- **--client**: 고객사 이름 (선택)
- **--contact**: 고객사 담당자 이름 (선택)
- **--analysis**: 난이도/리스크 분석 포함 여부 (선택)

### 1.2 파일 검증

1. 프로젝트 내용 파일 존재 확인
2. 지원 형식: `.txt`, `.md`, `.pdf`
3. 파일이 비어있지 않은지 확인

### 1.3 로고 파일 확인

로고 파일 위치: `.claude/templates/logo.svg`

로고 파일이 없으면 경고 메시지 출력 후 로고 없이 진행:
```
Warning: Logo file not found at .claude/templates/logo.svg
Proceeding without logo watermark.
```

### 1.4 에러 처리

**파일 경로 누락:**
```
Error: 프로젝트 내용 파일 경로가 필요합니다.
Usage: /generate-korean-prd /path/to/project.txt [--client "고객사"] [--contact "담당자"]
```

**파일 없음:**
```
Error: 파일을 찾을 수 없습니다: [file_path]
```

---

## Step 2: 프로젝트 내용 분석

### 2.1 파일 읽기

프로젝트 내용 파일을 읽고 다음 정보를 추출:

1. **프로젝트명** - 서비스/앱 이름
2. **프로젝트 배경** - 왜 이 프로젝트가 필요한가
3. **프로젝트 목표** - 달성하고자 하는 것
4. **대상 사용자** - 누가 사용하는가
5. **주요 기능** - 핵심 기능 목록
6. **기술 요구사항** - 외부 연동, 보안 등

### 2.2 PRD 구조 생성

추출된 정보를 바탕으로 PRD 섹션 구성:

```
1. 개요
   1.1 프로젝트 배경
   1.2 프로젝트 목표
   1.3 대상 사용자

2. 기능 요구사항
   2.1 [기능 카테고리 1]
   2.2 [기능 카테고리 2]
   ...

3. 기술 요구사항
   3.1 보안
   3.2 데이터 관리
   3.3 외부 연동

4. 화면 플로우 (해당 시)

[--analysis 옵션 시]
5. 프로젝트 난이도 분석
6. 개발 가능성 및 리스크
```

---

## Step 3: HTML 생성

### 3.1 저장 위치

**디렉토리**: `.claude-project/prd/`
**파일명**: `[ProjectName]_PRD.html`

디렉토리가 없으면 생성.

### 3.2 HTML 템플릿

다음 템플릿을 사용하여 HTML 파일 생성:

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[PROJECT_NAME] - 제품 요구사항 정의서 (PRD)</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
            line-height: 1.8;
            color: #333;
            background: #fff;
            position: relative;
        }

        /* 워터마크 */
        .watermark {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-30deg);
            opacity: 0.03;
            z-index: -1;
            pointer-events: none;
            width: 600px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
        }

        /* 헤더 */
        .header {
            text-align: center;
            padding-bottom: 30px;
            border-bottom: 3px solid #624DFF;
            margin-bottom: 40px;
        }

        .logo {
            width: 200px;
            margin-bottom: 20px;
        }

        .header h1 {
            color: #050042;
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header .subtitle {
            color: #666;
            font-size: 14px;
        }

        .confidential {
            background: #f8f8f8;
            border: 1px solid #ddd;
            padding: 10px 20px;
            border-radius: 5px;
            display: inline-block;
            margin-top: 15px;
            font-size: 12px;
            color: #e74c3c;
            font-weight: bold;
        }

        /* 문서 정보 */
        .doc-info {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 40px;
        }

        .doc-info table {
            width: 100%;
            border-collapse: collapse;
        }

        .doc-info td {
            padding: 8px 15px;
            border-bottom: 1px solid #eee;
        }

        .doc-info td:first-child {
            font-weight: bold;
            color: #624DFF;
            width: 150px;
        }

        /* 섹션 */
        section {
            margin-bottom: 40px;
            page-break-inside: avoid;
        }

        h2 {
            color: #050042;
            font-size: 20px;
            padding: 10px 0;
            border-bottom: 2px solid #624DFF;
            margin-bottom: 20px;
        }

        h3 {
            color: #624DFF;
            font-size: 16px;
            margin: 20px 0 10px 0;
        }

        h4 {
            color: #333;
            font-size: 14px;
            margin: 15px 0 8px 0;
            padding-left: 10px;
            border-left: 3px solid #624DFF;
        }

        p {
            margin-bottom: 12px;
            text-align: justify;
        }

        ul, ol {
            margin-left: 25px;
            margin-bottom: 15px;
        }

        li {
            margin-bottom: 8px;
        }

        /* 기능 카드 */
        .feature-card {
            background: #f9f9ff;
            border: 1px solid #e0e0ff;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .feature-card h4 {
            border-left: none;
            padding-left: 0;
            color: #624DFF;
            margin-top: 0;
        }

        /* 테이블 */
        table.data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }

        table.data-table th,
        table.data-table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }

        table.data-table th {
            background: #624DFF;
            color: white;
            font-weight: bold;
        }

        table.data-table tr:nth-child(even) {
            background: #f9f9f9;
        }

        /* 우선순위 뱃지 */
        .priority-high {
            background: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
        }

        .priority-medium {
            background: #f39c12;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
        }

        .priority-low {
            background: #27ae60;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
        }

        /* 난이도/리스크 뱃지 (--analysis 옵션 시) */
        .difficulty-very-high {
            background: #8e44ad;
            color: white;
            padding: 3px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }

        .difficulty-medium {
            background: #f39c12;
            color: white;
            padding: 3px 10px;
            border-radius: 3px;
            font-size: 12px;
        }

        .risk-unstable {
            background: #e67e22;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
        }

        .risk-ok {
            background: #27ae60;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
        }

        /* 경고 박스 */
        .warning-box {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-left: 4px solid #ffc107;
            padding: 15px 20px;
            border-radius: 5px;
            margin: 20px 0;
        }

        .warning-box h4 {
            color: #856404;
            border-left: none;
            padding-left: 0;
            margin-top: 0;
        }

        .warning-box ul {
            color: #856404;
            margin-bottom: 0;
        }

        /* 정보 박스 */
        .info-box {
            background: #e7f3ff;
            border: 1px solid #b6d4fe;
            border-left: 4px solid #0d6efd;
            padding: 15px 20px;
            border-radius: 5px;
            margin: 20px 0;
        }

        .info-box h4 {
            color: #084298;
            border-left: none;
            padding-left: 0;
            margin-top: 0;
        }

        /* 푸터 */
        .footer {
            text-align: center;
            padding-top: 30px;
            border-top: 1px solid #eee;
            margin-top: 50px;
            color: #999;
            font-size: 12px;
        }

        /* 페이지 나눔 */
        .page-break {
            page-break-before: always;
        }
    </style>
</head>
<body>
    <!-- 워터마크 (로고 SVG 삽입) -->
    <div class="watermark">
        [LOGO_SVG_CONTENT]
    </div>

    <div class="container">
        <!-- 헤더 -->
        <header class="header">
            [HEADER_LOGO_SVG]
            <h1>제품 요구사항 정의서 (PRD)</h1>
            <p class="subtitle">[PROJECT_NAME] - [PROJECT_DESCRIPTION]</p>
            <div class="confidential">CONFIDENTIAL - 대외비</div>
        </header>

        <!-- 문서 정보 -->
        <div class="doc-info">
            <table>
                <tr>
                    <td>문서 버전</td>
                    <td>1.0</td>
                </tr>
                <tr>
                    <td>작성일</td>
                    <td>[DATE]</td>
                </tr>
                <tr>
                    <td>작성자</td>
                    <td>Potential</td>
                </tr>
                [CLIENT_INFO_ROWS]
                <tr>
                    <td>문서 상태</td>
                    <td>초안</td>
                </tr>
            </table>
        </div>

        <!-- PRD 섹션들 -->
        [PRD_SECTIONS]

        <!-- 푸터 -->
        <footer class="footer">
            [FOOTER_LOGO_SVG]
            <p>본 문서는 Potential의 대외비 문서입니다.</p>
            <p>무단 복제 및 배포를 금지합니다.</p>
            <p style="margin-top: 10px;">&copy; [YEAR] Potential. All Rights Reserved.</p>
        </footer>
    </div>
</body>
</html>
```

### 3.3 변수 치환

| 변수 | 값 |
|------|-----|
| `[PROJECT_NAME]` | 프로젝트명 |
| `[PROJECT_DESCRIPTION]` | 프로젝트 한줄 설명 |
| `[DATE]` | 오늘 날짜 (YYYY년 MM월 DD일) |
| `[YEAR]` | 현재 연도 |
| `[LOGO_SVG_CONTENT]` | 로고 SVG 내용 (워터마크용) |
| `[HEADER_LOGO_SVG]` | 헤더 로고 (class="logo") |
| `[FOOTER_LOGO_SVG]` | 푸터 로고 (작게) |
| `[CLIENT_INFO_ROWS]` | 고객사/담당자 정보 행 (옵션) |
| `[PRD_SECTIONS]` | PRD 본문 섹션들 |

### 3.4 고객사 정보 행 (--client, --contact 옵션 시)

```html
<tr>
    <td>고객사</td>
    <td>[CLIENT_NAME]</td>
</tr>
<tr>
    <td>고객사 담당자</td>
    <td>[CONTACT_NAME]</td>
</tr>
```

---

## Step 4: PDF 변환

### 4.1 Chrome Headless 명령어

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless \
  --disable-gpu \
  --print-to-pdf="[OUTPUT_PDF_PATH]" \
  --no-margins \
  "file://[INPUT_HTML_PATH]"
```

### 4.2 대체 방법 (Chrome 없을 시)

Chrome이 설치되지 않은 경우 wkhtmltopdf 또는 다른 도구 사용 가능:

```bash
# wkhtmltopdf
wkhtmltopdf [INPUT_HTML_PATH] [OUTPUT_PDF_PATH]
```

### 4.3 에러 처리

**PDF 변환 실패:**
```
Error: PDF 변환에 실패했습니다.
Chrome이 설치되어 있는지 확인해주세요.
HTML 파일은 다음 위치에 저장되었습니다: [HTML_PATH]
```

---

## Step 5: 결과 보고

### 5.1 성공 메시지

```
✅ PRD 문서가 생성되었습니다.

📄 HTML: .claude-project/prd/[ProjectName]_PRD.html
📄 PDF:  .claude-project/prd/[ProjectName]_PRD.pdf

포함된 내용:
- 프로젝트 개요
- 기능 요구사항 ([N]개 섹션)
- 기술 요구사항
[--analysis 시] - 프로젝트 난이도 분석
[--analysis 시] - 개발 가능성 및 리스크

고객사: [CLIENT_NAME]
담당자: [CONTACT_NAME]
```

---

## Error Handling

| 에러 상황 | 메시지 | 대응 |
|----------|--------|------|
| 파일 경로 누락 | "프로젝트 내용 파일 경로가 필요합니다" | 사용법 안내 |
| 파일 없음 | "파일을 찾을 수 없습니다" | 경로 확인 요청 |
| 로고 없음 | "로고 파일을 찾을 수 없습니다" | 로고 없이 진행 |
| PDF 변환 실패 | "PDF 변환에 실패했습니다" | HTML 파일 위치 안내 |
| 빈 내용 | "프로젝트 내용이 비어있습니다" | 파일 내용 확인 요청 |

---

## Examples

### 예제 1: 기본 사용

```bash
/generate-korean-prd /Users/dongsub/Downloads/어플기능.txt
```

**출력:**
```
✅ PRD 문서가 생성되었습니다.

📄 HTML: .claude-project/prd/StreamShare_PRD.html
📄 PDF:  .claude-project/prd/StreamShare_PRD.pdf
```

### 예제 2: 고객사 정보 포함

```bash
/generate-korean-prd /path/to/project.txt --client "인스티드컴퍼니" --contact "김정수"
```

### 예제 3: 난이도 분석 포함

```bash
/generate-korean-prd /path/to/project.txt --client "테스트회사" --contact "홍길동" --analysis
```

---

## Notes

1. **로고 파일**: `.claude/templates/logo.svg`에 회사 로고 SVG 파일이 있어야 워터마크가 적용됩니다.
2. **PDF 변환**: macOS에서 Google Chrome이 설치되어 있어야 합니다.
3. **한글 폰트**: 'Malgun Gothic' 또는 'Apple SD Gothic Neo' 폰트가 시스템에 있어야 합니다.
4. **출력 위치**: `.claude-project/prd/` 폴더에 HTML과 PDF 파일이 생성됩니다.
