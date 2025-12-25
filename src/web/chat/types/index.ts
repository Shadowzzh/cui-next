// Re-export necessary types from backend
import type {
  ConversationSummary,
  ConversationMessage,
  StartConversationRequest,
  StartConversationResponse,
  ConversationDetailsResponse,
  StreamEvent,
  AssistantStreamMessage,
  UserStreamMessage,
  ResultStreamMessage,
  SystemInitMessage,
  PermissionRequest,
  PermissionDecisionRequest,
  PermissionDecisionResponse,
  FileSystemEntry,
  FileSystemListQuery,
  FileSystemListResponse,
  CommandsResponse,
  GeminiHealthResponse,
} from '@/types';

// Import ContentBlock from Anthropic SDK
import type {
  ContentBlock,
  ContentBlockParam,
} from '@anthropic-ai/sdk/resources/messages/messages';

export type {
  ConversationSummary,
  ConversationMessage,
  StartConversationRequest,
  StartConversationResponse,
  ConversationDetailsResponse,
  StreamEvent,
  AssistantStreamMessage,
  UserStreamMessage,
  ResultStreamMessage,
  SystemInitMessage,
  PermissionRequest,
  PermissionDecisionRequest,
  PermissionDecisionResponse,
  FileSystemEntry,
  FileSystemListQuery,
  FileSystemListResponse,
  CommandsResponse,
  GeminiHealthResponse,
};

// Chat-specific types
export interface Command {
  name: string;
  type: 'builtin' | 'custom';
  description?: string;
}
export interface ChatMessage {
  id: string; // Backend message ID (may not be unique, empty for pending user messages)
  messageId: string; // Client-side unique ID for React rendering
  type: 'user' | 'assistant' | 'system' | 'error';
  content: string | ContentBlock[];
  timestamp: string;
  workingDirectory?: string; // Working directory when the message was created
  parentToolUseId?: string; // For nested messages from Task tool use
  // isStreaming removed
}

export interface Theme {
  mode: 'light' | 'dark';
  toggle: () => void;
  colorScheme: 'light' | 'dark' | 'system';
}

export interface ApiError {
  error: string;
  code?: string;
}

// Working directories types
export interface WorkingDirectory {
  path: string; // Full absolute path
  shortname: string; // Smart suffix
  lastDate: string; // ISO timestamp
  conversationCount: number; // Total conversations
}

export interface WorkingDirectoriesResponse {
  directories: WorkingDirectory[];
  totalCount: number;
}

export interface Preferences {
  colorScheme: 'light' | 'dark' | 'system';
  language: string;
  notifications?: {
    enabled: boolean;
    ntfyUrl?: string;
  };
}

// Tool result types
export interface ToolResult {
  status: 'pending' | 'completed';
  result?: string | ContentBlockParam[];
  is_error?: boolean;
}

// Stream status types for live updates
export interface StreamStatus {
  /** SSE 连接状态 */
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  /** 最近的 SSE 事件 */
  lastEvent?: StreamEvent;
  /** 最近事件的时间戳 */
  lastEventTime?: string;
  /** 当前对话状态 */
  currentStatus: string;
  toolMetrics?: {
    /** 代码行数新增数 */
    linesAdded: number;
    /** 代码行数删除数 */
    linesRemoved: number;
    /** 读取次数 */
    editCount: number;
    /** 写入次数 */
    writeCount: number;
  };
}

// Extended conversation summary with live status
export interface ConversationSummaryWithLiveStatus extends ConversationSummary {
  liveStatus?: StreamStatus;
}
