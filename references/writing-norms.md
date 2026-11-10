# Top Journal Writing Norms

This file is the standard on its own. Where `pipeline-config.md` sets
`writing_hub`, that pack adds a target voice, a numeric band, paragraph moves and
precision checks on top of these norms; with no hub configured, these norms are
the whole of the house style.

## Baseline stance
Write like an experienced empirical finance or real estate researcher addressing skeptical referees. Every sentence should earn its place.

## Tone
- Be precise, not dramatic.
- Prefer concrete nouns and verbs over promotional adjectives.
- Avoid inflated novelty claims.
- Do not say a result is "important" without explaining the economic mechanism or quantitative magnitude.
- Distinguish clearly between association, causal interpretation, and mechanism evidence.
- Do not use em dashes. Use commas, parentheses, colons, or separate sentences instead.
- Do not use "crucially," "notably," or other filler intensifiers; "importantly" and "interestingly" at most once per document. Degree words that grade a true claim (very, much, even, substantial, important) are fine at the finance rates in `references/banned-words.md`.
- Fewer words is not easier reading. Keep linking words (however, thus, that is, for example) at about 12 to 15 per 1,000 words and the optional "that".

## Introduction spine
A paragraph formula, one paragraph per block unless noted. The `empirical-intro`
skill operationalises it and carries the full failure checklist.

1. **Motivation, and what is missing.** Big-picture motivation with an explicit
   statement of the gap in current knowledge, and where there is one, the reason
   the gap persisted (hard-to-get data, no credible exogenous variation, no
   computational route). No more than half a page, ideally a third.
2. **What the paper does.** Methods clearly, ideally one paragraph. Name the
   instrument and why it is valid, if there is one. Avoid excessive data detail.
   Do not mention extensions here.
3. **What the paper finds, and what it implies.** Not a list: each finding
   placed in context with a sentence on what it means. Robustness compressed to
   one clause. Relate back to the motivation.
4. **Extensions, heterogeneity, mechanisms.** One paragraph each if unrelated;
   one describing plus one summarising if closely related. More than four
   paragraphs here is hard to justify.
5. **Literature contributions.** At most two paragraphs, framed as your
   contribution rather than as summaries of other papers. No separate
   literature-review section.
6. **End on the contributions.** No roadmap paragraph by default; if one is
   included, cap it at two sentences.

Do not cheat by making paragraphs very long: a formula satisfied by a
page-length paragraph has not been satisfied.

## Empirical papers: directional hypotheses over formal models
- An empirical paper does not need a formal model. The default is a Hypothesis Development section: state each mechanism in prose, support it from prior literature, and close with a directional, falsifiable prediction (H1, H2, ...). See the `hypothesis-development` skill and Damle & Sinha (2026, BAR) §2 as the worked model.
- Write a formal model only where it earns its place: the paper estimates structural parameters, the contribution is a quantitative bound or comparative static prose cannot deliver, or identification depends on a model-implied restriction. Otherwise, a model adds notation without adding identification, and a referee will read it as padding.
- If accounting identities or flow equations help, keep them in a short appendix and reference them from the body in words.
- A null result is motivated by competing hypotheses (a displacement force and an offsetting force), so the net sign is the empirical question, not a hedge.

## Theory and model exposition
- When discussing a theoretical model, lead with the economic story and intuition. Place Greek letters and formal notation in parentheses after the plain-language explanation.
- BAD: "An increase in $\alpha$ raises $\pi$ through the complementarity channel."
- GOOD: "An increase in the firm's AI adoption intensity ($\alpha$) raises operating profit ($\pi$) because AI-augmented workers complete tasks faster, reducing per-unit costs."
- Every model parameter should be introduced with its economic meaning first. The reader should understand the mechanism from the prose alone; the notation confirms the mapping.
- For model predictions, state the testable implication in words before referencing the proposition or equation number.

## Results writing protocol
- Lead each paragraph with the empirical point, not with a table number.
- BAD: "Table 3, Column 2 shows that the coefficient on X is 0.023 (t = 4.2)."
- GOOD: "Firms exposed to the shock reduce investment by 2.3 percentage points (Table 3, Column 2), equivalent to one-third of the sample standard deviation."
- Then identify the specification and sample.
- Then quantify the magnitude in economically meaningful units.
- Then interpret cautiously: what is the result consistent with?
- Then explain what remains uncertain or what the design cannot claim.

## Magnitude reporting
- Always report economic magnitudes alongside statistical significance.
- Translate into real-world units: dollars, percentage points, standard deviations, relative to the mean.
- Compare to benchmarks when available: "This effect is comparable in magnitude to [known effect from prior literature]."
- Do not rely on stars alone. Report t-statistics alongside coefficients.

### Making magnitudes intuitive (tiered translation)

A magnitude translation is only useful if the reader immediately grasps whether the effect is large or small. Use a three-tier approach:

1. **Statistical units** (minimum): SD change, percentage-point change relative to the sample mean.
2. **Real-world units** (standard): dollars per firm, basis points of return, square feet, months of rent.
3. **Anchored comparison** (best): compare to a familiar quantity the reader already understands.

- BAD (mechanical): "A one-standard-deviation increase in AI adoption is associated with a 0.8 percentage-point increase in NOI margin."
- BETTER (real-world units): "A one-standard-deviation increase in AI adoption is associated with a 0.8 percentage-point increase in NOI margin, equivalent to roughly $1.2 million in additional annual operating income for the median REIT."
- BEST (anchored): "A one-standard-deviation increase in AI adoption is associated with roughly $1.2 million in additional annual operating income for the median REIT, comparable to the cost savings from a typical energy retrofit (Eichholtz, Kok, and Quigley, 2013)."

The anchored version works because it connects to something the reader already knows. Good anchors include: known effects from prior literature, familiar policy changes, typical firm decisions, or household-scale equivalents.

## Related literature
- Do not dump a long neutral summary.
- Organize by disagreement, mechanism, method, or setting.
- State exactly how the present paper differs from the closest papers.

## Tables and figures
- Each should have a single reason to exist. If you cannot state it in one sentence, reconsider.
- Titles and notes should allow a reader to understand the object, sample, variables, and inference method without reading the text.
- Prefer clean, readable, economically interpretable displays over decorative visuals.
- Table notes should specify: dependent variable, sample, fixed effects, clustering, and observation count.

## Robustness discussion
- Name the threat, name the check, report the result, move on.
- Do not narrate every column of a robustness table.
- Group checks by category and summarize.
- If a check fails, discuss what it means rather than ignoring it.

## Discussion and conclusion
- Narrow the claim to what the design can support.
- Explain external validity limits and the conditions under which the result may not generalize.
- End with the economic lesson, not a generic restatement.

## Common failure modes
- Narrating columns instead of making economic arguments
- Vague contribution language or excessive throat-clearing
- Treating statistical significance as the economic result
- Excessive robustness discussion that obscures the main finding
- Hiding the identifying assumption or being vague about what FE absorb
- Claiming mechanism without addressing competing channels
- Using "consistent with" as a universal hedge without being specific

---

## Section-specific writing guidance

### Introduction
- Use the `empirical-intro` skill, which operationalises the paragraph formula above, applies the citation and voice discipline, and runs the banned-word and AI-tell pass.
- Start with the contribution, not the literature (Cochrane: "put the punchline right up front"). The result lands in paragraph 3.
- Three pages is a good upper limit (Cochrane).
- **Omit the roadmap paragraph.** Two reasons, and the second is the stronger. The advice to include one is explicitly scoped to PhD-student writing, and this is journal submission. And the observed norms measured from recent acceptances say most published top-3 papers carry none: a third of JF intros, half of JFE, one in five RFS. Cochrane agrees. If one is included for a venue that expects it, cap it at two sentences and never narrate section by section. This rule was briefly reversed to "include it" and then reversed back on the author's decision; both moves are recorded so neither is re-litigated from scratch.
- Do not start with philosophy ("Financial economists have long wondered...") or abstract literature gaps. Ground paragraph 1 in a concrete, recent event.
- **Few citations before the contribution paragraphs.** One motivational cite is enough, prefixed "e.g.," if it is one of many. Heavy early citation makes the field look crowded and works against your own contribution.
- **First person, active voice.** "We estimate", not "regressions are estimated".
- **Aim for zero footnotes** in the introduction.

### Literature review
- Place after the contribution is explained, not before. The reader cannot assess differentiation before understanding your paper.
- **Prefer no separate literature-review section at all.** Two contribution paragraphs inside the introduction is the target.
- Focus on the 2-3 closest papers and give proper credit (Cochrane).
- Do not write a Journal of Economic Literature style review. Keep it targeted.
- Frame each citation as your contribution, not as a summary of the other paper: "Unlike Doe et al. (2012), our model includes X, and we show this overturns Y" beats two sentences describing what Doe et al. built.
- Make the reason for each citation visible: "By focusing on adults, our study complements work on infant mortality (...)" beats "Other studies include (...)".
- Be generous in citations, and stay neutral. "We build on", "We extend", "Our findings complement" — never "Prior literature has failed to" or "Prior estimates are of little value because".

### Data and methodology
- Describe what you do first, then explain why, then compare to alternatives (Cochrane: "first describe, then explain, then compare").
- Start with the main specification. Do not do warmup exercises, extensive description of well-known datasets, or preliminary estimates before the main result.
- The theory or model should be the minimum required for the reader to understand the empirical results. Do not write a "general" model and then specialize it.

### Results
- Start each results section with the main finding, not with table descriptions.
- Nothing should precede the main result that the reader does not need to understand the main result (Cochrane).
- Give stylized facts in the data that drive your result, not just estimates and p-values.
- Follow the main result with robustness, not the other way around.

### Robustness
- Summarize checks rather than narrating every column.
- Most robustness details belong in an appendix (Cochrane).
- If a check fails, discuss what it means rather than burying it.

### Conclusion
- Keep it short. Do not restate all findings (Cochrane: "one statement in the abstract, one in the introduction, once more in the body should be enough").
- A short paragraph acknowledging limitations and suggesting implications is appropriate.
- Do not speculate or write a grant application for future research.
- End with the economic lesson, not a generic restatement.

---

## Structural AI tells checklist

Use this checklist during revision to catch patterns that flag AI-generated text. These complement the structural tells listed in `references/banned-words.md`.

- [ ] **Paragraph opener variety**: No two consecutive paragraphs begin with the same grammatical construction. Vary: subject-verb, prepositional phrase, dependent clause.
- [ ] **Sentence length variation**: Mix short declarative sentences (8-12 words) with longer compounds (25-40 words). Five consecutive sentences of similar length is an AI tell.
- [ ] **Reflexive pronoun check**: Max 2 uses of "itself/themselves" per paper. When the pronoun adds emphasis but no semantic distinction, delete it.
- [ ] **Gerund density**: Max one gerund-phrase opener ("Using a large dataset, we...") per paragraph.
- [ ] **Meta-announcements**: Delete any sentence that announces the next topic without providing content ("We now turn to X"). Exception: one orienting sentence at section start if it names the specific question.
- [ ] **Enumeration overuse**: Max one "First...Second" structure per subsection. For causal chains, use prose.
- [ ] **Closing-summary paragraphs**: Do not end a section with a paragraph that merely restates. Summary belongs in Conclusion only.
- [ ] **Symmetric hedges**: Replace "can be positive or negative, depending on..." with the empirical answer when data exist.
- [ ] **Padding appositives**: Define a concept once. After definition, use the name without restating the definition.
- [ ] **Uniform paragraph length**: Vary paragraph length (some 2-sentence, some 6-sentence).

See also `references/banned-words.md` for the complete hard-ban and soft-ban word lists with empirical evidence.

## Writing about AI, LLMs, and agentic systems

When a paper mentions language models or agentic systems, hold a controlled
vocabulary for the project and apply it consistently. What that needs:
- one term per concept, defined at first use and never varied afterwards;
- definitions taken from a citable source, not from a vendor's marketing;
- a list of the words that overclaim (reasons, understands, knows, decides),
  with what to write instead;
- a disclosure checklist covering the model, version, dates, prompts and
  temperature, and the usual order of an LLM method section.

Top journals lag AI practice. Use current terms, define each at first use, and cite an approved source.
