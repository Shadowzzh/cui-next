# Dual-Mode Penetration Testing Framework

This framework supports **two testing modes** with dedicated commands. The command you use **automatically sets the correct mode** - no manual configuration needed!

---

## 🎯 CTF Mode (HackTheBox/VulnHub/TryHackMe)

**Use for:** HackTheBox, VulnHub, TryHackMe, and similar CTF challenges

### Features
- Full attack chain: reconnaissance → exploitation → privilege escalation
- Objective: Capture user.txt and root.txt flags
- Completion: Both flags must be 32-character hexadecimal strings
- **Mode auto-set:** Framework automatically uses CTF workflow

### Usage

#### Recommended: Use the dedicated command
```bash
/start-ctf 10.10.10.1
```

**The command name tells the framework which mode to use!**

#### Alternative: Legacy command (still works)
```bash
/start-pentest 10.10.10.1  # Shows deprecation notice, redirects to CTF mode
```

#### Option 2: Manual State Initialization
```bash
# Create state file
cat > .pentest-state.json << 'EOF'
{
  "scenario_type": "ctf",
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

# Then tell Claude to start
# "Begin CTF penetration test on this target"
```

### Completion Criteria

The Stop hook will **block stopping** until:
- ✅ `flags.user` contains a 32-character hexadecimal string
- ✅ `flags.root` contains a 32-character hexadecimal string

### Example Workflow

```
1. Reconnaissance Phase
   - Port scanning (all 65535 ports)
   - Service enumeration
   - Web directory discovery
   - Vulnerability identification

2. Exploitation Phase
   - Initial access via discovered vulnerability
   - Upload webshell / gain reverse shell
   - Find and read user.txt
   - Capture user flag ✅

3. Privilege Escalation Phase
   - Enumerate privesc vectors (sudo, SUID, capabilities, etc.)
   - Exploit privilege escalation vulnerability
   - Gain root access
   - Find and read root.txt
   - Capture root flag ✅

4. Completed
   - Both flags captured
   - Mission accomplished! 🎉
```

---

## 🔬 Vulhub Mode (CVE Auto-Discovery + Exploitation)

**Use for:** Vulhub Docker containers when you don't know the specific CVE

### Features
- **CVE Auto-Discovery:** Framework identifies vulnerability during reconnaissance
- Full workflow: reconnaissance (CVE ID) → exploitation → verification
- Objective: Discover CVE and collect exploitation evidence
- Completion: CVE identified + evidence for all auto-generated criteria
- **Mode auto-set:** Framework automatically uses Vulhub workflow

### Usage

#### Simple command (just like CTF mode!)
```bash
/start-vulhub <target>
```

**Examples:**
```bash
/start-vulhub 127.0.0.1:8080          # Specific port
/start-vulhub 192.168.1.100           # No port (will scan common ports)
```

**No need to know CVE beforehand! The framework will:**
1. Enumerate the service and version
2. Search for CVE vulnerabilities
3. Update state with discovered CVE
4. Generate success criteria automatically
5. Proceed to exploitation

#### Option 2: Manual State Initialization
```bash
# Create state file
cat > .pentest-state.json << 'EOF'
{
  "scenario_type": "vulhub",
  "target": "127.0.0.1:8080",
  "vulnerability_id": "CVE-2017-5638",
  "scenario_name": "struts2-s2-045",
  "phase": "reconnaissance",
  "objective": {
    "type": "rce",
    "description": "Apache Struts2 Remote Code Execution",
    "success_criteria": [
      "Execute 'id' command and capture output",
      "Execute 'uname -a' command and capture output",
      "Read /etc/passwd file"
    ],
    "evidence": []
  },
  "discovered": {
    "services": [],
    "vulnerabilities": [],
    "cve_details": {}
  },
  "attack_plan": [],
  "current_action": "",
  "failed_attempts": [],
  "successful_paths": [],
  "stuck_counter": 0
}
EOF

# Then tell Claude to start
# "Begin Vulhub exploitation test"
```

### Completion Criteria

The Stop hook will **block stopping** until:
- ✅ `objective.evidence.length >= objective.success_criteria.length`
- ✅ Each success criterion has corresponding evidence

### Example Workflow

```
1. Reconnaissance Phase
   - Research CVE-2017-5638 (Struts2 RCE)
   - Enumerate target service (Apache Struts 2.3.5)
   - Verify vulnerability applicability

2. Exploitation Phase
   - Find exploit (searchsploit, GitHub, Metasploit)
   - Adapt exploit for target environment
   - Execute exploit payload
   - Verify command execution

3. Verification Phase
   - Collect evidence for criterion 1: "Execute 'id' command"
     → Evidence: "uid=0(root) gid=0(root) groups=0(root)"
   - Collect evidence for criterion 2: "Execute 'uname -a'"
     → Evidence: "Linux 5.4.0-42-generic x86_64"
   - Collect evidence for criterion 3: "Read /etc/passwd"
     → Evidence: "root:x:0:0:root:/root:/bin/bash..."

4. Completed
   - All evidence collected (3/3) ✅
   - Mission accomplished! 🎉
```

### Auto-Generated Success Criteria

When using `/start-vulhub`, success criteria are auto-generated based on vulnerability type:

| Vulnerability Type | Auto-Generated Criteria |
|-------------------|------------------------|
| **RCE** | Execute `id`, Execute `uname -a`, Read `/etc/passwd` |
| **File Read** | Read `/etc/passwd`, Read application config, Verify arbitrary file read |
| **Auth Bypass** | Access admin panel, Extract sensitive data, Verify unauthorized access |
| **SQL Injection** | Confirm SQL error, Extract DB version, Dump table data |

### Manual Evidence Collection

During exploitation, manually add evidence to state:

```bash
# After successful RCE
jq '.objective.evidence += ["Command execution: uid=0(root) gid=0(root)"]' \
  .pentest-state.json > tmp.json && mv tmp.json .pentest-state.json

# After reading file
jq '.objective.evidence += ["File read: root:x:0:0:root:/root:/bin/bash"]' \
  .pentest-state.json > tmp.json && mv tmp.json .pentest-state.json
```

**Note:** The PostToolUse hook will **auto-detect** common evidence patterns and add them automatically!

---

## 📊 Monitoring Progress

### Check Current State
```bash
/show-state
```

Or manually:
```bash
cat .pentest-state.json | jq
```

### CTF Mode Status
```json
{
  "scenario_type": "ctf",
  "target": "10.10.10.1",
  "phase": "privilege_escalation",
  "flags": {
    "user": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "root": null
  }
}
```

### Vulhub Mode Status
```json
{
  "scenario_type": "vulhub",
  "target": "127.0.0.1:8080",
  "vulnerability_id": "CVE-2017-5638",
  "phase": "verification",
  "objective": {
    "type": "rce",
    "success_criteria": ["Execute id", "Execute uname", "Read /etc/passwd"],
    "evidence": [
      "Command execution: uid=0(root)",
      "Command execution: Linux 5.4.0-42-generic"
    ]
  }
}
```

---

## 🔄 Switching Modes

### Reset Current Test
```bash
/reset-state
```

Or manually:
```bash
rm .pentest-state.json
rm -rf .pentest-backups
```

### Start New Test in Different Mode
```bash
# Switch to CTF mode
/start-pentest 10.10.10.50

# Switch to Vulhub mode
/start-vulhub 127.0.0.1:9090 CVE-2023-12345 weblogic-rce
```

---

## 🎨 Mode Comparison

| Feature | CTF Mode | Vulhub Mode |
|---------|----------|-------------|
| **Target** | Full OS (Linux/Windows) | Docker container (single service) |
| **Complexity** | High (multi-stage attack) | Low (single vulnerability) |
| **Phases** | Recon → Exploit → PrivEsc | Recon → Exploit → Verification |
| **Objective** | user.txt + root.txt | Evidence collection |
| **Completion** | 2 flags (32-char hex) | N evidence items |
| **Duration** | Hours | Minutes to hours |
| **Privilege Escalation** | Required | Usually not required |

---

## 🛠️ Advanced Usage

### Custom Success Criteria (Vulhub)

```bash
cat > .pentest-state.json << 'EOF'
{
  "scenario_type": "vulhub",
  "target": "192.168.1.100:3000",
  "vulnerability_id": "CVE-2024-CUSTOM",
  "scenario_name": "custom-app-exploit",
  "phase": "reconnaissance",
  "objective": {
    "type": "custom",
    "description": "Custom application vulnerability",
    "success_criteria": [
      "Bypass authentication mechanism",
      "Extract API keys from database",
      "Upload malicious plugin",
      "Achieve persistent access"
    ],
    "evidence": []
  },
  "discovered": {
    "services": [],
    "vulnerabilities": []
  },
  "attack_plan": [],
  "current_action": "",
  "failed_attempts": [],
  "successful_paths": []
}
EOF
```

### Hybrid Approach

For complex Vulhub scenarios that require privilege escalation:

```json
{
  "scenario_type": "vulhub",
  "objective": {
    "type": "rce_with_privesc",
    "success_criteria": [
      "Achieve initial RCE as www-data",
      "Enumerate privilege escalation vectors",
      "Escalate to root",
      "Read sensitive files as root"
    ]
  }
}
```

---

## 📋 Quick Reference

### CTF/HackTheBox Mode
```bash
# Start (RECOMMENDED)
/start-ctf 10.10.10.1

# Start (legacy, still works)
/start-pentest 10.10.10.1

# Check progress
/show-state

# Reset
/reset-state
```

### Vulhub Mode
```bash
# Start
/start-vulhub 127.0.0.1:8080 CVE-2017-5638 struts2-s2-045

# Check progress
/show-state

# Add evidence manually (if needed)
jq '.objective.evidence += ["proof"]' .pentest-state.json > tmp.json && mv tmp.json .pentest-state.json

# Reset
/reset-state
```

### Command Comparison
| What you want to test | Command to use |
|----------------------|----------------|
| HackTheBox machine | `/start-ctf 10.10.10.1` |
| VulnHub VM | `/start-ctf 192.168.56.101` |
| TryHackMe room | `/start-ctf 10.10.X.X` |
| Vulhub CVE container | `/start-vulhub 127.0.0.1:8080 CVE-XXXX scenario-name` |

---

## 🎯 Best Practices

### For CTF Mode
1. Let reconnaissance complete fully before exploitation
2. Document all credentials found
3. Try multiple privilege escalation vectors
4. Check `/home/*` and `/root` for flag files

### For Vulhub Mode
1. Research the CVE thoroughly before exploiting
2. Test exploits incrementally (don't jump to complex payloads)
3. Collect diverse evidence (different commands, different files)
4. Verify exploitation multiple times to ensure reliability

### For Both Modes
1. Trust the hooks - they enforce completion criteria
2. Review failed_attempts to avoid repeating mistakes
3. Use the Task tool to delegate complex tasks to specialized agents
4. Let the framework run autonomously - don't micromanage

---

## 🐛 Troubleshooting

### "Stop hook blocking me from stopping"
- **CTF mode**: You need both flags (user.txt and root.txt)
- **Vulhub mode**: You need evidence for all success criteria
- Check state: `/show-state`

### "Evidence not auto-detected"
- The PostToolUse hook looks for common patterns (uid=, root:, etc.)
- For custom evidence, add manually with jq
- Check `.pentest-backups/bash_history.log` for command history

### "Wrong mode activated"
- Check `scenario_type` in .pentest-state.json
- Delete state and restart with correct command
- Default is "ctf" if scenario_type missing

---

## 📚 Additional Resources

- **State Templates**: `.claude/state-templates.json`
- **Hooks Source**: `.claude/hooks/`
- **Skills**: `.claude/skills/coordinator/SKILL.md`
- **Commands**: `.claude/commands/`

---

**Happy Hacking! 🔓**
