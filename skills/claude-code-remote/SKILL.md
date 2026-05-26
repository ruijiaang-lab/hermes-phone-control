---
name: claude-code-remote
description: "从 Hermes 远程调用 Claude Code CLI，封装参数，不用记命令。触发词：调用 claude code、让 claude 做、claude code 帮忙、远程调 claude。"
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [claude-code, remote, CLI, delegation, coding]
---

# Claude Code 远程调用

## 概述

从 Hermes（微信/Telegram）远程调用 Claude Code CLI，无需记住参数。

## 基本用法

```bash
claude -p "你的任务描述" --allowedTools "Bash,Read,Write"
```

## 参数说明

| 参数 | 作用 | 何时需要 |
|------|------|----------|
| `-p "prompt"` | 一次性模式，不进入交互 | 始终需要 |
| `--allowedTools` | 授权工具 | 需要执行操作时 |
| `--cwd /path` | 指定工作目录 | 非默认目录时 |
| `--model` | 指定模型 | 需要特定模型时 |

## 常用模式

### 读取/分析（只读）
```bash
claude -p "分析这个文件的结构" --allowedTools "Read,Bash"
```

### 写代码/修改文件
```bash
claude -p "重构这个函数" --allowedTools "Bash,Read,Write"
```

### 全能模式
```bash
claude -p "完成这个任务" --allowedTools "Bash,Read,Write,Glob,Grep"
```

## 注意事项

- `claude -p` 是一次性执行，不会影响已有的 Claude Code 进程
- 必须加 `--allowedTools` 才能真正执行操作，否则只会文字回复
- 不加 `--allowedTools` 适合纯问答/分析场景
- 工作目录默认是 `~`，需要时用 `--cwd` 指定

## 与 Hermes delegate_task 的区别

| | Claude Code 远程调用 | Hermes delegate_task |
|---|---|---|
| 执行者 | Claude Code CLI | Hermes 子 agent |
| 工具 | Claude Code 原生工具 | Hermes 工具集 |
| 适合 | 复杂编码任务、需要 Claude 特有能力 | Hermes 工具链内的任务 |
| 上下文 | 独立，需要传入所有信息 | 继承 Hermes 上下文 |

## 何时使用

- 需要 Claude 的编码能力（比 Hermes 强）
- 任务需要多步骤文件操作
- 需要在特定项目目录下工作
- 用户明确要求"让 Claude Code 做"
