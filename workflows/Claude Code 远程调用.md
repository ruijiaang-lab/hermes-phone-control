# Claude Code 远程调用

从手机微信远程调用 Claude Code CLI，执行编码任务。

## 基本用法

```bash
# 纯问答（不执行操作）
claude -p "解释一下这个函数的作用"

# 执行操作（需要 --allowedTools）
claude -p "重构这个函数" --allowedTools "Bash,Read,Write"

# 指定工作目录
claude -p "跑一下测试" --allowedTools "Bash" --cwd ~/projects/my-app
```

## 常用模式

### 分析代码（只读）
```bash
claude -p "分析 ~/projects/app/src/main.py 的代码结构" --allowedTools "Read,Bash,Glob,Grep"
```

### 写代码/修改文件
```bash
claude -p "给这个项目加个 README" --allowedTools "Bash,Read,Write,Glob,Grep" --cwd ~/projects/app
```

### 跑测试
```bash
claude -p "跑测试，失败的帮我修" --allowedTools "Bash,Read,Write" --cwd ~/projects/app
```

## 关键参数

| 参数 | 作用 | 必须 |
|------|------|------|
| `-p "prompt"` | 一次性模式 | ✅ 始终需要 |
| `--allowedTools` | 授权工具列表 | 执行操作时需要 |
| `--cwd /path` | 工作目录 | 非 home 目录时 |
| `--model` | 指定模型 | 需要特定模型时 |
| `--max-turns` | 最大轮数 | 复杂任务时 |

## 注意事项

1. **必须加 `--allowedTools`** — 否则 Claude Code 只会文字回复，不执行操作
2. **不影响已有进程** — `-p` 是独立的一次性执行
3. **代理** — 如果需要访问外部资源，确保代理运行中
4. **超时** — 复杂任务可能需要较长时间，Hermes terminal 默认 180s 超时

## 与 Hermes 的分工

- **简单任务** → Hermes 直接做（文件读写、终端命令）
- **复杂编码** → 交给 Claude Code（重构、多文件修改、测试）
- **浏览器操作** → Hermes + Playwright
