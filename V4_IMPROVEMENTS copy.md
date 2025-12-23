# T-Bug V4 Improvements

## Core Changes

### 1. Hooks System (Deterministic Enforcement)

**Stop Hook** - Architecturally prevents stopping without flags
```bash
# Outputs JSON decision control to block stopping
{"decision": "block", "reason": "Flags not captured"}
```

**PostToolUse Hook** - Automatically captures flags from command output
- Detects 32-char hex strings
- Updates state automatically
- No manual jq needed

**SessionStart Hook** - Detects and resumes active pentest sessions

**SubagentStop Hook** - Ready to capture sub-agent results when Task tool is used

### 2. Lightweight Coordinator (82% Reduction)

- Old: 1100 lines of detailed instructions
- New: 200 lines of strategic guidance
- Focus: Delegation over execution
- Recommends using Task tool for sub-agents

### 3. Automatic State Management

- Flags auto-detected from output
- State auto-updated via hooks
- Zero jq syntax errors
- No manual updates needed

## Expected Benefits

### Guaranteed (Architectural)
✅ Cannot stop without both flags (Stop hook blocks)
✅ Flags detected automatically (PostToolUse)
✅ Cleaner context (200 vs 1100 lines)
✅ Session awareness (SessionStart)

### Conditional (Behavioral)
⚠️ Task tool delegation (recommended in SKILL.md, not enforced)
⚠️ Parallel execution (requires Task tool usage)

## File Structure

```
.claude/
├── CLAUDE.md                           # Global config
├── commands/                           # Slash commands
│   ├── start-pentest.md
│   ├── quick-scan.md
│   ├── show-state.md
│   └── reset-state.md
├── hooks/                              # Automation & enforcement
│   ├── hooks.json                      # Hook configuration
│   ├── session-start.sh                # Session detection
│   ├── post-tool-use.sh                # Auto flag capture
│   ├── stop.sh                         # Block stopping
│   └── subagent-stop.sh                # Sub-agent results
└── skills/                             # Knowledge bases
    ├── coordinator/
    │   ├── SKILL.md                    # Strategic orchestrator (200 lines)
    │   └── AD_ATTACK_SUPPLEMENT.md     # AD-specific techniques
    ├── recon/SKILL.md                  # Reconnaissance knowledge
    ├── exploitation/SKILL.md           # Exploitation knowledge
    └── privesc/SKILL.md                # Privilege escalation knowledge
```

## Usage

```bash
/start-pentest <target-ip>
```

The system will:
1. SessionStart hook detects/initializes session
2. Coordinator makes strategic decisions
3. PostToolUse hook auto-captures flags
4. Stop hook prevents stopping until complete

## Key Improvements Over V3

1. **Deterministic enforcement** (not just instructions)
2. **Automatic state management** (no manual jq)
3. **Cleaner context** (200 vs 3000 lines)
4. **Session awareness** (auto-resume)

## Version

**V4.1** - Architecture redesign based on official Claude Code documentation
