# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此仓库中工作提供指导。

使用中文回复

## 项目概述

CUI (Common Agent UI) 是一个基于 Claude Code SDK 的 Web UI Agent 平台，为各种 LLM 提供现代化的 Web 界面。项目包含：
- TypeScript Express 后端，管理 Claude CLI 进程
- React 前端，采用简洁的 UI 设计
- 单端口架构 (默认端口 3001)
- 通过 Server-Sent Events (SSE) 实现实时流式响应
- MCP (Model Context Protocol) 集成，用于权限管理

## 核心架构

### 进程管理架构

项目的核心是**进程管理**和**流式传输**双层架构：

1. **ClaudeProcessManager** (src/services/claude-process-manager.ts)
   - 每个对话对应一个独立的 Claude CLI 子进程
   - 使用 `spawn()` 启动进程，通过 JSONL 格式的 stdout 接收 Claude 输出
   - 关键方法：
     - `startConversation()`: 启动新对话，返回 `streamingId` 和 `systemInit` 消息
     - `waitForSystemInit()`: 等待并验证第一条系统初始化消息
     - `stopConversation()`: 优雅关闭进程 (SIGTERM → SIGKILL)
   - 生成两类 ID：
     - `streamingId`: CUI 内部的流式标识符 (UUID)
     - `session_id`: Claude CLI 的会话 ID (来自系统初始化消息)

2. **StreamManager** (src/services/stream-manager.ts)
   - 管理 SSE 连接到多个客户端
   - 使用 `Map<streamingId, Set<Response>>` 存储客户端连接
   - 广播消息给订阅特定 `streamingId` 的所有客户端
   - 发送心跳保持连接活跃 (每 30 秒)

3. **事件流**：
   ```
   用户请求 → ClaudeProcessManager.startConversation()
            ↓
   spawn Claude CLI 子进程 (--output-format stream-json)
            ↓
   JsonLinesParser 解析 stdout
            ↓
   ProcessManager 发出 'claude-message' 事件
            ↓
   CUIServer 监听事件并调用 StreamManager.broadcast()
            ↓
   SSE 推送给所有订阅的客户端
   ```

### MCP 服务器集成

- **MCPConfigGenerator** (src/services/mcp-config-generator.ts) 在服务器启动时动态生成 MCP 配置
- **MCP Server** (src/mcp-server/index.ts) 提供 `approval_prompt` 工具
- **PermissionTracker** (src/services/permission-tracker.ts) 管理权限请求的生命周期
- 权限请求通过 SSE 推送给前端，用户批准/拒绝后，MCP 服务器继续执行

### 状态管理

- **ConversationStatusManager** (src/services/conversation-status-manager.ts)
  - 追踪活跃会话：`streamingId` ↔ `session_id` 映射
  - 注册/注销会话，用于快速查询会话状态

- **SessionInfoService** (src/services/session-info-service.ts)
  - 使用 SQLite 存储扩展的会话元数据
  - 支持自定义名称、固定、归档、续写会话 ID 等
  - 数据库位于 `~/.cui/session-info.db`

### 路由器服务 (Router Service)

- **ClaudeRouterService** (src/services/claude-router-service.ts)
  - 支持多模型供应商 (OpenRouter, Ollama 等)
  - 使用 `@musistudio/llms` 库配置路由
  - 通过设置 `ANTHROPIC_BASE_URL` 环境变量代理 Claude CLI 请求

## 常用命令

### 开发

```bash
# 启动开发服务器 (前端 + 后端，端口 3001)
npm run dev

# 仅启动前端开发服务器 (端口 3000，需要单独启动后端)
npm run dev:web

# 启用 debug 日志
LOG_LEVEL=debug npm run dev
```

### 构建

```bash
# 清理构建目录
npm run clean

# 完整构建 (前端 + 后端 + MCP 服务器)
npm run build

# 仅构建前端
npm run build:web

# 仅构建 MCP 服务器
npm run build:mcp
```

### 测试

```bash
# 运行所有测试
npm test

# 仅运行单元测试
npm run unit-tests

# 仅运行集成测试
npm run integration-tests

# 运行特定测试文件
npm test -- claude-process-manager.test.ts

# 运行匹配特定模式的测试
npm test -- --testNamePattern="should start conversation"

# 运行测试并生成覆盖率报告
npm run test:coverage

# 观察模式 (TDD)
npm run test:watch

# 启用详细日志调试测试
npm run test:debug
```

### 代码质量

```bash
# TypeScript 类型检查
npm run typecheck

# ESLint 检查
npm run lint

# 运行生产环境服务器
npm run start
```

## 测试架构

### Mock Claude CLI

- 项目包含 Mock Claude CLI (`tests/__mocks__/claude`)
- 模拟真实 Claude CLI 行为，输出有效的 JSONL 格式
- 用于测试，无需实际安装 Claude CLI

### 测试覆盖率要求

所有 PR 必须满足以下覆盖率阈值：
- **Lines**: 75%
- **Functions**: 80%
- **Branches**: 60%
- **Statements**: 75%

### 测试原则

- **优先使用真实实现**而非 mock (项目指导原则)
- 测试中使用 `LOG_LEVEL=silent` 减少噪音
- 服务器测试使用随机端口避免冲突
- 适当清理资源和进程

### 测试模式示例

```typescript
// 使用 Mock Claude CLI 的集成测试模式
function getMockClaudeExecutablePath(): string {
  return path.join(process.cwd(), 'tests', '__mocks__', 'claude');
}

// 使用随机端口避免冲突
const serverPort = 9000 + Math.floor(Math.random() * 1000);
const server = new CUIServer({ port: serverPort });

// 使用 Mock 路径覆盖 ProcessManager
const mockClaudePath = getMockClaudeExecutablePath();
const { ClaudeProcessManager } = await import('@/services/claude-process-manager');
(server as any).processManager = new ClaudeProcessManager(mockClaudePath);
```

## 代码风格与最佳实践

### TypeScript

- **严格类型**：避免使用 `any`, `undefined`, `unknown`
- 遵循现有的类型模式
- 使用 Zod schemas 进行运行时验证

### 路径别名

- 使用 `@/` 别名进行导入 (例如: `@/services/...`)
- TypeScript 配置在 `tsconfig.json` 中定义

### 关键模式

1. **流式架构**: 使用 newline-delimited JSON (JSONL)，而非传统的 SSE
2. **进程管理**: 每个对话 = 独立的 Claude CLI 进程
3. **错误处理**: 使用自定义 `CUIError` 类型，包含适当的 HTTP 状态码
4. **事件监听清理**: 在流式逻辑中确保适当清理事件监听器
5. **安全**: 永远不要暴露或记录秘密/密钥

### 前端

- 使用 React Router v6 进行导航
- Vite 作为构建工具
- Tailwind CSS 用于样式
- PWA 支持，包含 Service Worker

## 项目结构要点

### 后端服务 (src/services/)

关键服务及其职责：
- `claude-process-manager.ts`: 生成和管理 Claude CLI 进程
- `stream-manager.ts`: 处理 HTTP 流式连接
- `claude-history-reader.ts`: 从 ~/.claude 读取对话历史
- `conversation-status-manager.ts`: 追踪活跃会话状态
- `session-info-service.ts`: 管理扩展会话元数据 (SQLite)
- `permission-tracker.ts`: 管理 MCP 权限请求
- `mcp-config-generator.ts`: 动态生成 MCP 配置
- `claude-router-service.ts`: 多模型路由支持
- `notification-service.ts`: 处理通知 (ntfy / web-push)
- `commands-service.ts`: 读取和管理自定义 Commands

### API 路由 (src/routes/)

- `conversation.routes.ts`: 启动、列出、获取、继续、停止对话
- `streaming.routes.ts`: 实时对话更新 (SSE)
- `permission.routes.ts`: MCP 权限批准/拒绝
- `system.routes.ts`: 系统状态和健康检查
- `config.routes.ts`: 配置管理
- `filesystem.routes.ts`: 文件系统操作
- `gemini.routes.ts`: Gemini 语音转文字
- `notifications.routes.ts`: Web Push 通知订阅

### 前端 (src/web/)

- `chat/`: 主聊天应用组件
- `inspector/`: 日志查看器组件
- `hooks/`: React hooks (useAuth, useLocalStorage 等)
- `components/`: 共享组件 (Login 等)

### 配置文件

- `~/.cui/config.json`: 服务器和界面设置
- `~/.cui/session-info.db`: 会话元数据 (SQLite)
- `~/.cui/mcp-config-*.json`: 动态生成的 MCP 配置

## 重要实现细节

### 进程生成参数

ClaudeProcessManager 根据选项动态构建参数：
- `-p`: 打印模式 (编程使用必需)
- `--output-format stream-json`: JSONL 输出
- `--verbose`: 使用 stream-json 时必需
- `--resume <session_id>`: 恢复现有会话
- `--mcp-config <path>`: MCP 配置路径
- `--permission-mode`: 权限处理模式
- `--model`, `--allowedTools`, `--disallowedTools` 等

### 环境变量清理

在生成 Claude CLI 子进程时，过滤掉调试相关的环境变量：
```typescript
const { NODE_OPTIONS, VSCODE_INSPECTOR_OPTIONS, ...cleanEnv } = spawnConfig.env;
```
这防止 VSCode 调试器附加到子进程。

### MCP 权限请求

- 必须同步处理
- 通过 SSE 推送给前端
- 用户批准后，MCP 服务器收到响应并继续执行

### Git 集成

- 检测工作目录是否为 git 仓库
- 在新会话开始时记录 `initial_commit_head`
- 用于跟踪会话期间的更改

## Commands 和 Skills 支持

CUI 完全支持 Claude Code CLI 的 **Commands**（自定义命令）和 **Skills**（自动触发技能）功能：

### Commands（自定义命令）

- **后端支持**: `commands-service.ts` 读取 `.claude/commands/*.md` 文件
- **API 端点**: `GET /api/system/commands?workingDirectory=<path>`
- **前端集成**: 类型定义和 API 调用已实现
- **工作方式**: 用户输入 `/command-name` 后，内容直接传递给 Claude CLI 子进程执行

### Skills（自动触发技能）

- **透明支持**: 无需额外代码，Claude CLI 自动处理
- **工作方式**: CLI 启动时自动加载 `.claude/skills/*/SKILL.md` 文件
- **触发机制**: 对话中出现关键词时自动激活相应技能
- **完全兼容**: CUI 作为中间层完全透明，不影响 Skills 功能

### 存放位置

Commands 和 Skills 可存放在两个位置（优先级从高到低）：

1. **项目级别**（仅当前项目）:
   - `<工作目录>/.claude/commands/*.md`
   - `<工作目录>/.claude/skills/*/SKILL.md`

2. **全局级别**（所有项目）:
   - `~/.claude/commands/*.md`
   - `~/.claude/skills/*/SKILL.md`

### 示例使用

```markdown
# .claude/commands/research.md
---
description: 开始深度研究任务
argument-hint: "<主题>"
---

针对以下主题进行深入研究：$ARGUMENTS

## 研究策略
1. 拆解主题为 2-4 个子主题
2. 为每个子主题启动研究 subagent
3. 进行 3-7 次网页搜索
4. 保存到 files/research_notes/
```

在 CUI 中使用：`/research 区块链可扩展性`

**详细文档**: 参阅 `docs/COMMANDS_AND_SKILLS.md` 获取完整指南和示例

## 故障排查

### 首次运行测试前

运行 `npm run build` 以构建 MCP 可执行文件

### 测试期间不要运行 dev 服务器

避免在验证前端更新时运行 `npm run dev`，使用单独的构建

### 启用调试日志

```bash
LOG_LEVEL=debug npm run dev
LOG_LEVEL=debug npm run test
```

### MCP 配置问题

- 在测试环境中，MCP 配置生成失败是预期行为
- 在生产环境中，MCP 配置是必需的
- 检查 `dist/mcp-server/index.js` 是否存在且可执行

## 贡献指南参考

详细的贡献指南请参阅 `docs/CONTRIBUTING.md`，包括：
- 开发设置
- 测试要求
- PR 流程
- 代码风格
