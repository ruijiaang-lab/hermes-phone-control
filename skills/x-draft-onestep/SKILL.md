---
name: x-draft-onestep
description: "推特草稿一键流：润色→本地备份→存X草稿箱，一条指令全搞定。触发词：一键发推、存草稿、发推特、推特一键、快速发推、草稿全链路。"
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [twitter, x, draft, onestep, wechat, automation]
---

# X 草稿一键流

## 概述

用户发一段文字 + 说"存"/"发推"，Hermes 一条指令完成全部流程：
1. 润色（按账号人设）
2. 本地备份（`~/Desktop/推特草稿/`）
3. 存入 X 草稿箱（Playwright）

## 触发条件

- 用户发文字 + "存" / "发推" / "存草稿" / "一键发推"
- 用户说"润色一下存了" / "帮我改改发了"

## 执行流程

### 短推文（单条指令完成）

```
用户: 「今天打通了微信到推特的链路，躺着就把推发了。存」

Hermes 自动执行：
1. 润色（按人设规则）
2. write_file → ~/Desktop/推特草稿/标题.md
3. terminal → python3 ~/Desktop/x_save_draft.py "润色内容"
4. 回复用户：润色结果 + 保存状态
```

**关键：步骤 2 和 3 连续执行，不等用户确认。** 只有润色结果展示给用户看，保存动作自动完成。

### 长文（含封面）

```
用户: 「[长文内容] 存长文」

Hermes 自动执行：
1. 润色
2. write_file → ~/Desktop/推特草稿/标题.md
3. terminal → python3 ~/Desktop/x_save_article.py "润色内容"
4. 如果用户要封面 → image_generate
5. 回复结果
```

### 评论自评

```
用户: 「[评论内容] 这个是评论」

Hermes 自动执行：
1. 润色（评论区风格，更简洁）
2. write_file → ~/Desktop/推特草稿/标题_评论自评.md
3. terminal → python3 ~/Desktop/x_save_draft.py "润色内容"
4. 回复结果
```

## 批量模式

用户连续发多段内容：
- 每段独立处理，不合并
- 主帖和评论分开存
- 都自动走完整流程

## 人设规则（快速参考）

按你的账号人设润色。严格保持原意，只润色语言和结构，不添加用户没提到的内容。
（在 config 或 skill 中定义你的人设规则）

## 依赖

- `~/Desktop/x_save_draft.py` — 普通推文草稿
- `~/Desktop/x_save_article.py` — X Articles 长文
- `~/x-draft-profile/` — Playwright 持久化 profile
- 代理工具（如 Clash Verge，端口按你的配置）

## 与 x-post-polisher 的区别

| | x-post-polisher | x-draft-onestep |
|---|---|---|
| 润色后 | 展示等用户确认 | 展示但自动保存 |
| 步骤 | 分步，需多次交互 | 一条指令完成 |
| 适用 | 精心打磨 | 快速发布 |

用户说"润色"→ 走 polisher（精细模式）
用户说"存"/"发推"→ 走 onestep（一键模式）

## 注意

- 润色结果仍然回复给用户看（透明）
- 保存动作自动执行，不等确认
- 如果 Playwright 出错（代理断了、profile 锁了），报告错误但不阻塞
- 推特发布仍然需要用户手动（草稿 ≠ 发布）
