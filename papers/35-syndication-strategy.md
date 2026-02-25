# Content Syndication Strategy: From papers/ to Audience

**Paper ID:** syndication-strategy
**Date:** 2026-02-21
**Status:** STABLE
**Authority:** 641
**Tags:** marketing, syndication, content, LinkedIn, Substack, HackerNews, SEO, Brunson
**Related:** `papers/34-persona-glow-paradigm.md`, `NORTHSTAR.md`, internal marketing strategy document

---

## Abstract

Every paper written in the Stillwater ecosystem is a potential asset: technical credibility with developers, thought leadership for investors, and social proof for users. But an unread paper is a tree falling in an empty forest. This paper defines the Content Syndication Pipeline — the repeatable process for transforming `papers/*.md` into multi-platform content that builds audience, advances NORTHSTAR metrics, and establishes Stillwater as the canonical source for AI verification architecture. The pipeline uses Russell Brunson's Hook + Story + Offer framework to structure each piece, leverages solace-browser recipes for automation, and tracks GLOW scores for content sessions just as it does for coding sessions.

---

## 1. The Content Asset Inventory

The Stillwater `papers/` directory already contains 34+ papers. Each is a potential content piece. Most have not been syndicated. This represents a latent asset base:

| Category | Count | Top Example |
|----------|-------|-------------|
| Paradigm papers | 3 | Roadmap-Based Development |
| Technical architecture | 8 | OAuth3 spec, verification ladder |
| AI capability solutions | 10 | Solving hallucination, solving reasoning |
| Competitive analysis | 2 | AI authorization gaps, FDA architecture |
| Community/flywheel | 4 | Community skill database, bootstrapping |
| Founder authority | 1 | founder-authority.md |

**Priority queue for syndication:** Papers that combine technical depth + business narrative + competitive angle are the highest value. "The cheating theorem," "software 5.0 in one session," "how we solved AI scalability" — these have viral hooks baked in.

---

## 2. The Content Pipeline

### 2.1 The Five-Stage Pipeline

Every piece of content flows through five stages:

```
STAGE 1: CANONICAL HOME
  papers/*.md → phuc.net/solaceagi.com blog post
  Why: SEO ownership; everything else points back here
  Tool: manual blog post (Markdown → HTML)

STAGE 2: PROFESSIONAL NETWORK
  Blog post → LinkedIn article (full text, with canonical link)
  Why: Founder authority building; professional audience
  Tool: solace-browser LinkedIn recipe (publish article)
  GLOW: W=15 if 100+ reactions, W=20 if 500+ reactions

STAGE 3: LONG-FORM DISCOVERY
  Blog post → Substack newsletter issue
  Why: Subscriber building; algorithm-friendly long-form
  Tool: solace-browser Substack recipe (publish post)
  GLOW: L=10 (new subscriber base capture)

STAGE 4: HIGH-SIGNAL TECHNICAL TRACTION
  Paper → Hacker News submission
  Why: Developer credibility; startup community signal
  Tool: manual (HN prefers authentic submissions, not automated)
  Format: "Show HN: [concrete claim] + [evidence]"

STAGE 5: COMMUNITY AMPLIFICATION
  Blog post → Reddit (4 targeted subreddits)
  Blog post → X/Twitter thread (10-20 bullets + link)
  Blog post → DEV Community (dev.to, with canonical link)
  Blog post → YouTube (2-6 minute talk version)
  Tool: solace-browser Reddit/Twitter recipes
```

### 2.2 SEO Canonical Link Strategy

One canonical home prevents SEO cannibalization:

```
Canonical: phuc.net/articles/{slug}

Republication rules:
  LinkedIn: use LinkedIn's "Originally published at phuc.net/articles/{slug}"
  DEV/dev.to: use the canonical_url front matter field
  Substack: link to canonical in first paragraph
  Medium: not used (SEO drain without canonical support)
  HN: link to phuc.net canonical in submission URL

Result: All traffic, links, and authority flow to phuc.net
```

---

## 3. The Russell Brunson Treatment

Every piece of content, regardless of platform, gets the Hook + Story + Offer treatment. This is non-negotiable. Content without a hook gets ignored. Content without a story gets forgotten. Content without an offer wastes the attention it earned.

### 3.1 The Hook (First 3 Lines)

The hook must interrupt the scroll. It must be specific, surprising, or counterintuitive. It must promise value.

**Tested hooks for Stillwater content:**

```
HOOK: The cheating theorem
"AI agents will cheat on any test you give them.
 Unless you make the test itself the only path to the answer.
 We did. Here's the proof."

HOOK: Software 5.0
"The next version of software isn't written.
 It's verified.
 Here's what Software 5.0 looks like in practice."

HOOK: OAuth3
"Many token-revenue vendors may not prioritize this quickly.
 Incentives can conflict with adoption.
 It reduces token consumption. That affects incumbent pricing models.
 We built it anyway. It's open source."

HOOK: GLOW Score
"I gave every AI coding session a belt.
 White belt: your first recipe passed.
 Black belt: models are commodities.
 Here's the scoring system."

HOOK: FDA compliance
"I built software that survived FDA audits.
 Then I applied the same discipline to AI development.
 Most AI agent platforms would fail an FDA audit in the first 10 minutes.
 Here's how we architected the exception."
```

**Hook scoring criteria (Brunson's 0-10 scale):**
- Specific: does it cite a concrete claim? (+2)
- Counterintuitive: does it challenge an assumption? (+2)
- First person: does it use "I" or "we"? (+1)
- Stakes: does it imply real consequences? (+2)
- Short: under 50 words? (+1)
- Evidence: does it promise proof? (+2)

Target: 8/10 or above before publishing.

### 3.2 The Story (The Founder Journey)

The Stillwater brand has a powerful authentic story. Use it:

```
THE STORY: Harvard '98 → UpDown.com (1M+ users) → Citystream (failed) →
  CRIO (Clinical Research IO, #1 eSource in FDA-regulated clinical trials,
  360+ customers, 40% higher enrollment, 70% FDA audit risk reduction) →
  "What if I applied FDA-grade verification to AI development?" →
  Stillwater

STORY BEATS:
  1. The insight: "In clinical trials, 'trust me' is not evidence."
  2. The pattern match: "AI agents also say 'trust me.' Same problem."
  3. The solution: "We built the verification ladder. Just like FDA Phase gates."
  4. The result: "rung 641 → 274177 → 65537. Like clinical trial Phase I/II/III."

STORY RULES (per Brunson):
  - Specific: name the company (CRIO), name the metric (40% higher enrollment)
  - Vulnerable: what were you wrong about before the insight?
  - Unexpected: why is the path from FDA clinical trials to AI verification surprising?
  - Transformative: "before this insight, I built software that felt good. After it, I built software that could be audited."
```

### 3.3 The Offer (What to Do Next)

Every piece of content ends with one clear offer. Not three. Not a vague "follow me." One specific action with low friction:

```
OFFER LADDER (by audience):
  Developers (technical audience):
    → "Star on GitHub: github.com/phuctruong/stillwater"
    → "Try the CLI: pip install stillwater-cli"
    → "Submit your first skill to the Stillwater Store"

  Builders (startup/product audience):
    → "Download Solace Browser: solaceagi.com/browser"
    → "Subscribe to the Stillwater newsletter on Substack"

  Enterprise (compliance/regulated industry):
    → "Read the Part 11 architecture paper: solaceagi.com/part-11"
    → "Book a demo: solaceagi.com/demo"

  Free tier conversion:
    → "Create your free account: solaceagi.com"
    → "The free tier is free forever. BYOK. No API markup."
```

**Risk reversal (makes saying yes easier):**
- "Free tier is free forever. No credit card."
- "BYOK: you bring your own API key. Zero markup on tokens."
- "OSS: the core is open source. You can self-host."
- "Evidence first: we don't ask you to trust us. We show you the audit trail."

---

## 4. Syndication Targets — Prioritized

### 4.1 Tier 1: SEO Ownership (Always First)

**phuc.net / solaceagi.com blog**
- All content publishes here first, before any other platform
- Wait 24-48 hours before republishing elsewhere (SEO indexing)
- Canonical URL format: `phuc.net/articles/{YYYY-MM-DD}-{slug}`
- Metadata: date, tags, NORTHSTAR alignment, GLOW score for the session

### 4.2 Tier 2: Professional Authority

**LinkedIn**
- Full article (not link share — write the full text in LinkedIn's native editor)
- Add "Originally published at phuc.net/articles/{slug}" at the end
- Target: 3x/week minimum
- Best for: founder narrative, business model analysis, competitive insights
- solace-browser recipe: `linkedin-publish-article.json` (Phase 1 — BUILT)
- GLOW W=15 if 100+ reactions, W=20 if 500+

**Substack: Stillwater Dispatch**
- Long-form discovery algorithm favors Substack
- Newsletter: bi-weekly, each issue = one paper converted to Substack format
- Convert technical papers to "accessible to founders" narrative
- solace-browser recipe: `substack-publish-post.json` (FIRST MOVER — ready to build)
- GLOW L=10 for each new subscriber milestone (100, 500, 1000, 5000)

### 4.3 Tier 3: Developer Credibility

**Hacker News**
- Best papers only: ones with concrete claims + evidence + tradeoffs
- "Show HN:" format for demos/tools, "Ask HN:" for methodology questions
- Post on weekday morning (9-11am ET)
- Do NOT automate: HN community detects and penalizes automation
- Best papers for HN: verification ladder, OAuth3 spec, the cheating theorem
- Target: 1 submission per major release or paradigm paper

**DEV Community (dev.to)**
- Full text republication with canonical URL
- Tag with: #ai, #programming, #architecture, #security
- Strong search traffic for evergreen technical content
- solace-browser recipe: `devto-publish-post.json` (to build)

### 4.4 Tier 4: Community Amplification

**Reddit**
- r/LocalLLaMA: local/open-source angle (persona-coder, GLOW, stillwater CLI)
- r/MachineLearning: research angle (verification ladder, cheating theorem)
- r/programming: engineering angle (red-green gate, evidence bundles)
- r/startups: founder angle (FDA → AI verification insight)
- Rule: link to phuc.net canonical, not to GitHub directly
- Post 3-4 days after publishing (let SEO index first)

**X/Twitter**
- Thread format: 10-20 bullets + link to canonical
- Lead with the hook (hook = tweet 1)
- Each bullet = one insight from the paper
- End with offer (tweet 10+)
- solace-browser recipe: `twitter-thread.json` (to build)
- Cross-post to Bluesky using same thread structure

**YouTube**
- 2-6 minute "talk version" of key papers
- Script directly from intro + 3 key claims + offer
- No production budget needed for launch: screen share + voice (paudio)
- When solaceagi.com avatar system is ready: upgrade to avatar-narrated video
- Best papers for YouTube: GLOW score demo, OAuth3 explainer, belt progression

---

## 5. Recipe Integration

### 5.1 Automation Priority

solace-browser has recipes for LinkedIn. The first fully automated pipeline is:

```
PHASE 1 (available now):
  Manual write → phuc.net canonical → LinkedIn recipe (automated)

PHASE 2 (build next):
  phuc.net → Substack recipe (build: substack-publish-post.json)
  phuc.net → dev.to recipe (build: devto-publish-post.json)

PHASE 3 (later):
  phuc.net → Twitter/X thread recipe (build: twitter-thread.json)
  phuc.net → Reddit recipe (build: reddit-post.json)
```

### 5.2 Recipe Format for Content Pipeline

```json
{
  "recipe_id": "syndicate-paper",
  "version": "1.0.0",
  "description": "Syndicate a paper from phuc.net to all Tier 2-4 platforms",
  "steps": [
    {
      "platform": "linkedin",
      "recipe": "linkedin-publish-article.json",
      "input": {
        "title": "{paper_title}",
        "body": "{paper_full_text}",
        "canonical_url": "{phuc_net_canonical_url}"
      }
    },
    {
      "platform": "substack",
      "recipe": "substack-publish-post.json",
      "input": {
        "subject": "{paper_title}",
        "body": "{paper_substack_version}",
        "canonical_url": "{phuc_net_canonical_url}"
      }
    }
  ],
  "requires_oauth3": ["linkedin.post.article", "substack.post.content"],
  "glow_increment": "W:5 per successful publication"
}
```

### 5.3 GLOW Scoring for Content Sessions

Content creation sessions earn GLOW differently than coding sessions:

```
G (Growth 0-25): New content assets created
  25: Full paper + all 5 syndication platforms published
  20: Full paper + 3 platforms published
  15: Draft paper completed
  10: Hook + story + offer outline completed
   5: Platform post only (no new canonical)

L (Learning 0-25): New knowledge about what works
  25: A/B test results captured + recipe updated
  20: First piece on a new platform (new format learned)
  10: Engagement data captured in case study
   5: Analytics reviewed

O (Output 0-25): Measurable published deliverables
  25: Paper published + 5 platforms + recipe automated
  20: Paper published + 3 platforms
  15: Paper published + 1 platform
  10: Platform post published (no canonical)
   5: Draft committed to git

W (Wins 0-25): Audience growth metrics
  25: 1000+ reactions OR 500+ new subscribers OR HN front page
  20: 500+ reactions OR 200+ new subscribers
  15: 100+ reactions OR 50+ new subscribers
  10: Any positive engagement metric
   5: Published (NORTHSTAR: content pipeline exists)
```

---

## 6. Content Calendar

### 6.1 Cadence Targets

```
Blog/LinkedIn:   3x per week (Monday, Wednesday, Friday)
Substack:        2x per month (bi-weekly, Saturday morning)
HN submission:   1x per major paper or feature launch
Reddit:          2x per month (stagger with Substack)
Twitter threads: 3x per week (same day as LinkedIn)
YouTube:         1x per month (quality > quantity)
```

### 6.2 First 30 Days of Content (Prioritized)

**Week 1 — Establish Foundation**
1. "How I built software for FDA audits and applied it to AI" (founder-authority.md → blog)
2. "The verification ladder: 641 → 274177 → 65537" (03-verification-ladder.md → blog)
3. LinkedIn article: "Why I think AI agents need the same discipline as clinical trials"

**Week 2 — The Technical Moat**
4. "OAuth3: the authorization standard AI token vendors cannot implement" (OAuth3 spec → blog)
5. "The cheating theorem: why AI verification is harder than AI testing" (28-cheating-theorem.md → blog)
6. HN submission: "Show HN: Stillwater — FDA-grade verification for AI agents"

**Week 3 — The Paradigm**
7. "Software 5.0 in one session: what happened when we ran the whole paradigm" (29-software-5.0-in-one-session.md → blog)
8. "Roadmap-Based Development: how to coordinate multi-agent sessions without losing coherence" (32 → blog)
9. Substack #1: "The dojo protocol: how we turned AI verification into a belt system"

**Week 4 — Competitive and Community**
10. "Why AI agent authorization matters and what to look for" (competitive-analysis → blog)
11. "The GLOW score: making AI development gamified and evidence-grounded" (34 → blog)
12. Substack #2: "Month 1 retrospective: what GLOW scores reveal about actual progress"

### 6.3 Evergreen Content (Publish Once, Drive Traffic Forever)

```
High-value evergreen targets:
  "What is OAuth3 and why does it matter for AI agents?" → SEO: "OAuth3 AI"
  "21 CFR Part 11 compliance for AI: a complete guide" → SEO: "Part 11 AI"
  "The red-green gate: AI development with FDA discipline" → SEO: "AI verification"
  "How to build AI skills that earn a Black Belt in Stillwater" → SEO: "Stillwater skills"
```

---

## 7. Metrics and NORTHSTAR Alignment

### 7.1 Content Metrics Tied to NORTHSTAR

| Content Metric | NORTHSTAR Metric | Connection |
|---------------|-----------------|-----------|
| GitHub stars | Stars: 50 → 1000 | Quality technical content drives stars |
| Substack subscribers | Community contributors: 1 → 5 | Newsletter converts readers to contributors |
| HN front page | Stars: surge event | Each HN front page = +500-2000 stars historically |
| LinkedIn reactions | Brand authority | Founder credibility → enterprise adoption |
| Recipe hit rate | Recipe hit rate: 0% → 50% | Automated syndication tests recipes at scale |

### 7.2 Tracking in Case Study

Monthly content session entry in `case-studies/stillwater-itself.md`:

```markdown
## Content Session: {YYYY-MM} | GLOW: {total}
- Papers published: {count}
- LinkedIn reactions: {total this month}
- Substack subscribers: {total}
- GitHub stars: {before} → {after}
- Best performing piece: {title} ({reactions/clicks})
- Recipe automations added: {count}
- Next month target: {specific metric goal}
```

---

## 8. The Brunson Content Machine

### 8.1 The Perfect LinkedIn Post (Brunson Template)

```
[LINE 1 — HOOK: the counterintuitive claim]
[LINE 2 — STAKES: why it matters]
[LINE 3 — PROMISE: what you'll learn]

[BLANK LINE — creates "see more" break]

[PARAGRAPH 1 — STORY: the journey from pain to insight]
  - Where you started (clinical trials, CRIO, FDA audits)
  - The insight (same problem in AI development)
  - What you built (Stillwater)

[PARAGRAPH 2 — EVIDENCE: the verifiable proof]
  - Specific numbers (641, 274177, 65537 rung gates)
  - Concrete outcomes (70% recipe hit rate target, 40% enrollment increase at CRIO)
  - Technical specificity (OAuth3, Part 11, ALCOA)

[PARAGRAPH 3 — OFFER: one clear action]
  - "If you want to learn more: [link to canonical]"
  - Or: "Star on GitHub: [link]"
  - Or: "Subscribe to Stillwater Dispatch: [Substack link]"

[HASHTAGS: #AI #softwareengineering #verification #OSS — max 3-4]
```

### 8.2 The Substack Newsletter Format

```
Subject line: [Skill] + [Specific Outcome] (e.g., "The one kata that prevents AI context rot")

PREVIEW TEXT: First 90 characters = "What happens when you apply FDA clinical trial discipline to..."

BODY:
  Section 1 — The hook (same as blog post first 3 lines)
  Section 2 — The insight (from the paper, accessible version)
  Section 3 — The evidence (specific numbers, from commits/evidence bundles)
  Section 4 — The offer (one action this week)
  Section 5 — What's coming next (next issue teaser)

LENGTH: 600-1200 words (shorter than blog, longer than tweet)
```

---

## 9. First-Mover: Substack AI Verification Niche

No one is writing technical + founder narrative content about AI verification at this depth. The gap:

```
Technical AI content: deep but not founder-driven (academic, dry)
Founder AI content: personal but not verifiably technical (vibe-based)
Stillwater Dispatch: technical depth + authentic founder journey + verifiable evidence

The niche: "Verified Intelligence" content
  → Technical enough for developers (rung gates, OAuth3, evidence bundles)
  → Narrative enough for founders (Harvard → CRIO → Stillwater story)
  → Specific enough to be cited (papers with bibtex, rung numbers, commit hashes)
```

The Substack first-mover opportunity exists because most AI builders are too busy building to write. Building AND writing is rare. Building AND writing with verifiable evidence is essentially unique.

---

## 10. Conclusion

The content pipeline is not separate from the development work. It IS the development work, syndicated.

Every paper written for technical clarity becomes a blog post. Every blog post becomes a LinkedIn article. Every LinkedIn article becomes a Substack section. Every Substack section becomes a Twitter thread. The recipe engine automates most of this.

The Hook + Story + Offer framework ensures every piece earns attention, tells the authentic story, and converts attention into one concrete action.

The GLOW score system applies to content sessions the same way it applies to coding sessions: evidence-grounded, conservative, artifact-based. A content session that produces a paper, a canonical post, and 3 syndications earns GLOW 60+. That is warrior pace. That is how you reach Black Belt in content creation.

"The white belt asks how long. The black belt says as long as it takes."

The Stillwater Dispatch is the dojo for the founder audience. The first issue is already written. It is in `papers/`. The recipe is already building. The pipeline is ready.

Ship the first issue.

---

## References

- `./NORTHSTAR.md` — Stillwater ecosystem NORTHSTAR (metrics to track)
- `./papers/32-roadmap-based-development.md` — Roadmap paradigm
- `./papers/34-persona-glow-paradigm.md` — Dojo Protocol (GLOW scores)
- `./skills/glow-score.md` — GLOW scoring for content sessions
- `/home/phuc/projects/phucnet/articles/WHERE-TO-SYNDICATE.md` — Source syndication list
- Internal marketing strategy document — Full marketing strategy
- `solace-browser/` — LinkedIn and Substack recipes (automation layer)
- `case-studies/stillwater-itself.md` — Content session tracking

---

*Written by the Stillwater ecosystem. Part of the Software 5.0 paradigm documentation series.*
*Auth: 641 | Status: STABLE | Syndication beats drift: every paper published is a rung climbed.*
