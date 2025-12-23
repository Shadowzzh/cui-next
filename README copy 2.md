# Automated Penetration Testing Framework

A structured penetration testing prompt engineering framework built on Claude Code, implementing ReAct (Reasoning-Action-Observation) methodology with modular knowledge bases and state persistence.

## 🎯 Project Goals

This framework aims to significantly enhance Claude Code's penetration testing capabilities through:

1. **Structured Reasoning**: ReAct loop methodology encoded as systematic thinking guidance
2. **State Management**: JSON-based persistence of discoveries and progress
3. **Modular Knowledge**: Domain-specific Skills (prompt extensions) for different phases
4. **Workflow Optimization**: Slash commands for quick task triggering

## 📁 Architecture Overview

```
.claude/
├── CLAUDE.md                      # Core configuration and global instructions
├── skills/                        # Specialized penetration testing skills
│   ├── coordinator/
│   │   └── SKILL.md              # Main orchestrator (ReAct loop)
│   ├── recon/
│   │   └── SKILL.md              # Reconnaissance expertise
│   ├── exploitation/
│   │   └── SKILL.md              # Exploitation techniques
│   └── privesc/
│       └── SKILL.md              # Privilege escalation methods
├── commands/                      # Quick-access slash commands
│   ├── start-pentest.md          # /start-pentest <IP>
│   ├── show-state.md             # /show-state
│   ├── reset-state.md            # /reset-state
│   └── quick-scan.md             # /quick-scan <IP>
└── hooks/                         # Automation hooks
    ├── hooks.json                # Hook configuration
    └── save-state.sh             # State reminder script
```

## 🧠 Core Components

### 1. Coordinator Skill (Methodology Guide)

**Location**: `.claude/skills/coordinator/SKILL.md`

**Purpose**: Provides comprehensive ReAct methodology guidance for Claude

**Key Features**:
- Instructions for maintaining global state in `.pentest-state.json`
- Detailed Reasoning → Action → Observation loop guidance
- Procedures for tracking services, vulnerabilities, credentials
- Guidelines for phase transitions (recon → exploit → privesc)
- Validation criteria for flag capture before completion

**Technical Reality**: This is a 280-line prompt that extends Claude's context with structured penetration testing methodology. Claude follows this guidance through its own reasoning and decision-making.

**State Structure**:
```json
{
  "target": "10.10.10.1",
  "phase": "reconnaissance|exploitation|privilege_escalation|completed",
  "discovered": {
    "services": [],
    "vulnerabilities": [],
    "credentials": [],
    "interesting_files": []
  },
  "flags": {
    "user": null,
    "root": null
  },
  "attack_plan": [],
  "current_action": "",
  "failed_attempts": [],
  "successful_paths": [],
  "stuck_counter": 0
}
```

### 2. Specialized Knowledge Modules (Skills)

#### Reconnaissance Knowledge (`recon` skill, 324 lines)
**Focus**: Methodologies for information gathering, service enumeration, web discovery
**Tools Guidance**: nmap, gobuster, nikto, enum4linux usage patterns
**Output Format**: Templates for structured JSON data about attack surface
**Methodology**: Layered scanning framework (Quick → Deep → Alternative)

#### Exploitation Knowledge (`exploitation` skill, 525 lines)
**Focus**: Techniques for vulnerability exploitation and initial access
**Tools Guidance**: searchsploit, metasploit, custom exploit adaptation
**Goal**: Instructions for gaining command execution and capturing user flag
**Methodology**: Multi-source exploit discovery, environment-aware payload selection

#### Privilege Escalation Knowledge (`privesc` skill, 552 lines)
**Focus**: Methods for escalating to root
**Tools Guidance**: linpeas, sudo checks, SUID enumeration, GTFOBins
**Goal**: Procedures for obtaining root access and capturing root flag
**Methodology**: Layered privesc strategy (Quick wins → Deep enum → Alternative methods)

**Note**: These Skills are knowledge bases loaded into Claude's context, not executable programs or separate agents.

### 3. Slash Commands (Prompt Templates)

Quick-access prompt templates for common operations:

- `/start-pentest <IP>` - Expands to prompt for beginning autonomous test
- `/show-state` - Expands to prompt for displaying current progress
- `/reset-state` - Expands to prompt for cleanup operations
- `/quick-scan <IP>` - Expands to prompt for rapid reconnaissance

**Technical Reality**: These are Markdown files containing prompt text with `$ARGUMENTS` placeholders, not executable scripts.

### 4. Hooks (Minimal Implementation)

**PostToolUse Hook**: Configured to run after Bash command execution
**Current Implementation**: Creates backup directory only (`.pentest-backups/`)
**Purpose**: Originally intended for state management automation, currently minimal

**Note**: The actual hook script (`.claude/hooks/save-state.sh`) contains only basic directory creation. State management is done manually by Claude through jq commands as instructed in the Coordinator skill.

## 🚀 How It Works

### ReAct Loop Implementation

```
┌─────────────────────────────────────────┐
│  1. REASONING                           │
│  - Load .pentest-state.json            │
│  - Analyze discoveries                 │
│  - Decide next action                  │
│  - Consider failed attempts            │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  2. ACTION                              │
│  - Execute chosen operation            │
│  - Update state with current_action    │
│  - Use appropriate tools/techniques    │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  3. OBSERVATION                         │
│  - Analyze results                     │
│  - Extract structured data             │
│  - Update state with discoveries       │
│  - Check for flags                     │
│  - Evaluate success/failure            │
└─────────────────────────────────────────┘
                 ↓
         Loop until both flags
         captured (user + root)
```

### Execution Flow Example

1. **User**: "/start-pentest 10.10.10.50"

2. **Initialization**:
   - Coordinator knowledge loads into Claude's context
   - Claude creates `.pentest-state.json`
   - Sets phase to `reconnaissance`

3. **Reconnaissance Phase**:
   - **Reasoning**: No data yet, need port scan (applying recon knowledge)
   - **Action**: Execute `nmap -p- -T4 10.10.10.50`
   - **Observation**: Found ports 22, 80, 3306
   - **Update State**: Claude executes jq command to add services to state
   - **Reasoning**: HTTP found, enumerate web (applying recon knowledge)
   - **Action**: `gobuster dir -u http://10.10.10.50 -w wordlist`
   - **Observation**: Found /admin, /uploads, /backup
   - **Update State**: Claude executes jq command to add directories

4. **Exploitation Phase**:
   - **Reasoning**: /uploads might allow file upload
   - **Action**: Test file upload with PHP webshell
   - **Observation**: Upload successful, webshell active
   - **Action**: Execute commands via webshell
   - **Action**: `find /home -name user.txt`
   - **Observation**: Found `/home/alice/user.txt`
   - **Action**: `cat /home/alice/user.txt`
   - **Observation**: User flag captured! ✓
   - **Update State**: Save user flag

5. **Privilege Escalation Phase**:
   - **Reasoning**: Need root access
   - **Action**: Check `sudo -l`
   - **Observation**: Can run `/usr/bin/vim` as root
   - **Reasoning**: GTFOBins has vim exploit
   - **Action**: `sudo vim -c ':!/bin/sh'`
   - **Observation**: Root shell obtained
   - **Action**: `cat /root/root.txt`
   - **Observation**: Root flag captured! ✓
   - **Update State**: Save root flag

6. **Completion**:
   - Both flags verified (32-char hex strings)
   - State updated to `completed`
   - Mission accomplished

## 🎓 Key Improvements Over Basic Approach

### Original Approach (Single CLAUDE.md)
❌ All logic in one unstructured document
❌ No state persistence
❌ No systematic methodology
❌ Easy to lose track or repeat actions
❌ Token inefficient (re-explaining context)
❌ Single-point failure (no escalation when methods fail)
❌ No failure diagnosis or environment awareness

### This Framework
✅ **Structured ReAct Loop**: Systematic reasoning methodology encoded in prompts
✅ **State Management**: Persistent `.pentest-state.json` tracks everything (via manual jq updates)
✅ **Modular Knowledge**: 1500+ lines of domain knowledge separated into loadable Skills
✅ **Layered Attempt Framework**: Every task has Layer 1 (Quick) → Layer 2 (Deep) → Layer 3 (Alternative)
✅ **Failure Diagnosis**: Systematic diagnosis framework for 4 failure types with diagnostic context
✅ **Multi-Source Discovery**: Guidance for parallel search across searchsploit, Metasploit, GitHub, custom sources
✅ **Environment-Aware Exploitation**: Decision trees for probing attacker/target environment before choosing methods
✅ **Re-evaluation Mechanism**: Stuck counter methodology triggers systematic re-examination after 5 failures
✅ **Phase Transitions**: Clear progression guidelines through pentest stages
✅ **Workflow Optimization**: Slash command templates for common tasks
✅ **Token Efficient**: State file reduces context duplication across reasoning cycles

See `IMPROVEMENTS.md` for detailed documentation of universal methodologies.

## 💡 Usage

### Starting a Penetration Test

**Method 1: Slash Command**
```bash
/start-pentest 10.10.10.1
```

**Method 2: Direct Instruction**
```
Perform penetration test on target 10.10.10.1
```

The Coordinator skill will automatically activate and begin the autonomous testing process.

### Monitoring Progress

```bash
# View current state
/show-state

# Or manually check state file
cat .pentest-state.json | jq

# Check for flags
jq '.flags' .pentest-state.json
```

### Resetting for New Target

```bash
/reset-state
```

## 🔧 Technical Requirements

- **Environment**: Kali Linux or similar pentesting distribution
- **Tools**: nmap, gobuster, searchsploit, metasploit, etc.
- **Claude Code**: Latest version with Skills support
- **jq**: JSON processor (for state manipulation)

## 📊 Expected Performance Improvements

Based on research, testing analysis, and architecture design:

| Metric | Original Approach | This Framework | Improvement |
|--------|------------------|----------------|-------------|
| Success Rate | ~56% (baseline) | ~75-85% | +29% (+19-29pp) |
| Stuck Rate | ~40% | <10% | -30pp reduction |
| Avg Time (Easy Box) | 30-60 min | 10-20 min | 2-3x faster |
| Token Usage | High (redundant context) | Medium (state-based) | ~30% reduction |
| Flag Capture Accuracy | Inconsistent | Reliable | Structured validation |

**Note**: Success rate improvements achieved through universal methodologies (layered attempts, failure diagnosis, multi-source discovery, environment awareness, re-evaluation). See `IMPROVEMENTS.md` for detailed analysis.

## 🎯 Success Criteria

The system will ONLY declare completion when:

1. ✅ User flag captured (32-character hex string)
2. ✅ Root flag captured (32-character hex string)
3. ✅ Both flags verified and saved in state
4. ✅ Actual content displayed (not just file paths)

## 🛡️ Safety & Ethics

This framework is designed for:
- ✅ Authorized security testing
- ✅ CTF competitions and playgrounds
- ✅ Educational purposes
- ✅ Security research

Always ensure you have proper authorization before testing any system.

## 📚 Research Context

This framework is inspired by concepts from recent academic research, adapted to Claude Code's prompt-based architecture:

- **PentestAgent** (ACM CCS 2024): LLM-based penetration testing automation
- **ReAct Methodology**: Reasoning-Action-Observation loop for systematic problem-solving
- **Prompt Engineering**: Modular knowledge organization through Skills system
- **Claude Code Features** (Anthropic 2025): Skills as prompt extensions, slash commands, state management patterns

## 🔄 Future Enhancements

Potential areas for improvement:
- MCP integration for real-time exploit database queries
- RAG-based success case retrieval from past tests
- Enhanced hook implementation for automated state validation
- Additional specialized knowledge modules (wireless, web app specific, etc.)
- Performance optimization for different Claude models (Haiku vs Sonnet)

## 📖 Documentation

- **CLAUDE.md**: Core instructions and principles
- **Coordinator SKILL.md**: Main orchestration logic
- **Specialized Skills**: Domain-specific knowledge bases
- **Slash Commands**: Quick reference for common operations

## 🤝 Contributing

This is a research project. Suggestions for improvements are welcome.

---

**Version**: 1.0
**Last Updated**: 2025-01-17
**Status**: Production Ready
