---
name: mimic-build
description: >-
  Builds your better version slice by slice from the architecture and the recon, clean
  room: every screen with all its states, or for a service or local business every step
  the customer goes through (order page, forms, messages, checklists). Writes every word
  fresh, uses open or owned assets, builds the review fixes into the slice they belong to,
  and keeps features.csv honest. Use when the user says "build it", "start building",
  "build the first slice", "make the booking page", "code the core flow", "build the
  order page", "set up the customer steps", "next slice", or after /mimic-architect or
  /replica-design. Refuses to copy a competitor's code, text, images or logo.
---

# mimic-build

The aim is a working product the user can click through after every slice, not a big
reveal at the end. Small, checked steps catch wrong turns while they are cheap.

## Reads and writes

Reads, in the user's project:

- `mimic/architecture.md` (stack, schema, build order with "done when" checks)
- `mimic/recon.md` (screens or customer steps, flows, states seen)
- `mimic/features.csv` (what to build and its priority)
- `mimic/fixes.md` (the fixes that make it better)
- `mimic/design/` (tokens and component specs, if replica-design ran)
- the business context (founder-context) for tone and who it serves

Writes:

- code or assets in the project
- `mimic/features.csv`, the `clone` column, filled honestly
- `mimic/build-log.md`, one entry per slice (template below)

## The clean room

The product does the same jobs as the competitor's, in its own way. That protects the
user from takedowns and gives customers a reason to switch.

- **Copy what it does, never what it owns.** No code, HTML, CSS, scripts, images, icons,
  logos, fonts, photos, menu text, or marketing copy from a competitor. Screenshots in
  `mimic/screens/` are for looking at, never for tracing or shipping.
- **If asked to copy any of it**, say no to that part and build an own version of the same
  function. Explain in one line why: it is their property, and it is easy to spot.
- **Write every word fresh**: labels, buttons, empty states, errors, emails. Use the brand
  voice if `mimic/brand.md` exists, else the tone in the business context.
- **Assets**: an open icon set (Lucide, Phosphor, Heroicons, Tabler), open fonts (Inter,
  Source Sans, IBM Plex and similar), and the user's own photos or placeholders marked
  `TODO: own photo`.
- **Licensed content and networks are out.** If a feature depends on what the competitor
  licenses or owns (a catalogue, their users, partner deals), mark it `skip` with a reason.

## Step 0: check the ground

- No `mimic/architecture.md`? Build only the core loop as a first slice, write down the
  stack you assumed at the top of the build log, and suggest `/mimic-architect` next.
- No design tokens? Use a plain neutral theme with clear roles (background, surface, text,
  muted text, accent, danger) so replica-brand can swap the values later.

## Step 1: one slice at a time

Take the next slice from the build order. Before writing code, list:

- the screens or steps it covers, from `recon.md`
- every state each one needs: empty, loading, filled, error, no permission, small screen
- the fixes from `fixes.md` that belong in this slice
- the "done when" check from the architecture

Then build it. Keep the project runnable after each slice. If it is a new project, set up
the skeleton first with the stack's standard starter, and say the commands.

Build the fixes inside the slice they belong to. A reminder fix belongs with booking, not
in a "later" pile. Fixes are why this product exists.

Build the whole slice, not its easy half. Every screen and state the architecture and
recon list for it gets built, including the sign-in and "connect" steps those screens
depend on. When a step needs an outside service (OAuth sign-in, a calendar connect), build
the working flow through the official SDK with keys from env vars. mimic-backend then
checks and hardens it: scopes, webhooks, token storage, the security list. Why: a button
that does nothing is a dead end the user clicks on day one, and the slice is not done.
Defer a piece only when it truly cannot work yet, and then say so in the reply and the log.

## Step 2: check the slice

Run the "done when" check yourself where you can: start the app, run the type checker or
linter, hit the route. If you cannot run it here, say so and give the user the exact steps
to check it, with what they should see.

Look for the states you listed. An empty state you did not build is a blank screen a real
customer will see on day one.

## Step 3: record it honestly

Update `mimic/features.csv`: `yes` only when it runs, `partial` with a note on what is
missing, `no` otherwise. The parity score later depends on this being true.

Add an entry to `mimic/build-log.md`:

```
## Slice 1: Core loop, guest books a slot  (YYYY-MM-DD)
built: S07 booking page, S08 pick a time, S09 details, S10 confirmed
states: empty (no slots), loading, filled, error (slot taken), mobile
fixes in this slice: time zone confirm step (fixes.md #3)
how to run: npm run dev, open /book/demo
done when: passed (second booking for the same slot refused with a clear message)
left: reschedule link (next slice)
```

## Services, local businesses and physical products

The slices are the steps of the customer path in `recon.md` (C01, C02...). Build what each
step needs, with every "state" of that step: sold out, late, wrong order, refund.

- **Online parts**: a landing or order page, an order or booking form, confirmation and
  reminder messages, a small admin view or a shared sheet for incoming orders.
- **Offline parts**: a written checklist or SOP for each step (prep, pickup, delivery,
  handover), the message templates staff send, a partner or supplier sign-up form.
- The "done when" check is a dry run: place a test order, follow the checklist, receive
  the messages.

Use the tools picked in the architecture (a booking tool, a form, a sheet). Do not build
custom software where a tool does the job.

## Where files go

Code goes where the stack puts it. Plans, specs, checklists and message templates for a
service or local business go in `mimic/build/` so the other skills can find them.

## Rules

- Every choice you make that is not in the inputs (a time window, a default, a price) is
  written as "assumed" in the build log, so the user can change it.

- Never mark a feature `yes` that does not run.
- Never paste a competitor's text, even "for now". Placeholders are fine: `{{headline}}`.
- Keep secrets out of the code. Use env vars; mimic-backend sets them up properly.
- Lock each user's data to that user from the first slice: access rules on every table
  (row-level security policies, or the stack's own version), and requests that run as the
  signed-in user. Keep the service role or admin key for server jobs only. Keep OAuth
  tokens where the browser cannot read them. Why: an open table leaks every customer at
  once, and it is much harder to add later.
- A save that replaces the user's data must not lose it if it fails halfway. Write the new
  rows before removing the old ones, or do both in one transaction or upsert.
- If a slice is too big for one pass, say so up front, finish part of it well, and log the rest.

## Writing

Every file and reply is read by a busy founder. Plain words, sentences under 25 words, no
em dashes, no hype. Skip these words in everything you write:
delve, leverage, seamless, streamline, comprehensive, journey, unlock, elevate, empower, foster, robust, crucial, utilize, simple. <!-- allow-words -->
If the humanize skill is installed, run copy that a person will publish or send through it.

## Output

The slice built, `features.csv` and `build-log.md` updated, then a short summary: what
works now, how to see it, what is next.

End the reply with: "Next: the next slice (name it), then `/mimic-backend`, then
`/mimic-test`." Run `/mimic-run` to see where you are.
