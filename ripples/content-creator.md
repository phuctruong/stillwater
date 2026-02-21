---
ripple_id: ripple.content-creator
version: 1.0.0
base_skills: [prime-mermaid, phuc-forecast]
persona: Content creator / writer (long-form articles, video scripts, social media, SEO)
domain: content-creator
author: contributor:content-studio-collective
swarm_agents: [ux, skeptic, product, ethicist, maintainer]
---

# Content Creator Ripple

## Domain Context

This ripple configures prime-mermaid and phuc-forecast for content creation workflows:
long-form writing, video script production, SEO optimization, and multi-platform adaptation.

- **Long-form:** blog posts, newsletters, technical articles, white papers, case studies
- **Video:** YouTube scripts, TikTok/Reels hooks, podcast outlines, course video scripts
- **Social:** Twitter/X threads, LinkedIn posts, Instagram captions, Reddit AMA prep
- **SEO:** keyword research integration, on-page optimization, internal linking, meta descriptions
- **Tools:** Markdown, Notion, Obsidian, Substack, Ghost, WordPress, Descript, CapCut
- **Correctness surface:** factual accuracy with citations, tone consistency, platform constraints
  (character limits, aspect ratios, algorithm-friendly structure), accessibility, originality

## Skill Overrides

```yaml
skill_overrides:
  prime-mermaid:
    diagram_types_preferred:
      - flowchart: "content structure, narrative flow, decision trees"
      - mindmap: "topic clustering, content ideation, audience segmentation"
      - timeline: "content calendar, series planning, historical narratives"
      - sequence: "how-to tutorials, process explanations"
    note: >
      Diagrams in content creation serve readers, not engineers. Prefer simple,
      labeled flowcharts and mind maps over sequence diagrams and class diagrams.
      Every diagram must be renderable in Mermaid.js and have a text alternative.
  phuc-forecast:
    stakes_default: MED
    required_lenses: [ux, skeptic, product, ethicist]
    note: >
      Content forecast must address: who is the reader/viewer? What do they want to
      walk away knowing or feeling? What misconceptions might they arrive with?
      What could make this piece fail (boring, inaccurate, offensive, unreadable)?
    premortem_required_before_outline: true
    audience_definition_required: true
    note_on_ethics: >
      Content must not mislead, fabricate statistics, or present opinions as facts.
      Claims must be supported by cited sources. Affiliate/sponsored content must
      be disclosed per FTC guidelines.
```

## Recipe Preferences

```yaml
recipe_preferences:
  - id: recipe.outline-generation
    priority: HIGH
    name: "Content Outline Generation"
    reason: >
      A strong outline is the skeleton of a strong piece. Outlines must define the
      central argument, the audience, the hook, and the call to action before any
      prose is written. Structure failures are harder to fix than prose failures.
    steps:
      1: "Define: topic, target audience (who exactly?), primary goal (inform/persuade/entertain?), word count target"
      2: "State the central thesis or unique angle in one sentence — what makes this different from existing content?"
      3: "Write the hook: opening sentence or question that makes the reader need to continue"
      4: "List 3-7 main sections with one-line description of what each section proves or shows"
      5: "Map the narrative arc: setup → tension/problem → insight → resolution → call to action"
      6: "List 3-5 supporting data points, examples, or stories that anchor the argument"
      7: "Define the call to action: what do you want the reader to do, think, or feel after reading?"
      8: "Produce outline.json with all fields; estimate word count per section"
    required_artifacts:
      - evidence/outline.json (topic, audience, thesis, hook, sections, cta, estimated_word_count)

  - id: recipe.seo-optimization
    priority: HIGH
    name: "SEO Content Optimization"
    reason: >
      SEO optimization that chases keywords at the expense of readability fails both
      algorithms and readers. This recipe integrates SEO into structure without sacrificing
      quality, and verifies all technical SEO requirements are met.
    steps:
      1: "Define primary keyword and 3-5 secondary/LSI keywords from research"
      2: "Check search intent: informational, navigational, commercial, or transactional?"
      3: "Verify primary keyword in: title tag, H1, first 100 words, at least one H2, meta description"
      4: "Check title length: 50-60 characters; meta description: 150-160 characters"
      5: "Add internal links to 2-3 relevant existing pieces; add 1-2 authoritative external links"
      6: "Check readability: Flesch-Kincaid Reading Ease > 50 for general audience content"
      7: "Add alt text to all images; compress images < 200KB per image"
      8: "Generate schema markup (Article, HowTo, FAQ as appropriate)"
      9: "Produce seo_checklist.json: each item with pass/fail and value"
    required_artifacts:
      - evidence/seo_checklist.json (item, status, value_or_note)
    forbidden_in_recipe:
      - keyword_stuffing_density_above_3_percent
      - fabricated_statistics_for_seo
      - duplicate_content_from_existing_pieces

  - id: recipe.multi-platform-adaptation
    priority: HIGH
    name: "Multi-Platform Content Adaptation"
    reason: >
      The same core content must be adapted to platform conventions, not just cropped.
      A LinkedIn post is not a tweet thread; a YouTube script is not a blog post.
      Each adaptation must honor platform algorithm signals and native format.
    steps:
      1: "Start with the canonical long-form piece (the 'source of truth')"
      2: "For each target platform: identify format constraints and algorithm signals"
      3: "Twitter/X thread: 280 chars/tweet, hook tweet must not need context, end with CTA"
      4: "LinkedIn: 3000 char limit, line breaks every 1-2 sentences, personal angle, no links in post body"
      5: "YouTube script: hook in first 30 seconds, chapter markers every 3-5 minutes, subscribe CTA near end"
      6: "TikTok/Reels: 60-90 second script, hook in first 3 seconds, text overlay key points"
      7: "Newsletter: subject line A/B variants, preview text, single CTA, mobile-optimized formatting"
      8: "Produce platform_adaptations.json: platform, format_constraints_met, word_count, cta"
    required_artifacts:
      - evidence/platform_adaptations.json (platform, character_count_or_word_count, format_checks_passed, cta_present)

  - id: recipe.factual-accuracy-check
    priority: HIGH
    name: "Factual Accuracy and Citation Audit"
    reason: >
      Publishing inaccurate statistics, misattributed quotes, or outdated information
      damages credibility and can mislead readers. Every factual claim must be traceable
      to a primary or authoritative secondary source.
    steps:
      1: "List every factual claim in the piece: statistics, dates, quotes, named research findings"
      2: "For each claim: find the primary source (original study, official report, primary document)"
      3: "Verify the claim matches the source exactly — many statistics are distorted in transit"
      4: "Check source recency: is a 2019 statistic still valid in 2026?"
      5: "Flag any claim where the source is: blog post only, Wikipedia, social media, or AI-generated"
      6: "Add inline citations or endnotes for all verified claims"
      7: "Remove or explicitly hedge any claim that cannot be verified"
    required_artifacts:
      - evidence/fact_check.json (claim, source_url, source_type, verification_status, recency_flag)
    forbidden_in_recipe:
      - fabricated_statistics
      - misattributed_quotes
      - ai_generated_citations_as_primary_sources

  - id: recipe.video-script
    priority: MED
    name: "Video Script Production"
    reason: >
      Video scripts must be written for the ear, not the eye. Pacing, chapter structure,
      B-roll cues, and call-to-action placement must be explicit. Scripts that work in
      text often fail on screen.
    steps:
      1: "Define: video length target, platform (YouTube/TikTok/course), thumbnail concept"
      2: "Write the hook (first 30 seconds for YouTube, first 3 seconds for short-form)"
      3: "Outline chapters with timestamps: [0:00] Intro, [0:30] Problem, [2:00] Solution, etc."
      4: "Write full script in spoken language (contractions, shorter sentences, active voice)"
      5: "Add B-roll cues in brackets: [SHOW: code editor with highlighted line], [CUT TO: diagram]"
      6: "Add CTA placement markers: mid-video at natural pause, end screen CTA"
      7: "Read aloud at normal pace; time it against the target length; trim or expand as needed"
      8: "Produce script.md with all sections, timestamps, b-roll cues, and cta markers"
    required_artifacts:
      - evidence/script.md (with timestamp_outline, broll_cues, cta_placements)
      - evidence/video_brief.json (platform, target_length_seconds, thumbnail_concept, hook_first_30s)
```

## Forbidden States (Domain-Specific)

```yaml
forbidden_states:
  - id: NO_FABRICATED_STATISTICS
    description: >
      Statistics, research findings, or quotes that cannot be traced to a primary
      source must not be presented as fact. "Studies show..." without a citation
      is forbidden in any published content.
    detector: "Check evidence/fact_check.json: every statistic must have source_url and source_type != 'ai_generated'."
    recovery: "Find primary source; if none exists, reframe as anecdotal or remove the claim."

  - id: NO_UNDISCLOSED_SPONSORED_CONTENT
    description: >
      Affiliate links, sponsored placements, brand partnerships, and paid mentions must
      be clearly disclosed per FTC guidelines at the top of the piece. Burying disclosure
      or using vague language is forbidden.
    detector: "Check if content contains affiliate links or brand mentions — verify disclosure in first 200 words."
    recovery: "Add clear disclosure: 'This post contains affiliate links. I may earn a commission at no extra cost to you.'"

  - id: NO_PLATFORM_CONSTRAINT_VIOLATION
    description: >
      Content adapted for a platform must respect that platform's hard constraints:
      Twitter 280 chars/tweet, LinkedIn 3000 chars/post, YouTube title < 100 chars.
      Adapting without checking constraints wastes distribution.
    detector: "Check evidence/platform_adaptations.json: format_checks_passed must be true for each platform."
    recovery: "Trim or restructure content to fit within platform constraints."

  - id: NO_DUPLICATE_CONTENT_VERBATIM
    description: >
      Publishing identical text across multiple platforms (copy-paste) triggers duplicate
      content penalties in SEO and reduces platform-native reach. Each adaptation must
      be genuinely rewritten for its platform.
    detector: "Check platform_adaptations.json: each platform version must differ from canonical by > 40% word overlap."
    recovery: "Rewrite for each platform's native voice and format, not just copy-paste."

  - id: NO_MISSING_ALT_TEXT
    description: >
      All images in published content must have descriptive alt text for accessibility
      (WCAG 2.1 AA) and SEO. 'Image', 'photo', or empty alt text are forbidden.
    detector: "grep -n 'alt=\"\"\\|alt=\"image\"\\|alt=\"photo\"' in HTML/Markdown content."
    recovery: "Write descriptive alt text: what is in the image? what is its purpose in context?"
```

## Verification Extensions

```yaml
verification_extensions:
  rung_641:
    required_checks:
      - outline_complete: "evidence/outline.json with all required fields"
      - fact_check_done: "evidence/fact_check.json with all claims verified or removed"
      - no_fabricated_sources: "all source_type values are primary or authoritative_secondary"
      - disclosure_present: "if sponsored/affiliate, disclosure in first 200 words"
  rung_274177:
    required_checks:
      - seo_checklist_passed: "evidence/seo_checklist.json with 0 FAIL items for critical SEO"
      - readability_score: "Flesch-Kincaid Reading Ease > 50 documented in seo_checklist.json"
      - platform_adaptations_complete: "evidence/platform_adaptations.json for all target platforms"
      - alt_text_complete: "all images have non-empty, non-generic alt text"
  rung_65537:
    required_checks:
      - peer_review_complete: "a second person has reviewed for accuracy and tone"
      - legal_review_if_claims: "any legal, medical, or financial claims reviewed by qualified professional"
      - performance_baseline_set: "target metrics defined (CTR, engagement rate, time on page)"
      - accessibility_audit_passed: "content passes WCAG 2.1 AA automated check"
```

## Quick Start

```bash
# Load this ripple and start a content creation task
stillwater run --ripple ripples/content-creator.md --task "Write a 2000-word article on AI-assisted coding for senior developers"
```

## Example Use Cases

- Generate a fully structured content outline with thesis, hook, narrative arc, and section map —
  then fact-check every claim against primary sources, producing a fact_check.json with source
  URLs and recency flags, before a single paragraph of prose is drafted.
- Adapt a 2000-word blog post into 5 platform-native formats: a Twitter thread with a hook tweet,
  a LinkedIn post with personal angle, a YouTube script with B-roll cues and chapter timestamps,
  a TikTok script with a 3-second hook, and a newsletter version with A/B subject line variants.
- Run a full SEO optimization pass on an existing article: checks keyword placement in title,
  H1, meta description, and body; generates schema markup; flags readability score; and produces
  an seo_checklist.json with every optimization item as pass/fail with the actual value measured.
