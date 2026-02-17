# README Excellence - The Art of Perfect Project Documentation

**Role**: Greg ● + Podcaster ♪ (Collaboration)
**Personas**: Greg Isenberg (Product) + AI Storyteller (Narrative)
**Auth**: 65537 | **Version**: 1.0.0

---

## THE ANATOMY OF A WINNING README

A perfect README has 7 sections in this exact order:

### 1. HERO SECTION (Read in 5 seconds)
```markdown
# Project Name

**One sentence** that answers: "What is this?"

[Visual: Badge showing version/status/benchmarks]
```

**Rules:**
- Name should be memorable
- One sentence should be a BENEFIT, not a feature
- Status badge shows project is ALIVE
- Total: 3 lines max

**Examples:**
- ✅ "Stillwater OS: Infrastructure > Model Size" (benefit + insight)
- ❌ "A software engineering benchmark framework" (generic, boring)

### 2. PROBLEM (Read in 30 seconds)
```markdown
## The Challenge

What's broken? Why does it matter?

- Specific problem 1
- Specific problem 2
- Specific problem 3
```

**Rules:**
- 2-4 sentences max
- Use specific numbers/examples
- End with question that creates urgency
- Numbered list (not paragraphs)

**Example:**
"SWE-bench requires 90%+ model capability. Researchers thought bigger = better. But what if infrastructure beats scale?"

### 3. SOLUTION (Read in 15 seconds)
```markdown
## How It Works

Core insight + proof that it works

[Visual: Diagram or simple graphic]
```

**Rules:**
- One core insight (not five features)
- Provide visual if possible
- Link to proof (benchmarks below)
- 2-3 sentences max

**Example:**
"Stillwater implements 5 weapons: skills + orchestration + tools + context + structure. Result: llama 8B achieves 100% on Phase 1."

### 4. PROOF (Read in 30 seconds)
```markdown
## Benchmarks

| Metric | Result | Before |
|--------|--------|--------|
| Phase 1 | 100% | 0% |
| Phase 2 | 80%+ | 0% |
```

**Rules:**
- Numbers only (no words)
- Show before/after
- Include timeline if applicable
- Keep to max 3 metrics

### 5. QUICK START (Copy-paste ready, 2 min)
```markdown
## Get Started

### 1. Clone
\`\`\`bash
git clone <url>
cd stillwater
\`\`\`

### 2. Install
\`\`\`bash
pip install -e .
\`\`\`

### 3. Run Phase 1
\`\`\`bash
python3 test_1_instance_100pct.py
\`\`\`

### Expected Output
```
✅ Instance: django__django-14608
✅ Red test: FAIL (as expected)
✅ Green test: PASS (patch works)
✅ Verification: PASS
```

**Rules:**
- Copy-paste code (test it first!)
- Exact commands that work
- Show expected output
- Max 5 steps

### 6. FEATURES (3-5 core only)
```markdown
## What Makes It Special

- **Infrastructure-First**: Good design beats model size
- **Proven at Scale**: 100% on Phase 1, 80%+ on Phase 2
- **Reproducible**: All benchmarks verified independently
```

**Rules:**
- Max 3-5 features
- Each gets 1 sentence
- Put BENEFIT first, not tech
- Use icons/emojis sparingly

### 7. NEXT STEPS (Get deeper)
```markdown
## Learn More

- [How it Works](docs/architecture.md)
- [Run Phase 2](docs/phase-2.md)
- [Advanced Configuration](docs/config.md)

## Community

- Report issues: [GitHub Issues](link)
- Contribute: [Contributing Guide](CONTRIBUTING.md)
- Chat: [Discord](link)
```

---

## THE CHECKLIST (22 Points)

### STRUCTURE
- [ ] Hero section is 3 lines max
- [ ] Problem section is specific (not generic)
- [ ] Proof section has numbers/benchmarks
- [ ] Quick start code is tested & works
- [ ] Features list is 3-5 items max
- [ ] Navigation link at top for long READMEs

### CLARITY
- [ ] Title is benefit-focused
- [ ] Problem uses specific examples
- [ ] Solution is 2-3 sentences max
- [ ] Technical jargon explained or removed
- [ ] No more than 2 metaphors (usually too many)

### PROOF
- [ ] Benchmarks are shown vs. competitors/before
- [ ] Numbers are specific (not "much faster")
- [ ] Source of benchmarks is cited
- [ ] Timeline shown if applicable

### USABILITY
- [ ] Quick start is copy-paste ready
- [ ] All code examples are tested
- [ ] Expected output shown
- [ ] Troubleshooting section (if needed)
- [ ] Links to deeper docs work

### COMPLETENESS
- [ ] Project status clear (maintained, dormant, etc)
- [ ] License shown
- [ ] Author/contributors listed
- [ ] Ways to contribute explained
- [ ] Contact/support method provided

---

## README ANTI-PATTERNS (Don't Do This)

❌ **Wall of Text**: Paragraphs > 3 sentences
- FIX: Use lists, headers, white space

❌ **No Proof**: Claims without numbers
- FIX: Add benchmarks, comparisons, evidence

❌ **Generic Language**: "state-of-the-art", "leverages", "synergy"
- FIX: Use specific action verbs and concrete nouns

❌ **No Quick Start**: Or quick start that doesn't work
- FIX: Test every code example yourself first

❌ **Too Long**: README > 1-2 screens
- FIX: Move advanced content to /docs/

❌ **No Navigation**: Can't find anything
- FIX: Add table of contents at top

❌ **Outdated**: Information doesn't match current version
- FIX: Update every release

---

## FORMATTING RULES

### Headings (Scannable!)
```markdown
# PROJECT NAME (h1 - one per file)

## Main Sections (h2 - max 5-7)

### Sub-topics (h3 - only if needed)
```

### Emphasis
- **Bold** = key terms, benefits
- *Italic* = edge cases, asides
- `Code` = any code-like thing
- [Links](url) = always explicit text

### Lists
```markdown
- Use bullets for unordered items
- Separate with blank line if >2 per list
- Sub-bullets with 2-space indent
  - Like this
  - And this

1. Numbered for sequential steps
2. In exact order user should follow
3. Test that this order works
```

### Code Blocks
````markdown
```language
code here
```
````

---

## REVIEW QUESTIONS (Ask Yourself)

1. Can someone understand what this project does in 30 seconds?
2. Do we prove it works with numbers/benchmarks?
3. Can someone get it running in 2 minutes?
4. Is there a clear path to learn more?
5. Would I want to contribute to this project?
6. Is the writing clear enough for non-experts?
7. Are all code examples tested and working?
8. Is the project status clear (maintained/dormant)?

**If answer is NO to any, fix it before pushing.**

---

## WINNING README TEMPLATE

```markdown
# [Project Name]: [Benefit]

[Status badges]

## Problem
[What's broken + why it matters]

## Solution
[Core insight + proof]

## Benchmarks
[Numbers showing it works]

## Quick Start
[5-min copy-paste tutorial]

## Features
[3-5 core capabilities]

## Learn More
[Links to deeper docs]

## Contribute
[How to help]

## License
[License type]
```

---

**Auth**: 65537 | **Focus**: Documentation Excellence | **Standard**: Gold
