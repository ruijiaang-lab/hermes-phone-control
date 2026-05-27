#!/usr/bin/env python3
"""
HermesRemote - Mac Mini Screenshot Tool
Called by Hermes. Takes screenshot, returns path.
Hermes handles sending via weixin gateway.
"""

import os
import sys
import json
import time
import logging
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

CONFIG_PATH = Path(__file__).parent / "config.json"
BASE_DIR = Path(__file__).parent

def load_config():
    if not CONFIG_PATH.exists():
        return {
            "temp_screenshot_dir": "~/HermesRemote/temp_screenshots",
            "log_dir": "~/HermesRemote/logs",
            "delete_after_minutes": 10,
            "cleanup_expired_on_start": True,
        }
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

CONFIG = load_config()
TEMP_DIR = Path(os.path.expanduser(CONFIG['temp_screenshot_dir']))
LOG_DIR = Path(os.path.expanduser(CONFIG['log_dir']))
TEMP_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOGGING
# ============================================================

log_file = LOG_DIR / f"hermes_remote_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('HermesRemote')

# ============================================================
# SCREENSHOT
# ============================================================

def take_screenshot():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"screenshot_temp_{timestamp}.png"
    filepath = TEMP_DIR / filename
    try:
        result = subprocess.run(
            ['screencapture', '-x', str(filepath)],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0 or not filepath.exists():
            logger.error(f"screenshot_failed | error: {result.stderr}")
            return None
        logger.info(f"screenshot_taken | file: {filename} | size: {filepath.stat().st_size}")
        return filepath
    except Exception as e:
        logger.error(f"screenshot_failed | error: {e}")
        return None

# ============================================================
# CLEANUP
# ============================================================

def schedule_cleanup(filepath, minutes=None):
    if minutes is None:
        minutes = CONFIG.get('delete_after_minutes', 10)
    def cleanup():
        time.sleep(minutes * 60)
        try:
            if filepath.exists():
                filepath.unlink()
                logger.info(f"temp_file_deleted | file: {filepath.name} | deleted: true")
        except Exception as e:
            logger.error(f"temp_file_delete_failed | file: {filepath.name} | error: {e}")
    t = threading.Thread(target=cleanup, daemon=True)
    t.start()
    logger.info(f"cleanup_scheduled | file: {filepath.name} | delete_in: {minutes}min")

def cleanup_expired():
    if not CONFIG.get('cleanup_expired_on_start', True):
        return
    max_age = timedelta(minutes=CONFIG.get('delete_after_minutes', 10))
    now = datetime.now()
    for f in TEMP_DIR.glob('screenshot_temp_*.png'):
        try:
            if now - datetime.fromtimestamp(f.stat().st_mtime) > max_age:
                f.unlink()
                logger.info(f"expired_file_cleaned | file: {f.name}")
        except Exception as e:
            logger.warning(f"cleanup_failed | file: {f.name} | error: {e}")

def manual_cleanup():
    """Delete all screenshot_temp_*.png immediately."""
    deleted = 0
    for f in TEMP_DIR.glob('screenshot_temp_*.png'):
        try:
            f.unlink()
            deleted += 1
        except:
            pass
    return deleted

# ============================================================
# COMMANDS
# ============================================================

def cmd_screenshot():
    cleanup_expired()
    filepath = take_screenshot()
    if not filepath:
        return {"ok": False, "msg": "❌ 截图失败，请检查屏幕录制权限。"}
    schedule_cleanup(filepath)
    return {"ok": True, "path": str(filepath), "msg": f"✅ 截图已保存: {filepath.name}，{CONFIG.get('delete_after_minutes',10)}分钟后自动删除。"}

def cmd_status():
    count = len(list(TEMP_DIR.glob('screenshot_temp_*.png')))
    return {"ok": True, "msg": f"📊 运行中 | 临时截图: {count} | 自动删除: {CONFIG.get('delete_after_minutes',10)}分钟后 | 目录: {TEMP_DIR}"}

def cmd_help():
    return {"ok": True, "msg": "📖 命令：/h screenshot（截图）| /h status（状态）| /h help（帮助）| /h stop（停止）| /h cleanup（清理所有临时截图）"}

def cmd_stop():
    return {"ok": True, "msg": "🛑 已停止。"}

def cmd_cleanup():
    deleted = manual_cleanup()
    logger.info(f"manual_cleanup | deleted: {deleted}")
    return {"ok": True, "msg": f"🗑️ 已清理 {deleted} 个临时截图。"}

COMMANDS = {
    "screenshot": cmd_screenshot,
    "status": cmd_status,
    "help": cmd_help,
    "stop": cmd_stop,
    "cleanup": cmd_cleanup,
}

def run(cmd):
    handler = COMMANDS.get(cmd)
    if handler:
        return handler()
    return {"ok": False, "msg": f"❓ 未知命令: {cmd}，发送 /h help 查看帮助。"}

# ============================================================
# CLI
# ============================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python remote_screenshot.py <command>")
        sys.exit(1)
    cmd = sys.argv[1].strip().lower().lstrip('/')
    if cmd.startswith('h '):
        cmd = cmd[2:].strip()
    result = run(cmd)
    print(result.get('msg', ''))
    # Output path for Hermes to pick up
    if result.get('path'):
        print(f"PATH:{result['path']}")
