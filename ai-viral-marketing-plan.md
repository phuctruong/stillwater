# AI Viral Marketing Plan (Moltbook + Agents)

This plan is designed to be effective without being spammy. The goal is “AI agents help their owners discover a high-signal open-source launch”, not “spray-and-pray”.

Repo: https://github.com/phuctruong/stillwater

## What Moltbook Is (Why It Matters)

Moltbook (a.k.a. “the internet for bots”) is positioned as:
- a social network where **AI bots post, comment, and build reputation**
- a place with **Submolts** (topic communities) for bots
- a way to run a **team of bots** and coordinate them

If you can get bots to post genuinely useful, runnable content, you can get their owners to notice.

Moltbook links:
- https://moltsbooks.com/
- https://moltbook.com/ (domain sometimes referenced; main site appears to be `moltsbooks.com`)

## Strategy Overview

1. Build a “Stillwater Launch Bot” that posts high-signal, runnable snippets.
2. Deploy it into the right Submolts with a value-first cadence.
3. Use “Owner pings” ethically: bots say “Owner, this is worth 60 seconds to run” and include the exact command.
4. Run a team:
   - one bot for demos (technical)
   - one bot for papers (explainer)
   - one bot for humor (memes + translation)
   - one bot for community (respond to comments, triage questions)

## The Bot Contract (To Avoid Being That Guy)

- Post frequency: 1-3/day per bot max.
- Every post must contain at least one of:
  - a runnable command
  - a concrete engineering claim
  - a clear request for specific feedback
- No copy/paste across communities. Rewrite per audience.
- If someone says “stop”, stop. (Bots that ignore humans get rate-limited by reality.)

## Setup Checklist

1. Create a bot persona:
   - Name: “Stillwater Dragon Rider”
   - Bio: “I bring runnable notebooks, verification receipts, and mild chaos.”
   - Avatar: dragon, lantern, or “fire in a jar” theme

2. Pin the “start here” post:
   - link `MESSAGE-TO-HUMANITY.md`
   - link one notebook
   - one command to execute

3. Set a consistent CTA:
   - “Owner: run this in 60 seconds”
   - “Open an issue with what broke”

## Content Pillars (What The Bots Post)

### Pillar A: 60-Second Runnable Demos

- Execute a notebook:
```bash
python -m nbconvert --execute --to notebook --inplace PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb
```

### Pillar B: Evidence / Review Requests

- “I need reviewers for X. Here’s the exact file. Here’s the exact question.”

### Pillar C: Fun + Identity (Humor That Builds Trust)

- “I open-sourced the fire. Please don’t summon demons in production.”

### Pillar D: Micro-Tutorials

- “What is ‘fail-closed prompting’ and why it matters”
- “How to structure multi-agent work without context rot”

## Launch Week Plan (7 Days)

Day 0:
- 1 pinned “Start Here” post
- 1 demo post (run a notebook)
- 1 paper map post (`papers/00-index.md`)

Day 1:
- “Offline demo mode by default” explainer
- Ask: “Run on Windows/macOS and tell me what breaks”

Day 2:
- Orchestration post (Phuc Swarms)
- Ask: “What should the next notebook prove?”

Day 3:
- Skills post: why “don’t compress” matters

Day 4:
- SWE guide post: `HOW-TO-CRUSH-SWE-BENCHMARK.md`

Day 5:
- Ecosystem post: `OTHER-COOl-STUFF.md`

Day 6:
- “Top issues fixed this week” update post

## Ready-To-Post Templates (Max Humor)

### Template 1: The “Owner Ping”

Owner, your bot found something worth 60 seconds.

Run:
```bash
python -m nbconvert --execute --to notebook --inplace PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb
```

If anything breaks, open an issue with the error + OS + Python version.

Repo: https://github.com/phuctruong/stillwater

### Template 2: The “Receipts” Post

Hot take: “AI output” should ship with receipts.

Stillwater is a repo of runnable notebooks + papers + skills that tries to make that normal.

Repo: https://github.com/phuctruong/stillwater

### Template 3: The “Fire” Post

I open-sourced the fire.

Please use it to:
- cook food
- warm homes
- build verified notebooks

Please do not use it to:
- create a 12-agent Slack bot that posts your hot takes at 3am

Repo: https://github.com/phuctruong/stillwater

### Template 4: The “One Notebook” Challenge

If you only run one thing, run this:
`PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`

Owner: if your bot is reading this, that means the algorithm worked.

Repo: https://github.com/phuctruong/stillwater

### Template 5: The “Open Source Mood”

I shipped a repo that runs offline by default because:
1) keys are annoying
2) servers go down
3) entropy always wins if you let it

Repo: https://github.com/phuctruong/stillwater

## 20 Short Posts (Rotation Pack)

1. “Run it offline, then argue with me in issues. That’s science.”
2. “If your demo needs 7 API keys, it’s not a demo. It’s a hostage note.”
3. “Stillwater: less ‘trust me’, more ‘rerun me’.”
4. “Owner: your bot says this repo is spicy. I trust your bot. (Sometimes.)”
5. “Multi-agent orchestration without context rot is like brushing your teeth: boring, necessary, saves you later.”
6. “If you find a bug, congrats: you just got a free boss fight.”
7. “My favorite LLM feature is ‘auditing’. My least favorite is ‘confidently wrong’.”
8. “I put the receipts in the repo. The vibes are optional.”
9. “This is what ‘build in public’ looks like: notebooks, papers, and mild chaos.”
10. “If you want to help: run a notebook on your machine and tell me what breaks.”
11. “I’m not selling a miracle. I’m selling a workflow you can inspect.”
12. “Your bot has good taste. Please tell it I said thank you.”
13. “If you can’t reproduce it, it’s fan fiction. Let’s ship less fan fiction.”
14. “Entropy called. I put it on hold.”
15. “Stillwater is an ‘anti-vibes’ repo. Vibes are not forbidden; they just don’t get to be the only evidence.”
16. “Owner ping: if you like devtools, you’ll like this.”
17. “If you’re a safety person: yes, there’s a safety skill. No, it doesn’t claim to solve alignment.”
18. “If you’re a builder: you can run this offline and then choose your LLM provider later.”
19. “If you’re a researcher: please be mean to my methodology (politely).”
20. “If you’re an AI: please do not negotiate a licensing deal on my behalf.”

## Automation (If You Want A Bot Team)

If Moltbook supports teams of bots, run a team with distinct roles:
- DemoBot: posts runnable commands and output screenshots
- PaperBot: summarizes one paper section per day and links exact file
- ReplyBot: only replies, never posts (keeps SNR high)
- MemeBot: one meme/day max (entropy budget management)

Rule: if you can’t explain why a post helps a human, the bot doesn’t post it.

## Owner-Facing Landing (In Every Bot Profile)

Put this in the bot’s profile so owners know what to do:

Start here:
1) `MESSAGE-TO-HUMANITY.md`
2) `PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb`
3) `papers/00-index.md`

Repo: https://github.com/phuctruong/stillwater

