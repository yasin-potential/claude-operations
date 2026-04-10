"""
Convert markdown file to Notion blocks and update a Notion page.
Usage: python scripts/md-to-notion.py <page_id> <markdown_file>
"""
import sys, re, json, time, os
import urllib.request, urllib.error

API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"

def api_request(method, path, body=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Notion-Version", NOTION_VERSION)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"API Error {e.code}: {err[:300]}")
        raise

def delete_all_blocks(page_id):
    """Delete all existing blocks from a page."""
    print("Deleting existing blocks...")
    cursor = None
    block_ids = []
    while True:
        path = f"/blocks/{page_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        data = api_request("GET", path)
        block_ids.extend(b["id"] for b in data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")

    for bid in block_ids:
        api_request("DELETE", f"/blocks/{bid}")
        time.sleep(0.05)  # rate limit
    print(f"  Deleted {len(block_ids)} blocks")

def rich_text(text, bold=False, italic=False, code=False, link=None):
    """Create a Notion rich_text object."""
    rt = {
        "type": "text",
        "text": {"content": text},
        "annotations": {
            "bold": bold, "italic": italic, "code": code,
            "strikethrough": False, "underline": False, "color": "default"
        }
    }
    if link:
        rt["text"]["link"] = {"url": link}
    return rt

def parse_inline(text):
    """Parse inline markdown (bold, code, links) into rich_text array."""
    result = []
    i = 0
    while i < len(text):
        # Bold **text**
        m = re.match(r'\*\*(.+?)\*\*', text[i:])
        if m:
            result.append(rich_text(m.group(1), bold=True))
            i += m.end()
            continue
        # Inline code `text`
        m = re.match(r'`(.+?)`', text[i:])
        if m:
            result.append(rich_text(m.group(1), code=True))
            i += m.end()
            continue
        # Link [text](url)
        m = re.match(r'\[(.+?)\]\((.+?)\)', text[i:])
        if m:
            result.append(rich_text(m.group(1), link=m.group(2)))
            i += m.end()
            continue
        # Plain text - consume until next special char
        m = re.match(r'[^*`\[]+', text[i:])
        if m:
            result.append(rich_text(m.group(0)))
            i += m.end()
            continue
        # Single special char that didn't match a pattern
        result.append(rich_text(text[i]))
        i += 1
    return result if result else [rich_text(text)]

def md_to_blocks(md_text):
    """Convert markdown text to Notion blocks."""
    lines = md_text.split('\n')
    blocks = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Horizontal rule
        if line.strip() == '---':
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            i += 1
            continue

        # Headings
        m = re.match(r'^(#{1,3})\s+(.+)', line)
        if m:
            level = len(m.group(1))
            text = m.group(2)
            htype = f"heading_{level}"
            blocks.append({
                "object": "block",
                "type": htype,
                htype: {"rich_text": parse_inline(text), "is_toggleable": False}
            })
            i += 1
            continue

        # Code block
        if line.strip().startswith('```'):
            lang = line.strip()[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            code_content = '\n'.join(code_lines)
            if code_content:
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [rich_text(code_content)],
                        "language": lang if lang else "plain text"
                    }
                })
            continue

        # Toggle (details/summary)
        if line.strip().startswith('<details>'):
            # Find summary
            i += 1
            summary_text = "Toggle"
            while i < len(lines):
                sm = re.match(r'<summary>.*?<b>(.+?)</b>.*?</summary>', lines[i])
                if sm:
                    summary_text = sm.group(1)
                    i += 1
                    break
                sm2 = re.match(r'<summary>(.+?)</summary>', lines[i])
                if sm2:
                    summary_text = sm2.group(1)
                    i += 1
                    break
                i += 1

            # Collect toggle content until </details>
            toggle_content = []
            while i < len(lines) and '</details>' not in lines[i]:
                toggle_content.append(lines[i])
                i += 1
            i += 1  # skip </details>

            # Parse toggle children
            children = md_to_blocks('\n'.join(toggle_content))

            block = {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": parse_inline(summary_text),
                    "is_toggleable": True
                }
            }
            if children:
                block["heading_3"]["children"] = children[:100]  # Notion limit
            blocks.append(block)
            continue

        # Table
        if line.strip().startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1

            if len(table_lines) >= 2:
                # Parse header
                header_cells = [c.strip() for c in table_lines[0].strip('|').split('|')]
                width = len(header_cells)

                rows = [header_cells]
                for tl in table_lines[2:]:  # skip separator row
                    cells = [c.strip() for c in tl.strip('|').split('|')]
                    # Pad or trim to match header width
                    cells = (cells + [''] * width)[:width]
                    rows.append(cells)

                table_block = {
                    "object": "block",
                    "type": "table",
                    "table": {
                        "table_width": width,
                        "has_column_header": True,
                        "has_row_header": False,
                        "children": []
                    }
                }
                for row in rows:
                    table_block["table"]["children"].append({
                        "object": "block",
                        "type": "table_row",
                        "table_row": {
                            "cells": [parse_inline(cell) for cell in row]
                        }
                    })
                blocks.append(table_block)
            continue

        # Blockquote / callout
        if line.strip().startswith('>'):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote_lines.append(re.sub(r'^>\s*', '', lines[i]))
                i += 1
            quote_text = ' '.join(l for l in quote_lines if l.strip())
            if quote_text:
                blocks.append({
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": parse_inline(quote_text),
                        "icon": {"type": "emoji", "emoji": "💡"},
                        "color": "gray_background"
                    }
                })
            continue

        # Checklist item
        m = re.match(r'^(\s*)- \[([ x])\]\s+(.+)', line)
        if m:
            indent = len(m.group(1))
            checked = m.group(2) == 'x'
            text = m.group(3)
            block = {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": parse_inline(text),
                    "checked": checked
                }
            }
            blocks.append(block)
            i += 1
            # Collect nested checklist items as children
            children = []
            while i < len(lines):
                nm = re.match(r'^(\s+)- \[([ x])\]\s+(.+)', lines[i])
                if nm and len(nm.group(1)) > indent:
                    children.append({
                        "object": "block",
                        "type": "to_do",
                        "to_do": {
                            "rich_text": parse_inline(nm.group(3)),
                            "checked": nm.group(2) == 'x'
                        }
                    })
                    i += 1
                else:
                    break
            if children:
                block["to_do"]["children"] = children
            continue

        # Bullet list item
        m = re.match(r'^(\s*)- (.+)', line)
        if m:
            text = m.group(2)
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": parse_inline(text)}
            })
            i += 1
            continue

        # Numbered list item
        m = re.match(r'^(\s*)\d+\.\s+(.+)', line)
        if m:
            text = m.group(2)
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": parse_inline(text)}
            })
            i += 1
            continue

        # Skip HTML tags
        if re.match(r'^\s*</?[a-z]', line):
            i += 1
            continue

        # Regular paragraph
        if line.strip():
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": parse_inline(line.strip())}
            })
        i += 1

    return blocks

def append_blocks(page_id, blocks):
    """Append blocks to a page in batches of 100."""
    for start in range(0, len(blocks), 100):
        batch = blocks[start:start+100]
        api_request("PATCH", f"/blocks/{page_id}/children", {"children": batch})
        print(f"  Appended blocks {start+1}-{start+len(batch)}")
        if start + 100 < len(blocks):
            time.sleep(0.3)

def main():
    if len(sys.argv) != 3:
        print("Usage: python md-to-notion.py <page_id> <markdown_file>")
        sys.exit(1)

    page_id = sys.argv[1]
    md_file = sys.argv[2]

    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    print(f"Converting {md_file}...")
    blocks = md_to_blocks(md_content)
    print(f"  Generated {len(blocks)} blocks")

    delete_all_blocks(page_id)
    append_blocks(page_id, blocks)
    print("Done!")

if __name__ == "__main__":
    main()
