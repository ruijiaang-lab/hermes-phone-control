#!/usr/bin/env python3
"""X 文章草稿保存 — 通过 Playwright 保存长文到 X 草稿箱（含封面图上传）"""
import sys
import json
import time
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

PROXY = "http://127.0.0.1:7897"
PROFILE = os.path.expanduser("~/x-draft-profile")


def clean_lock():
    for f in ["SingletonLock", "SingletonSocket", "SingletonCookie"]:
        p = os.path.join(PROFILE, f)
        if os.path.exists(p):
            os.remove(p)


def remove_mask(page):
    page.evaluate('document.querySelectorAll("[data-testid=mask]").forEach(e=>e.remove())')


def save_article(title: str, body: str, cover_path: str = None) -> tuple[bool, str]:
    """Save a long-form article to X drafts.

    Args:
        title: Article title
        body: Article body text
        cover_path: Optional path to cover image

    Returns:
        (success, message) tuple
    """
    clean_lock()
    os.makedirs(PROFILE, exist_ok=True)

    pw = sync_playwright().start()
    ctx = pw.chromium.launch_persistent_context(
        user_data_dir=PROFILE,
        headless=False,
        proxy={"server": PROXY},
        viewport={"width": 1280, "height": 900},
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()

    # Navigate to article compose page
    page.goto("https://x.com/compose/articles", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    if "/login" in page.url or "/i/flow" in page.url:
        ctx.close()
        pw.stop()
        return False, "未登录 X"

    remove_mask(page)

    # Click the "撰写" / create button (empty_state_button_text)
    write_btn = page.query_selector('[data-testid="empty_state_button_text"]')
    if write_btn:
        write_btn.click()
        time.sleep(3)
        remove_mask(page)
    else:
        # Maybe already in editor or no such button
        print("未找到'撰写'按钮，尝试直接定位编辑器...")

    # Find the composer
    composer = page.query_selector('[data-testid="composer"]')
    if not composer:
        # Try waiting a bit more
        time.sleep(3)
        remove_mask(page)
        composer = page.query_selector('[data-testid="composer"]')

    if not composer:
        ctx.close()
        pw.stop()
        return False, "未找到文章编辑器 (composer)"

    # Find contenteditable elements inside composer
    editables = page.query_selector_all('[data-testid="composer"] [contenteditable="true"]')
    if not editables:
        # Try broader selector
        editables = page.query_selector_all('[contenteditable="true"]')

    if len(editables) < 1:
        ctx.close()
        pw.stop()
        return False, "未找到可编辑区域"

    # First contenteditable = title, second = body (or first = body if single)
    title_editor = editables[0]
    title_editor.click()
    time.sleep(0.5)
    page.keyboard.type(title, delay=5)
    time.sleep(0.5)

    # Move to body: press Enter or click the second editor
    if len(editables) >= 2:
        body_editor = editables[1]
        body_editor.click()
        time.sleep(0.3)
    else:
        page.keyboard.press("Enter")
        time.sleep(0.3)

    # Type body text
    page.keyboard.type(body, delay=3)
    time.sleep(1)

    # Upload cover image if provided
    if cover_path and os.path.exists(cover_path):
        try:
            _upload_cover(page, cover_path)
        except Exception as e:
            print(f"封面图上传失败: {e}")

    # X articles auto-save, wait for it
    time.sleep(5)

    # Close the editor (go back)
    page.keyboard.press("Escape")
    time.sleep(2)

    # If there's a save/discard dialog, try to save
    save_btn = page.query_selector('[data-testid="confirmationSheetConfirm"]')
    if save_btn:
        save_btn.click()
        time.sleep(2)

    ctx.close()
    pw.stop()
    return True, "文章已保存到 X 草稿箱"


def _upload_cover(page, cover_path: str):
    """Upload cover image to the article editor."""
    abs_path = os.path.abspath(cover_path)

    # Method 1: Look for image/media upload button in the composer toolbar
    # X article editor has a toolbar with media insertion
    media_btn = page.query_selector('[data-testid="composer"] [aria-label*="Media"]')
    if not media_btn:
        media_btn = page.query_selector('[data-testid="composer"] [aria-label*="media"]')
    if not media_btn:
        media_btn = page.query_selector('[data-testid="composer"] [aria-label*="Image"]')
    if not media_btn:
        media_btn = page.query_selector('[data-testid="composer"] [aria-label*="image"]')
    if not media_btn:
        media_btn = page.query_selector('[data-testid="composer"] [aria-label*="Photo"]')

    if media_btn:
        # Use file chooser approach
        with page.expect_file_chooser() as fc_info:
            media_btn.click()
        file_chooser = fc_info.value
        file_chooser.set_files(abs_path)
        time.sleep(3)
        print(f"封面图已上传: {abs_path}")
        return

    # Method 2: Find hidden file input
    file_input = page.query_selector('[data-testid="composer"] input[type="file"]')
    if not file_input:
        file_input = page.query_selector('input[type="file"][accept*="image"]')
    if file_input:
        file_input.set_input_files(abs_path)
        time.sleep(3)
        print(f"封面图已通过 input 上传: {abs_path}")
        return

    # Method 3: Drag and drop (last resort)
    print("未找到图片上传入口，跳过封面图上传")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: x_save_article.py <title> <body> [cover_path]")
        sys.exit(1)

    title_arg = sys.argv[1]
    body_arg = sys.argv[2]
    cover_arg = sys.argv[3] if len(sys.argv) > 3 else None

    ok, msg = save_article(title_arg, body_arg, cover_arg)
    print(json.dumps({"status": "ok" if ok else "error", "message": msg}, ensure_ascii=False))
