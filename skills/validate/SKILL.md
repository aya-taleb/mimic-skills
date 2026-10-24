---
name: validate
description: Tests whether people want an idea before the founder builds it. Names the riskiest assumption, designs 1 to 3 cheap demand tests (fake door, waitlist, pre-order, concierge), sets and locks pass and fail lines before anything runs, writes the copy for the waitlist or pre-order page, and later reads the results into a go, pivot or stop call. Writes founder/validate.md. Use it when someone says "how do I validate this", "should I build this", "test demand", "fake door test", "will people pay for this", "make me a waitlist page", "pre-order page", "I'll decide based on signups", "here are my test results", "did my test work", or after market research or customer interviews. Use it for any waitlist or coming-soon page for an unlaunched idea, since that page is a demand test. Never makes up results or social proof.
---

# validate

Find out if people will act on the idea, cheaply, before the founder spends months
building. Then read the results honestly, against lines set in advance.

Two modes. Pick from the message:

- **Design**: no test yet. Name the risk, design the tests, lock the lines, draft the page.
- **Read results**: they have numbers back. Judge them against the locked lines.

Every run writes `founder/validate.md`, even when the founder only asked for a page or a
quick answer. The page is only useful as a test if its lines are written down first.

## What you read and write

- **Reads** the business file (`founder/context.md`, else the active one under
  `~/.founder/`). Goals give the numbers the pass lines work back from. If there is
  none, say so in one line, ask for the goal in the same message, or offer
  `/founder-context`. If they're in a hurry, carry on and label your starting lines as
  assumptions to swap for their numbers.
- **Reads** `founder/market.md` ("what we don't know yet") and
  `founder/discovery/evidence.md` if they exist. Their open guesses are the test candidates.
- **Reads** competitor pain points if they exist: `mimic/fixes.md` (the recommended angle
  and its riskiest assumption) and `mimic/pain-points.csv` from mimic-reviews, and the
  Complaints table in `founder/competitors.md`. A test of the angle the reviews point to
  beats one built on guesses. Quote their counts as the tool wrote them.
- **Writes** `founder/validate.md` (the plan, the page copy, later the results and the
  call) and `founder/validate-plan.json` (the locked lines the tool reads).

## Design

### 1. Name the riskiest assumption

List the three or four guesses the idea rests on (people have the problem, they'll pay
this price, they'll find us through this channel, we can deliver at this cost). Pick the
one that, if wrong, kills the idea and has the least evidence so far. Say why in two
lines. Testing an easy assumption first feels productive and proves nothing.

### 2. Design 1 to 3 tests

Pick from fake door, waitlist, pre-order and concierge (`references/test-types.md`).
Prefer the test where people give up the most: money beats an email, an email beats a
click. For each test write: what it is, who sees it and how they get there, what you
count, the cost in money and time, and the end date.

Three is the most. A founder running five tests at once runs none of them well.

### 3. Set the pass and fail lines, then lock them

For each test: a **pass line** (at or above, it's a go signal), a **fail line** (below,
it's a stop signal), a **minimum sample** and an **end date**. Between the two lines is
"unclear". Work the pass line back from the founder's goal where you can, and show that
math. If you can't, label the line as a starting assumption and say why.

Write them to `founder/validate-plan.json` (format in the script's header) and lock them:

```bash
python3 <skill-dir>/scripts/testplan.py lock founder/validate-plan.json
```

`<skill-dir>` is the folder this SKILL.md is in. Locking stamps the date and a
fingerprint, so if anyone moves a line after seeing results, the read flags it. That's
the whole point: lines set after the fact always get set to "it worked".

### 4. Draft the test page copy

For a fake door, waitlist or pre-order, draft the page copy in `founder/validate.md`
(and in a page file too, if the founder asked for one):
headline, one line on who it's for, three short lines on what they get, the call to
action, and for a pre-order the price, the delivery date and the refund promise.

- Write the full copy into `founder/validate.md` under "Page copy", word for word, even
  if you also write a page file. A pointer ("see index.html") isn't enough: the plan file
  is what the founder and the next skills read.
- Use only claims the founder can stand behind today. No testimonials, logos, user
  counts or "as seen in" unless they're real and in the business file's proof. Features
  too: describe only what the founder said the product does, and leave
  `{{what it does, in one line}}` where you don't know.
- If asked for fake proof (a made-up join counter, invented testimonials), say no in a
  line and say why: it misleads the people signing up, and it ruins the test, because
  signups would measure the fake proof, not the idea. Then do the rest of the job.
- A fake door says on the next screen that it isn't built yet. A pre-order states the
  date and the refund. Taking money for something with no honest date is not a test.
- Run the copy through the humanize skill if it's available, and show its score. If it
  isn't, check by hand for long dashes and stock phrases, and say so.
- The founder publishes the page. Point them to any page builder or form they already
  use; don't sign them up for anything that costs money without a yes.

If the test spends money (ads), show the budget and wait for the founder's yes. Default
cap $5 for anything this skill runs itself; ad budgets are the founder's call, in their
own ad account.

## Read results

1. Get the numbers from the founder: the count for each test and the denominator
   (visitors, people asked). Don't estimate missing numbers. If one is missing, ask.
2. Put them in a small results file and run the read:

   ```bash
   python3 <skill-dir>/scripts/testplan.py read founder/validate-plan.json founder/validate-results.json
   ```

   The tool says pass, fail, unclear, too early or no data for each test, and flags any
   line that moved after the lock.
   Keep the numbers you report to what the tool printed. Don't mix a test's count with
   the business goal ("4 pre-orders is 40% of the 10-office goal") unless they measure the
   same thing.
3. Make one call, in `founder/validate.md` under "Results". Pick one, not "pivot or
   retest". The founder came for a decision:
   - **Go**: the riskiest assumption passed. Name the next riskiest one, or the next step.
   - **Pivot**: it failed or was unclear, but the evidence points at a change (a different
     buyer, price or offer). Name the one change and the retest. Add the retest to
     `founder/validate-plan.json` as a new test with its own lines and end date, and run
     `lock` again so the new lines are fixed before it runs.
   - **Stop**: it failed and nothing in the evidence points to a better version. Say it
     plainly, and say what was learned. Stopping early is a good result; it saves months.
   If the plan was never locked, or a line moved, say the read is soft.

## Rules

- **Lines before results.** Never set or change pass and fail lines after seeing numbers.
- **Never invent results**, sample sizes or benchmark rates. A "typical conversion rate"
  with no source is a guess; label it.
- **Honest tests only.** No fake scarcity, no fake reviews, no taking money without a
  real date and refund. Not legal advice: for pre-orders, say to check consumer rules
  where they sell.
- **The founder runs it.** Draft pages and posts; never post, run ads or message people
  for them.

## Finish every run with

1. The files written, with paths.
2. For design: the tests and their lines in a short list, and the end date. For results:
   the verdict per test and the call.
3. What the founder does next, and the next skill by name (below).

## Next step

After design: "Publish the page, send traffic, and come back with the numbers on
<end date>", then name `/validate` again for the read. After a go: `/competitors` or the next launch skill if installed. After a
pivot: `/customer-discovery` on the new segment. After a stop: `/market-research` on the
next idea.
