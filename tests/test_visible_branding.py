import os
import unittest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VISIBLE_TEXT_FILES = [
    "frontend/.env.development",
    "frontend/.env.production",
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/index.html",
    "frontend/embedded.html",
    "frontend/public/vite-sqlbot.svg",
    "frontend/src/assets/LOGO.svg",
    "frontend/src/i18n/en.json",
    "frontend/src/i18n/zh-CN.json",
    "frontend/src/i18n/zh-TW.json",
    "frontend/src/i18n/ko-KR.json",
    "frontend/src/components/layout/index.vue",
    "frontend/src/stores/appearance.ts",
    "frontend/src/stores/chatConfig.ts",
    "frontend/src/utils/utils.ts",
    "frontend/src/views/chat/index.vue",
    "frontend/src/views/work/index.vue",
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

ALLOWED_INTERNAL_IDENTIFIERS = [
    "SQLBotLogUtil",
    "getSQLBotName",
    "getSQLBotAddr",
]


class TestVisibleBranding(unittest.TestCase):
    def test_visible_text_files_do_not_show_sqlbot_brand(self):
        failures = []
        for rel_path in VISIBLE_TEXT_FILES:
            path = os.path.join(PROJECT_ROOT, rel_path)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            for allowed in ALLOWED_INTERNAL_IDENTIFIERS:
                content = content.replace(allowed, "")
            if "SQLBot" in content:
                failures.append(rel_path)

        self.assertEqual([], failures)

    def test_visible_binary_brand_assets_are_blank_placeholders(self):
        for rel_path in VISIBLE_BINARY_FILES:
            path = os.path.join(PROJECT_ROOT, rel_path)
            with open(path, "rb") as f:
                content = f.read()
            self.assertNotIn(b"SQLBot", content, rel_path)
