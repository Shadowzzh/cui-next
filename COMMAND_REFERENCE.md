# Command Reference

## 🎯 Mode Selection Commands

The command you use **automatically selects the testing mode**. No manual configuration needed!

### CTF/HackTheBox Mode

```bash
/start-ctf <target-ip>
```

**Examples:**
```bash
/start-ctf 10.10.10.1              # HackTheBox machine
/start-ctf 192.168.56.101          # VulnHub VM
/start-ctf 10.10.14.50             # TryHackMe room
```

**What it does:**
- Creates state with `scenario_type: "ctf"`
- Sets phases: reconnaissance → exploitation → privilege_escalation → completed
- Sets goal: Capture user.txt + root.txt flags (32-char hex)
- Activates CTF workflow in coordinator

**Completion criteria:**
- ✅ `flags.user` = 32-character hexadecimal string
- ✅ `flags.root` = 32-character hexadecimal string

---

### Vulhub CVE Mode

```bash
/start-vulhub <target>
```

**Examples:**
```bash
/start-vulhub 127.0.0.1:8080          # Target with specific port
/start-vulhub 192.168.1.100:7001      # Another specific port
/start-vulhub 10.10.10.1              # Target (will scan common ports)
```

**What it does:**
- Creates state with `scenario_type: "vulhub"`
- Initializes with `vulnerability_id: "unknown"` (will be discovered)
- Sets phases: reconnaissance → exploitation → verification → completed
- **Reconnaissance phase:** Identifies CVE through service enumeration
- **Auto-generates** success criteria after CVE identification
- Activates Vulhub workflow in coordinator

**Reconnaissance process:**
1. Enumerate service and version (nmap)
2. Identify CVE (searchsploit)
3. Update state with CVE ID
4. Generate success criteria based on CVE type

**Completion criteria:**
- ✅ CVE identified (`vulnerability_id != "unknown"`)
- ✅ `objective.evidence.length >= objective.success_criteria.length`
- ✅ Each success criterion has corresponding evidence

---

### Legacy Command (Deprecated)

```bash
/start-pentest <target-ip>
```

**Status:** Still works but shows deprecation warning

**Redirects to:** CTF mode

**Recommendation:** Use `/start-ctf` instead for clarity

---

## 📊 Monitoring Commands

### Show Current State

```bash
/show-state
```

**Displays:**
- **CTF mode**: Target, phase, flags (user/root), discovered services, failed attempts
- **Vulhub mode**: Target, CVE, success criteria, evidence collected, phase

**Alternative:**
```bash
cat .pentest-state.json | jq
```

---

### Quick Scan (Reconnaissance Only)

```bash
/quick-scan <target-ip>
```

**What it does:**
- Fast reconnaissance without exploitation
- Port scan + service enumeration
- Does NOT create persistent state
- Does NOT attempt exploitation

**Use when:** You just want to see what's running on a target

---

## 🔄 State Management Commands

### Reset Everything

```bash
/reset-state
```

**What it does:**
- Deletes `.pentest-state.json`
- Deletes `.pentest-backups/` directory
- Cleans up all testing artifacts
- Ready for new test

**Use when:** Switching to a different target or mode

---

## 🆚 Command Comparison

| Scenario | Command | Mode | Completion |
|----------|---------|------|------------|
| HackTheBox machine | `/start-ctf 10.10.10.1` | CTF | user.txt + root.txt |
| VulnHub VM | `/start-ctf 192.168.56.101` | CTF | user.txt + root.txt |
| TryHackMe room | `/start-ctf 10.10.X.X` | CTF | user.txt + root.txt |
| Vulhub (unknown CVE) | `/start-vulhub 127.0.0.1:8080` | Vulhub | Auto-discovered CVE + evidence |
| Vulhub (no port) | `/start-vulhub 192.168.1.100` | Vulhub | Auto-discovered CVE + evidence |
| Quick recon only | `/quick-scan 10.10.10.1` | N/A | Info gathering only |
| View progress | `/show-state` | Auto-detect | Display state |
| Clean up | `/reset-state` | N/A | Delete state |

---

## 🎨 Mode Auto-Detection Flow

```
User runs command
      ↓
┌─────────────────┐
│  /start-ctf ?   │────── YES ──→ Create CTF state → scenario_type="ctf"
└─────────────────┘
         NO
         ↓
┌─────────────────┐
│ /start-vulhub ? │────── YES ──→ Create Vulhub state → scenario_type="vulhub"
└─────────────────┘
         NO
         ↓
┌─────────────────┐
│ /start-pentest ?│────── YES ──→ Show warning → Use CTF mode (deprecated)
└─────────────────┘
         NO
         ↓
    Manual setup required
```

---

## 📖 Detailed Documentation

For comprehensive usage examples, see:
- **[DUAL_MODE_USAGE.md](DUAL_MODE_USAGE.md)** - Full guide with examples
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start in 2 minutes
- **[.claude/CLAUDE.md](.claude/CLAUDE.md)** - Framework architecture

---

## 💡 Pro Tips

### Tip 1: Use the Right Command
```bash
# ✅ GOOD: Clear intent
/start-ctf 10.10.10.1
/start-vulhub 127.0.0.1:8080 CVE-2017-5638 struts2-s2-045

# ⚠️  WORKS BUT DEPRECATED: Not clear which mode
/start-pentest 10.10.10.1
```

### Tip 2: Check Mode Before Starting
```bash
# If state already exists, check what mode it's in
jq '.scenario_type' .pentest-state.json

# Output: "ctf" or "vulhub"
```

### Tip 3: Switch Modes
```bash
# To switch from CTF to Vulhub (or vice versa)
/reset-state
/start-vulhub 127.0.0.1:8080 CVE-2017-5638 struts2-s2-045
```

### Tip 4: Monitor Evidence (Vulhub Mode)
```bash
# See what evidence has been collected
jq '.objective.evidence' .pentest-state.json

# See what criteria remain
jq '.objective.success_criteria' .pentest-state.json
```

### Tip 5: Monitor Flags (CTF Mode)
```bash
# Check flag status
jq '.flags' .pentest-state.json

# Output:
# {
#   "user": "a1b2c3d4...",  or null
#   "root": "f6e5d4c3..."   or null
# }
```

---

## 🔧 Troubleshooting

### "Command not found"
```bash
# Make sure you're in the project directory
cd /path/to/t-bug

# Verify commands exist
ls .claude/commands/
```

### "State file not created"
```bash
# Check if template file exists
ls .claude/state-templates.json

# Manually create state if needed (see DUAL_MODE_USAGE.md)
```

### "Wrong mode activated"
```bash
# Check current mode
jq '.scenario_type' .pentest-state.json

# Reset and restart with correct command
/reset-state
/start-ctf 10.10.10.1  # or /start-vulhub ...
```

---

**Quick Navigation:**
- [Main README](README.md)
- [Quick Start](QUICKSTART.md)
- [Dual Mode Usage](DUAL_MODE_USAGE.md)
- [Framework Architecture](.claude/CLAUDE.md)
