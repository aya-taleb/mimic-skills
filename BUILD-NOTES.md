# Build notes

Built 2026-10-23, unattended. What is done, what is not, and what Aya should look at.

## Not finished

- **Synced skills are not in the repo yet.** market-research, validate (entrepreneur-skills),
  competitors (biz-ready-skills) and launch-video (multimedia-skills) are listed in
  `skills.json` and arrive with the sync step. Until then `/validate` and the other three do
  not exist in a mimic-only install, and mimic-run says so.
- **Linked skills were never run.** replica-design, replica-diff and replica-brand got a
  read-through only (the protocol says so). `get_linked.py` was not run, because it fetches
  from GitHub. The first real test of the full chain is on Aya's machine.
- **No test ran a real browser, app server or payment.** Build, backend and test runs wrote
  code and plans. The test sandbox did not allow `npm install`, Playwright or Stripe test
  mode. So those outputs are judged on what they wrote, not on whether the code runs.
- **Evals use fictional data on purpose** (Tidyslot, Slotbook, MeetMate, Noon Wheels,
  Lunchbox Club, Curbside Eats, `.example` domains). No real company or review is in the repo.

## Needs Aya

- **Check the first-line notice on the 3 reworked skills** and the CREDITS wording for Jake.
  It follows CONVENTIONS section 3 and 7, but it is his name on it.
- **Decide on the replica/ vs mimic/ folder gap.** Jake's linked skills write to `replica/`.
  Ours write to `mimic/`. mimic-run tells the linked skills to use `mimic/`, and the file
  names line up, so it works in practice. A cleaner fix would be to ask Jake for a
  `--folder` option, or to switch our folder to `replica/`. I kept `mimic/` because
  CONVENTIONS section 5 says so.
- **Real-business check before launch.** Run `/mimic-recon` and `/mimic-reviews` once on a
  real competitor of one of her own ventures, privately, before posting the repo. The
  evals are fictional, so a real run is the only test of the live feeds.
- **Trademark on "mimic".** Not checked. Worth a quick USPTO search before the launch post.

## Calls I made

See TESTING.md, "Calls I made", for the full list. The ones worth a second look:

- mimic-reviews ships `collect.py` that reads saved feed files but never fetches. The skill
  fetches the official feed URL with Claude's own fetch tool (or the user saves it). That
  keeps the tool offline per CONVENTIONS section 9.
- `listing.py` gained a proof check that flags "trusted by", counts, star ratings and quoted
  testimonials in launch copy. mimic-deploy's preflight fails while any are unconfirmed.
  This can flag real proof too; the user adds it to `proof_ok` once checked.
- `preflight.py` treats "not run" as blocking. A missing linked tool keeps the gate closed.
- mimic-run never pushes optional steps (market-research, competitors) as "next". It lists
  them as "optional first" until recon starts.

## Fix round after review

- User data moved out of `~/.claude` (protected by Claude Code) to `~/.founder`: business files, social folders and the media ledger. Tools honor `FOUNDER_HOME`; tests use a temp one.
- mimic-reviews: the "0 a month budget" line came from an unquoted heredoc (`cat > mimic/fixes.md <<E`), where `$50` became `$5` (empty) plus `0`. The skill now says to write fixes.md with the Write tool, quote any heredoc delimiter, and grep for amounts that lost their `$`.
- mimic-deploy: the legal check fails stub pages (under 150 words or with placeholders) and a privacy policy that doesn't name each processor found in package.json, requirements.txt, .env.example names or host files. Tests and an app-preflight grader added.
- mimic-run `status.py` reads founder-context from `FOUNDER_HOME` or `~/.founder`.
