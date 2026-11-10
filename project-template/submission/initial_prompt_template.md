# Writing the initial prompt

The opening message of the first research session is the project's first act.
It is preserved verbatim in `submission/initial_prompt.md`, submitted, and read
by a discussant. It also carries the `theme`, which is the pipeline's stated
input: *give it a general question area, get back detailed research designs the
data can carry.*

This file is scaffolding for writing that message. It is **not** the prompt, it
carries no theme, and it can sit in the repository before the project begins
without becoming the artifact the ordering rule is about.

## What this prompt is for, and what it is not for

The machinery already carries the rules. `pipeline-config.md` sets the paths,
models, thresholds and budgets; `AGENTS.md` sets the two rails; the skills carry
their own gates and refusals; `workflow/pipeline-design.md` §4 is the gate table.
**None of that goes in the prompt.** Restating it produces two sources for the
same rule, and when they drift the agent has to guess which one is live.

What the prompt supplies is the part no file can derive: the question area, why
you think it is live, what would make the paper worth writing, and the
constraints that are real. That is also the part a discussant is reading for.
The call asks for the highest research quality per unit of human expertise, not
for the smallest possible prompt, and a one-line "write me a finance paper" is a
weak exhibit — it maximises apparent autonomy while showing no judgment to
assess.

The prompt must not specify the finding, the identification strategy, or the
specification. Not because that would be cheating, but because three things
break at once: the funnel's F0/F1 layers exist to generate and displace designs
and cannot do that against a design handed to them; the pre-registration would
have to disclose the design as retrospective; and the record would misstate
where the idea came from.

## The template

Fill the four blocks and send it as the opening message. Aim for what fits on
one screen. Length is not the goal and neither is brevity: every sentence should
be one the machinery cannot derive.

```text
I want to run this project end to end through the S0-S8 pipeline, to a paper
I could submit. You drive; I decide at the gates.

THEME
<Two to four sentences naming the question area, the setting, and the economic
mechanism you think is at work. A question area, not a question: the funnel's
job is to produce the specific designs. Name the friction or the agent whose
behaviour is in question, not the regression.>

WHY I THINK IT IS LIVE
<Two or three sentences. What changed, what is newly measurable, or what the
literature seems to assume and you doubt. Say plainly how confident you are;
"I suspect but have not checked" is useful information and "this is
established" is a different instruction.>

WHAT WOULD MAKE IT WORTH DOING
<One or two sentences on the bar. What would you want to be able to say at the
end, and what result would make you drop it. This is what G1 and G2 are
weighing, and it is the one input the calibration set cannot supply.>

WHAT I KNOW ABOUT THE CONSTRAINTS
<Anything real that bounds the work: the deadline, data you already have access
to, sources you know are closed, a method you cannot defend. Facts and their
consequences, not rules you would like followed.>

Where you have judgment, use it and tell me what you decided. Where the
decision is mine, stop and put it in front of me as one packet. If a rule in
the config and something I have written here disagree, the config is right and
the disagreement is worth telling me about.
```

## Why each block is shaped that way

**A question area rather than a question.** `run-pipeline` refuses a theme that
is a single word with no question area in it, and it never narrows a broad theme
to make the run easier. A theme pitched too tight collapses the funnel into
finding variants of an answer you already chose; pitched too loose it is the open
swarm path wearing a theme's clothes. Two to four sentences with a mechanism in
them is the size that works.

**Your confidence is an instruction.** "I suspect X" and "X is established" send
the funnel to different places: the first is a question the paper could answer,
the second is a premise it would build on and that F0 will try to displace. State
which one you mean, because the agent cannot tell from a flat sentence and will
pick one.

**The bar is the input nothing else carries.** The calibration set anchors what a
top-3 acceptance looks like in general. It cannot know what *you* would consider
a paper worth three weeks. G1 is a taste gate, and this block is the taste.

**Constraints as facts, not commands.** This is where prompts most often go
wrong here. If you want free sources only, set `data_access: free_only` in
`pipeline-config.md` — do not write "only use free data" in the prompt while the
config says `any`. Two sources for one rule is the failure mode: the agent has
to guess which is live, and the guess is invisible until something built on it
breaks. The same goes for `private_spine`, `g1_threshold` and `usable_min`.
Anything with a config key belongs in the config; the prompt carries what has no
key.

## Two checks before you send it

**Is every sentence true?** An instruction that holds ninety percent of the time
degrades the whole prompt, because the model applies it in the ten percent too.
"Always verify every number against the source" is that kind of sentence: it is
right about headline results and wasteful about a row count. Either scope it
("the numbers that carry a claim") or leave it out and let the claim ledger do
its job, which it already does.

**How could a careful reader misread this?** Read each sentence and ask what a
well-intentioned person who had never met you would do with it. "Keep it simple"
could mean a clean design or a thin one. "I don't have much time" could mean cut
scope or work faster. If a sentence has two readings, say which you mean or cut
it.

## What happens after you send it

In this order, in the same session:

1. `/init-submission` — validates the floor and populates
   `submission/initial_prompt.md` with this message verbatim. This is what
   releases the hooks from fail-closed.
2. Set `theme:` in `pipeline-config.md` from the prompt. Set `usable_min:` too
   if you already know the unit; it is owed before the first pilot, not before
   F0, so it is reasonable to set it once the theme's unit of observation is
   settled.
3. Hand control to `run-pipeline` at S0.

Run `python3 submission/preflight.py` first, before any of it. If the
harness-logging check fails, the session is not being recorded and the prompt
you just wrote is not in the submission record.
