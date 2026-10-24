# Job spec: mimic-build

Written before reading any other version of this skill.

## The job

Turn the plan into a working product, one slice at a time, without copying anything the
competitor owns. For an app, that means screens with every state. For a service, local
business or physical product, it means each step a customer goes through, made real: the
page, the form, the message, the checklist.

## Inputs

- `mimic/architecture.md` (build order, stack, schema)
- `mimic/recon.md` (screens or customer steps, flows, states seen)
- `mimic/features.csv` (what to build, priority)
- `mimic/fixes.md` (the fixes that make it better)
- `mimic/design/` (tokens and component specs from replica-design, if run)

## Outputs

- Code or assets in the user's project.
- `mimic/features.csv` with the `clone` column filled honestly (yes, partial with a note, no).
- `mimic/build-log.md`: per slice, what was built, states covered, what is left, how to run it.

## What good looks like

- Follows the build order. The core loop works end to end before any extra screen.
- Each screen has its states: empty, loading, filled, error, and small screen.
- Every word on screen is written fresh. Nothing lifted from the competitor's copy.
- Icons, fonts and images are open licensed or the user's own. Screenshots are reference only.
- The fixes from reviews are built into the slice they belong to, not left for later.
- `partial` is used when it is partial. A feature is `yes` only when it runs.
- Small steps the user can check: how to run it, what to click, what should happen.

## Edge cases

- Asked to copy the competitor's HTML, CSS, JavaScript, images or text: refuse that part,
  build an own version of the same function.
- No architecture yet: build only the first slice with a stated assumption, or point to
  mimic-architect.
- Feature depends on content the competitor licenses (a catalogue, a network): skip it and say why.

## Handoff

Next: mimic-backend for auth, payments, email and integrations, then mimic-test.
