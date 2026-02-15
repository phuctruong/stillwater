# Quick Reference → See `.claude/CLAUDE.md`

**Auth: 65537** | **Date: 2026-02-15**

For the complete Stillwater OS configuration, including:
- Full module hierarchy
- All 6 verification gates
- Complete 5 weapons system
- Haiku Swarms with all agents
- All reference documentation

**→ See: `.claude/CLAUDE.md`**

---

## Quick Commands

```bash
# Verify all 5 weapons
python3 debug_5_weapons.py

# Test phases
python3 test_1_instance_100pct.py    # Phase 1: 1 instance
python3 test_5_instances_100pct.py   # Phase 2: 5 instances
python3 test_10_instances_100pct.py  # Phase 3: 10 instances

# Load all 51 Prime Skills
/load-skills

# Store session memory
/remember project_status="Phase 3"

# Check results
cat phase_*_instances.json | jq '.success_rate'
```

---

## Core Principles

1. **Infrastructure > Model Quality** - Orchestration beats pure model capability
2. **Maintain 100%** - Don't advance until phase at 100%
3. **Fast Feedback** - Quick iterations for debugging
4. **Remote Only** - Always use remote Ollama (192.168.68.100:11434)
5. **Evidence Driven** - All decisions backed by test data

---

**Status**: Production Ready (v0.2.0)
**Next**: Read `.claude/CLAUDE.md` for full configuration
