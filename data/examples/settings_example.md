---
api_key: sw_sk_a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6
firestore_project: stillwater-prod
firestore_enabled: true
sync_interval_seconds: 300
last_sync_timestamp: null
last_sync_status: pending
---

# Data Settings — Example (filled in)

This is what your `data/settings.md` should look like once you have set it up.
Replace the example `api_key` with the real key from your account.

## What each field means

**api_key** — Your personal key from solaceagi.com. Starts with `sw_sk_`
followed by 48 characters. Get yours at:
https://solaceagi.com/account/api-keys

**firestore_project** — Leave as `stillwater-prod` to use Stillwater's shared
cloud. Only change this if you are running your own self-hosted cloud backend.

**firestore_enabled** — Set to `true` to turn on automatic background sync.
Set to `false` if you want to sync only when you run the command manually
(or if you do not want cloud sync at all).

**sync_interval_seconds** — How often the background sync runs, in seconds.
300 means every 5 minutes. Minimum recommended: 60.

**last_sync_timestamp** and **last_sync_status** — Updated automatically after
each sync attempt. Do not edit these by hand. Check them by running:
`stillwater data sync status`

## Important reminders

- This file is gitignored — it will never be committed to GitHub
- Do not share this file or paste its contents anywhere
- If you think your key was seen by someone else, go to
  solaceagi.com/account/api-keys and rotate it immediately
