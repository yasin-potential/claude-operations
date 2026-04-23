---
name: hwp-fill
description: Fill a Korean HWP/HWPX form with values from a markdown file or user-provided content. Use when the user asks to "fill the hwp form", "populate hwpx", or "write the 한글 form".
---

# Fill Korean HWP/HWPX Form

## Input
$ARGUMENTS

## OS-specific approach

### Windows: use `pyhwpx` (recommended)

On Windows with the 한글 (Hangul Word Processor) application installed, use `pyhwpx`.

```python
from pyhwpx import Hwp

hwp = Hwp()
hwp.open("form.hwp")  # both .hwp and .hwpx supported

# Fill fields
hwp.put_field_text("연구과제명", "AI-based diagnostic system")
hwp.put_field_text("연구책임자", "홍길동")

# Save
hwp.save_as("result.hwp")
hwp.quit()
```

Install: `pip install pyhwpx`

**Note**: `pyhwpx` writes into 한글's "누름틀" (press-frame) fields. If the form has no 누름틀, you must locate the target table cell and edit it directly instead.

### macOS / Linux: edit XML directly (.hwpx only)

#### Procedure

##### 1. Unzip the HWPX

```bash
mkdir -p {tmpdir}
unzip -o {form}.hwpx -d {tmpdir}/
```

##### 2. Analyze the form

Read `{tmpdir}/Contents/section0.xml` and:
- Find every table (`<hp:tbl>`)
- For each row, read the first cell as the field label
- If the second cell is empty, mark it as a slot to fill

##### 3. Extract values from the content

Parse the MD file (or user-provided content) into label → value pairs:
```markdown
# 연구과제명
AI-based diagnostic system

## 연구책임자
홍길동
```
→ `{"연구과제명": "AI-based diagnostic system", "연구책임자": "홍길동"}`

##### 4. Smart matching

Labels do not need to match exactly — match flexibly:
- `과제명` → `연구과제명` (substring)
- `책임자` → `연구책임자` (synonym)
- `연구 기간` → `연구기간` (ignore whitespace)

**Always confirm with the user when ambiguous**:
- Multiple candidate labels
- Meanings could diverge
- No match found for a given field

##### 5. Show the proposed mapping and get confirmation

```
Proposed mapping:
- 연구과제명 ← "AI-based diagnostic system"
- 연구책임자 ← "홍길동"
- 연구기간 ← (no value supplied)

Proceed?
```

##### 6. Edit the XML

Use the Edit tool on `section0.xml` to replace the target cell content:

**Before**:
```xml
<hp:tc><hp:p><hp:t></hp:t></hp:p></hp:tc>
```

**After**:
```xml
<hp:tc><hp:p><hp:t>홍길동</hp:t></hp:p></hp:tc>
```

Note: look for empty `<hp:t>` tags or self-closing `<hp:t/>` and populate them.

##### 7. Re-zip

```bash
cd {tmpdir}
zip -r {output}.hwpx *
```

**Critical**: run `zip` from INSIDE the temp directory, otherwise the archive structure breaks and 한글 cannot open it.

##### 8. Clean up

```bash
rm -rf {tmpdir}
```

## Output

- Default filename: `{original}_filled.hwpx` (or `.hwp`)
- If the user specifies an output name, use it
- Report which fields were filled and which were left empty

## Caveats

- On macOS/Linux, `.hwp` is NOT supported → ask the user to re-save as `.hwpx` from 한글.
- On Windows, `pyhwpx` handles both `.hwp` and `.hwpx`.
- XML-escape special characters: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`.
- For multi-line values, use multiple `<hp:p>` tags.
- Never modify the original file — always write a new one.
