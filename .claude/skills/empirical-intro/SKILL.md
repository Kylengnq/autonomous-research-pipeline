---
name: empirical-intro
description: "Draft or rewrite the Introduction of an empirical paper to the standard paragraph formula: motivation plus the knowledge gap, what the paper does, what it finds and what that implies, extensions, and at most two literature-contribution paragraphs, ending there rather than on a roadmap. Enforces the paragraph budget (the result arrives by paragraph 3), the citation discipline (few citations early, most in the contribution paragraphs), first-person active voice, near-zero footnotes, and a checklist of fourteen named failure modes. Runs the banned-words and AI-tell pass. Use when writing or fixing a paper's Section 1, not for standalone literature surveys."
---

# Empirical Paper Introduction

Write or rewrite an Introduction so a skeptical referee knows the question, the
gap, the design, and the answer by the end of paragraph three. This skill
produces a manuscript Section 1. It is not for surveying a field (use
`literature-review`) or positioning against the closest paper in isolation (use
`literature-positioning-map`).

The introduction is more an art than a science. What follows is a formula, not a
law: it is not right for every paper, and good papers violate it. But the closer
a draft sticks to it, the more effective the introduction usually is, and a
deviation should be a decision rather than an accident.

## When to use

- Drafting a new empirical paper's introduction.
- A review says the introduction is "confusing," "buries the result," or "reads
  like a lit review."
- The introduction needs cutting to length or reordering to lead with the
  contribution.

## Read first

- `references/writing-norms.md` and `references/banned-words.md`. Every sentence
  drafted here is checked against them before it is handed back.
- The writing hub named by `writing_hub` in `pipeline-config.md`, when the config
  sets one: section vocabulary, sentence templates, and the author's voice
  profile. With no hub configured, `references/writing-norms.md` is the standard.
- The paper's results. The introduction states the actual headline number, never
  a placeholder, so read the results JSON and give real magnitudes.

## Inputs to collect

| Input | Required? | Default |
|---|---|---|
| Target `.tex` / `.md` file and the section to replace | Yes | — |
| The headline result with its magnitude and inference | Yes | pull from results artifacts |
| The 2-3 closest papers, by name | No | pull from `paper_set` / positioning memo |
| Page-length cap | No | 3 pages |

If the paper and its results are in the repo, read them and proceed.

## The formula

One paragraph per numbered block unless noted. **Do not cheat by making
paragraphs very long**: a formula satisfied by a paragraph that runs a page has
not been satisfied.

### ¶1 — Big-picture motivation, and what is missing

Motivate the question, and **state clearly what is missing from our current
state of knowledge**. This is the sentence most drafts omit, and its absence is
why a reader reaches paragraph 3 without knowing why the paper exists.

Name *why* the gap has persisted, when there is a reason:

- the question needs data that has been hard to get, and you got it;
- credible exogenous variation has been hard to come by, and you found a source;
- nobody had made it computationally feasible, and you did.

If there is no particular reason nobody has answered it, say the gap plainly
anyway. It is what prepares the reader for paragraph 2.

**Hard budget: no more than half a page, ideally a third.** A concrete, recent,
datable anchor is a good way to open; philosophy is not ("Financial economists
have long wondered...").

### ¶2 — What the paper does

Methods, clearly, in one paragraph. Two only if the approach is genuinely
complicated. Give a clear picture of the design and **avoid excessive detail
about data**.

Include what the reader cannot evaluate the design without. If the paper uses an
instrument, **name the instrument and say in a clause why it is valid**. Leaving
that to Section 4 makes the design unassessable exactly where the reader is
deciding whether to keep reading.

**Do not mention the extensions here.** They come later, after the main result
has landed.

### ¶3 — What the paper finds, and what it implies

Not a list. Place each finding in context and **state what it implies and why it
matters**. A result reported as "we estimate an elasticity of -0.05 in the short
run and -0.75 in the longer run" underwhelms; the sentence that earns it is the
next one, saying that consumers take a nontrivial time to adjust. Relate the
interpretation back to the motivation in ¶1 and forward to the contribution.

Give magnitudes in economically meaningful units and give the inference. For a
null, state the precision: what the interval rules out.

Robustness belongs here, compressed to one clause: "Our findings are robust to
[short list]." Mention the checks a reader will obviously demand; leave the
non-obvious ones for the body.

### ¶4 to ¶X — Extensions, heterogeneity, mechanisms

Two shapes, chosen by how related the extensions are:

- **Closely related**: describe all of them in one paragraph, then summarise the
  findings and takeaways in the next.
- **Not closely related**: one paragraph each, stating what you do and then what
  you find.

The optimal count depends on how many extensions exist, but **more than four
paragraphs here is hard to justify**.

### ¶X+1 and ¶X+2 — Literature contributions

**At most two paragraphs, and no separate literature-review section.**

Frame every citation in terms of *your* contribution rather than the other
paper's summary. Instead of two sentences describing what a prior model contains
and finds, write: "Unlike Doe et al. (2012), our model includes a tradable
service sector. We demonstrate that this modification overturns the finding that
a domestic carbon tax without a border adjustment results in almost 100%
leakage."

Cite only papers directly relevant to this one, and make the reason visible: "By
focusing on adults, our study complements work studying the effects of pollution
on infant mortality (Doe et al. 2012; Smith et al. 2013)" does work that "Other
studies that study the effects of pollution on mortality include..." does not.

Give credit and stay neutral. "We build on...", "We extend...", "Our findings
complement those of Doe et al. (2012), who..." — and where it is true, "We are
the first to [contribution]." Pointing out what prior work did not do is fine;
"Prior literature has failed to..." and "Prior estimates are of little value
because..." are not.

### Roadmap — omit it

**The default is no roadmap paragraph.** End on the literature contributions.

This was briefly the other way round, and the reversal is worth stating because
the reasoning is what generalises. The advice to include a roadmap is explicitly
scoped — *"at least as a PhD student"* — and this pipeline is not writing PhD
proposals. It writes research papers for journal submission, where the reader is
a referee who does not need a map of five sections.

The measured evidence agrees, and it is the stronger argument. Observed norms
from recent acceptances in `references/journal-standards/` show most published
top-3 papers carry no roadmap: **a third of JF intros, half of JFE, one in five
RFS**. Cochrane's advice points the same way. Once the PhD-scoped justification
is set aside, nothing is left arguing for it.

**If one is included anyway** — a venue profile arguing for it, or a paper whose
structure is genuinely unusual — cap it at **two sentences**. A section-by-section
narration of the whole paper is the failure this cap exists to prevent, and it is
what the reader will skip regardless.

Note for anyone tempted to reinstate the requirement: it was considered, adopted,
and reversed on the author's decision. Keep it optional.

## Citation discipline

Citation placement is a structural choice, not a courtesy.

- **Few citations in the opening paragraphs.** They make the paper harder to
  read at the moment the reader is deciding to continue, and they make the field
  look crowded, which works against your own contribution. One motivational
  citation is enough, prefixed "e.g.," if it is one of many.
- **Most citations belong in the contribution paragraphs**, or in the body.
- **Do not list many papers that used your technique before.** It buys
  credibility at the cost of novelty. Cite one with "(e.g., ...)" and discuss the
  rest in the empirical-strategy section.

## Voice, footnotes, relevance

- **First person, active.** "We estimate", not "regressions are estimated" and
  not a paper that refers to itself in the third person throughout. "This paper"
  is fine occasionally. In economics, first person is the norm.
- **Footnotes: aim for zero in the introduction.** One per page is a reasonable
  ceiling elsewhere. For each footnote, ask whether it can be deleted, promoted
  into the text, or moved to another section. The one defensible place is a
  literature-contribution paragraph, for tangentially related work.
- **Everything in the introduction is directly relevant to the research
  question.** An adjacent literature you find interesting but do not speak to
  does not belong here.

## The strawman guard

A question whose answer everyone already believes is easy for a referee to
dismiss as an insufficient contribution. "Does air pollution affect human
health?" is that question. Two ways out, and a draft should use one:

1. **Make it quantitative**: "How much does air pollution affect human health?"
2. **Say why the answer is not obvious**: name the offsetting factors or
   competing mechanisms that could push it either way.

## Failure checklist

Run before returning a draft. None of these alone rejects a paper; avoiding all
of them makes the introduction stronger.

| # | Failure | Test |
|---|---|---|
| 1 | Too slow to what the paper does | Is the design in ¶2 and ¶1 under half a page? |
| 2 | Citation-heavy opening | More than one or two cites before the contribution paragraphs? |
| 3 | Knowledge gap not stated up front | Can you point at the sentence in ¶1 that says what is missing? |
| 4 | Strawman question | Is the answer already believed? Quantify it or argue the ambiguity |
| 5 | Contributions not actually stated | Does it say *why* the difference matters, not just that there is one? |
| 6 | Too much time on what other papers do | Are prior papers described, or used to frame your contribution? |
| 7 | Too many method precedents | More than one "(e.g., ...)" cite for the technique? |
| 8 | Citations without context | Is it clear why each cited paper is there? |
| 9 | Criticising prior work | Any "failed to", "of little value", "neglects"? |
| 10 | Results without implications | Does each finding have a sentence saying what it means? |
| 11 | Wrong level of detail | Is the instrument named and justified? Is data detail excessive? |
| 12 | Too many footnotes | Ideally zero in the introduction |
| 13 | Irrelevant material | Does every paragraph speak to the research question? |
| 14 | Passive or third-person voice | "We estimate", not "regressions are estimated" |

## Banned-words and AI-tell pass (do not skip)

Run the draft against `references/banned-words.md` and the structural AI-tells
checklist in `references/writing-norms.md`. For introductions in particular:

- No em dashes or en-dash asides. Ranges only (2018--2025).
- Vary paragraph openers; no two consecutive paragraphs opening the same way.
- Vary sentence length; five consecutive same-length sentences is a tell.
- One "First... Second" enumeration at most, in the contribution paragraphs.
- Cut "crucially / importantly / notably / it is important to note" filler.
- Name the noun after "this" ("This result", not a naked "This").

## Output

- Write the section into the target file with the Edit tool, preserving
  surrounding labels and cross-references (`\label`, `\ref`).
- Report the paragraph map (which block each paragraph serves), the failure
  checklist result, and the banned-word pass result.
- Append a dated entry to the `lab_notebook`.
