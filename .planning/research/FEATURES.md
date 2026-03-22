# Feature Landscape

**Domain:** Automated daily English learning content pipeline (B1-B2 reading + exercises)
**Researched:** 2026-03-22
**Confidence note:** Web search unavailable. Analysis derived from project context, CEFR framework standards, and established language acquisition research (Krashen i+1 hypothesis, Nation's vocabulary learning principles).

---

## Table Stakes

Features users expect from a daily language learning content system. Missing any of these makes the output feel incomplete or unusable.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Real article content (not AI-generated text) | Authentic input is the foundation of acquisition — learners need exposure to how native speakers actually write | Low | VOA/BBC RSS are purpose-built for this; fetch + parse is straightforward |
| Correct B1-B2 level calibration | Content that is too hard or too easy produces no learning — learners abandon it immediately | Medium | VOA Special English is already calibrated for this level by design; filtering still needed |
| Vocabulary highlights (5-10 words) | Nation's research: targeted vocabulary in context is more effective than glossaries; learners expect this from any reading lesson | Low-Medium | Claude API prompt; key is selecting words at the right difficulty (not too basic, not too obscure) |
| Definitions in plain English | Definitions must themselves be at B1 level or below — circular complexity defeats the purpose | Low | Prompt engineering concern, not architectural |
| Comprehension questions (3-5 questions) | Standard expectation for any reading exercise since 1970s — without this it is a text dump, not a lesson | Low-Medium | Claude API prompt; mix of literal and inferential questions is the expected standard |
| Answer key included | Without answers the exercise has no closure — the learner cannot self-check | Low | Part of the same Claude API call as questions |
| Consistent daily availability | The whole value proposition is "it just works every day" — one missed day erodes trust | Medium | GitHub Actions scheduling + error handling + fallback logic |
| Idempotent output (no duplicate days) | Running twice on same day must not produce duplicate files — this is a CI correctness property | Low | File existence check before commit |
| Graceful source failure handling | RSS feeds go down; if the script crashes silently, the learner notices a gap with no explanation | Medium | Retry logic, fallback source, or skip-with-log |
| Readable Markdown output | Content must be legible in GitHub file browser, any Markdown viewer, and plain text — no special renderer required | Low | Pure Markdown, no frontmatter complexity |

---

## Differentiators

Features that go beyond the baseline and create real competitive advantage for a personal daily pipeline.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Example sentences for vocabulary in article context | Most vocabulary tools give generic examples; showing the word used in the same article the learner just read creates stronger memory encoding (contextual binding) | Medium | Requires Claude to reference specific article text, not generic usage |
| Explicit B1-B2 word classification label | Telling the learner "this is a B2 word" gives them a mental model of their own progress boundary — few free tools do this | Medium | Claude can classify against CEFR wordlists; accuracy is approximate but directionally useful |
| Inferential comprehension questions (not just factual) | Factual questions ("What did the article say about X?") require only memory. Inferential questions ("Why might the author have emphasized X?") develop actual reading skill. Most generators default to factual only | Medium | Prompt engineering: explicitly require at least one inferential question |
| Consistent Markdown structure enabling grep/search | Because output is files in git, a learner can `grep` for vocabulary across weeks — this is a compound benefit that grows over time and most SaaS tools cannot offer | Low | Template discipline: use consistent heading names |
| Source attribution with URL | Learner can read the original article, see how it was edited for learners, and explore related content — this connects the learning material to the real world | Low | Include source URL in file header |
| Article topic tagging | Over time a learner can filter by topic domain (science, politics, culture) — useful once there are 30+ files | Medium | Single line of metadata; Claude can classify topic from article text |
| Vocabulary reuse detection (skip already-taught words) | After 90 days, the same high-frequency words will keep appearing; de-prioritizing already-seen vocabulary and surfacing new ones improves coverage | High | Requires reading prior files or maintaining a seen-words list in state.json — adds significant complexity |

---

## Anti-Features

Features to explicitly NOT build in this system. These would add complexity without proportional learning value, or would violate the design constraints.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Interactive quizzes or fill-in-the-blank | Requires a runtime, a UI, or a bot — incompatible with static Markdown output constraint; also significant scope creep | Keep exercises as plain Markdown; reader completes them mentally or on paper |
| Spaced repetition scheduling | Duolingo-level infrastructure; requires user state per vocabulary item, a review engine, and session management — this system has none of that | Accept that some repetition happens naturally; vocabulary reuse detection (above) is the lightweight substitute if ever needed |
| Multiple articles per day | More content does not mean more learning — B1-B2 learners benefit from depth over breadth; one article worked deeply is better than three skimmed | Hard limit: one article per day |
| Audio/TTS generation | Adds API cost, binary assets in git (bad for repository health), and platform complexity — text-only is a virtue here | Out of scope for v1; if ever added, it belongs in a separate repository or CDN |
| AI-generated "article" content | AI-written text lacks the authentic pragmatic features that make real language learning work (idioms, register shifts, cultural references) | Always fetch from a real source (VOA, BBC, Guardian) |
| User accounts or progress dashboards | This is a personal git repository — adding a web layer would eliminate the entire simplicity advantage | The git log is the progress dashboard |
| Grammar exercises (fill-blank, correction) | Requires knowing the learner's specific grammar gaps; generated grammar exercises without personalization are low-value | Focus on reading comprehension and vocabulary, which are universally applicable at B1-B2 |
| Push notification for new content | Already explicitly out of scope per PROJECT.md — the existing notification system handles daily reminders; content is discovered by opening the repo | The learner reads files directly |

---

## Feature Dependencies

```
Source fetch (RSS/API)
  └─→ Level filtering (B1-B2 calibration)
        └─→ Claude API call (vocabulary + questions + answers)
              └─→ Markdown assembly
                    └─→ Git commit (content/YYYY-MM-DD.md)

Idempotency check ─────────────────────────────→ blocks Git commit if file exists

Graceful failure handling ──→ wraps Source fetch + Claude API call
```

---

## MVP Recommendation

Prioritize (in order):

1. **Source fetch + level calibration** — VOA Special English RSS; no filtering needed beyond selecting the day's top article since VOA is already B1-B2 calibrated
2. **Claude API: vocabulary highlights** — 5-8 words, plain-English definition, example from article text
3. **Claude API: comprehension questions** — 3-5 questions (at least one inferential), with answers
4. **Markdown assembly + git commit** — consistent template, source URL in header, date-named file
5. **Idempotency + graceful failure** — skip if file exists; log and exit non-zero on fetch/API failure

Defer:
- **Article topic tagging** — adds one line of metadata but requires an extra classification prompt or a second Claude call; defer until core pipeline is stable
- **B1-B2 word classification labels** — useful differentiator but accuracy depends on CEFR wordlist access; defer to avoid scope creep
- **Vocabulary reuse detection** — High complexity, Low early value (no vocabulary history in first 30 days anyway); revisit at Week 8+

---

## Sources

- Analysis derived from: CEFR framework (Council of Europe), Nation (2001) "Learning Vocabulary in Another Language", Krashen comprehensible input hypothesis
- Project constraints from: `/Users/andrew/study-all/.planning/PROJECT.md`
- VOA Learning English design rationale: publicly documented as targeting B1-B2 non-native speakers
- Confidence: MEDIUM — core feature categories are well-grounded in SLA research; specific prioritization reflects project constraints and tradeoffs that are subjective
