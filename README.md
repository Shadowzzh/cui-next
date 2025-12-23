<div align="center" style="margin-bottom: 40px;">
  <img src="docs/assets/logo.png" alt="cui logo" width="150">
</div>

# cui: 通用 Agent UI

[![npm version](https://badge.fury.io/js/cui-server.svg)](https://www.npmjs.com/package/cui-server)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D20.0.0-brightgreen.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Built with React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![codecov](https://codecov.io/gh/BMPixel/cui/branch/main/graph/badge.svg)](https://codecov.io/gh/BMPixel/cui)
[![CI](https://github.com/BMPixel/cui/actions/workflows/ci.yml/badge.svg)](https://github.com/BMPixel/cui/actions/workflows/ci.yml)

为你的 Agent 提供现代化的 Web UI。启动服务器，在浏览器中随时随地访问你的 Agent。Common Agent UI 基于 [Claude Code SDK](https://claude.ai/code) 开发,支持各类 LLM 和最强大的 Agentic 工具。

<div align="center">
  <img src="docs/assets/demo.gif" alt="Demo" width="100%">
</div>

## 亮点

- **🎨 现代化设计**: 精致、响应式的 UI,随处可用
- **⚡ 并行后台 Agent**: 同时流式处理多个会话
- **📋 任务管理**: 访问所有对话,支持分支/恢复/归档
- **🤖 多模型支持**: 在任何模型上享受 Agentic 工作流的强大能力
- **🔧 Claude Code 一致性**: 熟悉的自动补全和 CLI 交互体验
- **🔔 推送通知**: Agent 完成时收到通知
- **🎤 语音输入**: 由 Gemini 2.5 Flash 提供精准的语音识别

## 快速开始

1. 使用 Node.js >= 20.19.0 启动服务器:

    ```bash
    npx cui-server
    ```
    或全局安装:
    ```bash
    npm install -g cui-server
    ```

2. 在浏览器中打开 http://localhost:3001/#your-token (token 将在 cui-server 命令输出中显示)。
3. 选择模型提供商:
    - 如果你已登录 Claude Code 或环境中有有效的 Anthropic API key,cui 可直接使用。
    - 或者前往 `设置 -> 提供商` 选择模型提供商。cui 使用 [claude-code-router](https://github.com/musistudio/claude-code-router) 配置,支持从 OpenRouter 到 Ollama 的各种模型提供商。
4. (可选) 配置通知和语音输入设置。

## 使用指南

### 任务

- **开始新任务**

  cui 会自动扫描 `~/.claude/` 中现有的 Claude Code 历史记录,并在主页显示,让你可以恢复之前的任务。输入区域的下拉菜单显示所有之前的工作目录。

- **任务分支**

  要从现有任务创建分支(仅支持从 cui 启动的任务),导航到主页的"历史"标签,找到要分支的会话,并使用新消息恢复它。

- **管理任务**

  启动任务后可以随意关闭页面——任务将继续在后台运行。运行多个任务时(从 cui 启动),可以在"任务"标签中查看它们的状态。你还可以点击"归档"按钮归档任务。归档的任务仍可在"已归档"标签中访问。

### 语音输入

cui 使用 [Gemini 2.5 Flash](https://deepmind.google/models/gemini/flash/) 提供高精度的语音识别,特别适合长句子。要启用此功能,你需要一个具有慷慨免费额度的 [Gemini API key](https://aistudio.google.com/apikey)。在启动服务器前设置 `GOOGLE_API_KEY` 环境变量。注意:使用此功能将与 Google 共享你的音频数据。

### 通知

当任务完成或 Claude 等待你授权使用工具时,你可以收到推送通知。通知通过 [ntfy](https://ntfy.sh/) 或原生 [web-push](https://www.npmjs.com/package/web-push) 发送。要接收通知,请按照设置中的说明操作。

### 键盘快捷键

更多快捷键即将推出。当前可用:

- `Enter`: 换行
- `Command/Ctrl + Enter`: 发送消息
- `/`: 列出所有命令
- `@`: 列出当前工作目录中的所有文件

所有内联语法如 `/init` 或 `@file.txt` 均与 CLI 中的用法一致。

### 远程访问

1. 打开 `~/.cui/config.json` 设置 `server.host` (0.0.0.0) 和 `server.port`。或者,启动服务器时可以使用 `--host` 和 `--port` 标志。
2. 如果从本地网络外访问服务器,请确保使用安全的认证令牌。认证令牌在启动服务器时生成,可在 `~/.cui/config.json` 文件中更改。
3. 推荐:使用 HTTPS 访问服务器。你可以使用像 [Caddy](https://caddyserver.com/) 这样的反向代理来设置。在 iOS 上,语音输入功能仅在使用 HTTPS 时可用。

### 配置

所有配置和数据存储在 `~/.cui/` 目录中。

- `config.json` - 服务器和界面设置
- `session-info.db` - 会话元数据

要卸载 cui,只需删除 `~/.cui/` 目录并使用 `npm uninstall -g cui-server` 移除包。

## 故障排查

遇到安装或运行问题？查看 [故障排查指南](docs/TROUBLESHOOTING.md) 了解常见问题的解决方案，包括：

- better-sqlite3 原生模块编译失败
- workbox-precaching 构建失败
- 依赖安装问题

## 贡献

贡献的最佳方式是在 [issues](https://github.com/BMPixel/cui/issues) 中提出改进建议或报告 bug,并给我们一个 star ⭐!

在提交 PR 之前,请确保你(或你的 AI 助手)已阅读 [CONTRIBUTING.md](docs/CONTRIBUTING.md)。
