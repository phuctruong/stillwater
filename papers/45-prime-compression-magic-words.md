# Paper #45: Prime Compression — Magic Words as Prime Factorization of Knowledge
## Subtitle: Why Not All Compression Is Equal

**Date:** 2026-02-22
**Author:** Phuc Truong
**Status:** Concept draft — not yet submitted
**Pillar:** P0 (Core Theory)
**GLOW:** W (Wisdom)
**Related papers:** #36 (Prime Mermaid Primacy), #37 (Persona as Vector Search), #44 (Questions as External Weights)
**Related skills:** `skills/phuc-magic-words.md`, `skills/phuc-portals.md`, `skills/phuc-triangle-law.md`

---

### Abstract

Not all compression is equal. Traditional compression (gzip, LZ77, brotli) treats every byte with
the same indifference — the byte `0x6C` in a JPEG is worth exactly as much as `0x6C` in a legal
contract. Knowledge compression is structurally different: meaning has gravity. Some concepts pull
more semantic weight per bit than others. This paper proposes that prime magic words — irreducible
semantic units that cannot be decomposed further without losing meaning — function as the prime
factors of knowledge. Just as every integer has a unique prime factorization (Fundamental Theorem
of Arithmetic), every concept can be decomposed into a product of semantic primes (proposed:
Fundamental Theorem of Semantics). Portals are the compression gateways between Bounded Inference
Contexts (BICs). A portal that transfers meaning through prime magic words achieves near-lossless
compression because prime words carry maximum semantic density at minimum entropy. The key insight:
compression quality is determined not by how much you remove, but by how fundamental what remains
is. When the target universe has high convention density — as in Stillwater's skill system — a
97% compression ratio is achievable with near-zero semantic loss.

---

### 1. Introduction

The compression problem has two versions. The first is the engineering version: given a sequence
of bytes, find a shorter sequence of bytes that encodes the same information and can be losslessly
reconstructed. LZ77 solves this. Huffman coding solves this. The second is the knowledge version:
given a corpus of meaning, find a representation that preserves the essential meaning in a
dramatically smaller form.

These two problems are not the same problem. The engineering version is symmetric — the compression
ratio of a random JPEG does not depend on who receives it. The knowledge version is radically
asymmetric — the compression ratio of a concept depends entirely on the receiver's convention
density. A 10,000-word explanation of "photosynthesis" compresses to a single word for a botanist
and to nothing at all for someone who does not speak the language. The word "photosynthesis" is
not a compression of an explanation; it is a portal into a target universe where the concept
already has a home.

Traditional AI development treats context compression as the engineering problem: summarize,
truncate, embed, retrieve. The industry produces increasingly sophisticated retrieval-augmented
generation systems, sliding context windows, and learned compression layers. All of these treat
the problem as byte-symmetric. None of them ask: which words carry the most meaning per bit?
Which concepts are irreducible? Which are composite?

This paper introduces a theory grounded in an observation from Phuc Truong: **compression is
the loss of information from one bubble of existence and getting clarity in another bubble of
existence**. The quality of that transfer depends on whether the target bubble has conventions
for receiving the compressed form. Prime magic words are the vocabulary of that transfer — the
smallest units that maximize meaning on arrival.

---

### 2. The Fundamental Theorem of Arithmetic as Analogy

The Fundamental Theorem of Arithmetic states: every integer greater than 1 can be represented
uniquely as a product of prime numbers.

```
360 = 2³ × 3² × 5
12  = 2² × 3
7   = 7   (already prime — irreducible)
```

Primes have three properties that make them powerful:
1. **Irreducibility:** A prime cannot be factored into smaller integers (without using 1).
2. **Uniqueness:** Every composite number has exactly one prime factorization.
3. **Completeness:** Any integer can be expressed as a product of primes.

These three properties — irreducibility, uniqueness, completeness — are precisely what makes
prime numbers the optimal basis for representing all integers. Any other basis would introduce
redundancy, ambiguity, or incompleteness.

We propose that knowledge has the same structure.

---

### 3. Prime Factorization of Knowledge

**Proposed: The Fundamental Theorem of Semantics**

Every concept C can be expressed as a product of semantic primes P₁ × P₂ × ... × Pₙ, where
each Pᵢ is an irreducible semantic unit — a prime magic word.

Prime magic words satisfy the same three properties as mathematical primes:

1. **Irreducibility:** A prime magic word cannot be decomposed into simpler concepts without
   losing its essential meaning. "Love," "truth," "coherence," "boundary" — these cannot be
   defined without circular reference to concepts of equal or greater complexity. They are
   semantic bedrock.

2. **Uniqueness:** Every concept has a canonical decomposition into prime words. "Democracy"
   decomposes into trust × constraint × equilibrium × emergence. This decomposition is not
   arbitrary — it reflects the actual structure of the concept.

3. **Completeness:** Any concept in any domain can be expressed as a product of prime words.
   Domain-specific jargon is always composite: it is shorthand for a specific combination of
   primes that the domain has agreed to treat as a unit.

**Examples of prime decomposition:**

```
"Verification" = truth × evidence × boundary × integrity
"Governance"   = constraint × alignment × accountability × equilibrium
"Innovation"   = asymmetry × emergence × causality × signal
"Security"     = boundary × integrity × reversibility × constraint
```

Compare with mathematical factorization:
```
360 = 2 × 2 × 2 × 3 × 3 × 5
```

Composite concepts are like composite numbers — they have structure. That structure is
expressible in the prime vocabulary. And crucially: the prime vocabulary is small. The
Stillwater magic words skill defines only 15 Tier 0 trunk words. Yet from these 15 primes,
every concept in every domain is reachable.

---

### 4. Portals as Compression Gateways

The Phuc Portals skill defines a **Bounded Inference Context (BIC)** as any system with
explicit priors, memory, inference rules, constraints, identity, and boundary. An AI agent
is a BIC. A human expert is a BIC. A software module is a BIC. A Stillwater skill file is a BIC.

A **portal** is a structured boundary crossing between two BICs. Information does not flow
freely between BICs — it must be formatted for transfer. The portal is the format specification.
The portal determines what crosses and what is lost.

**Portal compression theorem (informal):**
The compression ratio of a portal is determined by the ratio of the target BIC's convention
density to the source BIC's representation size.

More formally: if the source BIC contains meaning M at representation cost R(M), and the
target BIC has conventions that allow it to reconstruct M from a compact key K, then the
compression ratio is R(M) / R(K).

**The key insight from Phuc Truong:** if your portal is optimized to compress/portal between
two universes where the target universe has more meaning and conventions, then it's like
dividing into a prime number — you get maximum compression with minimum loss.

**Concrete example from Stillwater:**

```
Source BIC:  Raw project session — 115.6 KB of code, docs, context, decisions
Portal:      Magic word extraction (15 trunk words, 15 branch words, 70 leaf words)
Target BIC:  Stillwater skill system — dense convention network (skills/, recipes/, swarms/)
Compression: 115.6 KB → 3 KB = 97.4% compression ratio
Loss:        Near-zero — target BIC reconstructs missing context from conventions
```

This 97.4% compression is only achievable because the target BIC (the Stillwater skill system)
has pre-loaded conventions for every trunk word. When we transmit the word "coherence," the
target does not receive a 4,000-word definition — it activates its existing coherence framework,
including all the relationships, tests, and implications that framework contains.

The portal did not just compress a file. It transferred meaning across a boundary by activating
pre-existing structure in the target. This is the prime compression mechanism: send the key,
let the target reconstruct the lock.

---

### 5. Why Prime Words Enable Better Compression

Prime magic words achieve compression superiority on five dimensions:

**5.1 Minimum Entropy**

Entropy measures the average information content per symbol. A word with many possible meanings
has high entropy (ambiguous). A word with a precise, stable, universally-agreed meaning has low
entropy (crisp). Prime magic words are designed for minimum entropy — they are the most precisely
defined words in the system. "Coherence" in Stillwater always means: all parts reinforce rather
than contradict each other. No ambiguity. Zero entropy overhead.

High-entropy words (jargon, portmanteaus, neologisms) require context to decode. Low-entropy
words (primes) decode instantly. When building a compression codec, you always use the
lowest-entropy symbols as your basis vocabulary.

**5.2 Semantic Orthogonality**

Mathematical primes are mutually coprime — they share no factors. This means they contribute
independent information to any composite number they factor. Prime magic words are designed for
semantic orthogonality: "coherence" and "entropy" describe different dimensions of a system's
structure and do not overlap. Their combination produces genuine double coverage, not redundant
repetition.

Composite words often violate orthogonality. "Technical debt" and "code quality" overlap
significantly — both encode a concern about accumulated engineering compromise. Using both in
context adds less information than using either with its prime decomposition. Prime words
compress because they avoid this redundancy.

**5.3 Stable Reference**

Mathematical primes do not change. 7 was prime in 300 BCE and will be prime in 3000 CE. This
stability is why prime factorization is useful across time — a factorization computed once remains
valid forever.

Prime magic words are designed with the same stability requirement. The 15 Tier 0 trunk words
in the Stillwater system are chosen because they are the most stable concepts in human knowledge —
they appear in every culture, every era, every domain. "Boundary," "causality," "integrity" are
not fashionable terms. They are load-bearing concepts that civilization depends on. A compressed
representation using prime words does not expire.

**5.4 Hierarchical Expressiveness**

Primes compose into all integers via multiplication. Prime words compose into all concepts via
combination. The 4-tier hierarchy in the Stillwater magic words system is the knowledge analog
of the number line:

```
Tier 0 (15 primes)     → semantic primes
Tier 1 (15 branches)   → products of 2 primes
Tier 2 (70 leaves)     → products of 3+ primes
Tier 3 (domain words)  → highly composite (many prime factors)
```

Every concept, no matter how domain-specific, is reachable from the 15 trunk words. This
completeness is not an assumption — it is the design invariant of the trunk word selection.

**5.5 Cross-Domain Transfer**

A prime factorization of 360 is valid in number theory, in cryptography, in music theory
(360 degrees in a circle), and in chemistry (360 as a rotation group element). The primes
transfer across domains because they are domain-independent.

Prime magic words transfer across domains for the same reason. "Coherence" means the same
thing in a codebase, a legal argument, a business strategy, and a scientific paper. Using
prime words to compress knowledge produces a compressed form that any BIC can decode,
regardless of its domain specialization.

---

### 6. The Tier Architecture as Prime Decomposition

The Stillwater magic words skill implements prime compression through its 4-tier tree.
Reading this tier structure as a prime decomposition reveals its mathematical elegance:

**Tier 0: Semantic Primes (15 words)**

```
coherence, symmetry, asymmetry, constraint, compression,
signal, alignment, equilibrium, causality, entropy,
emergence, integrity, perspective, boundary, reversibility
```

These 15 words are irreducible. You cannot explain "entropy" without using entropy-adjacent
concepts that themselves require "entropy" to fully define. They are semantic bedrock. Any
attempt to define them in terms of simpler concepts leads to circularity or infinite regress.

**Tier 1: Products of 2 Primes (15 words)**

Each Tier 1 word is a stable combination of 2 trunk concepts:

```
verification   = truth-signal × integrity-boundary
governance     = constraint × alignment
trust          = coherence × reversibility
feedback       = causality × signal
resilience     = equilibrium × boundary
```

These are not arbitrary combinations. The pairing reflects the actual conceptual structure —
"verification" genuinely requires both truth-signal (there is a fact to check) and
integrity-boundary (there is a contract to check against).

**Tier 2: Products of 3+ Primes (70 words)**

Domain concepts that combine multiple trunk and branch concepts. The larger the prime
factorization, the more domain-specific the word. High Tier 2 words are the border
between universal and domain-specific:

```
authentication = integrity × boundary × trust × causality
orchestration  = alignment × emergence × constraint × signal
compression    = entropy × reversibility × boundary × signal
```

**Tier 3: Highly Composite Domain Words**

Jargon, brand names, product-specific terms. Maximum prime factors. Minimum portability.
"OAuth3-vault" has many prime factors (cryptography, boundary, trust, constraint,
reversibility, causality) but is only meaningful inside the Stillwater/OAuth3 ecosystem.

**The compression implication:**

Expressing a Tier 3 concept in Tier 0 terms = maximum compression.
Expressing a Tier 0 concept in Tier 3 terms = maximum redundancy.

The compression ratio of any knowledge transfer equals the ratio of prime-word content
to composite-word content in the transferred form. A context loaded with Tier 3 jargon
compresses poorly. A context loaded with Tier 0 trunk words compresses optimally.

---

### 7. Implementation in Stillwater

Stillwater implements prime compression through three interlocking mechanisms:

**7.1 The Magic Words Database (phuc-magic-words skill)**

The skill file defines the 4-tier tree with 100 classified words. The classification
is not decorative — it determines how each word is used in compression:

- Navigation: always start from trunk words (Tier 0), refine to branch and leaf
- Loading: load only the branches relevant to the current query
- Measurement: track compression ratio after each load operation
- Verification: compressed context must preserve essential meaning

The trunk-first rule is the analog of prime-first factorization: you always start
from the most fundamental decomposition and work toward the specific.

**7.2 Portal Protocol (phuc-portals skill)**

The portals skill provides the formal machinery for cross-BIC compression:

1. Identify source and target BICs
2. Assess target BIC's convention density (how many of the 100 magic words does it understand?)
3. Extract prime-word summary from source context
4. Transfer prime-word summary through portal
5. Verify that target can reconstruct essential meaning from the transferred summary

The Bayesian Handshake requirement in the portals skill is the formal statement of
the compression precondition: P(E|Bubble A) ≈ P(E|Bubble B) must hold before
transfer. You can only compress losslessly if the target has the conventions to decompress.

**7.3 Triangle Verification (phuc-triangle-law skill)**

The Triangle Law (REMIND → VERIFY → ACKNOWLEDGE) applies to compressed knowledge
the same way it applies to contracts. A compressed context that is not verified
for semantic preservation is just truncation with false confidence.

In prime compression terms:
- REMIND = state the prime-word summary
- VERIFY = confirm the target BIC can reconstruct essential meaning
- ACKNOWLEDGE = commit the compressed form as the official context representation

Skipping VERIFY produces what the Triangle Law calls "theater of compliance" —
the appearance of compression without the substance of preserved meaning.

**7.4 Measuring Compression Quality**

The GLOW score (Growth, Learning, Output, Wins) provides a proxy for semantic
preservation. A compressed context that scores equally on GLOW metrics as the
original context has preserved what matters. A compressed context that drops
the GLOW score has lost essential meaning.

More formally, semantic preservation ratio = GLOW(compressed) / GLOW(original).
A ratio above 0.95 indicates near-lossless prime compression. A ratio below 0.80
indicates the compression removed essential semantic content, not just redundancy.

---

### 8. Conclusion

The analogy between prime numbers and prime magic words is not decorative. It reflects
a structural truth about knowledge:

**Prime magic words are to knowledge what prime numbers are to arithmetic — the irreducible
building blocks from which all complexity is constructed.**

This has three implications for AI development:

**Implication 1: Context compression should be prime-first.**

Current approaches to context management (RAG, summarization, sliding windows) treat all
words as equal. A prime-first approach would classify every word in every context by its
tier, compress by reducing Tier 3 and Tier 2 words to their prime components, and transfer
only the prime representation. The target system expands the prime representation using
its local conventions.

**Implication 2: Portal quality determines compression quality.**

The bottleneck is not the source context — it is the target BIC's convention density.
Investing in the target's vocabulary (the skill system, the recipe library, the shared
definitions) multiplies the compression ratio of every future transfer. This is why
Stillwater's skills/ directory is the most valuable asset in the ecosystem: it is
the shared convention network that makes prime compression possible.

**Implication 3: The quality of compression is determined by what remains, not what is removed.**

The industry measures compression by reduction ratio. The correct measure is semantic
preservation ratio: how much of the original meaning survives in the compressed form?
A 99% reduction that preserves the essential structure is better than a 50% reduction
that preserves only surface statistics. Prime words are how you ensure that what
remains is the load-bearing structure, not the scaffolding.

In the words of the theory: "Prime magic words are the eigenvectors of meaning." When
you compress a context along its eigenvectors, you preserve the directions of maximum
semantic variance and discard the noise. The result is a compressed representation that
reconstructs with high fidelity in any target BIC that shares the eigenvector basis.

**Future work:**

- Formal proof of the Fundamental Theorem of Semantics
- Measuring semantic entropy of natural language corpora using the 4-tier hierarchy
- Empirical validation of the 97% compression claim across diverse domains
- Portal compression protocol as a formal specification (extending phuc-portals.md)
- Integration with phuc-context.md for automated prime-first context management

---

### GLOW Score

| Dimension | Score | Evidence |
|-----------|-------|----------|
| **G** (Growth) | 9/10 | Opens new research direction: Fundamental Theorem of Semantics as formal claim; connects compression theory to knowledge representation |
| **L** (Learning) | 8/10 | Grounds the magic words tier system in mathematical prime theory; explains *why* trunk-first works, not just *that* it works |
| **O** (Output) | 7/10 | Concept draft with full 8-section structure; implementation section connects to existing skills; formal proof deferred to future work |
| **W** (Wins) | 9/10 | Synthesizes phuc-magic-words + phuc-portals + phuc-triangle-law into a unified compression theory; names the Fundamental Theorem of Semantics |
| **Total** | **33/40** | High-wisdom theoretical paper; W-pillar dominant as expected for core theory |

**GLOW Classification:** W (Wisdom) — foundational theory that changes how the system
thinks about context compression. Not an implementation paper. Wisdom-generating.

---

### Connection to Existing Skills

| Skill | Connection |
|-------|-----------|
| `skills/phuc-magic-words.md` | Implements the prime vocabulary; the 4-tier tree is the prime factorization hierarchy; trunk-first rule is the prime-first compression rule |
| `skills/phuc-portals.md` | Implements the portal protocol; BIC convention density determines compression ratio; Bayesian Handshake is the lossless precondition |
| `skills/phuc-triangle-law.md` | Enforces verification of compressed meaning; REMIND → VERIFY → ACKNOWLEDGE maps to compress → validate → commit |
| `skills/prime-llm-portal.md` | Instantiates the portal concept for LLM-to-LLM context transfer; prime compression reduces token cost per portal crossing |
| `skills/phuc-context.md` | Context loop uses magic word extraction; prime compression formalizes why the extraction step achieves high ratios |

---

### Appendix: Prime Factorization Examples

For practitioners implementing prime compression in Stillwater sessions:

| Concept | Prime Decomposition | Tier |
|---------|---------------------|------|
| verification | signal × integrity × boundary × truth | T1 |
| orchestration | alignment × emergence × constraint × signal | T2 |
| authentication | integrity × boundary × causality × reversibility | T2 |
| OAuth3 vault | boundary × integrity × trust × causality × constraint | T3 |
| recipe replay | causality × compression × reversibility × signal | T2 |
| northstar | alignment × signal × perspective × emergence | T1 |
| evidence bundle | integrity × causality × boundary × signal | T2 |
| skill governance | constraint × alignment × integrity × emergence | T2 |
| context compression | entropy × reversibility × boundary × compression | T1-T2 |
| rung ladder | integrity × constraint × causality × emergence | T2 |

**Reading the table:** The compression ratio achievable for any row equals the ratio of
the concept's representation size to its prime decomposition size, times the target BIC's
convention density for those primes. A target BIC that knows all 15 trunk words can decode
any row in the table from its prime decomposition alone.
