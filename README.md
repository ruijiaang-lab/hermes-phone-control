# hermes-phone-control

**手机 → Hermes Agent → 电脑全栈控制**

通过微信/Telegram 发消息，在 Mac 上远程执行命令、写代码、管理文件、操控浏览器。

## 它能做什么

| 能力 | 示例 |
|------|------|
| 文件读写 | "帮我看看 ~/Desktop 下有什么文件" |
| 终端命令 | "跑一下 npm test" |
| Claude Code 调用 | "让 Claude Code 帮我重构这个函数" |
| 浏览器操控 | "打开 X 帮我存个草稿" |
| AI 润色 | "帮我润色一下这段文字发推" |
| 定时任务 | "每天早上 9 点给我发个日报" |

## 架构

```
手机（微信/Telegram）
    │
    ▼
Hermes Agent（你的 Mac）
    ├── 文件系统（读写、编辑）
    ├── 终端（任意命令）
    ├── Claude Code（远程调用）
    ├── Playwright（浏览器自动化）
    ├── 本地模型（MiMo / Qwen）
    └── 记忆 + 技能（跨会话）
```

## 快速上手

### 1. 安装 Hermes Agent

```bash
# macOS
brew install hermes-agent
# 或
pip install hermes-agent
```

### 2. 配置

```bash
# 复制推荐配置
cp config.template.yaml ~/.hermes/config.yaml

# 编辑配置，填入你的 API key
vim ~/.hermes/config.yaml
```

### 3. 连接微信

```bash
hermes setup weixin
```

### 4. 开始使用

在微信发消息给 Hermes，它会在你的 Mac 上执行。

## 推荐配置（关键项）

```yaml
# 自动批准命令 —— 从手机操控的核心
approvals:
  mode: auto        # 不用手动 approve
  timeout: 60

# 关闭安全扫描 —— 减少 pipe 命令的审批弹窗
security:
  tirith_enabled: false

# 终端
terminal:
  backend: local
  persistent_shell: true
  timeout: 180
```

完整配置见 `config.template.yaml`。

## Skills（技能）

把常用工作流封装成 skill，一条指令触发：

| Skill | 用途 |
|-------|------|
| `x-draft-onestep` | 推特草稿一键流：润色→备份→存草稿箱 |
| `x-post-polisher` | 推文润色，匹配账号人设 |
| `claude-code-remote` | 远程调用 Claude Code CLI |
| `viral-content-rewrite` | 爆款拆解改写 |

### 安装 skill

```bash
# 复制 skill 到 Hermes 目录
cp -r skills/* ~/.hermes/skills/
```

## 安全边界

- **自动执行** = Hermes 决定跑什么命令
- **你控制** = 最终发布（推特、GitHub push）需要你确认
- **记忆系统** = 越用越懂你的意图，减少歧义

## 前置条件

- macOS（已测试 Mac Mini M2 16GB）
- Hermes Agent
- Python 3.11+
- Playwright（浏览器自动化用）
- 代理工具（如 Clash Verge，访问 X/Google 等）

## 许可证

MIT
