# Job spec: mimic-backend

Written before reading any other version of this skill.

## The job

Add the parts that make the product real and safe: sign in, payments, email, and the
integrations the recon found, all through official APIs with the user's own accounts. Then
check it against a security list before anything goes near real users.

## Inputs

- `mimic/architecture.md` (stack, services, schema)
- `mimic/features.csv` (which integrations are must)
- `mimic/fixes.md` (billing and trust complaints to fix in the product)
- The code from mimic-build.

## Outputs

- Code for auth, payments, email, integrations.
- `mimic/backend.md`: each service, why, the account and keys the user must create, env var
  names (never values), webhooks and how they are verified, test mode steps, the security
  checklist with pass, fail, or not checked.
- `.env.example` with names only.

## What good looks like

- Official SDKs and APIs only. The user creates the accounts and keys.
- Secrets live in env vars, never in code or the repo. `.env` is ignored by git.
- Payments: hosted checkout or the provider's elements, so card data never touches our
  server. Webhooks are signature checked and handled once (idempotent).
- Billing complaints from reviews turn into product behavior (easy cancel, renewal notice).
- Email: a transactional provider, the domain records to set, and an unsubscribe for
  anything that is not transactional.
- OAuth integrations ask for the smallest scopes that work.
- Security checklist covers auth, sessions, access checks on every record, input checks,
  rate limits, secrets, logging without personal data, backups, data export and delete.
- Nothing is marked passed without a check.
- Not an app: payment links or point of sale, booking tool, email list with consent, and the
  same secrets and access rules for the tools picked.

## Edge cases

- Asked to call the competitor's private API, reuse their keys, or log into a platform as
  the user: refuse and offer the official route.
- Asked to store card numbers or passwords in plain text: refuse, explain the safe way.
- No keys yet: build against test mode and leave clear steps.

## Handoff

Next: mimic-test.
