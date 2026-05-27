---
name: remote-screenshot
description: "Mac 远程截图。触发词：看看、看看进度、看电脑、看桌面、截个屏、看下屏幕、screenshot。也支持 /h screenshot。"
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [screenshot, remote, automation]
---

# Remote Screenshot

## 触发条件

用户说以下任意话时，自动截图并发到当前对话：

- "看看"、"看看进度"、"看看电脑"、"看看桌面"
- "看下屏幕"、"截个屏"、"截个图"
- "看电脑"、"给我看看"、"看下现在什么情况"
- "screenshot"
- `/h screenshot`

直接执行，不用确认。

## 执行流程

1. 运行：
```bash
python3 <repo>/scripts/remote_screenshot.py screenshot
```
（`<repo>` 替换为本仓库实际路径）

2. 从输出提取 `PATH:` 开头的文件路径

3. 发图到用户当前对话：
```
send_message(message="📸 MEDIA:<文件路径>", target="<当前对话>")
```

4. 临时截图 10 分钟后自动删除（脚本内部处理）

## 其他命令

- "看状态" / `/h status` → `python3 scripts/remote_screenshot.py status`
- "清理截图" / `/h cleanup` → `python3 scripts/remote_screenshot.py cleanup`

## 依赖

仅 Python 标准库 + macOS `screencapture`，无需额外安装。

## 权限

macOS → 系统设置 → 隐私与安全性 → 屏幕录制 → 添加 Terminal
