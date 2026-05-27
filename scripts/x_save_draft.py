#!/usr/bin/env python3
"""
X 草稿保存 - 一步到位版
启动浏览器 → 等你登录 → 保存草稿 → 关闭
登录态不保存，每次需要重新登录（但整个过程在一个脚本里完成）
"""
import os, sys, json, time
from playwright.sync_api import sync_playwright

PROXY = os.environ.get("HTTPS_PROXY", os.environ.get("HTTP_PROXY", ""))


def run(content):
    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=False,
        proxy={"server": PROXY} if PROXY else None,
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = browser.new_page(viewport={"width": 1280, "height": 900})

    # 1. 打开 X
    page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=20000)
    time.sleep(3)

    # 2. 检查是否已登录
    url = page.url
    if "/login" in url or "/i/flow/login" in url:
        print("NOT_LOGGED_IN: 请在浏览器中登录 X", flush=True)
        print("WAITING_LOGIN", flush=True)
        # 等待用户登录成功（检测 URL 变成 home）
        for _ in range(300):  # 最多等 5 分钟
            time.sleep(1)
            if "/home" in page.url:
                print("LOGIN_OK", flush=True)
                break
        else:
            print("LOGIN_TIMEOUT", flush=True)
            browser.close()
            pw.stop()
            return False, "登录超时"

    time.sleep(2)

    # 3. 打开发帖框
    page.keyboard.press("n")
    time.sleep(2)

    # 4. 找到编辑器
    editor = page.query_selector('[data-testid="tweetTextarea_0"]')
    if not editor:
        # 重试
        page.keyboard.press("Escape")
        time.sleep(1)
        page.keyboard.press("n")
        time.sleep(2)
        editor = page.query_selector('[data-testid="tweetTextarea_0"]')

    if not editor:
        print("COMPOSE_FAILED", flush=True)
        browser.close()
        pw.stop()
        return False, "打开发帖框失败"

    # 5. 输入内容
    editor.click()
    time.sleep(0.5)
    page.keyboard.type(content, delay=5)
    time.sleep(1)
    print("CONTENT_TYPED", flush=True)

    # 6. 关闭发帖框 → 触发保存草稿对话框
    page.keyboard.press("Escape")
    time.sleep(2)

    # 7. 点击 Save Draft 按钮
    saved = False
    btns = page.query_selector_all("button")
    for btn in btns:
        t = (btn.inner_text() or "").strip()
        if "save draft" in t.lower() or "save" in t.lower() or "草稿" in t or "保存" in t:
            btn.click()
            saved = True
            print(f"DRAFT_SAVED: {t}", flush=True)
            break

    if not saved:
        # 截图调试
        page.screenshot(path="/tmp/x_draft_debug.png")
        print("SAVE_BUTTON_NOT_FOUND - 截图已保存到 /tmp/x_draft_debug.png", flush=True)
        # 列出所有按钮
        for btn in btns:
            t = (btn.inner_text() or "").strip()
            if t and len(t) < 40:
                print(f"  BTN: {t}", flush=True)

    time.sleep(2)
    browser.close()
    pw.stop()

    if saved:
        return True, "已保存到 X 草稿箱"
    return False, "未找到保存按钮"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        content = sys.argv[1]
    else:
        content = "测试草稿 - Hermes 自动化"

    ok, msg = run(content)
    print(f"RESULT: {'OK' if ok else 'FAIL'} - {msg}", flush=True)

