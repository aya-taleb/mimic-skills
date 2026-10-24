# Job spec: mimic-architect

Written before reading any other version of this skill.

## The job

A founder has a recon map of one or more competitors and a list of fixes from real reviews.
They need a plan they can build from on Monday: what to build it with, how the data is
shaped, what the routes are, and in what order to build it so something works end to end
early.

## Inputs

- `mimic/recon.md` and `mimic/features.csv` (from mimic-recon): type of business, the core
  loop, screens or customer steps, flows, inferred data model, hard parts, size.
- `mimic/fixes.md` (from mimic-reviews): the fixes that make this version better.
- `founder/validate.md` (from validate): did the demand test pass?
- Founder context: who builds it, their skills, budget, deadline.

## Outputs

- `mimic/architecture.md`: stack with a reason per choice, schema, routes or API, services,
  build order, risks, monthly cost at launch scale.
- A schema file in the stack's own format when the stack is picked (SQL, Prisma, or similar).

## What good looks like

- Every stack choice is tied to a constraint the founder gave (skills, budget, platform,
  time). Boring, well known tools by default. No choice without a reason.
- The schema comes from the inferred model, keeps the evidence and confidence, and adds
  the rules the data needs: keys, unique and check constraints, indexes on the hot queries.
  The constraint that stops the core loop from breaking (double booking, double charge) is
  named.
- Fixes from reviews show up in the plan (a table, a field, a job, a route).
- Build order is vertical slices with a done check each. The core loop works end to end
  first, then the rest.
- Third party services go through their official APIs and SDKs with the user's own keys.
- Costs: real numbers only with the pricing page link and date. Otherwise a placeholder.
- Not an app (service, local, product): the "stack" is the tools (site, booking, payments,
  point of sale), the data to track, and the order to set up each step of the customer path.

## Edge cases

- Validate not run or failed: say so, suggest running it first, proceed only if the user
  says so.
- Asked to reuse the competitor's private API, code, or database dump: refuse that part,
  plan an own version.
- Missing recon: stop and point to mimic-recon, or work from what the user gives and mark
  the guesses.

## Handoff

Next: replica-design (linked, reads mimic/ instead of replica/), then mimic-build.
