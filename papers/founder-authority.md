# Founder Profile: From Boat Refugee to Building the Verification Layer for AI

**Status:** Founder Authority Document
**Date:** 2026-02-21
**Author:** Stillwater Project
**Scope:** Establishing the biographical and professional foundation for the Stillwater and SolaceAGI ecosystem.

---

## 1. The Thread

Every significant system Phuc Truong has built shares a single organizing principle: the evidence must survive adversarial review.

Not "the evidence must exist." Not "the evidence must be plausible." Must survive adversarial review. Must hold up when an FDA auditor arrives without notice. Must hold up when a clinical site's data is subpoenaed. Must hold up when a skeptic is actively trying to find the flaw.

This is not a design philosophy that emerged from reading papers. It emerged from years of building software where the stakes of evidence failure are measured in failed drug approvals, patient safety events, and regulatory action. It emerged from watching what happens when a clinical trial's audit trail breaks down — and from building the system that prevented that from happening.

Stillwater and SolaceAGI are the application of that same principle to AI agents. LLM outputs are probabilistic. Agent actions are consequential. The gap between those two facts is the trust gap, and the verification OS is built to close it.

The thread runs from a boat off the coast of Vietnam in 1980 to a clinical trial platform serving 360+ customers to an open-source verification OS for AI. It is the same thread.

---

## 2. Background

**Born 1976, Vietnam.**

Phuc Truong was born in Vietnam in 1976. In 1980, at age four, his family escaped by boat. They arrived in America as refugees with nothing except the skills and work ethic they carried. The boat crossing — dangerous, uncertain, with no guarantee of safe harbor — is the first and deepest data point in a life characterized by building toward better conditions rather than accepting the constraints of present ones.

**Harvard University, A.B. Economics, Class of 1998.**

Phuc studied Economics at Harvard, graduating in 1998. The analytical discipline of economics — modeling incentive structures, identifying where systems fail, understanding that institutions are made of rules and rules can be redesigned — is visible in how Phuc builds software. OAuth3 is an incentive-compatible protocol. The rung system is a structured market for verifiable claims. The Stillwater Store is a governed ecosystem with reputation economics.

**Serial founder.**

After Harvard, Phuc built multiple companies. Most failed. The failures are part of the story — not something to hide:

- **UpDown.com** — a social investing platform with over 100,000 users. Early experiment in social-proof investing. Did not succeed commercially.
- **Citystream** and other ventures — failed. Each failure sharpened judgment about what matters: evidence over hope, architecture over hype, humility over narrative.
- **Clinical Research IO (CRIO)** — the one that worked. The defining company of Phuc's career. Founded 2015 with Raymond Nomizu. More on CRIO below.

Being transparent about failure builds more trust than a polished success narrative. The failures are the training data for CRIO and Stillwater.

---

## 3. Clinical Research IO (CRIO)

**Co-founded 2015 with Raymond Nomizu.**

CRIO was built to solve a specific, costly problem in clinical research: the paper gap. Clinical trials generate enormous amounts of source data — patient assessments, lab values, adverse events, consent signatures — and that data has historically been captured on paper, then manually transcribed into electronic systems. Every transcription is a potential error. Every paper form is a potential loss. Every gap in the chain of custody is a potential audit failure.

CRIO built the eSource platform: electronic capture of clinical trial data at the point of care, with a complete audit trail from the moment of capture. No transcription. No paper intermediary. The original electronic record is the source document.

**Outcomes at scale:**

- 360+ active customers: site networks, pharmaceutical companies, contract research organizations
- 40% higher patient enrollment at CRIO-powered sites
- 40% faster site startup
- 70% reduction in FDA audit risk
- Investors achieved exceptional returns

**What those numbers mean in practice:**

Faster site startup means that life-saving drugs reach patients faster. Higher enrollment means that trials reach statistical significance sooner, accelerating the evidence base for medical interventions. Reduced audit risk means that the data underlying drug approvals is more trustworthy. These are not abstract metrics. They represent real patients, real diseases, and real decisions about what treatments are safe and effective.

**The regulatory crucible.**

CRIO's customers operate under 21 CFR Part 11. Their records are subject to FDA inspection. Their data is the foundation for regulatory submissions worth hundreds of millions of dollars in development costs. In that context, "trust me" is not an acceptable answer to any question. Only the record speaks.

Phuc built and operated in that environment for years. The design decisions that resulted — timestamped everything, hash-chain the audit log, scope access to minimum necessary, store the original record and not a summary — are not theoretical preferences. They are lessons that cost real money and real effort to learn.

**The foundational insight:**

"In clinical trials, 'trust me' is not evidence. Only the original, timestamped, attributable record is evidence."

This sentence is the intellectual seed of Stillwater. Transplanted from clinical data to AI outputs, it becomes: LLM prose is not evidence. Only the original artifact, captured at execution time, with a hash-linked audit trail and attribution to the authorizing principal, is evidence.

---

## 4. Why This Background Matters for AI

The translation from clinical trials to AI verification is not metaphorical. It is architectural.

| Clinical Trials (CRIO) | AI Agent Verification (Stillwater) |
|---|---|
| FDA 21 CFR Part 11 (electronic records) | OAuth3 + rung system |
| ALCOA data integrity standard | Evidence bundles (Lane A / B / C) |
| Clinical trial phases (Phase I/II/III) | Verification rungs (641 / 274177 / 65537) |
| eSource: eliminates the paper-to-digital gap | Stillwater: eliminates the claim-to-evidence trust gap |
| GCP (Good Clinical Practice) | Software 5.0 Never-Worse doctrine |
| Audit trail must survive FDA inspection | Evidence bundle must survive adversarial skeptic review |
| Chain of custody from source to submission | Hash-chained AuditChain from token issuance to action |
| Principal investigator authorization | OAuth3 principal consent + scope gate |

Every design choice in Stillwater has a CRIO ancestor:

**FDA 21 CFR Part 11 becomes OAuth3.**
Part 11 requires that electronic signatures be uniquely attributable to the individual who signed, that the record includes the date and time of the signature, and that the meaning of the signature is captured. OAuth3's AgencyToken carries exactly this: `issuer`, `issued_at`, `scopes`, and an `intent` field that records the human-readable meaning of the delegation. The architecture is a direct translation.

**ALCOA data integrity becomes Lane A/B/C.**
ALCOA requires Attributable, Legible, Contemporaneous, Original, Accurate records. Stillwater's evidence lanes enforce exactly this hierarchy: Lane A requires an original executable artifact (test output, diff, benchmark result). Lane B is a secondary witness. Lane C is prose analysis — useful for interpretation, but never sufficient as a PASS claim. The clinical trial analogy is precise: you cannot submit a trial to the FDA with only a narrative summary of the data.

**Clinical trial phases become rungs.**
Phase I establishes basic safety in a small population. Phase II tests efficacy with more patients. Phase III is the large-scale, statistically powered confirmation. The three-rung verification ladder in Stillwater mirrors this structure exactly: Rung 641 (edge sanity, small-scale correctness), Rung 274177 (stress and adversarial testing, broader population of inputs), Rung 65537 (formal verification, production-grade proof). Each rung is a more demanding evidence standard, not just a higher threshold.

**GCP becomes Never-Worse doctrine.**
Good Clinical Practice is the international ethical and scientific quality standard for the design, conduct, and reporting of trials that involve the participation of human subjects. Its core principle is that the trial must be conducted in a way that protects the rights, safety, and well-being of subjects and that the data generated is credible. Stillwater's Never-Worse doctrine — no patch or change is accepted unless the system is at least as good as before, measured by passing tests — is the software equivalent.

---

## 5. The Vision

The arc of Phuc's career is a compounding argument for one idea: verification architecture is not a constraint on capable systems. It is the foundation of trustworthy ones.

CRIO proved this in clinical trials. A site that captures data in CRIO has a verifiable, auditable record. A site that relies on paper and transcription has hope and exposure. The sites using CRIO enroll more patients, start faster, and survive audits. The verification architecture is not the cost of operating in a regulated industry — it is the competitive advantage within that industry.

Stillwater and SolaceAGI are making the same argument for AI agents. An agent operating with OAuth3 tokens, PZip-archived browsing history, hash-linked audit logs, and rung-gated verification is not a constrained agent. It is a trustworthy one. Enterprise buyers, regulated industries, and sophisticated users will pay a premium for trustworthy over merely powerful.

"Stillwater was born from a boat, forged at Harvard, battle-tested in startups, now open-sourced for the world."

The goal is not to build a better chatbot. The goal is to make AI verification as foundational as clinical trial verification — a baseline expectation for any agent operating in consequential domains. OAuth3 is the GCP for AI agents. The rung system is the phase structure for AI verification. The evidence bundle is the electronic source document for AI actions.

When that infrastructure is in place, the question "did the AI agent do what it was supposed to do, and can you prove it?" has a definitive, auditable answer. That answer is what regulated industries need. It is what enterprise buyers will eventually require. And it is what the AI industry currently cannot provide.

Stillwater was built to provide it.

---

## 6. Credentials Summary

| Domain | Credential |
|---|---|
| Education | Harvard University, A.B. Economics, Class of 1998 |
| Founding track record | Multiple companies; most failed; CRIO is the one that worked |
| FDA regulatory experience | Clinical Research IO — 21 CFR Part 11 eSource platform, 360+ customers, live FDA audit environment |
| Robotics recognition | MIT AMD Robotics Innovation Challenge winner (Phuc Labs) |
| Open-source leadership | Stillwater v1.4.0 — verification OS for AI agents, open-sourced |
| Protocol authorship | OAuth3 — delegated agency authorization protocol for AI |
| Current focus | Building the verification OS and trust infrastructure for the next generation of AI agents |

---

## Appendix: The Dojo Parallel

Bruce Lee trained at a dojo before he understood what training meant. The dojo did not give him rules to follow. It gave him a discipline that became reflex — guard position, footwork, economy of motion — until the responses were automatic and the principles were embodied.

Stillwater is the dojo for AI agents. The skills are not rules that the agent memorizes and applies consciously. They are training that shapes how the agent reasons about every action: Is there evidence? Is the evidence original? Is the action scoped to what was authorized? Is the audit trail complete?

An agent trained in the Stillwater dojo does not ask "should I produce evidence?" any more than a trained fighter asks "should I keep my guard up?" The answer is already in the form.

The clinical trial experience is the proof that this model works. CRIO's sites did not have to remember to keep Part 11 records. The software made it automatic. The evidence was produced as a side effect of doing the work correctly, not as an afterthought.

That is what Part 11 Architected means. That is what Stillwater is building for AI.

---

**Auth: 65537**
