# Quick Start Guide

## 🚀 Getting Started in 2 Minutes

### Step 1: Verify Setup

```bash
# Check that all components are in place
ls -la .claude/

# Should see:
# - CLAUDE.md
# - skills/ (4 skills)
# - commands/ (4 commands)
# - hooks/ (hooks.json + save-state.sh)
```

### Step 2: Start a Penetration Test

**Option A: Using Slash Command**
```bash
/start-pentest 10.10.10.1
```

**Option B: Direct Instruction**
```
Start penetration test on target 10.10.10.1
```

**Option C: Natural Language**
```
Please pentest 10.10.10.50 and get both user and root flags
```

### Step 3: Monitor Progress

```bash
# Check current state
/show-state

# Or view state file directly
cat .pentest-state.json | jq

# Monitor what phase we're in
jq '.phase' .pentest-state.json

# Check if flags are captured
jq '.flags' .pentest-state.json
```

### Step 4: Wait for Completion

Claude, guided by the Coordinator methodology, will:
1. ✅ Scan and enumerate services
2. ✅ Find and exploit vulnerabilities
3. ✅ Gain initial access (user flag)
4. ✅ Escalate privileges (root flag)
5. ✅ Verify both flags are captured

**Do not interrupt** - Claude will follow the ReAct loop until both flags are obtained.

## 📊 What to Expect

### Typical Execution Flow

```
[00:00] Initialization
  └─ Creating .pentest-state.json
  └─ Setting target: 10.10.10.1
  └─ Phase: reconnaissance

[00:30] Reconnaissance
  └─ Port scanning (nmap)
  └─ Service enumeration
  └─ Web directory discovery (if HTTP found)
  └─ Services found: 22 (SSH), 80 (HTTP), 3306 (MySQL)

[05:00] Exploitation
  └─ Searching for exploits
  └─ Testing file upload vulnerability
  └─ Uploading webshell
  └─ Executing commands
  └─ Finding user.txt
  └─ User flag captured: abc123...

[10:00] Privilege Escalation
  └─ Checking sudo permissions
  └─ Finding SUID binaries
  └─ Exploiting sudo vim
  └─ Gaining root access
  └─ Reading root.txt
  └─ Root flag captured: def456...

[12:00] ✅ Mission Complete
  └─ Both flags verified and saved
```

## 🎯 Success Indicators

You'll know the test is complete when you see:

```json
{
  "phase": "completed",
  "flags": {
    "user": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "root": "f6e5d4c3b2a1098765432109876543210"
  }
}
```

Both flags must be **32-character hexadecimal strings**.

## 🛠️ Troubleshooting

### "Coordinator knowledge not loading"

Make sure CLAUDE.md and Skills are in place:
```bash
# Verify files exist
ls -la .claude/CLAUDE.md
ls -la .claude/skills/coordinator/SKILL.md
```

The Coordinator skill should auto-load when you mention penetration testing or use `/start-pentest`.

### "State file not updating"

Manually initialize:
```bash
cat > .pentest-state.json << 'EOF'
{
  "target": "10.10.10.1",
  "phase": "reconnaissance",
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
EOF
```

### "Test seems stuck"

Check current action:
```bash
jq '.current_action' .pentest-state.json
```

Check failed attempts:
```bash
jq '.failed_attempts' .pentest-state.json
```

### "Want to start over"

Reset everything:
```bash
/reset-state

# Or manually
rm -f .pentest-state.json
rm -f .pentest-findings-backup.txt
rm -rf .pentest-backups/
```

## 💡 Tips for Best Results

### 1. Let It Run Autonomously
- Don't interrupt the process
- The system is designed to recover from failures
- It will try multiple approaches automatically

### 2. Trust the ReAct Loop
- Each action is based on reasoning
- Failed attempts inform future decisions
- The coordinator learns what doesn't work

### 3. State File is Key
- Always check `.pentest-state.json` for progress
- It contains all discoveries
- Claude updates it manually via jq commands as instructed

### 4. Use Slash Commands for Convenience
```bash
/start-pentest <IP>    # Start test
/show-state            # Check progress
/quick-scan <IP>       # Just recon (fast)
/reset-state           # Clean up
```

## 📈 Performance Expectations

### Easy Boxes (HTB/VulnHub)
- **Time**: 10-20 minutes
- **Success Rate**: 80-90%
- **Token Usage**: ~50k-100k tokens

### Medium Boxes
- **Time**: 20-40 minutes
- **Success Rate**: 60-70%
- **Token Usage**: ~100k-200k tokens

### Hard Boxes
- **Time**: 40-60+ minutes
- **Success Rate**: 40-50%
- **Token Usage**: 200k+ tokens

## 🎓 Understanding the Architecture

### ReAct Loop in Action

**Reasoning Phase** (Think before acting)
- What do we know?
- What should we try next?
- What has failed before?

**Action Phase** (Execute)
- Run commands
- Test exploits
- Update state

**Observation Phase** (Learn from results)
- What did we discover?
- Did it work?
- What's next?

### Skills as Knowledge Modules

Skills are **prompt extensions** that load knowledge into Claude's context:
- **Coordinator** (280 lines): Methodology guide for ReAct loop and state management
- **Recon** (324 lines): Reconnaissance techniques and tool usage patterns
- **Exploitation** (525 lines): Exploitation methodologies and decision trees
- **PrivEsc** (552 lines): Privilege escalation techniques and procedures

When relevant, these knowledge modules load automatically, extending Claude's context with specialized guidance. Claude then applies this knowledge through its own reasoning.

## 🔍 Example State Progression

**Initial State (t=0)**
```json
{
  "target": "10.10.10.1",
  "phase": "reconnaissance",
  "discovered": { "services": [] },
  "flags": { "user": null, "root": null }
}
```

**After Recon (t=5min)**
```json
{
  "phase": "exploitation",
  "discovered": {
    "services": [
      {"port": 80, "service": "http", "version": "Apache 2.4.29"}
    ],
    "vulnerabilities": ["Unrestricted file upload on /uploads"]
  }
}
```

**After User Flag (t=10min)**
```json
{
  "phase": "privilege_escalation",
  "flags": { "user": "abc123def456..." }
}
```

**Completed (t=15min)**
```json
{
  "phase": "completed",
  "flags": {
    "user": "abc123...",
    "root": "def456..."
  }
}
```

## ✅ Checklist

Before starting your first test:

- [ ] All files in `.claude/` directory present
- [ ] Hook script is executable (`chmod +x .claude/hooks/save-state.sh`)
- [ ] `jq` is installed (for JSON processing)
- [ ] Basic pentest tools available (nmap, gobuster, etc.)
- [ ] You have a target IP from a playground/CTF

Start with:
```bash
/start-pentest <YOUR_TARGET_IP>
```

And watch the magic happen! 🎯

---

**Need Help?** Check README.md for detailed architecture explanation.
