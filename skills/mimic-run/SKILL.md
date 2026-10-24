---
name: mimic-run
description: >-
  The front door of the mimic pack. Reads the project's mimic/ and founder/ folders, shows
  where you are in the chain (research, reviews, validate, build, launch), checks which
  linked and shared skills are installed and how to get the missing ones, then runs the
  next step. Use it whenever someone says "where am I", "what's next", "continue",
  "pick up where we left off", "start the mimic flow", "I want to build a better version
  of X", "copy this competitor but better", "run the whole thing", or opens a project that
  has a mimic/ folder and is not sure which skill to use. Also use it when another mimic
  skill is missing its input files and the user does not know which step makes them.
---

# mimic-run

People lose track of a nine-step chain. This skill reads what is on disk, says plainly
where the user is, and starts the next step. It never guesses progress from memory,
because files are the only record that survives between sessions.

## What it reads and writes

Reads, in the user's project:

- `mimic/` (recon, features, reviews, fixes, architecture, build log, tests, brand, launch, deploy)
- `founder/` (market, competitors, validate, context)
- the business context from founder-context: `founder/context.md`, else
  `~/.founder/active` and `~/.founder/businesses/<slug>.md`

Writes nothing of its own. The step it starts writes its own files.

## Step 1: run the status check

```bash
python3 <this skill's folder>/scripts/status.py --project .
```

It lists each step as done, partial or to do, the demand test result, must-have features
built, open S1 and S2 bugs, and which linked skills are installed. It reads files only.
If Python is not available, check the same files by hand with the table in
`references/chain.md`.

Show the user the output as it is (in a code block), then add two or three lines in plain
words: where they are and what the next step does. Do not guess how long a step takes.

## Step 2: handle what is missing

**Linked skills.** replica-design, replica-diff and replica-brand are Jake Schincariol's
(MIT). They are not copied into this repo, so they may not be installed. When the next
step needs one and the check says NOT installed, tell the user to run:

```bash
python3 scripts/get_linked.py
```

from the mimic-skills folder (the status output prints the full path). It fetches them
from Jake's repo at a pinned commit into `~/.claude/skills/`. Then they need a new session
for the skills to load. Do not try to rebuild a linked skill from memory. His tools have
tests yours would not.

**Linked skills read replica/, not mimic/.** When you run one, tell it to read and write
`mimic/` wherever its instructions say `replica/`. The file names line up on purpose
(`features.csv`, `fixes.md`, `brand.json`, `design/tokens.json`), so the tools work as
they are. Pass paths to the tools, for example
`python3 <replica-diff folder>/parity.py mimic/features.csv`. If the user already has a
`replica/` folder, offer to move its files into `mimic/`.

**Shared skills.** market-research, validate, competitors and launch-video come from
Aya's other repos and are copied in by a sync step. If one is missing, say which repo it
comes from (see `references/chain.md`) and offer to skip it if it is optional.

**No business context.** Ask once for the name, who it serves and the stage, or point to
founder-context. Do not invent it.

**Partial steps.** If a step is partial because a file is missing, say which file and
which skill writes it. Never write a stand-in file to make a step look done.

## Step 3: respect the gates

Two gates stop the chain. When one is closed, stop there in this reply: say what it
protects, give the options, and wait. Do not start the next skill in the same reply.

- **Demand test said stop or no-go.** Building first and finding out later is the most
  expensive way to learn. Offer two ways forward: rerun validate with a narrower angle
  (name one from `mimic/fixes.md`), or go ahead on purpose. "I don't care" or "just do
  it" said before seeing the risk is frustration, not a decision. Ask one plain question,
  such as "Build anyway, knowing 9 of 40 signed up?", and go on only on a clear yes to
  it. Then write that choice and the date at the top of the next skill's output.
- **Open S1 or S2 bugs.** Deploy waits until they are fixed. Point to mimic-test.

Validate is skipped by the check until reviews are done, because a test built on the
real complaints is a better test.

## Step 4: run the next step

Ask "Run /<next skill> now?" and wait for a yes, unless the user already said "go on" or
"run the whole thing". If yes, load that skill and follow it. After it finishes, run the
check again and show the new state.

Even when you go straight into the next skill, your final reply still starts with the
status block and the two or three lines from Step 1 (including the design skipped line
when it applies). The user needs to see where they were before reading what was done.

"Run the whole thing" still stops at each gate and at every point where a skill needs
the user: accounts and keys, anything that costs money, and the go-live yes. A chain
that runs past those is a chain the user cannot trust. Whenever the user asks for the
whole chain, say these stop points in your reply, so they know what to expect.

## Types of business

The chain is the same for an app, a service, a local business or a physical product.
What changes is inside each step: recon maps customer steps instead of screens, and
design (replica-design) is skipped when there are no screens to build. The check reads
the type from `mimic/recon.md`. When it marks design skipped, say so in one line: "Design
is skipped: no app screens for this business."

## Rules

- Files on disk are the truth. If a file says something different from what the user
  remembers, show both and ask.
- Never mark a step done for the user. Only the step's own files count.
- Never run a linked skill that is not installed by writing a stand-in for it.
- Never post, send or publish anything. Skills write; the user posts and sends.

## Writing

Every file and reply is read by a busy founder. Plain words, sentences under 25 words, no
em dashes, no hype. Skip these words in everything you write:
delve, leverage, seamless, streamline, comprehensive, journey, unlock, elevate, empower, foster, robust, crucial, utilize, simple. <!-- allow-words -->
If the humanize skill is installed, run copy that a person will publish or send through it.

## Output

The status, two or three lines on where the user is, any install command needed, and
the question to start the next skill. See `references/chain.md` for every step, its
files and its home repo.
