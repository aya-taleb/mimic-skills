---
name: mimic-architect
description: >-
  Turns the competitor recon and the review fixes into a plan you can build from: the stack
  or tools with a reason for each pick, the data schema with the rules that keep it
  correct, routes or API, outside services, monthly cost, risks, and a build order in
  slices that work end to end. Works for apps and for services, local businesses and
  physical products (tools, records and setup order instead of code). Use when the user
  says "plan the build", "what stack should I use", "design the database", "schema for my
  version", "how should I build this", "what tools do I need to run this", "architecture",
  or after /mimic-reviews and validate. Run it before /mimic-build.
---

# mimic-architect

A plan is only useful if the user can start on it Monday. So every choice here is tied to
something real: who builds it, what they already know, the budget, the deadline, and what
the reviews said customers need.

## Reads and writes

Reads, in the user's project:

- `mimic/recon.md` and `mimic/features.csv` (mimic-recon): type of business, core loop,
  screens or customer steps, flows, inferred data model, hard parts, size
- `mimic/fixes.md` (mimic-reviews): the fixes that make this version better
- `founder/validate.md` (validate): the demand test and its result
- the business context (founder-context): who it serves, stage, goals

Writes `mimic/architecture.md` (template: `references/architecture-template.md`) and, once
the stack is picked, a schema file in that stack's own format (for example
`mimic/schema.sql` or `prisma/schema.prisma`).

## Step 0: check the ground

- **No recon?** Stop and point to `/mimic-recon`. If the user wants to go on anyway, work
  from what they tell you and mark every inferred piece as a guess.
- **Validate missing or failed?** Say it plainly: a plan for something nobody asked for is
  the most expensive thing in this pack. Suggest running validate first. Go on only if the
  user says so, and write that choice at the top of the plan.
- **Asked to reuse the competitor's private API, code, database dump or customer data?**
  Decline that part. It breaks the clean room and usually the law. Plan an own version of
  the same job instead.

## Step 1: constraints first

Take what the business context already says. Ask in one batch only for what is missing.
If the user wants you to go on without answering, write your assumption in the table,
marked "assumed", so it is easy to spot and change.

1. Who builds it: the user, a developer, Claude in this repo? What do they already know?
2. Platform: web, iOS, Android, all three? Or no app at all?
3. Budget per month at launch, and the deadline.
4. Sensitive data: payments, health, kids, location? It changes hosting and checks.
5. Expected scale in the first six months, in plain numbers (or `{{unknown}}`).

The stack follows the answers, not taste. Write the answers at the top of the plan.

## Step 2: pick the stack or the tools

One row per layer: frontend, backend, database, auth, payments, email, hosting, file
storage, background jobs, analytics and errors. For each: the pick, one line on why it fits
the constraints, and the runner-up.

Pick boring, well documented tools the builder already knows. A known tool shipped is
worth more than a better one half learned. With no preference, a common web default is
Next.js with TypeScript and a managed Postgres (Supabase or Neon). Add the payment
provider's hosted checkout, a transactional email service, and a managed host. For mobile, a cross-platform framework such as Expo. Say these are
defaults, not the only answer.

**Not an app?** The "stack" is the set of tools the business runs on: the website, how
orders or bookings come in, payments or point of sale, the customer list and email, the
schedule, delivery or fulfilment, and where the records live (a spreadsheet is a fine
start). Same table, same reason per pick.

## Step 3: the data

Start from the inferred model in `recon.md`. For each entity: fields with types, keys,
relationships, and where it came from (screen or step IDs). Keep the confidence. Then add
the rules the data needs:

- primary keys, foreign keys, and what happens on delete
- unique and check constraints, especially the one that keeps the core loop correct
  (no double booking, no double charge, one active subscription per customer). Name it.
- indexes on the queries the core loop runs most
- timestamps in UTC, money in integer cents with a currency, soft delete where people
  expect undo
- who can read and write each table (row level rules if the database supports them)

Fixes from reviews often need data: a reminder needs a phone number and a sent-at time;
"swap a meal" needs a cutoff. Add those fields and say which fix they serve.

Write the schema file in the stack's format once the stack is agreed.

## Step 4: routes and services

- **Routes or API**: one line per route: method and path (or page), what it does, who can
  call it, which flow it serves (F01...).
- **Outside services**: each one through its official API or SDK, with the user's own
  account and keys. Name the webhooks the product must handle. mimic-backend wires them up.
- **Background jobs**: reminders, retries, cleanup, with the schedule.

## Step 5: build order

Vertical slices, each one usable on its own, each with a "done when" check a person can
run. The first slice is the core loop end to end, from the customer's first step to the
moment they get what they paid for, including how they pay or commit (test mode is fine).
Use fake data if you have to: for a
booking app, a guest books a real slot and both sides see it. Then the fixes that justify
the product. Then the rest by priority from `features.csv`.

```
Slice 1  Core loop: guest books a slot
         builds: S07, S08, S09, S10; tables users, event_types, bookings
         done when: a booking made on the public page shows on the host's list,
                    and a second booking for the same slot is refused
```

Five to eight slices is normal. More means the scope is too big; say so.

## Step 6: cost and risks

- **Monthly cost at launch**: one row per paid service. Use a number only if you read the
  pricing page in this session, with its URL and the date. Otherwise write
  `{{check pricing page}}` and the link. Never guess a price.
- **Vendor facts**: plan limits, review times, registration rules and free tier terms
  change. Write them as "check:" with the vendor's docs link, not as facts.
- **Risks**: the three to five things most likely to sink the build (an integration with
  strict review, a hard realtime part, a permit, a supplier), each with a way to test it
  early.

## Writing

Every file and reply is read by a busy founder. Plain words, sentences under 25 words, no
em dashes, no hype. Skip these words in everything you write:
delve, leverage, seamless, streamline, comprehensive, journey, unlock, elevate, empower, foster, robust, crucial, utilize, simple. <!-- allow-words -->
If the humanize skill is installed, run copy that a person will publish or send through it.

## Output

`mimic/architecture.md` and the schema file, then a short summary: the stack in one line,
the core constraint in the schema, the first slice, and the biggest risk.

End your reply with the next step, in this shape:

- Apps with screens: "Next: `/replica-design`, then `/mimic-build`. replica-design is a
  linked skill by Jake Schincariol. If it is not installed, run
  `python3 scripts/get_linked.py` from the mimic-skills folder and start a new session.
  Tell it to use `mimic/` where it says `replica/`."
- Services and local businesses: "Next: `/mimic-build`. Design is skipped: no app screens."
