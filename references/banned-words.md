# Banned Words and Phrases

## Hard Bans (never use)

| Banned | Replacement |
|--------|-------------|
| delve / delve into | examine, investigate, study, analyze |
| crucial | important, central |
| comprehensive | thorough, complete, detailed |
| multifaceted | complex, varied |
| utilize | use |
| leverage (verb for "use") | use, employ |
| facilitate | enable, allow, help |
| endeavor | effort, attempt, work |
| paramount | important, essential |
| myriad | many, numerous, various |
| plethora | many, abundance |
| noteworthy | notable (or just state the fact) |
| it is important to note that | [delete -- just state the thing] |
| it should be noted that | [delete] |
| in this regard | [delete or restructure] |
| due to the fact that | because |
| the vast majority of | most |
| at the present time | now, currently |
| as such | [delete or use "therefore" sparingly] |
| --- (em-dash) in LaTeX | Rewrite: use comma, semicolon, colon, period, or parentheses. Never use `---` in prose. |
| -- (en-dash) as parenthetical aside | NEVER use `--` for parenthetical insertions or asides in prose. Use comma, colon, semicolon, period, or parentheses instead. `--` is only for number ranges (e.g., 2002--2024) and compound modifiers (e.g., long--short). |
| underscores / underscoring | shows, emphasizes, demonstrates (Kobak r=13.8) |
| showcasing / showcase | showing, demonstrating (Kobak r=10.7) |
| pivotal | central, important (Liang top-4 AI marker) |
| intricate | complex, detailed (Kobak +117%) |
| meticulous / meticulously | careful, thorough (Kobak +137%) |
| illuminates / illuminate | reveals, shows, clarifies |
| unveil / unveils / unveiling | show, reveal, document |
| bolster / bolsters | support, strengthen |
| realm | field, area, domain (Liang top-4 AI marker) |
| landscape (metaphorical) | field, literature, area |
| foster | encourage, promote |
| encompass / encompassing | span, cover, include |
| enhancing | improving |
| exhibited | showed, displayed |
| aligns with | is consistent with, matches (IsGPT 16x) |
| Additionally, (sentence opener) | delete, or "also", "X is also Y" |
| whether or not | whether (Nikolov) |
| aforementioned | [delete; use "this" + noun] (McCloskey Rule 26) |
| it is easy to show that | [delete; just show it] (Cochrane) |
| as we will show / we will show | [delete or give forward ref: Section~X formalizes this] (Cochrane: no previewing) |
| shed light on | reveal, show, clarify (Kobak AI-corpus marker) |
| profound | deep, large, substantial (Kobak 2025) |
| grappling | addressing, confronting (Kobak + Liang AI marker) |
| commendable | [delete or be specific] (Gray +83%) |
| innovative | new (if truly novel) (Gray +30%, Liang) |
| versatile | flexible, adaptable (Liang AI marker) |
| in a manner that / in a way that | [state action directly] (verbose padding) |
| it is worth noting that | [delete; state the thing] (throat-clearing variant) |
| it is clear that / it is evident that | [delete; assert directly] (if clear, reader sees it) |
| one can see that | [delete] (passive hedge) |
| provide a foundation for | enable, support (nominalization + AI filler) |
| serves as (connector verb) | "is" (e.g., "is a proxy for") (AI connector) |
| plays a role in | [name the mechanism] (avoids naming cause) |
| stands in contrast to | differs from, contradicts (AI filler) |
| going forward | in future work, or [delete] (business-speak) |
| that said | [delete; use "however" or "but"] (AI filler transition) |
| taken together | [delete; state conclusion directly] (variant of banned "Together..."). **Exception:** allowed once to open a concluding synthesis sentence that combines several preceding findings. Never as a filler transition. |
| to be sure | [state qualification directly] (condescending hedge) |
| broadly speaking | [delete or quantify] (hedge + softener) |
| long-standing (intro opener) | [state the question directly] (cliche) |
| open the door to/for | [state what is now possible] (cliche metaphor) |
| reiterating | [delete] (gerund restatement tag) |
| as discussed in section X | [make the point here or use Section~\ref{}] (variant of "Recall from") |
| speaks to | is relevant to, bears on (vague connector) |
| a battery of | [name the specific checks] (cliche, finance-specific) |
| canonical (for data/methodology) | standardized, standard (overly formal register; use "standardized data source" not "canonical data source") |

## Soft bans: AI-register words (at most 1 or 2 per paper)
- significant/significantly (prefer "substantial", "material", "economically meaningful", or give the number)
- novel (prefer "new" or describe what's new)
- robust (fine in "robustness checks" but don't overuse)
- key (often filler)
- critical/critically (prefer "important" or be specific)
- highlights (prefer "shows", "reveals"; max 2 per paper)
- insights (prefer stating what was learned directly; max 1 per paper)
- compelling (prefer "strong" or just present the evidence)
- ultimately (often filler; delete or restructure)
- rather (as hedge, "rather large"; not in "rather than") (Nikolov)
- **"rather than": use it sparingly.** It is an AI-draft tell when overused, at roughly one per two pages or less in published work. Never use it twice in a paragraph. Keep it where the contrast is the claim, as in "fit noise rather than structure". Otherwise:
  - state the positive claim alone ("a target that cannot yet be verified", not "a target rather than a verified rate");
  - use a comparative ("limits performance more than the model does");
  - use "instead of" (finance rate about 0.1 per 1,000) or ", not X", sparingly.
- arguably (present evidence instead) (Nikolov); top-3 rate 0.02
- a variety of (name the types)
- the extent to which (prefer stating the result; top-3 rate 0.06)
- in general (quantify the exception where you can; top-3 rate 0.06)
- Indeed, as a sentence opener (top-3 rate 0.09; once per paper, after a claim it confirms)
- as noted above (restructure; variant of "Recall from")
- Importantly, Interestingly (top-3 rates 0.06 and 0.04; once per document at most, for the one point that really is the most important or surprising)
- Notably, Crucially (top-3 rates 0.04 and 0.01; avoid)

## Structural AI Tells to Avoid
- "Together, these results..." as a paragraph opener (max 1 per paper; vary with "Collectively," or restructure)
- "This finding" as sentence opener (max 1 per paper; vary: "The result", "The evidence", name the specific finding)
- "In this section, we..." throat-clearing (just start with the content)
- Naked "this" without a noun ("This implies..." → "This result implies...")
- "Notably," / "Crucially," as sentence-opening adverbs (delete or fold into the sentence). "Specifically," (top-3 0.19 per 1,000 as an opener) and "In particular," (0.17) are fine one at a time; "Importantly," at most once per document
- "Overall," as a paragraph opener (restructure)
- Uniform paragraph length (vary: some 2-sentence, some 6-sentence)
- Consecutive same-structure paragraph openers: No two consecutive paragraphs begin with the same grammatical construction (e.g., two adverb-comma openers, two "The..." openers). Vary: subject-verb, prepositional phrase, dependent clause. (GPTZero burstiness metric)
- Content-free meta-announcements: Delete any sentence that announces the next topic without providing content. "We now turn to X" → just start with the finding. Exception: one orienting sentence at section start if it names the specific question. (Sage peer-review guide 2025; Cochrane)
- "First...Second" enumeration overuse: Limit parallel enumeration to genuinely parallel, discrete items. For causal chains, use prose. Max one "First...Second" structure per subsection.
- Closing-summary paragraphs within sections: Do not end a section with a paragraph that merely restates. Each paragraph must advance the argument. Summary belongs in Conclusion only. (Detection research: "over-explanation without deepening")
- Symmetric hedges when data exist: Replace "can be positive or negative, depending on..." with the empirical answer when you have data.
- Gerund-phrase opener density: Max one gerund-phrase opener ("Using a large dataset, we...") per paragraph. High density is a syntactic AI tell. (Burstiness research)
- Padding appositives: Define a concept once. After definition, use the name without appositives restating the definition.
- Sentence length variation: Mix short declarative sentences (8-12 words) with longer compounds (25-40 words). Five consecutive sentences of similar length is an AI tell. Keep the standard deviation of sentence length at 14 words or more (top-3 papers 17; the frozen proposal 11). (GPTZero/Turnitin burstiness; Kobak 2025)
- Intensive reflexive pronouns as emphasis ("itself", "themselves"): When the pronoun adds emphasis but no semantic distinction, delete it. "rivals sampling uncertainty itself" → "rivals sampling uncertainty." When it distinguishes X from Y, make the contrast explicit instead: "the signal itself" → "the signal, not the mapping" or restructure. Max 2 uses of "itself/themselves" per paper, each earning its place.

## Never Stack Superlatives
Bad: "These results provide crucial new insights into this important phenomenon."
Good: "These results show that X."
