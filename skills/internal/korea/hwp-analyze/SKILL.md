---
name: hwp-analyze
description: Analyze the structure of a Korean HWP/HWPX file — tables, rows, fields, filled vs. empty cells. Use when the user asks to "analyze hwp", "inspect hwpx structure", or "list fields in a 한글 form".
---

# Analyze Korean HWP/HWPX File

## Input
$ARGUMENTS

## OS-specific approach

### Windows: use `pyhwpx` (recommended)

On Windows with the 한글 (Hangul Word Processor) application installed, use `pyhwpx`.

```python
from pyhwpx import Hwp

hwp = Hwp()
hwp.open("form.hwp")  # both .hwp and .hwpx supported

# List fields
fields = hwp.get_field_list()
print(fields)

# Read each field's value
for field in fields:
    value = hwp.get_field_text(field)
    print(f"{field}: {value}")

hwp.quit()
```

Install: `pip install pyhwpx`

### macOS / Linux: parse XML directly (.hwpx only)

An HWPX file is a ZIP archive.

```
form.hwpx/
├── Contents/
│   ├── section0.xml    # body content (first section)
│   ├── section1.xml    # additional sections (if any)
│   └── header.xml      # header metadata
├── settings.xml        # document settings
└── mimetype            # file-type marker
```

#### Procedure

1. **Unzip**
```bash
unzip -o {file}.hwpx -d {tmpdir}/
```

2. **Read the XML**: open `Contents/section0.xml` with the Read tool.

3. **Analyze structure**

**Namespace**: `hp` = `http://www.hancom.co.kr/hwpml/2011/paragraph`

| Tag | Meaning |
|-----|---------|
| `<hp:tbl>` | Table |
| `<hp:tr>` | Table row |
| `<hp:tc>` | Table cell |
| `<hp:t>` | Text content |
| `<hp:p>` | Paragraph |

**Example 2-column form row**:
```xml
<hp:tbl>
  <hp:tr>
    <hp:tc><hp:p><hp:t>field label</hp:t></hp:p></hp:tc>
    <hp:tc><hp:p><hp:t>value</hp:t></hp:p></hp:tc>
  </hp:tr>
</hp:tbl>
```

4. **Extract fields**: in a 2-column table the first cell is the label, the second cell is the value.

5. **Clean up the temp dir**
```bash
rm -rf {tmpdir}
```

## Report to the user

- Number of tables detected
- List of fields to be filled (empty cells)
- Fields already filled (if any)
- Next step — point them at `/hwp-fill`

## Caveats

- On macOS/Linux, `.hwp` is NOT supported → ask the user to re-save as `.hwpx` from 한글.
- On Windows, `pyhwpx` handles both `.hwp` and `.hwpx`.
- Tables with merged cells may surface with a different structure — flag them rather than guessing.
