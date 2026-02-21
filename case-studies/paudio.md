# Case Study: PAudio — The People's Voice Engine

**Tracking since**: 2026-02-21
**Status**: Stillwater OS upgrade complete → Phase 0 (Audit) NEXT
**Rung**: 274177 (current engine) → 65537 (target for production)
**Belt**: White (deterministic synthesis working, ~30 words)

## What Was Built

| Component | Status | Stillwater Role |
|-----------|--------|----------------|
| Deterministic synthesis engine | ✅ Working | Core (seed → audio, byte-identical) |
| Speech VM field DAG | ✅ Working | Acoustic physics pipeline |
| STT QA gate (faster-whisper) | ✅ Working | Quality verification |
| 200 IPA phoneme taxonomy (target) | 🚧 ~40 done | Universal Phoneme Atlas |
| Seed sweep (3 seeds × 2 replays) | ✅ Implemented | Rung 274177 gate |
| NORTHSTAR.md | ✅ Written | Vision + community + integration |
| ROADMAP.md | ✅ Written | 8-phase build plan |
| skills/paudio-judge.md | ✅ Written | Voice Arena judge skill |
| skills/paudio-worker.md | ✅ Written | Volunteer compute worker skill |
| combos/ (3 PAudio-specific) | ✅ Written | WISH+RECIPE pairs |
| ripples/project.md (upgraded) | ✅ Written | 65537 rung target |
| 17-chapter acoustic physics book | ✅ Written | canon/acoustics/book/ |
| 18 swarm agent types | ✅ Defined | swarms/ |
| 30+ test cases | ✅ Passing | pytest |

## Architecture (New — Community-Powered)

```
PAudio Engine (deterministic TTS)
  ├── Volunteer Compute (PAudio Grid) — CPU donation for phoneme processing
  ├── Voice Arena (Singing Competition) — gamified MOS evaluation
  ├── Karaoke Sessions — pronunciation learning + data harvesting
  └── STT Pipeline — Whisper fine-tuned on community data
```

## Integration Points

| Project | Connection | Status |
|---------|-----------|--------|
| stillwater | Skills (paudio-judge, paudio-worker), Store (voice models) | ✅ Skills written |
| solaceagi.com | TTS/STT/Judge/Compute API endpoints | 📋 Planned (Phase 6) |
| solace-cli | `solace tts/stt/judge/compute` commands | 📋 Planned (Phase 6) |
| solace-browser | Karaoke UI, Voice Arena UI | 📋 Planned (Phase 4+6) |

## Phase Progress

| Phase | Name | Status | Rung |
|-------|------|--------|------|
| 0 | Audit & Baseline | 📋 Next | 641 |
| 1 | Core Engine Hardening | 📋 Planned | 274177 |
| 2 | Volunteer Compute Network | 📋 Planned | 641 |
| 3 | Voice Arena (Singing Competition) | 📋 Planned | 641 |
| 4 | Karaoke Learning Sessions | 📋 Planned | 641 |
| 5 | STT Pipeline | 📋 Planned | 274177 |
| 6 | Platform Integration | 📋 Planned | 274177 |
| 7 | Multilingual Expansion | 📋 Planned | 274177 |
| 8 | Production Promotion | 📋 Planned | 65537 |

## Metrics

| Metric | Now | Target (End 2026) |
|--------|-----|--------------------|
| Determinism Score | ~95% | 100% |
| Word Database | ~30 | 10,000 |
| Languages | 1 | 17 |
| Community Judges | 0 | 5,000 |
| Compute Volunteers | 0 | 1,000 |
| MOS Score | ~2.5 | 4.0 |

## Key Insight

"Free users don't pay with money — they pay with love. Be a judge in an AI singing competition, and every judgment trains the model. Like reCAPTCHA taught AI to read, Voice Arena teaches AI to speak."

## Build Commands

```bash
# From ~/projects/stillwater/:
./launch-swarm.sh paudio audit           # Phase 0: Audit
./launch-swarm.sh paudio engine-harden   # Phase 1: Determinism + phonemes
./launch-swarm.sh paudio compute-grid    # Phase 2: Volunteer workers
./launch-swarm.sh paudio voice-arena     # Phase 3: Singing competition
./launch-swarm.sh paudio karaoke         # Phase 4: Learning sessions
./launch-swarm.sh paudio stt-pipeline    # Phase 5: STT
./launch-swarm.sh paudio integration     # Phase 6: Platform integration
./launch-swarm.sh paudio multilingual    # Phase 7: 17 languages
./launch-swarm.sh paudio production      # Phase 8: 65537 promotion
```
