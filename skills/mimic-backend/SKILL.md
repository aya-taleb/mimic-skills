---
name: mimic-backend
description: >-
  Wires up the parts that make your version real and safe: sign in, payments, email, and
  the integrations the recon found, all through official APIs and SDKs with your own
  accounts and keys. Secrets in env vars, signed and idempotent webhooks, billing
  complaints from reviews fixed in the product, then a security checklist marked pass,
  fail or not checked. Use when the user says "add login", "set up auth", "add Stripe",
  "take payments", "send emails", "connect Google Calendar", "add the integrations",
  "backend", "is it secure", "security check", or after /mimic-build. Also covers payment
  links, booking tools and email lists for services and local businesses.
---

# mimic-backend

This is where a demo becomes something people trust with their money and data. Most of
the damage a young product can do happens here, so take each piece slowly and check it.

## Reads and writes

Reads: `mimic/architecture.md` (stack, services, schema), `mimic/features.csv` (which
integrations are must), `mimic/fixes.md` (billing and trust complaints), the code from
mimic-build, and the business context.

Writes:

- the code for auth, payments, email and integrations
- `.env.example` with variable names only, never values
- `mimic/backend.md` (template: `references/backend-template.md`): each service, why, the
  account and keys the user creates, env var names, webhooks and how they are verified,
  test mode steps, and the security checklist

## The rules

- **Official routes only.** Each service through its official API or SDK, with an account
  the user creates and keys the user pastes into their own env. Never call a competitor's
  private API, reuse someone else's keys, or log into a platform as the user.
- **Secrets never touch the repo.** Env vars only. `.env` is in `.gitignore`. Ask the user
  to paste keys into `.env` themselves rather than into the chat.
- **Card data never touches the server.** Use the payment provider's hosted checkout or
  its own embedded fields. Never store card numbers. If asked to, decline and explain.
- **Passwords**: use the auth provider, or a slow hash (argon2id or bcrypt) if the stack
  rolls its own. Never plain text, never reversible.
- **Nothing is marked passed without a check.** "Looks fine" is `not checked`.
- **Costs**: if a service is paid beyond a free tier, say so, link its pricing page, and
  wait for the user's yes before they sign up for a paid plan.

## Step 1: auth

Pick from the architecture. A hosted auth provider or the framework's well known auth
library is the default; rolling your own is rarely worth it.

- sign up, sign in, sign out, password reset or magic link, email verification
- sessions: http-only, secure, same-site cookies; sensible expiry; sign out everywhere
- social sign-in only for providers the users actually use, with the smallest scopes
- **access checks on every record**: a user can only read and write their own rows. Put
  the rule in the database (row level security) or in one shared check every route uses.
  This is the bug that leaks other people's data, so test it on purpose.

## Step 2: payments

- products and prices created in the provider by the user (list them from
  `mimic/launch/pricing.md` if it exists, else from the architecture)
- hosted checkout or the provider's elements, in **test mode** first
- a webhook endpoint that verifies the signature with the provider's SDK, handles each
  event once (store the event id and skip repeats), and is the only thing that grants or
  removes access
- the customer portal or an equivalent for cancel and update card

**Fix the billing complaints in the product.** If reviews said "hard to cancel" or
"surprise renewal", build the fix here: cancel in one click from settings, an email
before renewal, receipts that show what was charged. Note each fix with its evidence.

## Step 3: email

- a transactional email provider for sign-in, receipts, reminders and notices
- the domain records the provider gives (SPF, DKIM, and a DMARC policy). List them for the
  user to add at their registrar. mimic-deploy checks them.
- any email that is not transactional (newsletters, promotions) needs consent and a
  working unsubscribe. Marketing to people who did not opt in is not something this skill
  sets up.

## Step 4: integrations

For each integration in `features.csv` (calendar, maps, messaging, storage...):

- the official API, the auth method (OAuth with the smallest scopes that work, or an API
  key the user creates), and the webhooks or polling it needs
- what the product does when the integration fails or a token expires
- rate limits from the provider's docs, linked

If a feature needs the competitor's own data or network, it cannot be integrated. Mark it
`skip` in `features.csv` with the reason.

## Step 5: security checklist

Go through `references/security-checklist.md` and mark each item `pass` (with how you
checked), `fail` (with the fix), or `not checked` (with why). Fix every `fail` you can
now. Put the result in `mimic/backend.md`. mimic-deploy reads it, and any `fail` there
blocks launch.

## Services and local businesses

Same rules, different tools: payment links or a point of sale instead of custom checkout,
a booking tool instead of a booking engine, an email list with consent, a shared sheet or
small admin page for orders. Still: accounts in the user's name, keys in env vars or the
tool's settings, two-factor sign-in on every admin account, and the same checklist for
who can see customer data.

## Always

Write `mimic/backend.md` on every run, even a short one, with the checklist as it stands.
mimic-deploy reads it. End the reply with "Next: `/mimic-test`" once the pieces asked for
are in place.

For every `must` integration in `features.csv`, either build it, or write in
`backend.md` why it is not built yet. A check marked `pass` names the test or command
that proved it, and the check has to cover the whole item (a search for one key prefix
does not prove "no secrets in code"). Reading the code is "reviewed, not tested", which
is `not checked`. "Nothing exists yet" and "by design" are `not checked`, not `pass`.

Package versions, plan limits and vendor rules you did not read in this session are
written as "check:" with the docs link, not as facts.

## Edge cases

- **No keys yet**: build against test mode, leave the env var names in `.env.example`,
  and give the steps to get each key.
- **"Just hardcode the key for now"**: decline. Put it in `.env` and show how.
- **Asked to scrape a platform or automate a user's social accounts**: decline. Offer the
  official API if one exists, or a manual step.

## Writing

Every file and reply is read by a busy founder. Plain words, sentences under 25 words, no
em dashes, no hype. Skip these words in everything you write:
delve, leverage, seamless, streamline, comprehensive, journey, unlock, elevate, empower, foster, robust, crucial, utilize, simple. <!-- allow-words -->
If the humanize skill is installed, run copy that a person will publish or send through it.

## Output

Code, `.env.example`, `mimic/backend.md` with the checklist, and a summary: what is wired,
what is in test mode, what the user must create or paste, and any `fail` left.

Next: `/mimic-test`.
