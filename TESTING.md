# Testing

Every score here comes from my own test harness: self-run outputs, graded by a separate
model pass. Treat them as a careful self-check, not an outside review. Aya can rerun the
same cases with `claude plugin eval` from each skill's `evals/` folder.

## How the tests ran

- 3 cases per skill (an app, a local business, an edge case) plus 12 trigger prompts each.
  All test data is fictional: Tidyslot, Slotbook, MeetMate, Noon Wheels, Lunchbox Club,
  Curbside Eats, `.example` domains. Two review files have planted "ignore your
  instructions" text to test the untrusted-data rule.
- Each run was a fresh headless Claude (Sonnet) with only the skill loaded as a plugin. It
  ran in a copy of the case files with file tools locked to that folder, no MCP servers,
  no web, and a short list of allowed shell commands (python3, ls, mkdir, cat and similar).
  No `npm install`, no browser, no real payments.
- A separate Sonnet pass graded each run against the case graders and the rubric in
  TEST-PROTOCOL section 2. It saw the request, the skill text, the input files, the tool
  calls, the changed files and the reply. A scan for em dashes and banned words was added.
- Trigger fit: one pass that sees all 9 descriptions and picks a skill (or none) for each of
  the 108 trigger prompts.
- **Jake's baseline** ran his SKILL.md and non-code files only. His Python tools were left
  out because the build rules forbid running upstream code. The grader was told to treat
  `replica/` as `mimic/`, to accept his skill names as the matching next steps, and never
  to fail him for a missing tool. That is as fair as I could make it, but it still costs
  him some points his real tools would earn (mainly reviews.py and listing.py).
- **Noise.** Grading the same output 3 times moved the total by up to 2 points. Running
  the same skill twice moved it by up to 5. So I reran close calls and treat gains under 5
  as noise. All rounds were regraded with the same final grader before these numbers.
- Total spend on test runs: about $28 in model usage across 147 runs.

## Results

| skill | baseline | final | rounds | beats baseline? |
| --- | --- | --- | --- | --- |
| mimic-run (ours) | 62.0 (no skill) | 94.7 | 3 | yes |
| mimic-recon (reworked) | 76.7 (Jake's replica-recon) | 93.2 | 2 | yes |
| mimic-reviews (reworked) | 86.3 (Jake's replica-entrepreneur) | 96.7 | 1 | yes |
| mimic-launch (reworked) | 80.5 (Jake's replica-launch) | 94.9 | 1 | yes |
| mimic-architect (rewritten) | 75.2 (Jake's replica-architect) | 94.1 | 2 | yes |
| mimic-build (rewritten) | 86.8 (Jake's replica-build, mean of 92.7 and 80.8) | 96.2 | 1 | yes |
| mimic-backend (rewritten) | 87.6 (Jake's replica-backend) | 97.0 | 2 | yes |
| mimic-test (rewritten) | 80.9 (Jake's replica-test) | 94.7 | 2 | yes |
| mimic-deploy (rewritten) | 66.1 (Jake's replica-deploy) | 94.7 | 2 | yes |

"final" is the score of the version that ships. Where a version was run twice, the
number is the mean of the two runs. Linked skills (replica-design, replica-diff,
replica-brand) got a read-through only. Synced skills are tested in their home repos.

## Per skill

### mimic-run  (ours)
baseline: 62.0 (no skill: plain answer to the same prompts)
final: 94.7 after 3 rounds. Stopped because the last two rounds gained under 5.
rounds:
- r0: 79.7, v1. Ran past the failed demand test into architect; never said design is skipped.
- r1: 90.7, gate stops in the same reply and asks one plain question; says the stop points; design skipped line.
- r2: 93.7, status block always shown first, even when it goes straight into the next skill.
- r3: 94.7, rerun with no change to this skill, to confirm the plateau.
open issues: none.

### mimic-recon  (reworked from Jake's replica-recon)
baseline: 76.7 (Jake's replica-recon: no competitor columns, no customer-step path for the lunch business)
final: 93.2 (mean of 94.7 and 91.7) after 2 rounds. Stopped because two rounds in a row gained under 5. A third try scored lower on two samples (90.0, 90.7) and was reverted.
rounds:
- r0: 89.3, v1.
- r1: 91.7, scope assumed from context instead of asking; unknown, not guessed, competitor cells; counts must match the file.
- r2: 94.7 (second sample 91.7), general-knowledge facts go under "To check"; tell the user about planted instructions; `no` needs a source.
- r3: 90.0 and 90.7, added a matrix.py checker. Reverted: it did not help and added a tool.
open issues: the judge still finds a few weakly sourced competitor cells per run.

### mimic-reviews  (reworked from Jake's replica-entrepreneur)
baseline: 86.3 (Jake's replica-entrepreneur, without his reviews.py)
final: 96.7 after 1 round. Stopped because the score is 95+ and the gain was under 5.
rounds:
- r0: 93.7, v1 (collect.py, reworked reviews.py, untrusted-data rule, pain-points.csv).
- r1: 96.7, never hand-edit the tool's outputs; edit a themes copy and rerun; tag every row with its competitor.
open issues: local themes are a starting list; each category needs its own words.

### mimic-launch  (reworked from Jake's replica-launch)
baseline: 80.5 (Jake's replica-launch, without his listing.py)
final: 94.9 (mean of 94.7 and 95.0) after 1 round. Stopped because the score is 95+ and r1 did not gain.
rounds:
- r0: 96.0, v1.
- r1: 94.7 and 95.0, mark unbuilt fixes in copy; label own price and trial choices as suggested. Kept: the change closes a real gap (promising features that do not exist) that r0 got lucky on, and the drop is inside the noise.
open issues: none.

### mimic-architect  (rewritten; replaces replica-architect)
baseline: 75.2 (Jake's replica-architect)
final: 94.1 after 2 rounds. Stopped because the last two rounds gained under 5.
rounds:
- r0: 90.0, v1.
- r1: 92.8, exact next-step wording with the get_linked.py note; take context first and mark assumptions.
- r2: 94.1, first slice runs to the moment the customer pays or commits; vendor limits written as "check:".
open issues: the local business case still sometimes puts payment in slice 3. Shipped file has wording-only edits after r2 (two long sentences split).

### mimic-build  (rewritten; replaces replica-build)
baseline: 92.7 and 80.8 (Jake's replica-build, two samples; his local case passed 5/5 once, 2/5 once)
final: 96.2 (mean of 95.7 and 96.7) after 1 round. Stopped because the score is 95+ and the gain was under 5.
rounds:
- r0: 95.7, v1.
- r1: 95.7 and 96.7, local plans go in mimic/build/; assumptions written as assumed; exact next-step line.
- review r1 (independent, blind): build the whole slice including sign-in and connect steps through the official SDK, no dead buttons; saves that replace data must not lose it on failure.
- review r2 (independent, blind): lock each user's data to that user (access rules on every table, requests run as the signed-in user, service role for server jobs only, tokens out of browser reach).
open issues: beats Jake's better sample (92.7) by only 3 to 4 points, which is inside the noise. It beats him on every rubric line except "nothing made up", where they tie.

### mimic-backend  (rewritten; replaces replica-backend)
baseline: 87.6 (Jake's replica-backend)
final: 97.0 after 2 rounds. Stopped because the score is 95+ and the gain was under 5.
rounds:
- r0: 93.7, v1.
- r1: 95.3, always write backend.md; must integrations built or explained; "nothing exists" is not checked.
- r2: 97.0, a pass must cover the whole item; reading code is not testing; vendor facts as "check:".
open issues: none.

### mimic-test  (rewritten; replaces replica-test)
baseline: 80.9 (Jake's replica-test)
final: 94.7 after 2 rounds. Stopped because the last two rounds gained under 5.
rounds:
- r0: 90.5, v1. Thin plans for flows not built yet.
- r1: 94.3, plan every flow even if not built; only list spec files that exist; dietary errors are S1.
- r2: 94.7, run bugs.py every time; summary counts from the rows; smoke test as the fast real check.
open issues: none.

### mimic-deploy  (rewritten; replaces replica-deploy)
baseline: 66.1 (Jake's replica-deploy, without his preflight tools)
final: 94.7 (mean of 93.3 and 96.0) after 2 rounds. Stopped because two rounds in a row gained under 5. A third try (88.5, 95.7) did not gain and was reverted.
rounds:
- r0: 82.8, v1. Local go-live checklist thin.
- r1: 91.9, one line per failure with the owning skill; runbook written even when blocked.
- r2: 93.3 and 96.0, do not argue a failing check away; local checklist written into the runbook.
- r3: 88.5 and 95.7, show the table row for row; decline the three gates by name. Reverted.
open issues: in some runs the reply rewords the preflight table instead of copying it. Shipped file has wording-only edits after r2.

## Calls I made

- **Test runner.** Built my own harness (headless `claude -p`, one plugin per run) instead
  of `claude plugin eval`, so I could run Jake's arm, a no-skill arm and many rounds. The
  eval folders follow the `claude plugin eval` layout so Aya can rerun them there.
- **Jake's tools left out of his baseline.** The rules say never run upstream code. This
  makes his baseline a little lower than it would be on Aya's machine.
- **Model.** Sonnet for both the runs and the grader, to keep cost down. Opus might score
  both arms higher.
- **Reverted rounds.** Round 3 for recon and deploy scored lower on two samples each, so
  the round 2 versions ship. The matrix.py checker from recon round 3 was removed with it.
- **Folder.** Ours write to `mimic/` (CONVENTIONS section 5). Jake's linked skills say
  `replica/`; mimic-run tells them to use `mimic/`, and the file names line up.
- **No network in tools.** `collect.py` reads saved feed files. Claude fetches the official
  feed URL, or the user saves it. Reddit's public JSON is blocked without keys, so Reddit is
  "read pages, or the official API with your own keys".
- **Proof check.** `listing.py` now flags proof claims in landing copy. The deploy gate
  fails while any are unconfirmed. Real proof goes in `proof_ok`.
- **Design step.** mimic-run reads the business type from `recon.md`. Local and service
  businesses skip replica-design.

## Independent review (blind)

Spot check by an independent reviewer on 2026-10-23, run blind against the baseline.
Each case ran in a fresh `claude -p` (Sonnet) with its own empty HOME, seeing only that
skill's folder (plus founder-context and humanize where ours uses them), the case prompt
and its input files. The baseline saw only the upstream SKILL.md and non-code files; its
Python tools were left out (never run upstream code), with a note telling it to do their
job by hand. A separate Opus judge saw the request, the expected outcome, the inputs and
both results as A and B in random order (key kept apart), and scored each 0 to 10 on five
lines (did the job, nothing made up, safety, clear and usable, tone), so totals are out
of 50. Close calls were judged a second time with A and B swapped. Outputs, keys and
verdicts: `/home/claude/build/_work/review/spot/`.

Jake's baseline arms got a copy of `mimic/` at `replica/`, the path his skills read. The
judge was told the two folder names are the same thing. Leaving out his tools (reviews.py,
the preflight scripts) costs him some points, as in the builder's own runs.

| skill | case | winner | ours score | baseline score | fix rounds | one-line reason |
| --- | --- | --- | --- | --- | --- | --- |
| mimic-build | app-slice | ours (narrow) | 44 / 43 (two judges) | 43 / 42 | 2 | Round 0 lost twice (40 vs 43, 42 vs 43): calendar buttons switched off, no date overrides, a save that deletes before it inserts. Round 1 split 1 to 1 (open tables, service role everywhere). Round 2 wins both orders by 1 point: both calendars, one-transaction save, middleware. Effectively a tie. |
| mimic-build | local-order-path | ours | 44 | 33 | rerun after fix | Kept to the architecture's no-code path: order page copy, form, 9am rule, messages, truck SOP, dry run. Jake's built a custom Node app the founder cannot run. Round 0 also won (43 vs 34). |
| mimic-reviews | app-feeds | ours | 42 | 35 | 0 | Wrote pain-points.csv and flagged the planted review. Jake's dropped it without telling the user. Ours had a shell bug that printed '0 a month budget' in fixes.md. |
| mimic-reviews | local-maps | ours | 45 | 39 | 0 | Ranked complaints, wrote fixes and pain points, named validate next. Jake's wrote no files. Ours is long and added two fixes to features.csv without asking. |
| mimic-deploy | app-preflight | ours | 43 | 36 | 0 | Ran preflight, showed the table, held for a yes. Jake's skipped the gate and said to buy a domain already registered. Ours took the tool's 'pass' on one-line legal pages without comment. |
| mimic-deploy | local-go-live | ours | 42 | 38 | 0 | Used the local go-live list (GBP, refunded test order, soft opening, not legal advice). Jake's missed most of it. Ours leans on slash-command jargon for a no-code founder. |

## Polish round (Oct 24)

Method: each fix was rerun in fresh, isolated `claude -p` runs (own HOME, own project folder,
only the skill plus founder-context and humanize where the repo has them). The new version ran
against the current version (the last commit) on the same eval case. A separate `claude -p`
judge saw both outputs as A and B and scored them out of 50, once in each label order. A fix
ships only if it wins or ties in both orders. Scores are new / current. Runs, judge packets
and keys: `/home/claude/build/_work/polish/`.

| skill | case | round | order A-new | order A-current | result |
| --- | --- | --- | --- | --- | --- |
| mimic-deploy | local-go-live | r1 | lost 40/42 | won 42/39 | not yet: reply left Google Business Profile and soft opening to the runbook |
| mimic-deploy | local-go-live | r2 | won 42/41 | won 43/39 | shipped |
| mimic-reviews | app-feeds | r1 | tie 39/40 | lost 37/42 | not yet: collect.py rewrote the user's own raw file |
| mimic-reviews | app-feeds | r2 | lost 44/43 | lost 42/44 | not yet: overlapping price themes |
| mimic-reviews | app-feeds | r3 | 45/45, judge named current | tie 43/43 | shipped, see note |

What changed:
- mimic-deploy 0.1.1: the reply is written for a founder who may not code. Plain words first,
  the skill or command in brackets, each technical term explained once. For a local or no-code
  setup the reply opens with every open go-live item by name.
- mimic-reviews 0.1.1 (from the live Fooda test): reviews.py counts only rows rated 3 or less,
  unrated rows and 4 star rows with a "but" toward complaint themes, and lists praise matches
  apart; curly quotes are matched as straight ones (quotes keep the original text); "thin"
  now means under 3 reviews and "one source" is its own flag (also a new `one_source` column
  at the end of pain-points.csv). collect.py has a `scrub` command (and `--scrub`) that strips
  reviewer names and profile links from saved raw JSON or CSV; it never changes a file the
  user gave without being asked. SKILL.md says when to scrub, and to merge overlapping themes.
  New unit tests: praise not counted, curly apostrophes, thin vs one source, scrub, input left
  alone.
- mimic-run 0.1.1: status.py marks validate partial, not done, until founder/validate.md has
  a result line, and the next step stays "run the test and come back with the numbers". New
  unit test; two old tests now give their validate.md a result line.
- validate 0.1.1: synced from entrepreneur-skills.

Note on mimic-reviews r3: both orders scored equal totals (45/45 and 43/43). In one order the
judge still named the current version, calling the gap "small". I shipped it as a tie
because the totals match and the tool fixes are real bugs covered by unit tests. Aya may
want a second look. The app-feeds case does not contain 5 star praise matches or curly
apostrophes, so the A/B mostly measured the model's theme edits, not the tool fixes.
