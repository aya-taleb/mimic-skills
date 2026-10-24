---
name: mimic-deploy
description: >-
  Puts your version live on your own domain, only after a preflight gate passes and you
  say yes. The gate blocks on open S1 or S2 bugs, missing must features, anything of the
  competitors left in the code (the linked rebrand sweep), secrets in the repo, failing
  security items, unchecked proof in the launch copy, and a missing or stub privacy policy
  or terms page (a real policy names the processors the app uses). Then
  production setup, env vars, DNS records, monitoring, backups and a tested rollback. For
  local businesses, a go-live checklist. Use when the user says "deploy", "ship it", "go
  live", "put it on my domain", "launch it", "is it ready to ship", "set up production",
  "DNS", "preflight", or after /mimic-launch. Never skips the gate.
---

# mimic-deploy

Going live is the one step that cannot be taken back quietly. Customers see it, search
engines cache it, and a competitor's lawyer can screenshot it. So this skill checks first,
shows the user everything, and only then asks for a yes.

## Reads and writes

Reads: `mimic/test/bugs.md`, `mimic/features.csv`, `mimic/brand.json`, `mimic/launch/`,
`mimic/architecture.md` (host, services), `mimic/backend.md` (env vars, checklist), the
code, and the business context.

Writes `mimic/deploy/preflight.md` (from the tool) and `mimic/deploy/runbook.md`
(template: `references/runbook-template.md`).

Tool:

```bash
python3 scripts/preflight.py --project .
```

It runs the checks below, writes `mimic/deploy/preflight.md`, and exits 1 while anything
blocks. It never deploys.

## Step 1: preflight

Run the tool and show the user the table as it is.

| check | blocks launch when | how |
| --- | --- | --- |
| bugs | any S1 or S2 not verified fixed | mimic-test's `bugs.py --gate` |
| parity | a must feature in `features.csv` is not built | reads the matrix, plus the linked `parity.py` score if installed |
| sweep | a competitor's name, domain or colour is left in the code | the linked replica-brand `sweep.py` with `mimic/brand.json` |
| secrets | a key or token is in tracked files, or `.env` is not ignored | pattern scan of tracked files |
| launch | the listing has errors, or proof claims are not confirmed | mimic-launch's `listing.py --proof` |
| security | any checklist item in `mimic/backend.md` is `fail` | reads the checklist |
| legal | a privacy policy or terms page is missing, under 150 words, has placeholders, or the policy doesn't name a processor the app uses | reads the pages; finds processors (Stripe, Supabase, Resend, Twilio, the host...) in `package.json`, `requirements.txt`, `.env.example` names and host files |
| payments | (asks, does not block) live keys, live webhook, one real refund | the user confirms |

A check that could not run is `not run`, and the gate stays closed. "Not run" is not
"pass", because the check that did not run is the one that would have caught it.

**Linked tools missing.** The sweep needs replica-brand and the parity score uses
replica-diff, both linked skills by Jake Schincariol. If the tool says they are not
installed, tell the user to run `python3 scripts/get_linked.py` from the mimic-skills
folder, start a new session, and rerun preflight. Do not write a stand-in sweep.

**Fixing failures.** For every check that is not `pass`, write one line. Give the check,
the fix, and the skill that owns it by name (`/mimic-test` for bugs, `/mimic-build` for missing
features, `/replica-brand` for leftovers, `/mimic-backend` for secrets and security,
`/mimic-launch` for proof and listing, the user and their lawyer for legal pages). Rerun
preflight after each fix.

Write `mimic/deploy/runbook.md` even while the gate is blocked, with what is known and
`{{to fill}}` for the rest, so the next deploy session starts from it. Say "rerun
preflight after each fix" in the reply.

**Legal pages.** A one-line page ("Privacy policy. Draft from our lawyer.") is not a pass,
whatever the user says. It protects nobody, and app stores and payment providers reject
it. A pass needs the full text on the page: what data is collected and why, how to ask for
deletion, and every processor by name with what it gets (for example "Stripe, payments";
"Twilio, phone numbers for text reminders"). If the tool lists processors the policy
doesn't name, show that list; the user or their lawyer adds them. You may draft a starting
version that names each processor, marked as a draft for a lawyer to check. Not legal
advice: say who to ask (a lawyer in their country, or a reputable policy generator).

Do not argue a failing check away. If you think a check is a false positive, say so in
one line and leave it failed. Then say what would make it pass (for a proof claim: cut it, or
add it to `proof_ok` with its source).

If the user asks to skip the checks and push anyway, decline to skip the bug gate, the
sweep and the secrets scan. Offer a private preview deploy instead (password protected or
an unlisted preview URL), which lets them see it live without customers or search engines
seeing it.

## Step 2: production setup

Write `mimic/deploy/runbook.md` as you go, so the next deploy is a checklist, not a memory.

- **Host**: from the architecture. A production project separate from preview.
- **Env vars**: every name from `.env.example`, set in the host's settings by the user,
  with live keys for production. List names, never values.
- **Database**: production instance, migrations run with the stack's migrate command,
  backups on, one restore tried.
- **Payments**: live mode products and prices, the live webhook endpoint added in the
  provider's dashboard with its new signing secret.
- **Email**: the domain records from mimic-backend added and verified in the provider.

## Step 3: the domain

The user owns the domain at their registrar. Give the exact records to add, from the
host's own instructions for this project, with what each does:

```
type   host   value                    what it does
A      @      {{from the host}}        points the bare domain at the host
CNAME  www    {{from the host}}        points www at the host
TXT    @      {{from email provider}}  lets the email provider send as you (SPF)
```

Never guess record values. Read them from the host's and email provider's dashboards or
docs for this project. HTTPS turns on at the host once DNS resolves; check it does.

## Step 4: monitoring

- **Errors**: an error tracker with alerts to the user's email or phone.
- **Uptime**: a check on the home page and the core loop's main route, every few minutes.
- **Analytics**: page views and the one launch metric from `mimic/launch/plan.md`. Respect
  the privacy policy; add a consent banner where the law needs one.
- **Logs**: kept long enough to debug a bad day, without personal data in them.

## Step 5: rollback

Write how to go back: redeploy the previous version on the host, and what to do with a
migration that cannot be undone (deploy a fix forward, restore from backup). Try the
rollback once on the preview deploy before launch day. A rollback nobody has tried is a
hope, not a plan.

## Step 6: the user's yes

Show: the preflight table, what will change (domain goes live, live payments on), the
rollback, and who gets alerts. Then ask plainly: "Go live now?" Deploy only on an explicit
yes in this session. Not on "looks good", not because the gate passed. If they say not
yet, leave everything ready and say what is left.

After go-live: open the live site, run the core loop once with a real low-value payment
and refund it, check an email arrives, and confirm the alerts work.

## Local businesses, services and physical products

Write the go-live checklist into `mimic/deploy/runbook.md` as checkboxes. It replaces most
of the above: the site or order page live on the
domain, booking or ordering tool in live mode, payments live and one real test order
refunded, Google Business Profile verified and matching the listing in
`mimic/launch/listing.json`, permits and insurance from the business's own plan confirmed
by the user (not legal advice; the city or county office is who to ask), staff checklists
printed, and a soft opening with friends or one office before the public date.

## Writing

Every file and reply is read by a busy founder. Plain words, sentences under 25 words, no
em dashes, no hype. Skip these words in everything you write:
delve, leverage, seamless, streamline, comprehensive, journey, unlock, elevate, empower, foster, robust, crucial, utilize, simple. <!-- allow-words -->
If the humanize skill is installed, run copy that a person will publish or send through it.

Write the reply for a founder who may not code. The table and files can stay technical; the
reply leads with plain words.
- Start each fix with what to do in everyday words, then the skill or command in brackets:
  "Make sure your passwords file is never uploaded (`/mimic-backend`)", not "`.env` not
  ignored, run `/mimic-backend`".
- Explain each technical term once, the first time, in a few words: S1 or S2 bug (one that
  stops people ordering or paying), secrets (keys and passwords for your services), `.env`
  (the file that holds them), DNS (the settings at your domain company that point your name
  at the site), webhook (how the payment service tells your site a payment went through),
  rollback (going back to the last working version), preflight (the check before going live).
- For a local business or a no-code setup, open the reply with the go-live items still
  open, each by name in one line: site live, payments live with one refunded test order,
  Google Business Profile, permits and insurance, soft opening. The code checks come after,
  one line each. The runbook holds the detail; the reply must still name every open item.
- Keep slash commands and file paths out of the opening lines. One "next" line at the end
  can name them.

## Output

`mimic/deploy/preflight.md`, `mimic/deploy/runbook.md`, and either "blocked by ..." with
the fix for each, or "ready for your go" and the question.

Next, after go-live: launch day in `mimic/launch/plan.md`, then the handoffs in
`mimic/launch/handoff.md` (biz-boost for leads and emails, the LinkedIn and Instagram plans).
