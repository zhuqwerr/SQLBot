# Report Q&A Platform Rebranding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove user-visible `SQLBot` branding and replace it with localized “Intelligent Report Q&A” platform and assistant names.

**Architecture:** Use a targeted replacement instead of a global rename. Add a regression test that scans known user-visible files for forbidden brand text while allowing internal identifiers, interfaces, package paths, and encryption keys to keep their existing names.

**Tech Stack:** Vue 3, Vite, TypeScript, Vue I18n, FastAPI, Python unittest/pytest, PowerShell, Pillow-compatible Python image generation when available.

---

## File Structure

- `tests/test_visible_branding.py`: new regression test for user-visible branding.
- `frontend/index.html`, `frontend/embedded.html`: browser title fallbacks.
- `frontend/src/i18n/en.json`, `frontend/src/i18n/zh-CN.json`, `frontend/src/i18n/zh-TW.json`, `frontend/src/i18n/ko-KR.json`: localized visible text.
- `frontend/src/stores/appearance.ts`, `frontend/src/stores/chatConfig.ts`, `frontend/src/utils/utils.ts`: frontend fallback names and titles.
- `frontend/src/views/chat/index.vue`, `frontend/src/views/system/appearance/index.vue`, `frontend/src/views/system/appearance/LoginPreview.vue`, `frontend/src/views/system/parameter/index.vue`, `frontend/src/views/system/user/User.vue`: hardcoded visible defaults.
- `backend/main.py`, `backend/common/core/config.py`, `backend/apps/chat/models/chat_model.py`: API docs, MCP metadata, default password, and visible chat model defaults.
- `docker-compose.yaml`, `installer/install.conf`, `installer/install.sh`, `installer/uninstall.sh`, `installer/sctl`, `installer/sqlbot/templates/sqlbot.conf`: deployment and terminal-facing defaults.
- `frontend/src/assets/embedded/LOGO-about.png`, `frontend/src/assets/login-bg-sqlbot.jpg`, `frontend/src/assets/LOGO.svg`, `frontend/public/vite-sqlbot.svg`: user-visible or metadata brand assets.

## Task 1: Add Failing Brand Scan Test

**Files:**
- Create: `tests/test_visible_branding.py`

- [ ] **Step 1: Write the failing test**

```python
import os
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VISIBLE_TEXT_FILES = [
    "frontend/index.html",
    "frontend/embedded.html",
    "frontend/src/i18n/en.json",
    "frontend/src/i18n/zh-CN.json",
    "frontend/src/i18n/zh-TW.json",
    "frontend/src/i18n/ko-KR.json",
    "frontend/src/stores/appearance.ts",
    "frontend/src/stores/chatConfig.ts",
    "frontend/src/utils/utils.ts",
    "frontend/src/views/chat/index.vue",
    "frontend/src/views/system/appearance/index.vue",
    "frontend/src/views/system/appearance/LoginPreview.vue",
    "frontend/src/views/system/parameter/index.vue",
    "frontend/src/views/system/user/User.vue",
    "backend/main.py",
    "backend/common/core/config.py",
    "backend/apps/chat/models/chat_model.py",
    "docker-compose.yaml",
    "installer/install.conf",
    "installer/install.sh",
    "installer/uninstall.sh",
    "installer/sctl",
    "installer/sqlbot/templates/sqlbot.conf",
]

VISIBLE_BINARY_FILES = [
    "frontend/src/assets/embedded/LOGO-about.png",
    "frontend/src/assets/login-bg-sqlbot.jpg",
]

class TestVisibleBranding(unittest.TestCase):
    def test_visible_text_files_do_not_show_sqlbot_brand(self):
        failures = []
        for rel_path in VISIBLE_TEXT_FILES:
            path = os.path.join(PROJECT_ROOT, rel_path)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if "SQLBot" in content:
                failures.append(rel_path)
        self.assertEqual([], failures)

    def test_visible_binary_brand_assets_are_blank_placeholders(self):
        for rel_path in VISIBLE_BINARY_FILES:
            path = os.path.join(PROJECT_ROOT, rel_path)
            with open(path, "rb") as f:
                content = f.read()
            self.assertNotIn(b"SQLBot", content, rel_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_visible_branding.py -q`

Expected: FAIL because existing visible files still contain `SQLBot`.

## Task 2: Replace Frontend Text Defaults

**Files:**
- Modify: listed frontend HTML, i18n, store, util, and view files.
- Test: `tests/test_visible_branding.py`

- [ ] **Step 1: Replace localized platform and assistant names**

Use these exact names:
- Simplified Chinese platform: `智能报表问数平台`
- Simplified Chinese assistant: `智能报表问数助手`
- Traditional Chinese platform: `智慧報表問數平台`
- Traditional Chinese assistant: `智慧報表問數助手`
- English platform: `Intelligent Report Q&A Platform`
- English assistant: `Intelligent Report Q&A Assistant`
- Korean platform: `지능형 보고서 데이터 질의 플랫폼`
- Korean assistant: `지능형 보고서 데이터 질의 도우미`

- [ ] **Step 2: Replace hardcoded browser and fallback names**

Change HTML titles and frontend fallbacks from `SQLBot` to the simplified Chinese platform name unless the file is locale-specific.

- [ ] **Step 3: Run brand scan**

Run: `python -m pytest tests/test_visible_branding.py -q`

Expected: still FAIL until backend, installer, and binary assets are handled.

## Task 3: Replace Backend, Deployment, and Installer Visible Defaults

**Files:**
- Modify: backend and installer files listed above.
- Test: `tests/test_visible_branding.py`

- [ ] **Step 1: Replace public API docs and MCP names**

Use `Intelligent Report Q&A Platform API Document`, `Intelligent Report Q&A Platform API Docs`, and `Intelligent Report Q&A MCP Server`.

- [ ] **Step 2: Replace default password**

Change visible and configured default password from `SQLBot@123456` to `Report@123456`.

- [ ] **Step 3: Replace terminal-facing product names**

Use `智能报表问数平台` in installer scripts where the text is shown to operators.

- [ ] **Step 4: Run brand scan**

Run: `python -m pytest tests/test_visible_branding.py -q`

Expected: still FAIL until branded images and SVG metadata are handled.

## Task 4: Replace Branded Images and SVG Metadata

**Files:**
- Modify: branded image and SVG assets listed above.
- Test: `tests/test_visible_branding.py`

- [ ] **Step 1: Generate white image placeholders**

Use same dimensions:
- `LOGO-about.png`: 720 x 180
- `login-bg-sqlbot.jpg`: 1250 x 1042

- [ ] **Step 2: Replace SVG visible brand or metadata**

Replace visible `LOGO.svg` with a blank same-size SVG and change `vite-sqlbot.svg` title metadata to the simplified Chinese platform name.

- [ ] **Step 3: Run brand scan**

Run: `python -m pytest tests/test_visible_branding.py -q`

Expected: PASS.

## Task 5: Full Verification

**Files:**
- No additional planned modifications.

- [ ] **Step 1: Run targeted brand scan**

Run: `python -m pytest tests/test_visible_branding.py -q`

Expected: PASS.

- [ ] **Step 2: Run existing focused tests**

Run: `python -m pytest tests/test_supplier_config.py -q`

Expected: PASS.

- [ ] **Step 3: Build frontend**

Run: `npm run build`

Working directory: `frontend`

Expected: build exits 0.

- [ ] **Step 4: Final source scan**

Run: `rg -n -S "SQLBot" frontend backend docker-compose.yaml installer tests --glob "!frontend/node_modules/**" --glob "!frontend/dist/**"`

Expected: remaining matches are internal identifiers, package paths, encryption keys, test names/comments, or explicitly allowed technical compatibility names.
