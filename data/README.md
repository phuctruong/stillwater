# Stillwater Data — Your Personal AI Memory

> Think of this folder as a **filing cabinet with two drawers**.
> The first drawer came with the cabinet (factory templates). The second
> drawer is yours — you decide what goes in it, and nobody can take it away.

---

## Quick Start (1 minute)

### What is `data/`?

This is where Stillwater keeps everything it knows and remembers: jokes it
tells, goals it helps you pursue, and combinations of skills it uses to get
things done. You can personalize all of it.

```
data/
├── default/                  📁 Your defaults (tracked in git, read-only)
│   ├── identity.json         ← your name, email, social (edit in custom/)
│   ├── preferences.md        ← theme, sync, learning settings (edit in custom/)
│   ├── profile.md            ← your bio, projects, goals (edit in custom/)
│   ├── jokes.json            ← example jokes (edit in custom/)
│   ├── wishes.md             ← your goals/task categories (edit in custom/)
│   └── templates/            ← templates for new data files
│
├── custom/                   📁 Your overrides (gitignored, safe to edit)
│   ├── (created as you edit files from default/)
│   └── .gitkeep              ← keeps this directory in git
│
└── settings.md               🔑 API key + sync config (gitignored)
```

**Core Framework** (stays outside `data/`):
```
skills/                        ← Global skill definitions
recipes/                       ← Global recipes/tutorials
combos/                        ← Global skill combinations
```

### Where do my files go?

Always in `data/custom/`. That is your personal drawer. Nothing goes anywhere
else.

### Can I edit `data/default/`?

**No.** When you update Stillwater with `git pull`, the default folder gets
overwritten. Any edits you made there will disappear. Your `custom/` folder
is never touched by git updates — it is always safe.

> ✓ Safe: editing files in `data/custom/`
> ✗ Not safe: editing files in `data/default/`

---

## Adding Your First Joke (5 minutes)

Stillwater tells jokes during sessions. It comes with some built-in ones, but
you can add your own — jokes that make you smile, jokes your team uses, or
jokes that fit your context better.

### Step 1 — Copy the factory jokes into your drawer

Open your terminal in the stillwater folder and run:

```bash
cp data/default/jokes.json data/custom/jokes.json
```

That command makes a copy of the built-in jokes and puts it in your personal
drawer. The original in `default/` stays untouched.

### Step 2 — Open your copy and add a joke

Open `data/custom/jokes.json` in any text editor. You will see a list that
looks like this (shortened for clarity):

```json
[
  {
    "id": "joke_001",
    "joke": "Why do programmers prefer dark mode? Because light attracts bugs.",
    "tags": ["programming", "humor", "general"],
    "min_glow": 0.0,
    "max_glow": 0.4,
    "confidence": 0.85,
    "freshness_days": 90,
    "added_by": "stillwater-default",
    "added_at": "2026-02-23"
  }
]
```

Scroll to the very end of the file. Just before the closing `]`, add a comma
after the last joke's closing `}`, then paste your joke in the same shape:

```json
  {
    "id": "joke_mine_001",
    "joke": "I asked the AI to tell me a joke. It said: Have you heard the one about the chatbot who took a coffee break? It was unresponsive for 20 minutes.",
    "tags": ["ai", "humor", "general"],
    "min_glow": 0.0,
    "max_glow": 0.5,
    "confidence": 0.85,
    "freshness_days": 90,
    "added_by": "your-name",
    "added_at": "2026-02-23"
  }
```

### Step 3 — Save the file

Save `data/custom/jokes.json`. Stillwater will pick up your joke the next time
it starts (or you can run `stillwater data reload` to apply it immediately).

### What just happened?

When Stillwater looks for jokes, it checks your `custom/` drawer first. Since
your drawer now has `jokes.json`, it uses your version — which includes all
the factory jokes plus your new one.

Your joke stays on your machine and is never shared publicly unless you choose
to share it.

> 📁 See a ready-to-use example: `data/examples/custom_jokes_example.json`

---

## Creating Personal Wishes (5 minutes)

### What is a wish?

A **wish** is a task category — a way of telling Stillwater "when I ask for
help with this kind of work, here is what I want you to do." For example:

- "code review" → use the security-aware agent, check for best practices
- "write a blog post" → use the writer agent, keep it under 800 words
- "set up Docker" → use the devops agent, include a health check

Stillwater comes with a set of wishes for common tasks. You can add your own
for the specific things you work on every day.

### Step 1 — Create your wishes file

Create a new file at `data/custom/wishes.md`. (This file does not exist yet —
you are starting fresh.)

### Step 2 — Add your wish using this pattern

Here is an example for someone who does a lot of code reviews:

```markdown
---
id: wish-my-wishes-v1
format: mermaid-statechart
source: custom
added_at: 2026-02-23
description: My personal wishes — code review focus
---

` ` `mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : wish_received
    Processing --> Matched : skill_found
    Processing --> Blocked : no_match
    Matched --> Dispatched : agent_launched
    Dispatched --> Done : task_complete
    Blocked --> [*]
    Done --> [*]
` ` `

## Wish Entry

| wish_id | name | category | swarm | skill_pack_hint | confidence |
|---------|------|----------|-------|-----------------|------------|
| my-code-review | Code Review | quality | coder | coder+security | 0.90 |
| my-blog-post | Blog Post Writing | docs | writer | writer | 0.85 |
| my-docker-setup | Docker Setup | devops | coder | coder+devops | 0.88 |
```

(Remove the spaces inside the backtick fences — those were added here to avoid
rendering issues. The real file uses three backticks with no spaces.)

### Step 3 — Save and reload

Save `data/custom/wishes.md` and run:

```bash
stillwater data reload
```

Stillwater now knows about your wishes and will route matching requests to the
right agent automatically.

> 📁 See a ready-to-use example: `data/examples/custom_wishes_example.md`

---

## Personalizing Your Identity & Preferences

Stillwater comes with defaults for your identity, preferences, and profile. You can
customize all of these by creating files in `data/custom/`.

### identity.json — Who you are

Your identity includes your name, email, role, timezone, and social media handles.

**To customize:**
1. Copy `data/default/identity.json` to `data/custom/identity.json`
2. Edit your name, email, role, location, social media handles
3. Save and reload

**What goes in identity:**
- Your name, email, role (Developer, Designer, Manager, etc.)
- Your timezone and location
- Your bio (one-liner)
- Social media: Twitter, GitHub, LinkedIn handles

### preferences.md — How you work

Your preferences control sync behavior, theme, learning settings, and notifications.

**To customize:**
1. Copy `data/default/preferences.md` to `data/custom/preferences.md`
2. Edit settings you want to change (leave others at defaults)
3. Save and reload

**What goes in preferences:**
- **Display**: theme (dark/light), font size, line numbers
- **Sync**: auto-sync frequency (default: 5 minutes), conflict handling
- **Learning**: enable/disable pattern learning, confidence thresholds
- **Notifications**: which events trigger alerts

### profile.md — Your story

Your profile is your public-facing bio: your projects, goals, skills, and milestones.

**To customize:**
1. Copy `data/default/profile.md` to `data/custom/profile.md`
2. Write your bio, list your projects and goals
3. Save and reload

**What goes in profile:**
- About you: your interests and background
- Current projects: what you're working on now
- Goals & vision: where you're heading
- Skills: your expertise areas and proficiency levels
- Milestones: your achievements and history

---

## Core Framework Files (Read-Only)

These directories contain the global Stillwater framework. You do not edit these:

- **skills/** — Skill definitions (prime-safety, prime-coder, phuc-forecast, etc.)
- **recipes/** — Tutorials and recipes (bugfix, qa-audit, ci-triage, etc.)
- **combos/** — Skill combinations for common workflows (plan, run-test, etc.)

If you want to add custom recipes or combos, create them in `recipes/custom/` or
`combos/custom/` (these directories can be created in your fork).

---

## Getting Started with Cloud Sync

Cloud sync lets your personal data follow you to every machine. Your jokes,
wishes, and settings live in Stillwater's secure cloud. When you set up a new
computer, one command brings everything back.

Cloud sync is **optional** — Stillwater works fine without it. Everything stays
on your machine unless you set this up.

### Step 1 — Generate your API key

An API key is like a special password that lets Stillwater prove to the cloud
that sync requests are coming from you. You create it at solaceagi.com.

1. Go to **[solaceagi.com/account/api-keys](https://solaceagi.com/account/api-keys)**
2. Sign in with your account (Google or email)
3. Click the **"Generate New Key"** button — it is in the top-right area of the
   API Keys page
4. A key appears on screen, starting with `sw_sk_` followed by a long string
   of letters and numbers
5. Copy it now — **you will only see this key once**. If you miss it, you
   will need to generate a new one.

Keep your key somewhere safe (a password manager is ideal). Treat it like a
password — do not paste it into a chat window or email.

### Step 2 — Create your settings file

Copy the settings template to create your personal settings file:

```bash
cp data/settings.md.template data/settings.md
```

Open `data/settings.md` and fill in your key:

```yaml
---
api_key: sw_sk_a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6
cloud_sync: true
sync_interval_seconds: 300
last_sync_timestamp: null
last_sync_status: pending
---
```

Replace the example `sw_sk_a1b2...` value with your actual key. Set
`cloud_sync: true` to turn on automatic sync.

> 🔑 Your `data/settings.md` file is gitignored — it will never be uploaded
> to GitHub. Your API key stays private on your machine.

> 📁 See a filled-in example: `data/examples/settings_example.md`

### Step 3 — Push your data to the cloud

Run this command to send your `custom/` folder to your cloud account:

```bash
stillwater data sync push
```

Stillwater will confirm what it uploaded. The first push may take a moment if
you have many custom files. After that, sync is fast because it only sends
what changed.

### Step 4 — Check sync status

```bash
stillwater data sync status
```

This shows you:
- When your data was last synced
- Which files are in sync vs. which have local changes waiting to upload
- Any errors (for example, if your API key is wrong)

Once `cloud_sync: true` is set, Stillwater also syncs automatically in
the background every 5 minutes. You do not need to remember to push — it
happens on its own.

---

## Managing Multiple Machines

This is where cloud sync really pays off. Here is a real scenario:

**You have a laptop and a desktop. You add jokes on your laptop. You want them
on your desktop too.**

### On your laptop (where you added the jokes)

Your `data/custom/jokes.json` already exists. Sync happens automatically if
you have `cloud_sync: true`. To push immediately:

```bash
stillwater data sync push
```

### On your desktop (the new machine)

1. Make sure you have cloned the stillwater repo
2. Create `data/settings.md` with your API key (same key as your laptop)
3. Run:

```bash
stillwater data sync pull
```

Your `data/custom/` folder fills up with everything from your laptop — jokes,
wishes, any other files you created. Your desktop now has your personal setup.

### How the cloud works here

The cloud is a **mirror**, not a storage box. Think of it this way:

```
Laptop:  data/custom/jokes.json  ──► Cloud (mirror)
Desktop: data/custom/             ◄── Cloud (mirror)
         jokes.json appears here
```

The cloud never tries to be smarter than your local files. If you edit a file
on your desktop, that version wins when you push. If you want to go back to an
older version, that is what the cloud has for you to pull.

---

## FAQ

**Q: Can I lose my data if I run `git pull`?**

No. Git only updates `data/default/`. Your `data/custom/` folder is never
touched. Every file you put in `custom/` stays exactly as you left it after a
git update. This is by design and cannot change accidentally.

**Q: What if I accidentally edit a file in `data/default/`?**

Do not worry. The next `git pull` will restore `data/default/` to its original
state. Your edits in `data/custom/` are completely separate — they are not
affected. If you want to keep your edits, copy them to `data/custom/` before
running `git pull`.

**Q: How do I share my jokes with a friend?**

Copy your `data/custom/jokes.json` file and send it to them (email, Slack,
wherever). They paste it into their own `data/custom/jokes.json`. That is the
whole process — no accounts, no permissions, just a file.

**Q: What if I lose my API key?**

Generate a new one at [solaceagi.com/account/api-keys](https://solaceagi.com/account/api-keys).
Then update your `data/settings.md` with the new key. Once you have confirmed
the new key works (run `stillwater data sync status`), revoke the old key on
the same page so it cannot be used by anyone who might have it.

**Q: Why does sync sometimes not update right away?**

Sync runs in the background every 5 minutes. If you added a file and want it
in the cloud immediately, run `stillwater data sync push`. Changes do not
disappear — they are queued and will upload on the next cycle. Check where
things stand with `stillwater data sync status`.

**Q: Do I need cloud sync to use Stillwater?**

No. Stillwater works fully offline. Cloud sync is an optional extra for people
who use multiple machines or want a backup. If you never set up `data/settings.md`,
nothing changes — your local data is still there and Stillwater uses it normally.

**Q: What data actually gets synced?**

Only the files in your `data/custom/` folder. Your `data/settings.md` (which
contains your API key) is never synced — it stays on your machine only.
The `data/default/` folder is never synced either — it comes from git.

---

## Troubleshooting

### Problem: I edited a file in `data/default/` and my changes disappeared

This happens after `git pull`. The default folder is managed by git and gets
refreshed on every update.

**Solution:** Copy your edited file to `data/custom/` and edit it there.
For example:

```bash
cp data/default/jokes.json data/custom/jokes.json
# now edit data/custom/jokes.json — your changes will persist
```

### Problem: Sync says "unauthorized"

Your API key may be wrong, expired, or revoked.

**Solution:** Open `data/settings.md` and check your `api_key` value. Make
sure it starts with `sw_sk_` and was copied correctly (no extra spaces, no
missing characters). If the key looks right but sync still fails, generate a
new key at [solaceagi.com/account/api-keys](https://solaceagi.com/account/api-keys)
and update `data/settings.md`.

### Problem: I cannot find the API key button on solaceagi.com

**Solution:** Log in, then go to: Account → Settings → API Keys. The button
labeled "Generate New Key" is near the top of that page. If you are having
trouble, see the help article at
[solaceagi.com/help/api-keys](https://solaceagi.com/help/api-keys).

### Problem: My custom file is not being used

Stillwater may have cached the old version.

**Solution:** First confirm your file is in `data/custom/` and not in
`data/default/`. Then run:

```bash
stillwater data reload
```

This tells Stillwater to re-read all data files without restarting.

### Problem: I ran `stillwater data sync pull` but my files are not there

**Solution:** Check that you are logged in with the same account you used when
you pushed. Run `stillwater data sync status` — it shows which account your
key belongs to and when the last sync happened. If the account is wrong,
update `api_key` in `data/settings.md` to the correct key.

---

## Advanced

This section is for people who want to go deeper. You can skip it entirely and
Stillwater will work just fine.

### Where `data/default/` comes from

The files in `data/default/` are part of the stillwater GitHub repository.
When you run `git pull`, git downloads the latest versions and puts them in
that folder. This is how Stillwater ships new jokes, wishes, and skill
combinations to everyone who uses it.

### Contributing your jokes back to the project

If you write jokes that you think other Stillwater users would enjoy, you can
contribute them to the official defaults. Here is how:

1. Fork the [stillwater repository on GitHub](https://github.com/stillwater-oss/stillwater)
2. Add your jokes to `data/default/jokes.json` in your fork
3. Open a Pull Request with the title "feat: add jokes to default set"
4. The maintainers will review and merge if the jokes fit the tone

Your name goes in the `"added_by"` field — that is how the project credits
contributors.

### Adding a new file type to `data/custom/`

The three built-in file types are `jokes.json`, `wishes.md`, and
`combos.mermaid`. If you want to experiment with a new format, create a file
in `data/custom/` with any name. Stillwater will not break — it only reads
file types it recognizes and ignores others.

### Self-hosting cloud sync

If you want to run your own cloud backend instead of using solaceagi.com, set
the cloud API URL in `data/settings.md` to your own server.
See the [self-hosting guide](https://github.com/stillwater-oss/stillwater/blob/main/docs/self-hosting.md)
for the full setup.

---

## Quick Reference

```
data/ layout
├── default/    ← git-managed (never edit directly)
├── custom/     ← yours (always safe across git updates)
└── settings.md ← your API key + sync settings (gitignored)

Safe commands
  stillwater data reload          ← reload files without restarting
  stillwater data sync push       ← upload custom/ to cloud
  stillwater data sync pull       ← download custom/ from cloud
  stillwater data sync status     ← show sync state and last timestamp

First-time setup
  cp data/default/jokes.json data/custom/jokes.json
  cp data/settings.md.template data/settings.md
  # edit data/settings.md — add your API key
  stillwater data sync push

Key management — at solaceagi.com/account/api-keys
  Generate New Key  ← creates a fresh key (one-time display, copy it)
  Rotate            ← swap old key for a new one (old stops working instantly)
  Revoke            ← permanently disable a key (use when retiring a machine)
```

---

*Questions? Open an issue at
[github.com/stillwater-oss/stillwater](https://github.com/stillwater-oss/stillwater)
or check the help center at
[solaceagi.com/help](https://solaceagi.com/help).*
