import json, requests, time, os

API_KEY = os.environ.get("NOTION_API_KEY", "")
PAGE_ID = "328b6d88d2cf804c92b3cacac1f8e996"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# 1. Delete existing blocks
resp = requests.get(f"https://api.notion.com/v1/blocks/{PAGE_ID}/children?page_size=100", headers=HEADERS)
blocks_to_delete = resp.json().get("results", [])
while True:
    for b in blocks_to_delete:
        requests.delete(f'https://api.notion.com/v1/blocks/{b["id"]}', headers=HEADERS)
    print(f"Deleted {len(blocks_to_delete)} blocks")
    if not resp.json().get("has_more"):
        break
    resp = requests.get(f'https://api.notion.com/v1/blocks/{PAGE_ID}/children?page_size=100', headers=HEADERS)
    blocks_to_delete = resp.json().get("results", [])


# Helper functions
def rich(text, bold=False, italic=False, code=False, link=None):
    t = {"type": "text", "text": {"content": text}}
    if link:
        t["text"]["link"] = {"url": link}
    ann = {}
    if bold: ann["bold"] = True
    if italic: ann["italic"] = True
    if code: ann["code"] = True
    if ann:
        t["annotations"] = ann
    return t

def h1(text): return {"type": "heading_1", "heading_1": {"rich_text": [rich(text)]}}
def h2(text): return {"type": "heading_2", "heading_2": {"rich_text": [rich(text)]}}
def h3(text): return {"type": "heading_3", "heading_3": {"rich_text": [rich(text)]}}
def para(*parts): return {"type": "paragraph", "paragraph": {"rich_text": list(parts)}}
def bullet(*parts): return {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": list(parts)}}
def todo(text, checked=False): return {"type": "to_do", "to_do": {"rich_text": [rich(text)], "checked": checked}}
def divider(): return {"type": "divider", "divider": {}}
def callout(text, emoji="💡"): return {"type": "callout", "callout": {"rich_text": [rich(text)], "icon": {"type": "emoji", "emoji": emoji}}}
def quote(text): return {"type": "quote", "quote": {"rich_text": [rich(text)]}}

def toggle(title, children):
    return {
        "type": "toggle",
        "toggle": {
            "rich_text": [rich(title)],
            "children": children
        }
    }

def table_row(cells):
    return {
        "type": "table_row",
        "table_row": {
            "cells": [[rich(c)] for c in cells]
        }
    }

def table(headers, rows):
    w = len(headers)
    return {
        "type": "table",
        "table": {
            "table_width": w,
            "has_column_header": True,
            "has_row_header": False,
            "children": [table_row(headers)] + [table_row(r) for r in rows]
        }
    }


# 2. Build blocks
blocks = []

# Title area
blocks.append(quote("Audience: Project Manager | Scope: Webview app -> Google Play & Apple App Store submission"))
blocks.append(divider())

# Environment Setup
blocks.append(h1("Before You Start: Environment Setup"))

blocks.append(toggle("First time setup", [
    h3("1. Install Claude Code"),
    para(rich("Follow the official installation guide: "), rich("https://docs.anthropic.com/en/docs/claude-code/overview", link="https://docs.anthropic.com/en/docs/claude-code/overview")),
    h3("2. Download the operations repo"),
    para(rich("cd ~/Desktop/potential/projects", code=True)),
    para(rich("git clone https://github.com/potentialInc/claude-operations.git", code=True)),
    h3("3. Sync store skills"),
    para(rich("cd ~/Desktop/potential/projects/pipeline/claude-operations", code=True)),
    para(rich("bash scripts/sync-store-skills.sh", code=True)),
    para(rich("After this, all /store-xxx commands will be available in Claude Code for any project.")),
]))

blocks.append(toggle("Already have the operations repo?", [
    para(rich("cd ~/Desktop/potential/projects/pipeline/claude-operations", code=True)),
    para(rich("git pull && bash scripts/sync-store-skills.sh", code=True)),
]))

blocks.append(callout("Restart Claude Code after syncing for the new skills to take effect.", "\u26a0\ufe0f"))
blocks.append(divider())

# Step 1
blocks.append(h1("Step 1. Inform the Development Team"))
blocks.append(para(rich("As soon as a project needs a webview app, "), rich("inform the dev team before any deadline.", bold=True)))
blocks.append(todo("Submission deadline \u2014 When the app needs to be live"))
blocks.append(todo("Feature list \u2014 Push notifications, payment, social login, camera/location, etc."))
blocks.append(todo("Target stores \u2014 Google Play, App Store, or both"))
blocks.append(callout("The dev team needs lead time for native setup (1-3 days) and build process (1-2 days).", "\u23f0"))

blocks.append(toggle("\U0001f916 Automate with Claude Code", [
    para(rich("Open Claude Code in the project folder and run: "), rich("/store-prep", code=True)),
    para(rich("Claude analyzes the codebase and PRD, then asks you 3 simple questions (target stores, pricing, countries). It generates: store listing text, privacy policy, terms of service, client guide, and technical checklist \u2014 all automatically.")),
]))
blocks.append(divider())

# Step 2
blocks.append(h1("Step 2. Check Client's Developer Account"))
blocks.append(h3("Google Play"))
blocks.append(bullet(rich("Personal account: ", bold=True), rich("$25 one-time fee")))
blocks.append(bullet(rich("Organization account: ", bold=True), rich("$25 + identity verification (3-7 business days)")))
blocks.append(h3("Apple App Store"))
blocks.append(bullet(rich("Personal account: ", bold=True), rich("$99/year")))
blocks.append(bullet(rich("Organization account: ", bold=True), rich("$99/year + requires a "), rich("D-U-N-S number", bold=True), rich(" (can take 2-4 weeks)")))
blocks.append(callout("Start this immediately \u2014 account verification is often the longest blocker. Don't wait until the app is ready.", "\U0001f6a8"))
blocks.append(todo("Client's account type confirmed (Personal or Organization)"))
blocks.append(todo("Developer account created and verified"))
blocks.append(todo("If Organization: D-U-N-S number obtained (Apple only)"))
blocks.append(divider())

# Step 3
blocks.append(h1("Step 3. Prepare Store Listing Text"))
blocks.append(h3("Google Play (Required)"))
blocks.append(bullet(rich("App name", bold=True), rich(" (max 30 characters)")))
blocks.append(bullet(rich("Short description", bold=True), rich(" (max 80 characters)")))
blocks.append(bullet(rich("Full description", bold=True), rich(" (max 4000 characters)")))
blocks.append(h3("App Store (Required)"))
blocks.append(bullet(rich("App name", bold=True), rich(" (max 30 characters)")))
blocks.append(bullet(rich("Description", bold=True), rich(" (max 4000 characters)")))
blocks.append(bullet(rich("Keywords", bold=True), rich(" (max 100 characters, comma-separated)")))
blocks.append(bullet(rich("Support URL", bold=True)))
blocks.append(bullet(rich("Copyright", bold=True), rich(' (e.g., "2026 Company Name")')))

blocks.append(toggle("\U0001f916 Automate with Claude Code", [
    para(rich("/store-prep", code=True), rich(" generates store listing text for both stores by analyzing the PRD and i18n files. You review and edit.")),
]))
blocks.append(divider())

# Step 4
blocks.append(h1("Step 4. Prepare Visual Assets"))
blocks.append(h3("App Icon"))
blocks.append(bullet(rich("Provide the original logo/icon file ("), rich("minimum 1024\u00d71024px", bold=True), rich(")")))
blocks.append(bullet(rich("The developer resizes it to all required dimensions")))
blocks.append(h3("Screenshots & Banners"))
blocks.append(para(rich("Create banners that explain one or two features per page, with screenshots of the app on phone and iPad.")))
blocks.append(callout("Copy the banner example images from the original SOP here", "\U0001f5bc\ufe0f"))
blocks.append(para(rich("Each screenshot should:")))
blocks.append(bullet(rich("Show a real app screen inside a device mockup (phone or iPad)")))
blocks.append(bullet(rich("Include a short feature description text at the top")))
blocks.append(bullet(rich("Have a clean, branded background")))
blocks.append(h3("Pricing Screenshot"))
blocks.append(para(rich("If the app has pricing/subscription plans, prepare a screenshot of the pricing page.")))
blocks.append(callout("Copy the pricing screenshot from the original SOP here", "\U0001f5bc\ufe0f"))
blocks.append(h3("Asset Specifications"))
blocks.append(table(
    ["Asset", "Google Play", "App Store"],
    [
        ["App Icon", "512\u00d7512", "1024\u00d71024"],
        ["Phone Screenshots", '1080\u00d71920, min 2', '1242\u00d72688 (6.5"), min 3, max 10'],
        ["iPad Screenshots", "\u2014", "2048\u00d72732 (required)"],
        ["Feature Graphic", "1024\u00d7500", "\u2014"],
    ]
))
blocks.append(callout("iPad screenshots: Xcode\uc5d0\uc11c iPad \uc9c0\uc6d0\uc774 \uc124\uc815\ub418\uc5b4 \uc788\uc73c\ubbc0\ub85c iPad \uc2a4\ud06c\ub9b0\uc0f7\uc774 \ud544\uc218\uc785\ub2c8\ub2e4. \uc2e4\uc81c iPad \ub610\ub294 Xcode \uc2dc\ubbac\ub808\uc774\ud130\uc5d0\uc11c \uce90\ud504\ucc98\ud558\uc138\uc694.", "\u26a0\ufe0f"))
blocks.append(todo("App icon source provided (1024\u00d71024+)"))
blocks.append(todo("Phone screenshots created with device mockups"))
blocks.append(todo("iPad screenshots created"))
blocks.append(todo("Feature graphic created (Google Play, 1024\u00d7500)"))
blocks.append(todo("Pricing screenshot included (if applicable)"))

blocks.append(toggle("\U0001f916 Automate with Claude Code", [
    para(rich("/store-assets", code=True), rich(" \u2014 Claude auto-resizes icons, captures screenshots via Playwright, and opens an HTML designer for adding device frames and captions.")),
    para(rich("Prerequisites: App must be running + login credentials.")),
]))
blocks.append(divider())

# Step 5
blocks.append(h1("Step 5. Prepare Legal Documents"))
blocks.append(todo("Privacy Policy \u2014 Must be hosted at a publicly accessible URL"))
blocks.append(todo("Terms of Service \u2014 Recommended"))
blocks.append(toggle("\U0001f916 Automate with Claude Code", [
    para(rich("/store-prep", code=True), rich(" generates both documents by analyzing which data the app collects.")),
]))
blocks.append(divider())

# Step 6
blocks.append(h1("Step 6. Prepare a Test Account"))
blocks.append(todo("Login credentials \u2014 Working username/password"))
blocks.append(todo("Pre-populated content \u2014 Account must already have data. Do NOT provide an empty account."))
blocks.append(todo("No unnecessary required fields \u2014 Phone, gender, etc. not required unless functionally necessary"))
blocks.append(todo("Special instructions \u2014 If anything specific is needed to test the app"))
blocks.append(callout("Common rejection reason: Providing an empty test account. Reviewers need to see the app with real content.", "\U0001f6a8"))
blocks.append(divider())

# Step 7-9
blocks.append(h1("Step 7\u20139. Developer Phases"))
DEV_SOP_URL = "https://www.notion.so/potentialinc/App-Store-Submission-Developer-SOP-328b6d88d2cf80d09572db36bab4e26b"
blocks.append(para(rich("These steps are handled by the development team. Refer to "), rich("App Store Submission \u2014 Developer SOP", bold=True, link=DEV_SOP_URL), rich(" for details.")))
blocks.append(table(
    ["Phase", "What Happens", "PM Action"],
    [
        ["7. Native Setup", "Web app \u2192 native app + required features (push, Apple login, account deletion)", "Confirm required features with dev"],
        ["8. Deployment", "Production server with HTTPS", "Verify production URL opens in browser"],
        ["9. Build & Test", "Release build \u2192 internal testing / TestFlight", "Smoke test the build"],
    ]
))
blocks.append(h3("Smoke Test (Step 9)"))
blocks.append(para(rich("When the developer shares a test build, verify:")))
blocks.append(todo("App opens without crash"))
blocks.append(todo("Login/signup works"))
blocks.append(todo("Core features function correctly"))
blocks.append(todo("Push notifications arrive"))
blocks.append(todo("All pages load properly"))
blocks.append(todo("No placeholder text or broken images"))
blocks.append(todo("Permission popups explain why they're needed"))
blocks.append(todo("iPad: Layout displays correctly (no stretched/broken UI)"))
blocks.append(divider())

# Step 10
blocks.append(h1("Step 10. Store Submission"))
blocks.append(h3("What PM enters in the store console:"))
blocks.append(todo("Store listing text (title, descriptions)"))
blocks.append(todo("Screenshots and icon uploaded"))
blocks.append(todo("Content rating questionnaire answered"))
blocks.append(todo("Data safety / privacy labels completed"))
blocks.append(todo("Privacy policy URL entered"))
blocks.append(todo("Test account credentials and review notes entered"))
blocks.append(todo("Submit for review"))
blocks.append(callout("Build file (AAB/IPA) upload is done by the developer. PM handles metadata and submission.", "\U0001f4a1"))

blocks.append(toggle("\U0001f916 Automate with Claude Code", [
    para(rich("/store-submit", code=True), rich(" \u2014 Claude auto-drafts data safety responses and age rating answers by analyzing the code. You review and enter them into the store console.")),
]))
blocks.append(divider())

# Checklist
blocks.append(h1("Checklist (Copy to your project page)"))
blocks.append(callout("\uc544\ub798 \uccb4\ud06c\ub9ac\uc2a4\ud2b8\ub97c \ubcf8\uc778\uc758 Notion \ud504\ub85c\uc81d\ud2b8 \ud398\uc774\uc9c0\uc5d0 \ubcf5\uc0ac\ud574\uc11c \uc9c4\ud589 \uc0c1\ud669\uc744 \uccb4\ud06c\ud558\uba70 \uc0ac\uc6a9\ud558\uc138\uc694.", "\U0001f4cb"))

blocks.append(h3("Preparation (PM)"))
blocks.append(todo("Dev team informed with deadline and feature list"))
blocks.append(todo("Client's developer account confirmed and verified"))
blocks.append(todo("Store listing text prepared and reviewed"))
blocks.append(todo("App icon source provided (1024\u00d71024+)"))
blocks.append(todo("Phone screenshots created with device mockups"))
blocks.append(todo("iPad screenshots created"))
blocks.append(todo("Feature graphic created (Google Play)"))
blocks.append(todo("Privacy policy hosted at public URL"))
blocks.append(todo("Terms of service prepared"))
blocks.append(todo("Test account ready with pre-populated content"))

blocks.append(h3("Developer Phases"))
blocks.append(todo("Native features implemented (push, Apple login, account deletion)"))
blocks.append(todo("Production server deployed with HTTPS"))
blocks.append(todo("Release build \u2192 internal testing / TestFlight"))
blocks.append(todo("PM smoke test passed (including iPad)"))

blocks.append(h3("Submission (PM)"))
blocks.append(todo("Store listing text entered"))
blocks.append(todo("Screenshots and icon uploaded"))
blocks.append(todo("Content rating questionnaire completed"))
blocks.append(todo("Data safety / privacy labels completed"))
blocks.append(todo("Test account credentials and review notes entered"))
blocks.append(todo("Submitted for review"))

blocks.append(h3("Post-Submission"))
blocks.append(todo("Review result received"))
blocks.append(todo("If rejected: forwarded to dev \u2192 fixed \u2192 re-submitted"))
blocks.append(todo("App is live on the store"))
blocks.append(divider())

# Client Communication Template
blocks.append(h1("Client Communication Template"))
blocks.append(callout("\ud504\ub85c\uc81d\ud2b8 \uc2dc\uc791 \uc2dc \ud074\ub77c\uc774\uc5b8\ud2b8\uc5d0\uac8c \uc544\ub798 \ub0b4\uc6a9\uc744 \uc694\uccad\ud558\uc138\uc694.", "\U0001f4e8"))

blocks.append(h3("1. \uc571 \uc774\ub984"))
blocks.append(para(rich("\uc2a4\ud1a0\uc5b4\uc5d0 \ud45c\uc2dc\ub420 \uc815\uc2dd \uc571 \uc774\ub984")))
blocks.append(callout("\uc571 \uc124\uba85(Description)\uc740 \uc694\uccad\ud558\ub418, \ub300\ubd80\ubd84 PM\uc774 \uc791\uc131\ud574\uc57c \ud569\ub2c8\ub2e4", "\U0001f4a1"))

blocks.append(h3("2. Google Play \uac1c\ubc1c\uc790 \uacc4\uc815"))
blocks.append(para(rich("\uc774\uba54\uc77c / \ube44\ubc00\ubc88\ud638")))
blocks.append(para(rich("\uacc4\uc815\uc774 \uc5c6\uc73c\uba74 \uc0dd\uc131 \uc548\ub0b4: "), rich("https://play.google.com/console", link="https://play.google.com/console"), rich(" ($25)")))

blocks.append(h3("3. Apple \uac1c\ubc1c\uc790 \uacc4\uc815"))
blocks.append(para(rich("Apple ID / \ube44\ubc00\ubc88\ud638")))
blocks.append(para(rich("\uacc4\uc815\uc774 \uc5c6\uc73c\uba74 \uc0dd\uc131 \uc548\ub0b4: "), rich("https://developer.apple.com", link="https://developer.apple.com"), rich(" ($99/year)")))

blocks.append(h3("4. \uc571 \uc544\uc774\ucf58 (\ub85c\uace0)"))
blocks.append(para(rich("1024\u00d71024px \uc774\uc0c1\uc758 \uc6d0\ubcf8 \ud30c\uc77c")))
blocks.append(callout("\ud074\ub77c\uc774\uc5b8\ud2b8\uac00 \uc900\ube44\ud558\uc9c0 \ubabb\ud560 \uacbd\uc6b0 \ub514\uc790\uc778\ud300\uc744 \ud1b5\ud574 \uc9c4\ud589", "\U0001f4a1"))

blocks.append(h3("5. \ub3c4\uba54\uc778"))
blocks.append(para(rich("\uad6c\uc785 \ud6c4 \uad6c\uc785\ucc98 \uc544\uc774\ub514/\ube44\ubc00\ubc88\ud638 \uc804\ub2ec (\uc608: Gabia, GoDaddy, Namecheap)")))

blocks.append(h3("6. AWS \uacc4\uc815"))
blocks.append(para(rich("\uac00\uc785 \ud6c4 \uc544\uc774\ub514/\ube44\ubc00\ubc88\ud638 \uc804\ub2ec")))
blocks.append(callout("\ub098\uba38\uc9c0 \uc11c\ubc84 \uc14b\ud305\uc740 \uac1c\ubc1c\ud300\uc774 \uc9c4\ud589\ud569\ub2c8\ub2e4", "\U0001f4a1"))


# 3. Upload in batches (max 100 per request)
total = len(blocks)
batch_size = 100
for i in range(0, total, batch_size):
    batch = blocks[i:i+batch_size]
    resp = requests.patch(
        f"https://api.notion.com/v1/blocks/{PAGE_ID}/children",
        headers=HEADERS,
        json={"children": batch}
    )
    if resp.status_code != 200:
        print(f"Error batch {i}: {resp.status_code} {resp.text[:300]}")
    else:
        print(f"Batch {i}-{i+len(batch)}: OK")
    if i + batch_size < total:
        time.sleep(0.5)

# 4. Update page title
resp = requests.patch(
    f"https://api.notion.com/v1/pages/{PAGE_ID}",
    headers=HEADERS,
    json={"properties": {"title": {"title": [{"text": {"content": "App Store Submission \u2014 PM SOP"}}]}}}
)
print(f"Title update: {resp.status_code}")
print(f"Done! Total blocks: {total}")
